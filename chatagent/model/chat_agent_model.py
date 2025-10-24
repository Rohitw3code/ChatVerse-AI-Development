from pydantic import BaseModel, Field, field_serializer
from typing import Any, Dict, Optional, Union

from chatagent.utils import prepare_db_current_message_and_text, get_message_role
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from chatagent.db.serialization import Serialization
from chatagent.model.tool_output import ToolOutput

import os
from dotenv import load_dotenv
load_dotenv()


class StreamChunk(BaseModel):
    # basic metadata
    stream_type: str
    provider_id: str
    thread_id: str

    # message info
    role: Optional[str] = None
    node: Optional[str] = None
    next_node: Optional[str] = None
    type_: Optional[str] = None
    next_type: Optional[str] = None

    message: Optional[str] = None
    reason: Optional[str] = None
    current_messages: Optional[Union[str, Dict[str, Any], list]] = None
    params: Dict[str, Any] = Field(default_factory=dict)

    # flow
    status: Optional[str] = None

    # tool info
    tool_output: Union[str, Dict[str, Any]] = Field(
        default_factory=lambda: ToolOutput(output="NO OUTPUT").to_dict())
    data: Any = None

    # embeddings + usage
    embedding_vector: Optional[Any] = None
    usage: Dict[str, Any] = Field(default_factory=dict)
    total_token: int = 0
    total_cost: float = 0.0

    @field_serializer('data', 'params', 'tool_output', 'usage',
                      'current_messages', 'embedding_vector')
    def _serialize_any(self, v):
        return Serialization.serialize_for_json(v)

    @classmethod
    def from_chunk(cls, stream_type: str, stream_data: Any, *,
                   provider_id: str = "1", thread_id: str = "1",
                   db_current_message: Any = None):
        node_name = next(iter(stream_data.keys()))
        node_data = {}

        role, message_text, status = None, None, None

        # Handle updates
        if stream_type == "updates":
            if node_name == "__interrupt__":
                print("stream ==> ", stream_data)
                stream_data = {
                    "interrupt_node": {
                        "current_message": [
                            AIMessage(
                                content=str(
                                    stream_data[node_name][0].value['data']['title']))],
                        "node": "interrupt_node",
                        "next_node": "input_node",
                        "type": "interrupt",
                        "next_type": "human",
                        "status": "success",
                        "data": stream_data[node_name][0].value}}
                node_name = "interrupt_node"

            node_data = stream_data.get(node_name)
            
            # Handle None node_data
            if node_data is None:
                node_data = {}
            
            current_message = node_data.get("current_message", [])
            db_current_message, message_text = prepare_db_current_message_and_text(
                current_message)
            role = get_message_role(
                current_message[0]) if current_message else "unknown"
            status = "success"

        elif stream_type == "custom":
            node_data = stream_data.get(node_name)
            
            # Handle None node_data
            if node_data is None:
                node_data = {}
            
            status = node_data.get("status", "failed")
            current_message = node_data.get("current_message", [])

            if current_message:
                db_current_message, message_text = prepare_db_current_message_and_text(
                    current_message)
                # Use the utility function to determine role
                role = get_message_role(current_message[-1])
            else:
                role = "tool_message"

        usage = node_data.get("usages", {})

        return cls(
            stream_type=stream_type,
            provider_id=provider_id,
            thread_id=thread_id,
            role=role,
            node=node_name,
            next_node=node_data.get("next_node", ""),
            type_=node_data.get("type") or node_data.get("type_", ""),
            next_type=node_data.get("next_type", ""),
            message=message_text,
            reason=node_data.get("reason", ""),
            current_messages=db_current_message,
            params=node_data.get("params", {}),
            tool_output=node_data.get("tool_output") or ToolOutput().to_dict(),
            usage=usage,
            status=status,
            total_token=usage.get("completion_tokens", 0) if isinstance(usage, dict) else 0,
            total_cost=usage.get("total_cost", 0.0) if isinstance(usage, dict) else 0.0,
            data=node_data.get('data', {}),
        )