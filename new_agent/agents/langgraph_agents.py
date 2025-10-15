"""
LangGraph-based Enhanced Agents with streaming and tool call tracking
"""

from typing import Dict, Any, List, Optional, AsyncGenerator
from datetime import datetime
import json

from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from langchain_core.tools import BaseTool
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

from new_agent.core.langgraph_state import AgentState, StreamingEvent, create_streaming_event_generator
from new_agent.tools.dummy_tools import dummy_tool_registry


class LangGraphBaseTool(BaseTool):
    """Wrapper to make dummy tools compatible with LangGraph"""
    
    name: str
    description: str
    
    def __init__(self, dummy_tool):
        super().__init__(
            name=dummy_tool.name,
            description=dummy_tool.description
        )
        self._dummy_tool = dummy_tool
    
    def _run(self, **kwargs) -> Any:
        """Execute the dummy tool"""
        import asyncio
        try:
            # If tool has async execute method
            if hasattr(self._dummy_tool, 'execute'):
                if asyncio.iscoroutinefunction(self._dummy_tool.execute):
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    try:
                        return loop.run_until_complete(self._dummy_tool.execute(**kwargs))
                    finally:
                        loop.close()
                else:
                    return self._dummy_tool.execute(**kwargs)
        except Exception as e:
            return {"error": str(e), "tool": self.name}


class LangGraphEnhancedAgent:
    """Enhanced agent using LangGraph for state management and streaming"""
    
    def __init__(self, agent_name: str, agent_description: str, capabilities: List[str]):
        self.name = agent_name
        self.description = agent_description
        self.capabilities = capabilities
        
        # Initialize OpenAI model
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.1,
            streaming=True  # Enable streaming
        )
        
        # Create tools from dummy tool registry
        self.tools = self._create_langgraph_tools()
        self.llm_with_tools = self.llm.bind_tools(self.tools)
        
        # Create the graph
        self.graph = self._create_graph()
        self.compiled_graph = self.graph.compile()
    
    def _create_langgraph_tools(self) -> List[LangGraphBaseTool]:
        """Create LangGraph-compatible tools"""
        tools = []
        
        # Get relevant tools for this agent
        agent_tools = self._get_agent_specific_tools()
        
        for tool_name in agent_tools:
            dummy_tool = dummy_tool_registry.get_tool(tool_name)
            if dummy_tool:
                tools.append(LangGraphBaseTool(dummy_tool))
        
        return tools
    
    def _get_agent_specific_tools(self) -> List[str]:
        """Get tools specific to this agent"""
        tool_mapping = {
            "LinkedInAgent": ["linkedin_search", "linkedin_profile_analysis"],
            "InstagramAgent": ["instagram_insights", "instagram_analytics"], 
            "GmailAgent": ["gmail_send", "gmail_compose"],
            "ResearchAgent": ["web_search", "data_analyzer"],
            "SummarizerAgent": ["summarizer", "report_generator"],
            "OrchestratorAgent": ["task_router", "workflow_manager"]
        }
        return tool_mapping.get(self.name, list(dummy_tool_registry.tools.keys())[:3])
    
    def _create_graph(self) -> StateGraph:
        """Create the LangGraph workflow"""
        
        def agent_node(state: AgentState) -> AgentState:
            """Main agent reasoning node"""
            messages = state["messages"]
            
            # Create agent-specific prompt
            system_prompt = f"""You are {self.name}, a specialized AI agent.
            
Your role: {self.description}
Your capabilities: {', '.join(self.capabilities)}

Current task: {state['query']}

Available tools: {[tool.name for tool in self.tools]}

Analyze the task and decide what action to take. You can:
1. Use tools to gather information or perform actions
2. Provide a direct response if you have enough information
3. Ask for clarification if the task is unclear

Be specific about your reasoning and tool usage."""
            
            # Add system message if not present
            if not messages or not isinstance(messages[0], HumanMessage):
                messages = [HumanMessage(content=system_prompt)] + messages
            
            # Update state with current agent
            state["current_agent"] = self.name
            
            # Call LLM with tools
            response = self.llm_with_tools.invoke(messages)
            
            # Update messages
            state["messages"].append(response)
            
            return state
        
        def tool_node(state: AgentState) -> AgentState:
            """Tool execution node"""
            messages = state["messages"]
            last_message = messages[-1]
            
            if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
                tool_outputs = []
                
                for tool_call in last_message.tool_calls:
                    tool_name = tool_call["name"]
                    tool_args = tool_call["args"]
                    
                    # Find and execute tool
                    for tool in self.tools:
                        if tool.name == tool_name:
                            try:
                                result = tool._run(**tool_args)
                                tool_outputs.append(ToolMessage(
                                    content=json.dumps(result),
                                    tool_call_id=tool_call["id"]
                                ))
                                
                                # Update state with tool result
                                state["tool_results"][tool_name] = result
                                
                            except Exception as e:
                                tool_outputs.append(ToolMessage(
                                    content=f"Error: {str(e)}",
                                    tool_call_id=tool_call["id"]
                                ))
                            break
                
                # Add tool messages to state
                state["messages"].extend(tool_outputs)
            
            return state
        
        def should_continue(state: AgentState) -> str:
            """Determine if we should continue or end"""
            messages = state["messages"]
            last_message = messages[-1]
            
            # If last message has tool calls, go to tools
            if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
                return "tools"
            
            # Otherwise, we're done
            return END
        
        # Build the graph
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("agent", agent_node)
        workflow.add_node("tools", tool_node)
        
        # Add edges
        workflow.add_edge(START, "agent")
        workflow.add_conditional_edges("agent", should_continue, ["tools", END])
        workflow.add_edge("tools", "agent")
        
        return workflow
    
    async def execute_with_streaming(
        self, 
        state: AgentState,
        config: Optional[Dict] = None
    ) -> AsyncGenerator[StreamingEvent, None]:
        """Execute agent with streaming events"""
        
        # Create event processor
        event_processor = create_streaming_event_generator()
        
        # Stream execution
        async for event in self.compiled_graph.astream_events(
            state, 
            version="v2",
            config=config or {}
        ):
            # Process each event
            for streaming_event in event_processor([event]):
                yield streaming_event
    
    def get_agent_info(self) -> Dict[str, Any]:
        """Get agent information"""
        return {
            "name": self.name,
            "description": self.description,
            "capabilities": self.capabilities,
            "available_tools": [tool.name for tool in self.tools],
            "supports_streaming": True,
            "langgraph_enabled": True
        }


