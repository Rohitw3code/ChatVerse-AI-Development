from contextvars import ContextVar
from typing_extensions import TypedDict
from typing import Annotated, List, Tuple
import operator
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
import json
from rich.table import Table
from rich.console import Console
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from typing import TypedDict, Annotated, Union, Literal, Optional, List
from langgraph.graph.message import add_messages
from langgraph.config import get_stream_writer
from chatagent.model.tool_output import ToolOutput
from typing_extensions import Annotated
from langgraph.prebuilt import InjectedState

JSON = Union[dict, list, str, int, float, bool, None]

# Allowed flow types (expanded for real-world consistency)
AllowedType = Literal[
    "starter",
    "planner",
    "thinker",
    "executor",
    "unknown",
    "interrupt",
    "human",
    "END",
]

NodeType = Literal[
    'starter',
    'planner',
    'supervisor',
    'agent',
    'tool',
    'interrupt',
    'human',
    'end'
]


# just for knowledge this data is already avaible in the data column
InterruptType = Literal[
    'input_field',
    'input_option',
    'connect',
]

from langchain_core.runnables import RunnableConfig

def get_user_id(config: RunnableConfig) -> str:
    user_id = config["configurable"].get("user_id")
    if user_id is None:
        raise ValueError("User ID needs to be provided to save a memory.")

    return user_id

class State(TypedDict, total=False):
    input: str
    messages: Annotated[list, add_messages]
    current_message: list
    reason: str | None

    provider_id:str

    next_node: str | None

    type: AllowedType | str
    next_type: AllowedType | str | None

    plans: List[str]
    current_task: str

    usages: JSON
    tool_output: JSON
    max_message:int = 10

    agent_search_count: int   # max agent search attempts

    agents: List[dict]  # list of agents available

    # Routing guardrails
    back_count: int
    max_back: int
    dispatch_retries: int
    max_dispatch_retries: int

    # Task tracking
    task_status: str


import json
from datetime import datetime

def normalize_db_current_messages(raw):
    """
    Normalize arbitrary `current_messages` stored in DB (str, list, dict, or list of
    LangChain messages) into a list of plain dicts suitable for JSONB storage
    and later reconversion.
    """
    if not raw:
        return []

    # If raw is a JSON string, try to parse it
    if isinstance(raw, str):
        try:
            parsed = json.loads(raw)
            raw = parsed
        except Exception:
            return [{"role": "ai", "content": str(raw)}]

    # If it's a dict like {"messages": [...]}
    if isinstance(raw, dict) and "messages" in raw and isinstance(raw["messages"], list):
        raw = raw["messages"]

    # If it's a list
    if isinstance(raw, list):
        normalized = []
        for m in raw:
            if isinstance(m, dict):
                normalized.append(m)
            else:
                try:
                    normalized.append(_safe_message_to_dict(m))
                except Exception:
                    normalized.append({"role": "ai", "content": str(m)})
        return normalized

    # If single dict
    if isinstance(raw, dict):
        return [raw]

    # Fallback
    return [{"role": "ai", "content": str(raw)}]


