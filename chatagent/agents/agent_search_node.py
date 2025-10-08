from typing_extensions import Literal
from langchain_core.messages import AIMessage, HumanMessage,SystemMessage
from langgraph.types import Command
from chatagent.config.init import llm
from chatagent.utils import State, usages
from langchain_community.callbacks import get_openai_callback
from pydantic import BaseModel, Field
from langchain_community.callbacks.openai_info import OpenAICallbackHandler
callback_handler = OpenAICallbackHandler()


class AgentCheck(BaseModel):
    recheck: bool = Field(
        description="You decide based on the given agent list and its description is it sufficient to handle the user query and it does not required to recheck with more agents then return False, if you think the given agent list is not sufficient to handle the user query and it required to recheck with more agents then return True"
    )
    reason: str = Field(
        description="if False do just retrun False, if True explain why the given agent list is not sufficient to handle the user query , never mention the agent names in the reason just explain the reason or approach in few words"
    )


def search_agent_node():
    SYSTEM_PROMPT = """
        You are the *Agent Availability Evaluator*.

        Your ONLY responsibility is to check if there is at least one relevant agent available 
        from the provided agent list that can handle the given user request.

        You do NOT need to understand or generate a solution for the request.  
        You do NOT need to ask for missing data or clarify the task.  
        You ONLY check for *availability* of a relevant agent.

        Rules:
        - If there is at least one agent whose description matches or relates to the user’s request,
        set `recheck = False` (sufficient agents found).
        - If no listed agent appears relevant or capable, set `recheck = True`.
        - Never mention agent names in the reason.
        - If `recheck = False`, the system will automatically route to the planner node, 
        which will handle content generation and clarification later.
        - If `recheck = True`, explain briefly why the current list seems insufficient (e.g., “no matching tools found”).

        Output must strictly follow:
        - `recheck`: True or False
        - `reason`: concise reason (e.g., “sufficient agents found” or “no matching tools”)
    """

    def search_agent(state: State) -> Command[Literal["search_agent_node", "planner_node", "__end__"]]:
        
        from chatagent.agents.agent_retrival import get_relevant_agents

        agents = get_relevant_agents(state["input"], top_k=5)

        print("\n\nAgents Retrieved for Search Agent Node:", agents,"\n\n")

        agent_search_count = state.get("agent_search_count", 0)

        with get_openai_callback() as cb:
            result: AgentCheck = llm.with_structured_output(AgentCheck).invoke(
                [
                    SystemMessage(content=SYSTEM_PROMPT),
                    HumanMessage(
                        content=(
                            "Available agents and tools:\n"
                            + "\n".join([f"- {agent['name']}: {agent['description']}" for agent in agents])
                            + f"\n\nUser Query: {state['input']}\n\n"
                            "Decide if any of these agents can handle the request. "
                            "If yes, return recheck=False; if not, return recheck=True."
                        )
                    ),
                ]
            )
        usages_data = usages(cb)


        print(f"Agent Searcher: {result} and Agents: {agents}")

        # **Condition 1: Agents are sufficient, proceed to planner.**
        if result.recheck is False:
            return Command(
                update={
                    "input": state["input"],
                    "messages": [AIMessage(content=f"Sufficient agents found: {result.reason}")],
                    "current_message": [AIMessage(content=f"{result.reason}")],
                    "reason": "Sufficient agents found to proceed with planning.",
                    "provider_id": state.get("provider_id"),
                    "next_node": "planner_node",
                    "type": "agent_searcher",
                    "next_type": "thinker",
                    "agents": agents,
                    "usages": usages_data,
                    "status": "success",
                    "current_task": state.get("current_task", "NO TASK"),
                    "tool_output": state.get("tool_output"),
                    "max_message": state.get("max_message", 10),
                },
                goto="planner_node"
            )

        # **Condition 2: Agents are insufficient, but we can still retry.**
        if result.recheck is True and agent_search_count < 3:
            return Command(
                update={
                    "input": state["input"],
                    "messages": [AIMessage(content=f"Retrying agent search: {result.reason}")],
                    "current_message": [AIMessage(content=f"{result.reason}")],
                    "reason": result.reason,
                    "agent_search_count": agent_search_count + 1,
                    "provider_id": state.get("provider_id"),
                    "next_node": "search_agent_node",
                    "type": "agent_searcher",
                    "agents": agents,
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
        final_reason = f"I am not capable of handling this request. After multiple searches, a suitable agent could not be found. Reason: {result.reason}"
        return Command(
            update={
                "input": state["input"],
                "messages": [AIMessage(content=final_reason)],
                "current_message": [AIMessage(content=final_reason)],
                "reason": final_reason,
                "provider_id": state.get("provider_id"),
                "next_node": "__end__",
                "type": "agent_searcher",
                "next_type": "end",
                "agents": agents,
                "usages": usages_data,
                "status": "fail",
                "current_task": state.get("current_task", "NO TASK"),
                "tool_output": state.get("tool_output"),
                "max_message": state.get("max_message", 10),
            },
            goto="__end__"
        )
        
    return search_agent