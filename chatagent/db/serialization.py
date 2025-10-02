import json
from langchain_core.messages import BaseMessage

class Serialization:
    """A utility class for data serialization and validation."""

    @staticmethod
    def serialize_for_json(obj):
        """Custom serializer for non-JSON serializable objects."""
        if isinstance(obj, BaseMessage):
            return {
                "type": obj.__class__.__name__,
                "content": obj.content,
                "additional_kwargs": obj.additional_kwargs,
                "response_metadata": getattr(obj, "response_metadata", {}),
                "id": getattr(obj, "id", None),
                "name": getattr(obj, "name", None),
            }
        elif hasattr(obj, "__dict__"):
            try:
                return {
                    k: Serialization.serialize_for_json(v)
                    for k, v in obj.__dict__.items()
                    if not k.startswith("_") and not callable(v)
                }
            except BaseException:
                return str(obj)
        elif isinstance(obj, (list, tuple)):
            return [Serialization.serialize_for_json(item) for item in obj]
        elif isinstance(obj, dict):
            return {k: Serialization.serialize_for_json(v) for k, v in obj.items()}
        elif isinstance(obj, (str, int, float, bool, type(None))):
            return obj
        else:
            return str(obj)

    @staticmethod
    def validate_and_map_role(role_value):
        """Validate and map role values to allowed database values."""
        if not role_value:
            return "human_message"

        role_str = str(role_value).lower().strip()

        allowed_roles = {
            "tool_message": "tool_message",
            "ai_message": "ai_message",
            "human_message": "human_message",
            "assistant": "ai_message",
            "user": "human_message",
            "tool": "tool_message",
            "system": "ai_message",
        }

        return allowed_roles.get(role_str, "human_message")

    @staticmethod
    def safe_json_dumps(obj):
        """Safely convert an object to a JSON string."""
        if obj is None:
            return None
        try:
            serialized_obj = Serialization.serialize_for_json(obj)
            return json.dumps(serialized_obj, default=str)
        except Exception as e:
            return json.dumps(
                {"error": f"Serialization failed: {str(e)}", "raw_data": str(obj)}
            )