class LangGraphLinkedInAgent(LangGraphEnhancedAgent):
    """LinkedIn-specialized agent using LangGraph"""
    
    def __init__(self):
        super().__init__(
            agent_name="LinkedInAgent",
            agent_description="Specialized agent for LinkedIn job searches, profile analysis, and professional networking tasks",
            capabilities=["job_search", "profile_analysis", "company_research", "networking"]
        )


class LangGraphInstagramAgent(LangGraphEnhancedAgent):
    """Instagram-specialized agent using LangGraph"""
    
    def __init__(self):
        super().__init__(
            agent_name="InstagramAgent", 
            agent_description="Specialized agent for Instagram analytics, content analysis, and social media insights",
            capabilities=["analytics", "content_analysis", "engagement_tracking", "hashtag_research"]
        )


class LangGraphGmailAgent(LangGraphEnhancedAgent):
    """Gmail-specialized agent using LangGraph"""
    
    def __init__(self):
        super().__init__(
            agent_name="GmailAgent",
            agent_description="Specialized agent for email composition, sending, and management tasks", 
            capabilities=["email_composition", "email_sending", "contact_management", "email_templates"]
        )


class LangGraphResearchAgent(LangGraphEnhancedAgent):
    """Research-specialized agent using LangGraph"""
    
    def __init__(self):
        super().__init__(
            agent_name="ResearchAgent",
            agent_description="Specialized agent for data research, analysis, and information gathering",
            capabilities=["web_research", "data_analysis", "fact_checking", "trend_analysis"]
        )


class LangGraphSummarizerAgent(LangGraphEnhancedAgent):
    """Summarizer-specialized agent using LangGraph"""
    
    def __init__(self):
        super().__init__(
            agent_name="SummarizerAgent",
            agent_description="Specialized agent for summarizing content, synthesizing information, and creating reports",
            capabilities=["text_summarization", "data_synthesis", "report_generation", "content_analysis"]
        )


class LangGraphOrchestratorAgent(LangGraphEnhancedAgent):
    """Orchestrator-specialized agent using LangGraph"""
    
    def __init__(self):
        super().__init__(
            agent_name="OrchestratorAgent",
            agent_description="Specialized agent for coordinating complex multi-agent workflows and task routing",
            capabilities=["workflow_management", "agent_coordination", "task_routing", "dependency_management"]
        )