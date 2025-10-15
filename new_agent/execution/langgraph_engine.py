"""
LangGraph-based Execution Engine with token streaming and tool call tracking
"""

import asyncio
from typing import Dict, Any, List, Optional, AsyncGenerator
from datetime import datetime

from langgraph.graph import StateGraph, START, END
from langchain_core.messages import HumanMessage, AIMessage
from langchain_openai import ChatOpenAI

from new_agent.core.langgraph_state import (
    AgentState, StreamingEvent, create_initial_state, 
    finalize_state, mark_state_failed, update_state_with_llm_usage
)
from new_agent.agents.langgraph_agents import (
    LangGraphLinkedInAgent, LangGraphInstagramAgent, LangGraphGmailAgent,
    LangGraphResearchAgent, LangGraphSummarizerAgent, LangGraphOrchestratorAgent
)


class LangGraphExecutionEngine:
    """Enhanced execution engine using LangGraph for state management and streaming"""
    
    def __init__(self):
        # Initialize LangGraph agents
        self.agents = {
            "LinkedInAgent": LangGraphLinkedInAgent(),
            "InstagramAgent": LangGraphInstagramAgent(), 
            "GmailAgent": LangGraphGmailAgent(),
            "ResearchAgent": LangGraphResearchAgent(),
            "SummarizerAgent": LangGraphSummarizerAgent(),
            "OrchestratorAgent": LangGraphOrchestratorAgent()
        }
        
        # Initialize planner LLM
        self.planner_llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.1,
            streaming=True
        )
        
        # Create main workflow graph
        self.workflow_graph = self._create_workflow_graph()
        self.compiled_workflow = self.workflow_graph.compile()
    
    def _create_workflow_graph(self) -> StateGraph:
        """Create the main workflow graph"""
        
        def planner_node(state: AgentState) -> AgentState:
            """Planning node that analyzes query and creates execution plan"""
            query = state["query"]
            
            # Create planning prompt
            planning_prompt = f"""Analyze this user query and create an execution plan: "{query}"

Available agents:
{self._get_agents_description()}

Create a JSON execution plan with:
1. Selected agents (only those needed)
2. Execution steps in order
3. Expected outcomes

Respond with a JSON object containing:
- selected_agents: list of agent names needed
- steps: list of step descriptions
- execution_mode: "sequential" or "parallel"
- reasoning: why these agents were selected

Query: {query}"""
            
            # Call planner
            messages = [HumanMessage(content=planning_prompt)]
            response = self.planner_llm.invoke(messages)
            
            # Parse response and update state
            try:
                import json
                plan_data = json.loads(response.content)
                
                state["execution_plan"] = plan_data
                state["available_agents"] = plan_data.get("selected_agents", [])
                state["total_steps"] = len(plan_data.get("steps", []))
                state["current_step"] = 0
                
            except Exception as e:
                # Fallback planning
                state["execution_plan"] = {
                    "selected_agents": ["LinkedInAgent"] if "linkedin" in query.lower() else ["ResearchAgent"],
                    "steps": ["Execute user query"],
                    "execution_mode": "sequential",
                    "reasoning": f"Fallback planning due to parsing error: {e}"
                }
                state["available_agents"] = state["execution_plan"]["selected_agents"]
                state["total_steps"] = 1
            
            return state
        
        def router_node(state: AgentState) -> AgentState:
            """Route to appropriate agent based on current step"""
            available_agents = state["available_agents"]
            current_step = state["current_step"]
            
            if current_step < len(available_agents):
                state["current_agent"] = available_agents[current_step]
            else:
                state["current_agent"] = available_agents[0] if available_agents else "ResearchAgent"
            
            return state
        
        def agent_executor_node(state: AgentState) -> AgentState:
            """Execute current agent"""
            current_agent_name = state["current_agent"]
            
            if current_agent_name in self.agents:
                agent = self.agents[current_agent_name]
                
                # Create agent-specific state
                agent_state = state.copy()
                
                # Execute agent (this will be handled by streaming)
                state["step_results"].append({
                    "agent": current_agent_name,
                    "step": state["current_step"],
                    "status": "completed"
                })
                
                # Increment step
                state["current_step"] += 1
            
            return state
        
        def should_continue(state: AgentState) -> str:
            """Determine next step in workflow"""
            current_step = state["current_step"]
            total_steps = state["total_steps"]
            
            if current_step < total_steps:
                return "router"
            else:
                return "finalizer"
        
        def finalizer_node(state: AgentState) -> AgentState:
            """Finalize execution and create summary"""
            # Create final output
            final_output = {
                "query": state["query"],
                "agents_used": [result["agent"] for result in state["step_results"]],
                "total_steps": state["total_steps"],
                "total_tokens": state["total_tokens"],
                "total_cost": state["total_cost"],
                "execution_time": (datetime.now() - state["started_at"]).total_seconds() if state["started_at"] else 0,
                "tool_results": state["tool_results"]
            }
            
            return finalize_state(state, final_output)
        
        # Build workflow
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("planner", planner_node)
        workflow.add_node("router", router_node)
        workflow.add_node("agent_executor", agent_executor_node)
        workflow.add_node("finalizer", finalizer_node)
        
        # Add edges
        workflow.add_edge(START, "planner")
        workflow.add_edge("planner", "router")
        workflow.add_edge("router", "agent_executor")
        workflow.add_conditional_edges("agent_executor", should_continue, ["router", "finalizer"])
        workflow.add_edge("finalizer", END)
        
        return workflow
    
    def _get_agents_description(self) -> str:
        """Get description of available agents"""
        descriptions = []
        for name, agent in self.agents.items():
            info = agent.get_agent_info()
            descriptions.append(f"- {name}: {info['description']}")
        return "\n".join(descriptions)
    
    async def execute_query_with_streaming(
        self, 
        query: str, 
        user_id: str = "default"
    ) -> AsyncGenerator[StreamingEvent, None]:
        """Execute query with full streaming support"""
        
        # Create initial state
        state = create_initial_state(query, user_id)
        
        # Yield start event
        yield StreamingEvent(
            event_type="execution_start",
            content=f"🚀 Starting execution for: {query}",
            metadata={"session_id": state["session_id"]}
        )
        
        try:
            # Stream through main workflow
            async for event in self.compiled_workflow.astream_events(
                state,
                version="v2"
            ):
                # Process different event types - check if event is dict first
                if not isinstance(event, dict):
                    continue  # Skip non-dict events
                
                event_type = event.get("event", "")
                event_name = event.get("name", "")
                

                
                if event_type == "on_chat_model_start":
                    yield StreamingEvent(
                        event_type="agent_start",
                        content=f"🧠 {event_name} starting to think...",
                        agent_name=event_name
                    )
                
                elif event_type == "on_chat_model_stream":
                    # Token-by-token streaming
                    chunk = event.get("data", {}).get("chunk", {})
                    if hasattr(chunk, 'content') and chunk.content:
                        yield StreamingEvent(
                            event_type="token",
                            content=chunk.content,
                            token=chunk.content,
                            agent_name=event_name
                        )
                
                elif event_type == "on_chat_model_end":
                    # Agent thinking complete
                    output = event.get("data", {}).get("output", {})
                    usage = {}
                    tokens = 0
                    
                    # Handle AIMessage with usage_metadata
                    if hasattr(output, 'usage_metadata') and output.usage_metadata:
                        usage = output.usage_metadata
                        tokens = usage.get("total_tokens", 0)
                    elif isinstance(output, dict):
                        usage = output.get("usage_metadata", {})
                        tokens = usage.get("total_tokens", 0)
                    
                    cost = tokens * 0.000375 / 1000  # Approximate cost for GPT-4o mini
                    
                    yield StreamingEvent(
                        event_type="agent_end",
                        content=f"✅ {event_name} completed reasoning",
                        agent_name=event_name,
                        tokens_used=tokens,
                        cost_incurred=cost,
                        metadata={"usage": usage}
                    )
                
                elif event_type == "on_tool_start":
                    tool_name = event.get("name", "unknown_tool")
                    tool_input = event.get("data", {}).get("input", {})
                    
                    yield StreamingEvent(
                        event_type="tool_start",
                        content=f"🔧 Starting tool: {tool_name}",
                        tool_name=tool_name,
                        tool_input=tool_input
                    )
                
                elif event_type == "on_tool_end":
                    tool_name = event.get("name", "unknown_tool")
                    output = event.get("data", {}).get("output")
                    
                    yield StreamingEvent(
                        event_type="tool_end",
                        content=f"✅ Completed tool: {tool_name}",
                        tool_name=tool_name,
                        tool_output=output
                    )
                
                elif event_type == "on_chain_start":
                    chain_name = event.get("name", "")
                    if chain_name in ["planner", "router", "agent_executor", "finalizer"]:
                        yield StreamingEvent(
                            event_type="step_start",
                            content=f"🔵 Starting: {chain_name}",
                            metadata={"step": chain_name}
                        )
                
                elif event_type == "on_chain_end":
                    chain_name = event.get("name", "")
                    if chain_name in ["planner", "router", "agent_executor", "finalizer"]:
                        yield StreamingEvent(
                            event_type="step_end",
                            content=f"✅ Completed: {chain_name}",
                            metadata={"step": chain_name}
                        )
            
            # Final completion event
            yield StreamingEvent(
                event_type="execution_complete",
                content="🎉 Execution completed successfully!",
                metadata={"session_id": state["session_id"]}
            )
            
        except Exception as e:
            import traceback
            yield StreamingEvent(
                event_type="error",
                content=f"❌ Execution failed: {str(e)}",
                metadata={
                    "error": str(e),
                    "traceback": traceback.format_exc()
                }
            )
    
    async def execute_agent_with_streaming(
        self,
        agent_name: str,
        query: str,
        context: Dict[str, Any] = None
    ) -> AsyncGenerator[StreamingEvent, None]:
        """Execute specific agent with streaming"""
        
        if agent_name not in self.agents:
            yield StreamingEvent(
                event_type="error",
                content=f"❌ Agent {agent_name} not found"
            )
            return
        
        agent = self.agents[agent_name]
        
        # Create state for agent execution
        state = create_initial_state(query)
        if context:
            state["metadata"] = context
        
        # Stream agent execution
        async for event in agent.execute_with_streaming(state):
            yield event


# Global instance
langgraph_execution_engine = LangGraphExecutionEngine()