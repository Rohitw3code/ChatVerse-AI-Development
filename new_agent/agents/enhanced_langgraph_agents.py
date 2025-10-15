"""
Enhanced LangGraph agents with proper tool execution and streaming
Based on LangGraph official patterns for ReAct agents and tool calling
"""

from typing import Dict, Any, List, Optional, AsyncGenerator
from datetime import datetime
import json

from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import create_react_agent, ToolNode
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage, BaseMessage
from langchain_core.tools import BaseTool
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from langchain_core.runnables import RunnableConfig

from new_agent.core.langgraph_state import AgentState, StreamingEvent
from new_agent.core.config import config
from new_agent.tools.dummy_tools import dummy_tool_registry


class LangGraphToolWrapper(BaseTool):
    """
    Enhanced tool wrapper for LangGraph compatibility with proper streaming
    """
    
    name: str
    description: str
    
    def __init__(self, dummy_tool):
        super().__init__(
            name=dummy_tool.name,
            description=dummy_tool.description
        )
        self._dummy_tool = dummy_tool
    
    def _run(self, **kwargs) -> Any:
        """Execute tool synchronously"""
        try:
            return self._dummy_tool.execute(**kwargs)
        except Exception as e:
            return {"error": str(e), "tool": self.name}
    
    async def _arun(self, **kwargs) -> Any:
        """Execute tool asynchronously"""
        try:
            if hasattr(self._dummy_tool, 'execute_async'):
                return await self._dummy_tool.execute_async(**kwargs)
            else:
                return self._dummy_tool.execute(**kwargs)
        except Exception as e:
            return {"error": str(e), "tool": self.name}


