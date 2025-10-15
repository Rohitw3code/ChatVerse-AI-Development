"""
LangGraph Supervisor Agent based on official LangGraph patterns
Handles agent orchestration, planning, and execution coordination
"""

from typing import Dict, Any, List, Optional, Literal
from typing_extensions import TypedDict
import json
from datetime import datetime

from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from langchain_core.tools import BaseTool

from new_agent.core.langgraph_state import AgentState, StreamingEvent
from new_agent.core.config import config
from new_agent.tools.dummy_tools import dummy_tool_registry


class SupervisorState(TypedDict):
    """State for supervisor coordination"""
    plan: Dict[str, Any]
    current_step: int
    next_agent: Optional[str]
    agent_results: List[Dict[str, Any]]
    should_continue: bool


class LangGraphSupervisor:
    """
    Supervisor agent that orchestrates other agents based on LangGraph patterns
    Reference: https://langchain-ai.github.io/langgraph/tutorials/multi_agent/agent_supervisor/
    """
    
    def __init__(self, agents: Dict[str, Any]):
        self.agents = agents
        self.agent_names = list(agents.keys())
        
        # Initialize OpenAI model for supervision
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.1,
            api_key=config.llm.api_key,
            streaming=True
        )
        
        # Create supervisor prompt
        self.supervisor_prompt = ChatPromptTemplate.from_messages([
            ("system", self._get_supervisor_system_prompt()),
            MessagesPlaceholder(variable_name="messages"),
            ("human", "Given the current state and previous results, which agent should act next? Respond with JSON containing 'next_agent' and 'reasoning'.")
        ])
        
        # Create supervisor chain
        self.supervisor_chain = self.supervisor_prompt | self.llm
        
        # Build supervisor graph
        self.graph = self._build_supervisor_graph()
        self.compiled_graph = self.graph.compile()
    
    def _get_supervisor_system_prompt(self) -> str:
        """Get the supervisor system prompt"""
        agent_descriptions = []
        for name, agent in self.agents.items():
            info = agent.get_agent_info()
            agent_descriptions.append(f"- {name}: {info['description']}")
        
        return f"""You are a supervisor agent responsible for coordinating the execution of specialized AI agents.

Available Agents:
{chr(10).join(agent_descriptions)}

Your responsibilities:
1. Analyze the current execution state and previous agent results
2. Determine which agent should act next based on the plan
3. Decide when the task is complete
4. Provide clear reasoning for your decisions

When selecting the next agent, consider:
- The current step in the execution plan
- Previous agent results and their success/failure
- Dependencies between agents (e.g., research before summarization)
- Whether the task is complete

Respond with JSON in this format:
{{
    "next_agent": "AgentName" or "FINISH",
    "reasoning": "explanation of why this agent should act next"
}}"""
    
    def _build_supervisor_graph(self) -> StateGraph:
        """Build the supervisor coordination graph"""
        
        # Create workflow graph
        workflow = StateGraph(AgentState)
        
        # Add supervisor node
        workflow.add_node("supervisor", self._supervisor_node)
        
        # Add agent nodes
        for agent_name in self.agent_names:
            workflow.add_node(agent_name, self._create_agent_node(agent_name))
        
        # Add edges from START to supervisor
        workflow.add_edge(START, "supervisor")
        
        # Add conditional edges from supervisor to agents
        workflow.add_conditional_edges(
            "supervisor",
            self._should_continue,
            {agent_name: agent_name for agent_name in self.agent_names} | {"FINISH": END}
        )
        
        # Add edges from agents back to supervisor
        for agent_name in self.agent_names:
            workflow.add_edge(agent_name, "supervisor")
        
        return workflow
    
    def _supervisor_node(self, state: AgentState) -> AgentState:
        """Supervisor decision node"""
        
        # Prepare context for supervisor
        context_messages = []
        
        # Add original query
        context_messages.append(HumanMessage(content=f"Original Query: {state['query']}"))
        
        # Add execution plan
        if state.get("execution_plan"):
            plan_text = json.dumps(state["execution_plan"], indent=2)
            context_messages.append(AIMessage(content=f"Execution Plan:\n{plan_text}"))
        
        # Add previous results
        if state["step_results"]:
            results_text = "\n".join([
                f"Step {i+1}: {result['agent']} - {result.get('status', 'unknown')}"
                for i, result in enumerate(state["step_results"])
            ])
            context_messages.append(AIMessage(content=f"Previous Results:\n{results_text}"))
        
        # Add current state
        context_messages.append(AIMessage(content=f"Current Step: {state['current_step']}/{state['total_steps']}"))
        
        # Get supervisor decision
        response = self.supervisor_chain.invoke({"messages": context_messages})
        
        try:
            # Parse supervisor decision
            decision = json.loads(response.content)
            next_agent = decision.get("next_agent", "FINISH")
            reasoning = decision.get("reasoning", "No reasoning provided")
            
            # Update state
            state["current_agent"] = next_agent if next_agent != "FINISH" else None
            state["metadata"]["supervisor_reasoning"] = reasoning
            
            # Add supervisor message to conversation
            supervisor_msg = AIMessage(
                content=f"Supervisor Decision: {next_agent}\nReasoning: {reasoning}"
            )
            state["messages"].append(supervisor_msg)
            
        except json.JSONDecodeError:
            # Fallback decision
            if state["current_step"] < state["total_steps"]:
                state["current_agent"] = state["available_agents"][0] if state["available_agents"] else None
            else:
                state["current_agent"] = None
        
        return state
    
    def _create_agent_node(self, agent_name: str):
        """Create a node function for a specific agent"""
        
        def agent_node(state: AgentState) -> AgentState:
            """Execute specific agent with tools"""
            
            if agent_name not in self.agents:
                state["step_results"].append({
                    "agent": agent_name,
                    "step": state["current_step"],
                    "status": "error",
                    "error": f"Agent {agent_name} not found"
                })
                return state
            
            agent = self.agents[agent_name]
            
            # Get agent's tools
            agent_tools = agent.get_tools()
            
            # Create agent prompt
            agent_prompt = self._create_agent_prompt(agent_name, agent_tools)
            
            # Create ReAct agent with tools
            react_agent = create_react_agent(
                self.llm,
                agent_tools,
                messages_modifier=agent_prompt
            )
            
            # Prepare messages for agent
            agent_messages = [
                HumanMessage(content=f"Task: {state['query']}")
            ]
            
            # Add context from previous steps
            if state["step_results"]:
                context = "\n".join([
                    f"Previous step by {result['agent']}: {result.get('output', 'No output')}"
                    for result in state["step_results"][-3:]  # Last 3 results
                ])
                agent_messages.append(AIMessage(content=f"Previous context:\n{context}"))
            
            try:
                # Execute agent
                agent_state = {
                    "messages": agent_messages
                }
                
                result = react_agent.invoke(agent_state)
                
                # Extract result
                final_message = result["messages"][-1]
                agent_output = final_message.content if hasattr(final_message, 'content') else str(final_message)
                
                # Update state with results
                state["step_results"].append({
                    "agent": agent_name,
                    "step": state["current_step"],
                    "status": "completed",
                    "output": agent_output,
                    "timestamp": datetime.now().isoformat()
                })
                
                # Add agent response to conversation
                state["messages"].append(AIMessage(
                    content=f"Agent {agent_name} completed: {agent_output[:200]}..."
                ))
                
                # Update tool results if any tools were used
                if "tool_calls" in result.get("metadata", {}):
                    state["tool_results"].update(result["metadata"]["tool_calls"])
                
            except Exception as e:
                # Handle agent execution error
                state["step_results"].append({
                    "agent": agent_name,
                    "step": state["current_step"],
                    "status": "error",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                })
                
                state["messages"].append(AIMessage(
                    content=f"Agent {agent_name} failed: {str(e)}"
                ))
            
            # Increment step
            state["current_step"] += 1
            
            return state
        
        return agent_node
    
    def _create_agent_prompt(self, agent_name: str, tools: List[BaseTool]) -> str:
        """Create agent-specific prompt"""
        
        agent_info = self.agents[agent_name].get_agent_info()
        tool_descriptions = "\n".join([
            f"- {tool.name}: {tool.description}"
            for tool in tools
        ])
        
        return f"""You are {agent_name}, a specialized AI agent.

Role: {agent_info['description']}
Capabilities: {', '.join(agent_info['capabilities'])}

Available Tools:
{tool_descriptions}

Instructions:
1. Analyze the given task and determine the best approach
2. Use your available tools when necessary to gather information or perform actions
3. Provide clear and actionable results
4. If you cannot complete the task, explain why and what would be needed

Remember: You are part of a multi-agent system. Focus on your specialty and provide results that other agents can build upon."""
    
    def _should_continue(self, state: AgentState) -> str:
        """Determine if workflow should continue"""
        current_agent = state.get("current_agent")
        
        if current_agent is None or current_agent == "FINISH":
            return "FINISH"
        elif current_agent in self.agent_names:
            return current_agent
        else:
            return "FINISH"
    
    async def execute_with_streaming(self, query: str, user_id: str) -> AgentState:
        """Execute supervisor workflow with streaming"""
        
        from ..core.langgraph_state import create_initial_state
        
        # Create initial state
        initial_state = create_initial_state(query, user_id)
        
        # Set up basic plan if not provided
        if not initial_state.get("execution_plan"):
            initial_state["execution_plan"] = {
                "selected_agents": self.agent_names[:2],  # Use first 2 agents as default
                "steps": ["Analyze task", "Execute actions"],
                "execution_mode": "sequential"
            }
            initial_state["available_agents"] = self.agent_names[:2]
            initial_state["total_steps"] = len(self.agent_names[:2])
        
        # Execute workflow
        final_state = await self.compiled_graph.ainvoke(initial_state)
        
        return final_state


def create_supervisor_with_agents(agents: Dict[str, Any]) -> LangGraphSupervisor:
    """Factory function to create supervisor with agents"""
    return LangGraphSupervisor(agents)