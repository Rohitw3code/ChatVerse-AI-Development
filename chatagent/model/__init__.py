"""
Model package initialization.
Exports interrupt models and helpers to avoid circular imports.
StreamChunk and ToolOutput should be imported directly from their modules.
"""

# Only import interrupt-related models to avoid circular import issues
# with utils.py which imports ToolOutput
from chatagent.model.interrupt_model import (
    InterruptType,
    InterruptData,
    InputOptionData,
    InputFieldData,
    ConnectData,
    InterruptRequest,
    InterruptResponse
)
from chatagent.model.interrupt_helpers import (
    ask_user_option,
    ask_user_input,
    ask_user_connect,
    parse_option_response,
    is_affirmative,
    is_negative
)

__all__ = [
    'InterruptType',
    'InterruptData',
    'InputOptionData',
    'InputFieldData',
    'ConnectData',
    'InterruptRequest',
    'InterruptResponse',
    'ask_user_option',
    'ask_user_input',
    'ask_user_connect',
    'parse_option_response',
    'is_affirmative',
    'is_negative',
]