class EnhancedLangGraphAgent:
    """
    Enhanced LangGraph agent with proper tool execution and streaming
    Based on LangGraph ReAct agent patterns
    """
    
    def __init__(self, name: str, description: str, capabilities: List[str], tool_names: List[str]):
        self.name = name
        self.description = description
        self.capabilities = capabilities
        self.tool_names = tool_names
        
        # Initialize LLM
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.1,
            api_key=config.llm.api_key,
            streaming=True
        )
        
        # Get and wrap tools
        self.tools = self._get_wrapped_tools()
        
        # Create ReAct agent - LangGraph's create_react_agent API
        self.react_agent = create_react_agent(self.llm, self.tools)
        
        # Create streaming workflow
        self.workflow = self._create_streaming_workflow()
        self.compiled_workflow = self.workflow.compile()
    
    def _get_wrapped_tools(self) -> List[BaseTool]:
        """Get wrapped tools for this agent"""
        tools = []
        
        for tool_name in self.tool_names:
            if tool_name in dummy_tool_registry.tools:
                dummy_tool = dummy_tool_registry.tools[tool_name]
                wrapped_tool = LangGraphToolWrapper(dummy_tool)
                tools.append(wrapped_tool)
        
        return tools
    
    def _get_system_message(self) -> str:
        """Get agent-specific system message"""
        tool_descriptions = "\n".join([
            f"- {tool.name}: {tool.description}"
            for tool in self.tools
        ])
        
        return f"""You are {self.name}, a specialized AI agent.

Role: {self.description}
Capabilities: {', '.join(self.capabilities)}

Available Tools:
{tool_descriptions}

Instructions:
1. Analyze the user's request carefully
2. Use your tools when necessary to gather information or perform actions
3. Think step by step and explain your reasoning
4. Provide clear, actionable results
5. If you need to use multiple tools, do so systematically

Always be helpful and thorough in your responses."""
    
    def _create_streaming_workflow(self) -> StateGraph:
        """Create streaming workflow for agent execution"""
        
        # Create workflow
        workflow = StateGraph(AgentState)
        
        # Add agent node
        workflow.add_node("agent", self._agent_node)
        
        # Add tool node if tools are available
        if self.tools:
            tool_node = ToolNode(self.tools)
            workflow.add_node("tools", tool_node)
            
            # Add conditional edges for tool calling
            workflow.add_conditional_edges(
                "agent",
                self._should_call_tools,
                {
                    "tools": "tools",
                    "end": END
                }
            )
            
            # Edge from tools back to agent
            workflow.add_edge("tools", "agent")
        else:
            # No tools, go directly to end
            workflow.add_edge("agent", END)
        
        # Start with agent
        workflow.add_edge(START, "agent")
        
        return workflow
    
    def _agent_node(self, state: AgentState, config: RunnableConfig = None) -> AgentState:
        """Main agent reasoning node with tool support"""
        
        # Prepare messages
        messages = state.get("messages", [])
        
        # Add task context if not already present
        if not messages or not any("Task:" in str(msg) for msg in messages):
            messages.append(HumanMessage(content=f"Task: {state['query']}"))
        
        # Call the ReAct agent
        try:
            result = self.react_agent.invoke({"messages": messages}, config=config)
            
            # Update state with new messages
            state["messages"] = result["messages"]
            
            # Track agent usage
            if self.name not in state.get("agents_used", []):
                if "agents_used" not in state:
                    state["agents_used"] = []
                state["agents_used"].append(self.name)
            
            return state
            
        except Exception as e:
            # Handle errors gracefully
            error_message = AIMessage(content=f"Error in {self.name}: {str(e)}")
            state["messages"].append(error_message)
            
            if "error" not in state:
                state["error"] = str(e)
            
            return state
    
    def _should_call_tools(self, state: AgentState) -> str:
        """Determine if tools should be called based on last message"""
        
        if not state.get("messages"):
            return "end"
        
        last_message = state["messages"][-1]
        
        # Check if last message has tool calls
        if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
            return "tools"
        
        return "end"
    
    def get_tools(self) -> List[BaseTool]:
        """Get agent's tools"""
        return self.tools
    
    def get_agent_info(self) -> Dict[str, Any]:
        """Get agent information"""
        return {
            "name": self.name,
            "description": self.description,
            "capabilities": self.capabilities,
            "tools": [tool.name for tool in self.tools],
            "tool_count": len(self.tools)
        }
    
    async def execute_with_streaming(self, query: str, user_id: str) -> AsyncGenerator[StreamingEvent, None]:
        """Execute agent with streaming events"""
        
        from ..core.langgraph_state import create_initial_state
        
        # Create initial state
        initial_state = create_initial_state(query, user_id)
        
        try:
            # Yield start event
            yield StreamingEvent(
                event_type="agent_start", 
                content=f"🧠 {self.name} starting to work on: {query}",
                agent_name=self.name
            )
            
            # Execute workflow with streaming
            config = RunnableConfig(
                configurable={"thread_id": initial_state["session_id"]},
                metadata={"agent_name": self.name}
            )
            
            async for event in self.compiled_workflow.astream_events(
                initial_state,
                config=config,
                version="v2"
            ):
                # Process different event types
                if not isinstance(event, dict):
                    continue
                
                event_type = event.get("event", "")
                event_name = event.get("name", "")
                
                if event_type == "on_chat_model_start":
                    yield StreamingEvent(
                        event_type="model_start",
                        content=f"🤔 {self.name} is thinking...",
                        agent_name=self.name
                    )
                
                elif event_type == "on_chat_model_stream":
                    # Token streaming
                    chunk = event.get("data", {}).get("chunk", {})
                    if hasattr(chunk, 'content') and chunk.content:
                        yield StreamingEvent(
                            event_type="token",
                            content=chunk.content,
                            token=chunk.content,
                            agent_name=self.name
                        )
                
                elif event_type == "on_chat_model_end":
                    # Model completed
                    output = event.get("data", {}).get("output", {})
                    
                    # Extract usage metadata
                    tokens = 0
                    if hasattr(output, 'usage_metadata') and output.usage_metadata:
                        tokens = output.usage_metadata.get("total_tokens", 0)
                    
                    yield StreamingEvent(
                        event_type="model_end",
                        content=f"✅ {self.name} completed reasoning ({tokens} tokens)",
                        agent_name=self.name,
                        metadata={"tokens": tokens}
                    )
                
                elif event_type == "on_tool_start":
                    # Tool execution started
                    tool_name = event.get("name", "unknown_tool")
                    tool_input = event.get("data", {}).get("input", {})
                    
                    yield StreamingEvent(
                        event_type="tool_start",
                        content=f"🔧 {self.name} starting tool: {tool_name}",
                        agent_name=self.name,
                        tool_name=tool_name,
                        tool_input=tool_input,
                        metadata={
                            "tool_name": tool_name,
                            "input": tool_input,
                            "agent": self.name
                        }
                    )
                
                elif event_type == "on_tool_end":
                    # Tool execution completed
                    tool_name = event.get("name", "unknown_tool")
                    tool_output = event.get("data", {}).get("output")
                    
                    yield StreamingEvent(
                        event_type="tool_end",
                        content=f"✅ {self.name} completed tool: {tool_name}",
                        agent_name=self.name,
                        tool_name=tool_name,
                        tool_output=tool_output,
                        metadata={
                            "tool_name": tool_name,
                            "output": tool_output,
                            "agent": self.name
                        }
                    )
            
            # Final completion event
            yield StreamingEvent(
                event_type="agent_complete",
                content=f"🎉 {self.name} completed successfully!",
                agent_name=self.name
            )
            
        except Exception as e:
            yield StreamingEvent(
                event_type="agent_error",
                content=f"❌ {self.name} encountered error: {str(e)}",
                agent_name=self.name,
                metadata={"error": str(e)}
            )


