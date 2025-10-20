# Streaming Configuration Guide

## Overview
This document explains the streaming behavior configuration for the ChatVerse AI system.

## Changes Made

### Problem
Previously, all LLM calls were streaming token-by-token, including:
- Structured outputs (Pydantic models, JSON responses)
- Router decisions
- Planning steps
- Final answers

This caused issues where JSON/structured data would stream character-by-character instead of being returned as complete objects.

### Solution

We now use **two separate LLM instances**:

#### 1. Non-Streaming LLM (`llm`)
- **Purpose**: For all structured outputs (Pydantic models, JSON)
- **Configuration**: `streaming=False`
- **Used by**:
  - `inputer_agent.py` - Router decisions
  - `planner_agent.py` - Plan generation
  - `supervisor_agent.py` - Routing decisions
  - `task_dispatcher.py` - Task routing
  - `agent_search_node.py` - Agent checks
  - `research_agent.py` - Structured data extraction
  - `email_agent.py` - Email drafts
  - All other agents using `with_structured_output()`

#### 2. Streaming LLM (`stream_llm`)
- **Purpose**: For final answers only (natural language responses)
- **Configuration**: `streaming=True`
- **Used by**:
  - `final_node.py` - Final answer generation (token-by-token)

## File Changes

### `/chatagent/config/init.py`
```python
# Non-streaming LLM for structured outputs (Pydantic models, JSON)
llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0,
    api_key=os.getenv("OPENAI_API_KEY"),
    streaming=False,
    tags=["nonstream"],
)

# Streaming LLM for final answers only (token-by-token)
stream_llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0,
    api_key=os.getenv("OPENAI_API_KEY"),
    streaming=True,
    tags=["stream"],
)
```

### `/chatagent/agents/final_node.py`
- Changed import from `llm` to `stream_llm`
- Changed instantiation: `FinalAnswerAgent(stream_llm).start`

## Behavior

### Before
- All outputs streamed character-by-character
- JSON responses appeared as: `{` `"` `n` `e` `x` `t` `"` `:` etc.
- Structured data was hard to parse on the frontend

### After
- **Structured outputs (JSON/Pydantic)**: Return complete objects immediately
- **Final answers**: Stream token-by-token for better UX
- Frontend receives clean JSON for routing decisions
- Users see streaming text only for final answers

## Stream Types in Router

In `chat_agent_router.py`, the stream handling works as follows:

1. **`stream_mode=["messages", "updates", "custom"]`**
   - `messages`: Token-by-token streaming (only from `final_node` now)
   - `updates`: Complete state updates from all other nodes
   - `custom`: Custom events

2. **Message Stream** (only from final_node with 'stream' tag):
   ```python
   if stream_type == "messages":
       metadata = stream_data[1]
       # ✅ CRITICAL: Only stream messages with 'stream' tag
       if metadata.get('tags') == ['stream']:
           # This now only streams from final_answer_node (stream_llm)
           # Sends: event: delta\ndata: {token}\n\n
   ```

3. **Updates Stream** (from all other nodes):
   ```python
   if stream_type == "updates":
       # Complete state objects from structured outputs
       # Sends: event: delta\ndata: {complete_json}\n\n
   ```

## Benefits

1. **Clean API responses**: Structured data arrives as complete JSON
2. **Better UX**: Final answers still stream for natural feel
3. **Easier parsing**: Frontend doesn't need to reconstruct JSON from character stream
4. **Performance**: Reduced overhead for structured outputs
5. **Type safety**: Pydantic validation works correctly with complete responses

## Testing

To verify the changes work correctly:

1. **Test structured output** (should return immediately):
   - Ask: "Send me an email"
   - Check: Router decision should arrive as complete JSON

2. **Test final answer** (should stream):
   - Ask: "What is Python?"
   - Check: Answer should stream token-by-token

## Migration Notes

- All existing agents automatically use non-streaming `llm`
- No changes needed to agent logic
- Only `final_node.py` uses streaming
- Backward compatible with existing code
