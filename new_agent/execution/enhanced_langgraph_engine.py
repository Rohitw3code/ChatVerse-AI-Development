"""
Enhanced LangGraph Execution Engine with Supervisor Pattern and Tool Streaming
Based on LangGraph official multi-agent supervisor patterns
"""

import asyncio
from typing import Dict, Any, List, Optional, AsyncGenerator
from datetime import datetime
import json

from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage, AIMessage
from langchain_openai import ChatOpenAI

from new_agent.core.langgraph_state import (
    AgentState, StreamingEvent, create_initial_state,
    finalize_state, mark_state_failed, update_state_with_llm_usage
)
from new_agent.core.config import config
from new_agent.agents.enhanced_langgraph_agents import (
    LangGraphLinkedInAgent, LangGraphInstagramAgent, LangGraphGmailAgent,
    LangGraphResearchAgent, LangGraphSummarizerAgent
)
from new_agent.agents.langgraph_supervisor import LangGraphSupervisor


class EnhancedLangGraphEngine:
    """
    Enhanced execution engine with supervisor pattern and comprehensive streaming
    Implements multi-agent coordination with proper tool call tracking
    """
    
    def __init__(self):
        # Initialize enhanced agents
        self.agents = {
            "LinkedInAgent": LangGraphLinkedInAgent(),
            "InstagramAgent": LangGraphInstagramAgent(), 
            "GmailAgent": LangGraphGmailAgent(),
            "ResearchAgent": LangGraphResearchAgent(),
            "SummarizerAgent": LangGraphSummarizerAgent()
        }
        
        # Initialize planner LLM
        self.planner_llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.1,
            api_key=config.llm.api_key
        )
        
        # Initialize supervisor
        self.supervisor = LangGraphSupervisor(self.agents)
        
        # Build main execution workflow
        self.main_workflow = self._build_main_workflow()
        self.compiled_workflow = self.main_workflow.compile()
    
    def _build_main_workflow(self) -> StateGraph:
        """Build the main execution workflow with planning and supervision"""
        
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("planner", self._planner_node)
        workflow.add_node("supervisor_execution", self._supervisor_execution_node)
        workflow.add_node("finalizer", self._finalizer_node)
        
        # Add edges
        workflow.add_edge(START, "planner")
        workflow.add_edge("planner", "supervisor_execution")
        workflow.add_edge("supervisor_execution", "finalizer")
        workflow.add_edge("finalizer", END)
        
        return workflow
    
    def _planner_node(self, state: AgentState) -> AgentState:
        """Enhanced planning node with agent selection"""
        
        query = state["query"]
        
        # Create planning prompt
        agent_descriptions = []
        for name, agent in self.agents.items():
            info = agent.get_agent_info()
            agent_descriptions.append(f"- {name}: {info['description']} (Tools: {', '.join(info['tools'])})")
        
        planning_prompt = f"""Analyze the following query and create an execution plan.

Available Agents:
{chr(10).join(agent_descriptions)}

Query: {query}

Create a JSON response with:
{{
    "selected_agents": ["AgentName1", "AgentName2"],
    "steps": ["Step 1 description", "Step 2 description"],
    "execution_mode": "sequential",
    "reasoning": "why these agents and steps were selected",
    "estimated_tools": ["tool1", "tool2"]
}}

Consider:
1. Which agents are most relevant for this query
2. The logical sequence of operations
3. Dependencies between agents
4. Tools that will likely be needed"""
        
        # Call planner
        messages = [HumanMessage(content=planning_prompt)]
        response = self.planner_llm.invoke(messages)
        
        # Parse and validate response
        try:
            plan_data = json.loads(response.content)
            
            # Validate selected agents exist
            valid_agents = [agent for agent in plan_data.get("selected_agents", []) 
                          if agent in self.agents]
            
            if not valid_agents:
                # Fallback: select agents based on query keywords
                valid_agents = self._select_agents_by_keywords(query)
            
            # Update state
            state["execution_plan"] = plan_data
            state["available_agents"] = valid_agents
            state["total_steps"] = len(valid_agents)
            state["current_step"] = 0
            
        except Exception as e:
            # Fallback planning
            fallback_agents = self._select_agents_by_keywords(query)
            state["execution_plan"] = {
                "selected_agents": fallback_agents,
                "steps": [f"Execute {agent}" for agent in fallback_agents],
                "execution_mode": "sequential",
                "reasoning": f"Fallback planning due to error: {e}"
            }
            state["available_agents"] = fallback_agents
            state["total_steps"] = len(fallback_agents)
            state["current_step"] = 0
        
        return state
    
    def _select_agents_by_keywords(self, query: str) -> List[str]:
        """Select agents based on query keywords"""
        query_lower = query.lower()
        selected = []
        
        if any(word in query_lower for word in ["linkedin", "job", "career", "professional"]):
            selected.append("LinkedInAgent")
        
        if any(word in query_lower for word in ["instagram", "social", "content", "post"]):
            selected.append("InstagramAgent")
        
        if any(word in query_lower for word in ["email", "gmail", "send", "message", "mail"]):
            selected.append("GmailAgent")
        
        if any(word in query_lower for word in ["research", "search", "find", "analyze", "data"]):
            selected.append("ResearchAgent")
        
        if any(word in query_lower for word in ["summary", "summarize", "report", "compile"]):
            selected.append("SummarizerAgent")
        
        # Default fallback
        if not selected:
            selected = ["ResearchAgent", "SummarizerAgent"]
        
        return selected
    
    def _supervisor_execution_node(self, state: AgentState) -> AgentState:
        """Prepare for individual agent execution"""
        
        # This node just prepares the state for streaming execution
        # The actual agent execution will happen in the streaming function
        # to ensure proper event generation
        
        state["supervisor_prepared"] = True
        state["agents_to_execute"] = state.get("available_agents", [])
        state["current_agent_index"] = 0
        
        return state
    
    def _finalizer_node(self, state: AgentState) -> AgentState:
        """Enhanced finalizer with comprehensive results"""
        
        # Create comprehensive final output
        successful_steps = [r for r in state["step_results"] if r.get("status") == "completed"]
        failed_steps = [r for r in state["step_results"] if r.get("status") == "error"]
        
        final_output = {
            "query": state["query"],
            "execution_plan": state.get("execution_plan", {}),
            "agents_used": list(set([r["agent"] for r in state["step_results"]])),
            "successful_steps": len(successful_steps),
            "failed_steps": len(failed_steps),
            "total_steps": state["total_steps"],
            "total_tokens": state["total_tokens"],
            "total_cost": state["total_cost"],
            "execution_time": (datetime.now() - state["started_at"]).total_seconds() if state["started_at"] else 0,
            "tool_results": state["tool_results"],
            "step_details": state["step_results"]
        }
        
        return finalize_state(state, final_output)
    
    async def execute_query_with_streaming(self, query: str, user_id: str) -> AsyncGenerator[StreamingEvent, None]:
        """Execute query with comprehensive streaming including tool calls"""
        
        # Create initial state
        state = create_initial_state(query, user_id)
        
        try:
            # Yield execution start
            yield StreamingEvent(
                event_type="execution_start",
                content=f"🚀 Starting enhanced execution for: {query}",
                metadata={"query": query, "user_id": user_id}
            )
            
            # Stream through main workflow
            async for event in self.compiled_workflow.astream_events(
                state,
                version="v2",
                include_names=["planner", "supervisor_execution", "finalizer"]
            ):
                # Process workflow events
                if not isinstance(event, dict):
                    continue
                
                event_type = event.get("event", "")
                event_name = event.get("name", "")
                
                # Node execution events
                if event_type == "on_chain_start" and event_name in ["planner", "supervisor_execution", "finalizer"]:
                    yield StreamingEvent(
                        event_type="step_start",
                        content=f"🔵 Starting: {event_name}",
                        metadata={"step": event_name}
                    )
                
                elif event_type == "on_chain_end" and event_name in ["planner", "supervisor_execution", "finalizer"]:
                    yield StreamingEvent(
                        event_type="step_end",
                        content=f"✅ Completed: {event_name}",
                        metadata={"step": event_name}
                    )
                
                # LLM events from planner
                elif event_type == "on_chat_model_start":
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
                    # Extract usage information
                    output = event.get("data", {}).get("output", {})
                    tokens = 0
                    cost = 0.0
                    
                    if hasattr(output, 'usage_metadata') and output.usage_metadata:
                        tokens = output.usage_metadata.get("total_tokens", 0)
                        cost = tokens * 0.000375 / 1000  # GPT-4o mini pricing
                    
                    yield StreamingEvent(
                        event_type="agent_end",
                        content=f"✅ {event_name} completed reasoning",
                        agent_name=event_name,
                        metadata={
                            "tokens": tokens,
                            "cost": cost
                        }
                    )
            
            # Execute workflow to get the final state with available agents
            final_state = await self.compiled_workflow.ainvoke(state)
            
            # Now stream individual agent executions step by step
            if final_state.get("available_agents"):
                agents_to_execute = final_state["available_agents"]
                
                yield StreamingEvent(
                    event_type="execution_plan_ready",
                    content=f"📋 Execution plan ready: {len(agents_to_execute)} agents selected",
                    metadata={
                        "total_agents": len(agents_to_execute),
                        "agent_list": agents_to_execute,
                        "execution_plan": final_state.get("execution_plan", {})
                    }
                )
                
                # Execute each agent step by step with detailed streaming
                for step_index, agent_name in enumerate(agents_to_execute):
                    if agent_name in self.agents:
                        agent = self.agents[agent_name]
                        
                        # Step start event
                        yield StreamingEvent(
                            event_type="step_start_detailed",
                            content=f"🎯 Step {step_index + 1}/{len(agents_to_execute)}: Starting {agent_name}",
                            agent_name=agent_name,
                            step_number=step_index + 1,
                            metadata={
                                "step": step_index + 1,
                                "total_steps": len(agents_to_execute),
                                "agent_name": agent_name,
                                "agent_description": agent.description
                            }
                        )
                        
                        # Agent initialization event
                        yield StreamingEvent(
                            event_type="agent_initializing",
                            content=f"🔧 Initializing {agent_name} with {len(agent.tools)} tools",
                            agent_name=agent_name,
                            step_number=step_index + 1,
                            metadata={
                                "tools_available": [tool.name for tool in agent.tools],
                                "tool_count": len(agent.tools),
                                "capabilities": agent.capabilities
                            }
                        )
                        
                        # Stream detailed agent execution
                        try:
                            agent_start_time = datetime.now()
                            
                            # Agent execution start
                            yield StreamingEvent(
                                event_type="agent_execution_start",
                                content=f"🚀 {agent_name} execution started",
                                agent_name=agent_name,
                                step_number=step_index + 1,
                                metadata={
                                    "start_time": agent_start_time.isoformat(),
                                    "query": query
                                }
                            )
                            
                            # Stream agent execution with token-by-token output
                            async for agent_event in agent.execute_with_streaming(query, user_id):
                                # Add step information to all agent events
                                agent_event.step_number = step_index + 1
                                if not hasattr(agent_event, 'metadata'):
                                    agent_event.metadata = {}
                                agent_event.metadata.update({
                                    "current_step": step_index + 1,
                                    "total_steps": len(agents_to_execute),
                                    "agent_name": agent_name
                                })
                                yield agent_event
                            
                            agent_end_time = datetime.now()
                            execution_duration = (agent_end_time - agent_start_time).total_seconds()
                            
                            # Agent execution completion
                            yield StreamingEvent(
                                event_type="agent_execution_complete",
                                content=f"✅ {agent_name} execution completed in {execution_duration:.2f}s",
                                agent_name=agent_name,
                                step_number=step_index + 1,
                                metadata={
                                    "end_time": agent_end_time.isoformat(),
                                    "duration_seconds": execution_duration,
                                    "status": "success"
                                }
                            )
                            
                        except Exception as agent_error:
                            # Agent execution error
                            yield StreamingEvent(
                                event_type="agent_execution_error",
                                content=f"❌ {agent_name} execution failed: {str(agent_error)}",
                                agent_name=agent_name,
                                step_number=step_index + 1,
                                metadata={
                                    "error": str(agent_error),
                                    "status": "error"
                                }
                            )
                        
                        # Step completion event
                        yield StreamingEvent(
                            event_type="step_complete_detailed",
                            content=f"🎉 Step {step_index + 1}/{len(agents_to_execute)}: {agent_name} completed",
                            agent_name=agent_name,
                            step_number=step_index + 1,
                            metadata={
                                "step": step_index + 1,
                                "total_steps": len(agents_to_execute),
                                "agent_name": agent_name,
                                "status": "completed"
                            }
                        )
                
                # All agents execution summary
                yield StreamingEvent(
                    event_type="all_agents_complete",
                    content=f"🎊 All {len(agents_to_execute)} agents completed successfully!",
                    metadata={
                        "total_agents_executed": len(agents_to_execute),
                        "agents_list": agents_to_execute
                    }
                )
            
            # Final completion
            yield StreamingEvent(
                event_type="execution_complete",
                content="🎉 Enhanced execution completed successfully!",
                metadata={"session_id": state["session_id"]}
            )
        
        except Exception as e:
            import traceback
            yield StreamingEvent(
                event_type="error",
                content=f"❌ Enhanced execution failed: {str(e)}",
                metadata={
                    "error": str(e),
                    "traceback": traceback.format_exc()
                }
            )
    
    def get_available_agents(self) -> Dict[str, Dict[str, Any]]:
        """Get information about all available agents"""
        return {name: agent.get_agent_info() for name, agent in self.agents.items()}


# Global instance
enhanced_langgraph_engine = EnhancedLangGraphEngine()