# Specialized agent implementations
class LangGraphLinkedInAgent(EnhancedLangGraphAgent):
    """LinkedIn-specialized agent"""
    
    def __init__(self):
        super().__init__(
            name="LinkedInAgent",
            description="Specialized in LinkedIn job searches, profile analysis, and professional networking",
            capabilities=["job_search", "profile_analysis", "networking", "career_insights"],
            tool_names=["linkedin_search", "linkedin_profile_analysis", "job_analyzer"]
        )


class LangGraphInstagramAgent(EnhancedLangGraphAgent):
    """Instagram-specialized agent"""
    
    def __init__(self):
        super().__init__(
            name="InstagramAgent", 
            description="Specialized in Instagram analytics, content insights, and social media management",
            capabilities=["content_analysis", "audience_insights", "engagement_metrics", "hashtag_research"],
            tool_names=["instagram_insights", "instagram_analytics", "content_analyzer"]
        )


class LangGraphGmailAgent(EnhancedLangGraphAgent):
    """Gmail-specialized agent"""
    
    def __init__(self):
        super().__init__(
            name="GmailAgent",
            description="Specialized in email composition, management, and communication",
            capabilities=["email_composition", "email_management", "communication", "scheduling"],
            tool_names=["gmail_send", "gmail_compose", "email_formatter"]
        )


class LangGraphResearchAgent(EnhancedLangGraphAgent):
    """Research-specialized agent"""
    
    def __init__(self):
        super().__init__(
            name="ResearchAgent",
            description="Specialized in web research, data analysis, and information gathering",
            capabilities=["web_research", "data_analysis", "fact_checking", "trend_analysis"],
            tool_names=["web_search", "data_analyzer", "fact_checker"]
        )


class LangGraphSummarizerAgent(EnhancedLangGraphAgent):
    """Summarization-specialized agent"""
    
    def __init__(self):
        super().__init__(
            name="SummarizerAgent",
            description="Specialized in content summarization, report generation, and synthesis",
            capabilities=["content_summarization", "report_generation", "data_synthesis", "key_insights"],
            tool_names=["summarizer", "report_generator", "content_synthesizer"]
        )