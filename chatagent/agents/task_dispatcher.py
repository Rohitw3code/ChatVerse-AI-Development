from typing import Optional
from pydantic import BaseModel, Field, field_validator
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, SystemMessage, HumanMessage, get_buffer_string
from langgraph.graph import END
from langgraph.types import Command
from chatagent.utils import State, usages
from typing import List, Optional, Literal
from chatagent.node_registry import NodeRegistry
from langchain_community.callbacks.openai_info import OpenAICallbackHandler
from langchain_core.runnables import RunnableConfig
from langchain_community.callbacks import get_openai_callback


callback_handler = OpenAICallbackHandler()


def task_dispatcher(
    llm: BaseChatModel,
    registry: NodeRegistry,
):
    
    node_name = "task_dispatcher"

    system_prompt = f"""<prompt>
        <role>You are {node_name}, an orchestrator supervisor. Your only job is to analyze the current state and route to the correct node to continue the plan. You must not end the process if there are still plans left to execute, unless repeated failures occur.</role>
        <output_format>
            Your response MUST be a single, valid JSON object and nothing else.
            <json_schema>
            {{
                "next": "<string: exact_node_name | 'END' | 'NEXT_TASK'>",
                "reason": "<string: concise justification for your choice>"
            }}
            </json_schema>
        </output_format>
        <instructions>
            <rule id="1">Analyze the `current_task` and `remaining_plans` provided in the user message to decide the next step.</rule>
            <rule id="2">Route to the node from `<available_nodes>` that is best equipped to handle the `current_task`.</rule>
            <rule id="3">Only select 'NEXT_TASK' if the current task is fully complete and you must proceed to the next plan.</rule>
            <rule id="4">You MUST ONLY select 'END' when the `remaining_plans` list is explicitly empty.</rule>
            <rule id="5">If after 1–2 attempts the AI keeps responding that there are no available tools, no capabilities, or that it cannot do the task, you MUST select 'END' to avoid infinite recursion.</rule>
            <rule id="6">Do not write too long write in brifly wihtout revealing the node name </rule>
        </instructions>
        <available_nodes>
            {registry.prompt_block("Supervisor")}
        </available_nodes>
        <allowed_choices>
            The "next" value must be one of the following exact strings: {registry.members() + ['END', 'NEXT_TASK']}
        </allowed_choices>
    </prompt>"""

    members = registry.members()+['final_answer_node']

    class Router(BaseModel):
        
        next: str = Field(
            ...,
            description="Exact node name to call next, or 'END' or 'NEXT_TASK' to handle special commands.")
        reason: str = Field(..., description="write as human what you did and what next never reveal the next node name here or any internal state talk like human approch")

        @field_validator("next")
        @classmethod
        def validate_next(cls, v: str) -> str:
            if not v or not v.strip():
                raise ValueError("'next' must not be empty")
            v = v.strip()
            allowed = members + ["END", "NEXT_TASK"]
            if v not in allowed:
                print(f"[WARN] Invalid next='{v}', falling back to END")
                return "END"
            return v

    def task_dispatcher_node(state: State) -> Command[Literal[*members]]:
        
        remaining_plans = state.get('plans', [])
        current_task = state.get('current_task', '')

        # If an agent marked the current task as completed, move to the next task deterministically
        if state.get('task_status') == 'completed':
            done_msg = AIMessage(content="Task completed. Moving to the next task.")
            return Command(
                goto="task_selection_node",
                update={
                    "input": state["input"],
                    "messages": [done_msg],
                    "current_message": [done_msg],
                    "reason": done_msg.content,
                    "provider_id": state.get("provider_id"),
                    "node": node_name,
                    "next_node": "task_selection_node",
                    "type": "thinker",
                    "next_type": "planner",
                    "usages": {},
                    "status": "success",
                    "plans": state.get("plans", []),
                    "current_task": state.get("current_task", "NO TASK"),
                    "tool_output": state.get("tool_output"),
                    "max_message": state.get("max_message", 10),
                    "dispatch_retries": 0,
                    "task_status": "",
                },
            )

        # Guardrails and loop-prevention counters
        dispatch_retries = state.get('dispatch_retries', 0)
        max_dispatch_retries = state.get('max_dispatch_retries', 3)
        new_dispatch_retries = dispatch_retries + 1

        # End after too many attempts on the same task
        if new_dispatch_retries >= max_dispatch_retries:
            replan_msg = AIMessage(content=(
                "Multiple attempts could not route/execute the current task. "
                "Sending to the replanner to adjust the plan so execution can continue."
            ))
            return Command(
                goto="replanner_node",
                update={
                    "input": state["input"],
                    "messages": [replan_msg],
                    "current_message": [replan_msg],
                    "reason": replan_msg.content,
                    "provider_id": state.get("provider_id"),
                    "node": node_name,
                    "next_node": "replanner_node",
                    "type": "thinker",
                    "next_type": "thinker",
                    "usages": {},
                    "status": "replan",
                    "plans": state.get("plans", []),
                    "current_task": current_task or "NO TASK",
                    "tool_output": state.get("tool_output"),
                    "max_message": state.get("max_message", 10),
                    "dispatch_retries": 0,
                },
            )

        prompt_context = HumanMessage(
            content=f"""Here is the current state of the workflow:
            <current_task>
            {current_task}
            </current_task>

            <remaining_plans>
            {remaining_plans}
            </remaining_plans>

            <attempt_info>
            dispatch_retries: {new_dispatch_retries} / {max_dispatch_retries}
            </attempt_info>

            Based on the `current_task` and the `remaining_plans`, decide the next step.
            Remember: Do NOT choose 'END' unless the `remaining_plans` list is empty.
            """
        )

        print("length ==> ",len(state['messages']))

        messages = [
            SystemMessage(content=system_prompt),
            prompt_context
        ]+state['messages']

        with get_openai_callback() as cb:
            try:
                response: Router = llm.with_structured_output(Router).invoke(
                    messages
                )
            except Exception as e:
                print(f"[ERROR] LLM failed to produce valid Router output: {e}")
                response = Router(next="END", reason="LLM failed, ending safely.")

        usages_data = usages(cb)

        if response.next.upper() == "NEXT_TASK":
            return Command(
                goto="task_selection_node",
                update={
                    "input": state["input"],
                    "messages": [AIMessage(content=f"Dispatcher: {response.reason}")],
                    "current_message": [AIMessage(content=response.reason)],
                    "reason": response.reason,
                    "provider_id": state.get("provider_id"),
                    "node": node_name,
                    "next_node": "task_selection_node",
                    "type": "thinker",
                    "next_type": "planner",
                    "usages": usages_data,
                    "status": "success",
                    "plans": state.get("plans", []),
                    "current_task": state.get("current_task", "NO TASK"),
                    "tool_output": state.get("tool_output"),
                    "max_message": state.get("max_message", 10),
                    "dispatch_retries": 0,
                },
            )

        if response.next.upper() in {"END", "FINISH"}:
            return Command(
                goto="final_answer_node",
                update={
                    "input": state["input"],
                    "messages": [AIMessage(content=f"All Tasks Completed: {response.reason}")],
                    "current_message": [AIMessage(content=f"{response.reason}")],
                    "reason": response.reason,
                    "provider_id": state.get("provider_id"),
                    "node": node_name,
                    "next_node": "final_answer_node",
                    "type": "thinker",
                    "next_type": "END",
                    "usages": usages_data,
                    "status": "success",
                    "plans": state.get("plans", []),
                    "current_task": state.get("current_task", "NO TASK"),
                    "tool_output": state.get("tool_output"),
                    "max_message": state.get("max_message", 10),
                    "dispatch_retries": new_dispatch_retries,
                },
            )

        spec = registry.get(response.next)
        resolved_type = spec.type if spec else "unknown"

        return Command(
            goto=response.next,
            update={
                "input": state["input"],
                "messages": [AIMessage(content=f"Dispatcher: {response.reason}")],
                "current_message": [AIMessage(content=f"Routing to {response.next} because {response.reason}")],
                "reason": response.reason,
                "provider_id": state.get("provider_id"),
                "node": node_name,
                "next_node": response.next,
                "type": "thinker",
                "next_type": "thinker" if resolved_type == "supervisor" else "executor",
                "usages": usages_data,
                "status": "success",
                "plans": state.get("plans", []),
                "current_task": state.get("current_task", "NO TASK"),
                "tool_output": state.get("tool_output"),
                "max_message": state.get("max_message", 10),
                "dispatch_retries": new_dispatch_retries,
            },
        )

    task_dispatcher_node.__name__ = node_name
    return task_dispatcher_node