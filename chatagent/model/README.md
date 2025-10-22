# Model Package

This package contains all the data models used in the ChatVerse AI agent system.

## Structure

```
chatagent/model/
├── __init__.py                   # Package exports
├── chat_agent_model.py           # StreamChunk model for agent responses
├── tool_output.py                # ToolOutput model for tool results
├── interrupt_model.py            # Interrupt system models (NEW)
├── interrupt_helpers.py          # Helper functions for interrupts (NEW)
├── email_model.py                # Email-related models
├── test_interrupt_model.py       # Unit tests for interrupt system
├── INTERRUPT_EXAMPLES.md         # Code examples for interrupts
└── README.md                     # This file
```

## Models

### StreamChunk (`chat_agent_model.py`)
Represents a chunk of streaming data from the agent system.

**Key Features:**
- Stream type tracking (updates, custom)
- Node and message information
- Tool output and usage statistics
- Serialization for database storage

### ToolOutput (`tool_output.py`)
Represents the output from tool executions.

**Key Features:**
- Output content
- Display settings (show, type)
- Formatting options

### Interrupt Models (`interrupt_model.py`) ⭐ NEW
Structured models for the three types of interrupts:

1. **InterruptType** - Enum for interrupt types
2. **InputOptionData** - Data for multiple choice interrupts
3. **InputFieldData** - Data for text input interrupts
4. **ConnectData** - Data for platform connection interrupts
5. **InterruptRequest** - Main class with factory methods
6. **InterruptResponse** - Helper for parsing responses

**Quick Start:**
```python
from chatagent.model import InterruptRequest

# Create input option
req = InterruptRequest.create_input_option(
    name="confirm",
    title="Proceed?",
    options=["Yes", "No"]
)

# Use with langgraph
from langgraph.types import interrupt
result = interrupt(req.to_dict())
```

### Interrupt Helpers (`interrupt_helpers.py`) ⭐ NEW
Convenient wrapper functions for common interrupt patterns.

**Available Functions:**
- `ask_user_option()` - Ask user to choose from options
- `ask_user_input()` - Ask user for text input
- `ask_user_connect()` - Request platform connection
- `parse_option_response()` - Check if specific option was selected
- `is_affirmative()` - Check if response is positive
- `is_negative()` - Check if response is negative

**Quick Start:**
```python
from chatagent.model import ask_user_option, is_affirmative

response = ask_user_option(
    name="confirm",
    question="Send this email?",
    options=["Yes", "No"]
)

if is_affirmative(response):
    print("User confirmed!")
```

## Usage

### Import All Models
```python
from chatagent.model import (
    StreamChunk,
    ToolOutput,
    InterruptRequest,
    InterruptResponse,
    ask_user_option,
    ask_user_input,
    ask_user_connect
)
```

### Import Specific Models
```python
from chatagent.model.interrupt_model import InterruptRequest, InterruptType
from chatagent.model.interrupt_helpers import is_affirmative
```

## Documentation

- **[Interrupt System Documentation](../../INTERRUPT_SYSTEM_DOCS.md)** - Complete guide to the interrupt system
- **[Interrupt Examples](./INTERRUPT_EXAMPLES.md)** - Practical code examples and migration guide

## Testing

Run the interrupt model tests:
```bash
pytest chatagent/model/test_interrupt_model.py -v
```

## Migration Guide

### Old Way (Raw Dictionaries)
```python
# ❌ Error-prone and hard to maintain
approval = interrupt({
    "name": "send_email",
    "type": "input_option",
    "data": {
        "title": "Send?",
        "options": ["Yes", "No"]
    }
})
```

### New Way (Structured Models)
```python
# ✅ Type-safe and validated
from chatagent.model import ask_user_option

approval = ask_user_option(
    name="send_email",
    question="Send?",
    options=["Yes", "No"]
)
```

## Best Practices

1. **Use Helper Functions**: Prefer `ask_user_*` functions for simplicity
2. **Use Factory Methods**: Use `InterruptRequest.create_*()` for complex cases
3. **Type Hints**: Always use type hints with these models
4. **Validation**: Let Pydantic handle validation automatically
5. **Testing**: Write tests using the models for better reliability

## Contributing

When adding new models:

1. Add the model class to the appropriate file
2. Update `__init__.py` to export the new model
3. Add tests in the corresponding test file
4. Update this README with documentation
5. Add examples if the model is user-facing

## Future Enhancements

Planned additions to the model package:

- [ ] YouTube models for video and channel data
- [ ] Instagram models for posts and profiles
- [ ] Research models for search results
- [ ] Validation helpers for common data types
- [ ] Serialization utilities for complex types
