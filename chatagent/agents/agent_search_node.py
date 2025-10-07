from typing_extensions import Literal
from langchain_core.messages import AIMessage, HumanMessage
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

    def search_agent(state: State) -> Command[Literal["search_agent_node", "planner_node", "__end__"]]:
        
        from chatagent.agents.agent_retrival import get_relevant_agents

        agents = get_relevant_agents(state["input"], top_k=5)
        agent_search_count = state.get("agent_search_count", 0)

        with get_openai_callback() as cb:
            result: AgentCheck = llm.with_structured_output(AgentCheck).invoke(
                [
                    HumanMessage(
                        content=f"Available agents & tools:\n"
                        + "\n".join(
                            [
                                f"- {agent['name']}: {agent['description']}"
                                for agent in agents
                            ]
                        )
                        + f"\n\nUser Query: {state['input']}\n\n"
                        + "Based on the above available agents and user query, do you think the given agent list is sufficient to handle the user query or not, if you think it is sufficient then return False, if you think it is not sufficient then return True and explain why?"
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