def messages_to_chat_history(messages):
    """
    Convert a list of LangChain Message objects into our chat_history list-of-dicts format.
    Each entry has at least 'role', 'content', and 'timestamp'.
    """
    result = []
    for m in messages or []:
        d = _safe_message_to_dict(m)
        entry = {
            "role": d.get("role"),
            "content": d.get("content"),
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
        # preserve optional fields if available
        if isinstance(d, dict):
            for opt in ("name", "additional_kwargs"):
                if d.get(opt) is not None:
                    entry[opt] = d.get(opt)
        result.append(entry)
    return result


def usages(callback_handler):
    # Try to get usage from callback first (this should work for OpenAI models)
    callback_data = {
        "total_cost": callback_handler.total_cost,
        "successful_requests": callback_handler.successful_requests,
        "prompt_tokens": callback_handler.prompt_tokens,
        "completion_tokens": callback_handler.completion_tokens,
        "total_tokens": callback_handler.total_tokens,
        "reasoning_tokens": callback_handler.reasoning_tokens,
        "prompt_tokens_cached": callback_handler.prompt_tokens_cached,
    }
    
    # If callback data is empty, check if there's a custom usage dict passed
    if hasattr(callback_handler, 'custom_usage') and callback_handler.custom_usage:
        # If callback didn't capture anything, use custom usage
        if callback_data["total_tokens"] == 0 and callback_data["total_cost"] == 0:
            callback_data.update(callback_handler.custom_usage)
        else:
            # Add custom usage to existing callback data
            for key, value in callback_handler.custom_usage.items():
                if isinstance(value, (int, float)) and key in callback_data:
                    callback_data[key] += value
                elif key not in callback_data:
                    callback_data[key] = value
    
    return callback_data

def extract_usage_from_response(response):
    """Extract usage information from LLM response when callback doesn't work"""
    usage_data = {
        "total_cost": 0.0,
        "successful_requests": 1,
        "prompt_tokens": 0,
        "completion_tokens": 0,
        "total_tokens": 0,
        "reasoning_tokens": 0,
        "prompt_tokens_cached": 0,
    }
    
    # Try to get usage from response_metadata.token_usage (newer format)
    if hasattr(response, 'response_metadata') and response.response_metadata:
        metadata = response.response_metadata
        if 'token_usage' in metadata:
            usage = metadata['token_usage']
            usage_data.update({
                "prompt_tokens": usage.get('prompt_tokens', 0),
                "completion_tokens": usage.get('completion_tokens', 0),
                "total_tokens": usage.get('total_tokens', 0),
            })
            # Extract reasoning tokens if available
            if 'completion_tokens_details' in usage:
                details = usage['completion_tokens_details']
                usage_data["reasoning_tokens"] = details.get('reasoning_tokens', 0)
            if 'prompt_tokens_details' in usage:
                details = usage['prompt_tokens_details']
                usage_data["prompt_tokens_cached"] = details.get('cached_tokens', 0)
    
    # Try to get usage from usage_metadata (newer LangChain versions)
    if hasattr(response, 'usage_metadata') and response.usage_metadata:
        usage = response.usage_metadata
        usage_data.update({
            "prompt_tokens": usage.get('input_tokens', 0),
            "completion_tokens": usage.get('output_tokens', 0),
            "total_tokens": usage.get('total_tokens', 0),
        })
        # Extract reasoning tokens from output details
        if hasattr(usage, 'output_token_details'):
            details = usage['output_token_details']
            usage_data["reasoning_tokens"] = details.get('reasoning', 0)
        if hasattr(usage, 'input_token_details'):
            details = usage['input_token_details']
            usage_data["prompt_tokens_cached"] = details.get('cache_read', 0)
    
    # Estimate cost for gpt-4o-mini (roughly $0.00015 per 1K prompt tokens, $0.0006 per 1K completion tokens)
    if usage_data["prompt_tokens"] > 0 or usage_data["completion_tokens"] > 0:
        prompt_cost = (usage_data["prompt_tokens"] / 1000) * 0.00015
        completion_cost = (usage_data["completion_tokens"] / 1000) * 0.0006
        usage_data["total_cost"] = prompt_cost + completion_cost
    
    return usage_data

def create_enhanced_callback():
    """Create a callback handler that can track custom usage data"""
    from langchain_community.callbacks.openai_info import OpenAICallbackHandler
    
    class EnhancedCallback(OpenAICallbackHandler):
        def __init__(self):
            super().__init__()
            self.custom_usage = {}
            
        def add_usage_data(self, usage_data):
            """Add custom usage data to the callback"""
            if not self.custom_usage:
                self.custom_usage = usage_data.copy()
            else:
                # Accumulate the data
                for key, value in usage_data.items():
                    if isinstance(value, (int, float)):
                        self.custom_usage[key] = self.custom_usage.get(key, 0) + value
                    else:
                        self.custom_usage[key] = value
    
    return EnhancedCallback()


def _to_params_dict(p):
    if isinstance(p, dict):
        return p
    for attr in ("model_dump", "dict"):
        if hasattr(p, attr):
            try:
                return getattr(p, attr)()
            except Exception:
                pass
    try:
        json.dumps(p)
        return {"value": p}
    except Exception:
        return {"value": str(p)}


def log_tool_event(
    tool_name: str,
    status: str,
    params,
    parent_node: str,
    tool_output: Union["ToolOutput", str, dict, None] = None,
    usages: dict | None = None,
    state:State={}
):
    """Emit a structured tool event into the LangGraph stream."""

    normalized_output = {}
    # Normalize tool_output
    if isinstance(tool_output, ToolOutput):
        normalized_output = tool_output.to_dict()
    else:
        normalized_output = ToolOutput(output=tool_output).to_dict()

    if usages is None:
        usages = {}

    writer = get_stream_writer()
    writer(
        {
            tool_name: {
                "current_message": [
                    {"role": "tool", "content": f"Called {parent_node} -> {tool_name}"}
                ],
                "reason": f"I need to execute {tool_name}",
                "messages":state.get('messages',[]) + [
                    {"role": "tool", "content": f"Called {parent_node} -> {tool_name}"}
                ],
                "next_node": parent_node,
                "type": "tool",
                "next_type": "executor",
                "status": status,
                "params": _to_params_dict(params),
                "tool_output": normalized_output,
                "parent_node": parent_node,
                "usages": usages
            }
        }
    )


def sanitize_messages(messages: list) -> list:
    """
    Remove AIMessages with tool_calls that don't have corresponding ToolMessage responses.
    This ensures LLM context is valid and prevents tool_call orphaning errors.
    
    Args:
        messages: List of LangChain message objects
        
    Returns:
        Sanitized list of messages with proper tool_call/ToolMessage pairing
    """
    sanitized = []
    i = 0
    while i < len(messages):
        msg = messages[i]
        
        # Handle AIMessage with tool_calls
        if isinstance(msg, AIMessage) and hasattr(msg, "tool_calls") and msg.tool_calls:
            has_tool_response = False
            if i + 1 < len(messages):
                next_msg = messages[i + 1]
                if isinstance(next_msg, ToolMessage):
                    has_tool_response = True
            
            if has_tool_response:
                # Include the AIMessage with tool_calls and the ToolMessage(s)
                sanitized.append(msg)
                i += 1
                while i < len(messages) and isinstance(messages[i], ToolMessage):
                    sanitized.append(messages[i])
                    i += 1
                continue
            else:
                # Create a copy without tool_calls to avoid orphaning
                msg_copy = AIMessage(content=msg.content if msg.content else "Continuing...")
                sanitized.append(msg_copy)
        elif isinstance(msg, ToolMessage):
            # Skip orphaned ToolMessages
            pass
        else:
            # Regular message, keep it
            sanitized.append(msg)
        
        i += 1
    
    return sanitized


def prepare_db_current_message_and_text(current_message):
    db_current_message, message_text = [], ""
    for msg in reversed(current_message or []):
        role, content = None, None
        entry = {}

        if isinstance(msg, AIMessage):
            role, content = "ai", msg.content
            entry = {
                "role": role,
                "content": content,
                "id": getattr(msg, "id", None),
                "additional_kwargs": getattr(msg, "additional_kwargs", {}),
            }

        elif isinstance(msg, HumanMessage):
            role, content = "user", msg.content
            entry = {
                "role": role,
                "content": content,
                "id": getattr(msg, "id", None),
            }

        elif isinstance(msg, ToolMessage):
            role, content = "tool", msg.content
            entry = {
                "role": role,
                "content": content,
                "id": getattr(msg, "id", None),
                "name": getattr(msg, "name", None),
                "tool_call_id": getattr(msg, "tool_call_id", None),
            }

        elif isinstance(msg, dict):
            role, content = msg.get("role"), msg.get("content")
            entry = msg  # trust dict as-is

        # Add to db + message_text
        if content and role in {"ai", "user", "tool"}:
            prefix = {"ai": "AI", "user": "User", "tool": "Tool"}[role]
            message_text += f"{prefix}: {content}\n\n"
            db_current_message.append(entry)

    return db_current_message, message_text


def get_message_role(msg):
    """Identify if message is AI, Human, or Tool."""
    if isinstance(msg, AIMessage):
        return "ai_message"
    elif isinstance(msg, HumanMessage):
        return "human_message"
    elif isinstance(msg, ToolMessage):
        return "tool_message"
    elif isinstance(msg, dict):
        return {
            "ai": "ai_message",
            "user": "human_message",
            "tool": "tool_message",
        }.get(msg.get("role"), "unknown")
    return "unknown"


console = Console()


def _safe_get_role(msg):
    """Extract role from AI/Human/Tool messages or dicts."""
    if isinstance(msg, AIMessage):
        return "ai"
    elif isinstance(msg, HumanMessage):
        return "user"
    elif isinstance(msg, ToolMessage):
        return "tool"
    elif isinstance(msg, dict):
        return msg.get("role")
    return "unknown"



def _safe_message_to_dict(msg):
    """Convert LangChain messages or dicts into a rich dict containing role, content and metadata."""
    if isinstance(msg, AIMessage):
        return {
            "role": "ai",
            "content": msg.content,
            "id": getattr(msg, "id", None),
            "additional_kwargs": getattr(msg, "additional_kwargs", {}),
        }
    elif isinstance(msg, HumanMessage):
        return {
            "role": "user",
            "content": msg.content,
            "id": getattr(msg, "id", None),
        }
    elif isinstance(msg, ToolMessage):
        return {
            "role": "tool",
            "content": msg.content,
            "id": getattr(msg, "id", None),
            "name": getattr(msg, "name", None),
            "tool_call_id": getattr(msg, "tool_call_id", None),
        }
    elif isinstance(msg, dict):
        # Trust dicts stored in DB (they may already include metadata)
        out = {"role": msg.get("role"), "content": msg.get("content")}
        # copy optional keys if present
        for opt in ("id", "name", "tool_call_id", "additional_kwargs"):
            if opt in msg:
                out[opt] = msg[opt]
        return out
    return {"role": "unknown", "content": str(msg)}



def print_stream_debug(stream_data: dict):
    """
    Pretty-print key fields from LangGraph stream_data using Rich.
    Handles both dict and LangChain Message objects safely.
    """
    if not stream_data:
        console.print("[red]⚠️ Empty stream_data[/red]")
        return

    node_name = next(iter(stream_data.keys()))
    node_data = stream_data[node_name]
    try:
        current_message = node_data.get("current_message") or []
    except BaseException:
        return
    # normalize to list of dicts
    normalized_messages = [_safe_message_to_dict(m) for m in current_message]

    debug_info = {
        # "input": node_data.get("input"),
        "node": node_name,
        "next_node": node_data.get("next_node"),
        "type": node_data.get("type") or node_data.get("type_", ""),
        "next_type": node_data.get("next_type"),
        "current_message": normalized_messages,
        "reason": node_data.get("reason"),
        "role": _safe_get_role(current_message[-1]) if current_message else None,
        "params": node_data.get("params"),
        "tool_output": node_data.get("tool_output"),
        "plans": node_data.get("plans", []),
        "status": node_data.get("status", "no found"),
        # "past_steps": node_data.get("past_steps", []),
        "current_task": node_data.get("current_task", "NO TASK"),

        # Routing guardrails (counters only)
        "back_count": node_data.get("back_count", 0),
        "max_back": node_data.get("max_back", 3),
        "dispatch_retries": node_data.get("dispatch_retries", 0),
        "max_dispatch_retries": node_data.get("max_dispatch_retries", 3),

        # Task tracking
        "task_status": node_data.get("task_status", "pending"),
    }

    table = Table(title="🔍 Stream Debug Info", show_lines=True)
    table.add_column("Field", style="cyan", no_wrap=True)
    table.add_column("Value", style="magenta")

    for k, v in debug_info.items():
        if isinstance(v, (dict, list)):
            v = json.dumps(v, indent=2, ensure_ascii=False)
        table.add_row(k, str(v))

    console.print(table)