from typing_extensions import Literal
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langgraph.types import Command
from chatagent.config.init import non_stream_llm
from chatagent.utils import State, usages
from langchain_community.callbacks import get_openai_callback
from pydantic import BaseModel, Field
from typing import List
from langchain_community.callbacks.openai_info import OpenAICallbackHandler
from chatagent.system.agent_search_models import AgentSelection

callback_handler = OpenAICallbackHandler()


def search_agent_node():
    AGENT_SELECTION_PROMPT = """You are an Agent Selector. Analyze the query and select the required agent names.
        Rules:
        - Select agents explicitly needed for the query
        - Multi-step tasks need multiple agents (e.g., "search and email" needs both research and email agents)
        - Return exact agent names from the list
        - Set sufficient=True if selected agents can handle the query
        - Set sufficient=False if no suitable agents found or agents cannot handle the request

        Example:
        Query: "find jobs and email results" → select [research, email] agents, sufficient=True
        Query: "draft an email" → select [email] agent, sufficient=True
        Query: "launch rocket to Mars" → select [], sufficient=False (no capable agents)
    """

    def search_agent(state: State) -> Command[Literal["search_agent_node", "planner_node", "final_answer_node"]]:
        
        from chatagent.agents.agent_retrival import get_relevant_agents

        # Step 1: Get relevant agents using embedding similarity
        all_relevant_agents = get_relevant_agents(state["input"], top_k=4)  # Reduced from 5 to 3

        print("\n\n=== AGENT SEARCH DEBUG ===")
        print(f"Step 1 - Agents from embedding search (top_k=3):", all_relevant_agents)
        
        # Step 2: Use LLM to filter and select only the specific agents needed
        agent_search_count = state.get("agent_search_count", 0)
        
        # Build minimal conversation context (only last 2 messages, max 200 chars each)
        conversation_history = ""
        recent_messages = state.get("messages", [])[-2:]  # Only last 2 messages
        if recent_messages:
            for msg in recent_messages:
                if isinstance(msg, (HumanMessage, AIMessage)):
                    role = "User" if isinstance(msg, HumanMessage) else "AI"
                    content = str(msg.content)[:200]  # Truncate to 200 chars
                    conversation_history += f"{role}: {content}\n"
        
        # Build agent list with their full descriptions (let LLM decide, no hardcoding)
        agent_summaries = [f"- {agent['name']}: {agent['description']}" for agent in all_relevant_agents]
        
        with get_openai_callback() as cb:
            # Filter agents using LLM - fully agentic decision making
            prompt_content = (
                "Available agents:\n" + "\n".join(agent_summaries) +
                (f"\n\nRecent context:\n{conversation_history}" if conversation_history else "") +
                f"\n\nUser query: {state['input']}\n\n" +
                "Analyze the query, select the exact agent names needed, and indicate if they are sufficient."
            )
            
            agent_selection: AgentSelection = non_stream_llm.with_structured_output(AgentSelection).invoke(
                [
                    SystemMessage(content=AGENT_SELECTION_PROMPT),
                    HumanMessage(content=prompt_content)
                ]
            )
        usages_data = usages(cb)
        
        # Filter agents to only include selected ones
        selected_agents = [
            agent for agent in all_relevant_agents 
            if agent['name'] in agent_selection.selected_agent_names
        ]
        
        # If no agents were selected, fall back to all relevant agents
        if not selected_agents:
            selected_agents = all_relevant_agents
            print(f"⚠️  No agents selected by LLM, using all relevant agents")
        
        print(f"Step 2 - LLM filtered agents: {[a['name'] for a in selected_agents]}")
        print(f"Step 2 - Selection reason: {agent_selection.reason}")
        print(f"Step 2 - Sufficient: {agent_selection.sufficient}")
        print("=== END AGENT SEARCH DEBUG ===\n\n")

        # **Condition 1: Agents are sufficient, proceed to planner.**
        if agent_selection.sufficient:
            return Command(
                update={
                    "input": state["input"],
                    "messages": [AIMessage(content=f"Agents found: {agent_selection.reason}")],
                    "current_message": [AIMessage(content=f"{agent_selection.reason}")],
                    "reason": "Sufficient agents found to proceed with planning.",
                    "provider_id": state.get("provider_id"),
                    "next_node": "planner_node",
                    "type": "agent_searcher",
                    "next_type": "thinker",
                    "agents": selected_agents,
                    "usages": usages_data,
                    "status": "success",
                    "current_task": state.get("current_task", "NO TASK"),
                    "tool_output": state.get("tool_output"),
                    "max_message": state.get("max_message", 10),
                },
                goto="planner_node"
            )

        # **Condition 2: Agents are insufficient, but we can still retry.**
        if not agent_selection.sufficient and agent_search_count < 3:
            return Command(
                update={
                    "input": state["input"],
                    "messages": [AIMessage(content=f"Retrying agent search: {agent_selection.reason}")],
                    "current_message": [AIMessage(content=f"{agent_selection.reason}")],
                    "reason": agent_selection.reason,
                    "agent_search_count": agent_search_count + 1,
                    "provider_id": state.get("provider_id"),
                    "next_node": "search_agent_node",
                    "type": "agent_searcher",
                    "agents": selected_agents,
                    "next_type": "agent_searcher",
                    "usages": usages_data,
                    "status": "success",
                    "current_task": state.get("current_task", "NO TASK"),
                    "tool_output": state.get("tool_output"),
                    "max_message": state.get("max_message", 10),
                },
                goto="search_agent_node"
            )
        
        # **Condition 3: Agents are insufficient and we are out of retries. End the process.**
        final_reason = f"I am not capable of handling this request. After multiple searches, suitable agents could not be found. Reason: {agent_selection.reason}"
        return Command(
            update={
                "input": state["input"],
                "messages": [AIMessage(content=final_reason)],
                "current_message": [AIMessage(content=final_reason)],
                "reason": final_reason,
                "provider_id": state.get("provider_id"),
                "next_node": "final_answer_node",
                "type": "agent_searcher",
                "next_type": "end",
                "agents": selected_agents,
                "usages": usages_data,
                "status": "fail",
                "current_task": state.get("current_task", "NO TASK"),
                "tool_output": state.get("tool_output"),
                "max_message": state.get("max_message", 10),
            },
            goto="final_answer_node"
        )
        
    return search_agent
