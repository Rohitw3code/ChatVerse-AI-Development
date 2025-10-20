# Tag-Based Streaming Filter - How It Works

## The Critical Filter

In `chat_agent_router.py`, this line is the key:

```python
if metadata.get('tags') == ['stream']:
    # Only stream messages with the 'stream' tag
    yield f"event: delta\ndata: {payload}\n\n"
```

## Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│ User Request → Graph Execution                               │
└─────────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│ inputer_node                                                 │
│ LLM: llm (streaming=False, tags=["nonstream"])              │
│ Output: RouterDecision (Pydantic)                           │
└─────────────────────────────────────────────────────────────┘
                         ↓
        ┌────────────────┴────────────────┐
        ↓                                  ↓
┌──────────────────┐              ┌──────────────────┐
│ Stream Mode:     │              │ Stream Mode:     │
│ "messages"       │              │ "updates"        │
├──────────────────┤              ├──────────────────┤
│ Metadata tags:   │              │ Node: inputer    │
│ ["nonstream"]    │              │ Status: success  │
│                  │              │ Next: search     │
│ ❌ FILTERED OUT  │              │ ✅ SENT          │
│ (tags != stream) │              │                  │
└──────────────────┘              └──────────────────┘
                                           ↓
                                  Frontend receives:
                                  Complete JSON object

┌─────────────────────────────────────────────────────────────┐
│ planner_node                                                 │
│ LLM: llm (streaming=False, tags=["nonstream"])              │
│ Output: Plan (Pydantic with steps)                          │
└─────────────────────────────────────────────────────────────┘
                         ↓
        ┌────────────────┴────────────────┐
        ↓                                  ↓
┌──────────────────┐              ┌──────────────────┐
│ Stream Mode:     │              │ Stream Mode:     │
│ "messages"       │              │ "updates"        │
├──────────────────┤              ├──────────────────┤
│ Metadata tags:   │              │ Node: planner    │
│ ["nonstream"]    │              │ Plans: [...]     │
│                  │              │ Next: dispatcher │
│ ❌ FILTERED OUT  │              │ ✅ SENT          │
│ (tags != stream) │              │                  │
└──────────────────┘              └──────────────────┘
                                           ↓
                                  Frontend receives:
                                  Complete Plan object

... (other nodes with llm - all filtered) ...

┌─────────────────────────────────────────────────────────────┐
│ final_answer_node                                            │
│ LLM: stream_llm (streaming=True, tags=["stream"])           │
│ Output: Natural language response                           │
└─────────────────────────────────────────────────────────────┘
                         ↓
        ┌────────────────┴────────────────┐
        ↓                                  ↓
┌──────────────────┐              ┌──────────────────┐
│ Stream Mode:     │              │ Stream Mode:     │
│ "messages"       │              │ "updates"        │
├──────────────────┤              ├──────────────────┤
│ Metadata tags:   │              │ Node: final      │
│ ["stream"]       │              │ Status: success  │
│                  │              │ Next: __end__    │
│ ✅ PASSED        │              │ ✅ SENT          │
│ Token-by-token!  │              │                  │
└──────────────────┘              └──────────────────┘
        ↓                                  ↓
Frontend receives:                Frontend receives:
Streaming tokens!                 Complete final state
"Here" "is" "your"...            (with full message)
```

## Code Comparison

### ❌ Before (No Tag Filter)
```python
# ALL messages streamed token-by-token
if stream_type == "messages":
    message_chunk = stream_data[0]
    metadata = stream_data[1]
    node_name = metadata.get('langgraph_node')
    
    if node_name and message_chunk.content:
        # ❌ Sends all messages, including structured outputs
        yield f"event: delta\ndata: {payload}\n\n"
```

**Result:**
- Router decisions: `{` `"` `n` `e` `x` `t` `"` `:` ... ❌
- Plans: `{` `"` `s` `t` `e` `p` `s` `"` `:` ... ❌
- Final answer: `H` `e` `r` `e` ` ` `i` `s` ... ✅

### ✅ After (With Tag Filter)
```python
# ONLY messages with 'stream' tag are streamed
if stream_type == "messages":
    message_chunk = stream_data[0]
    metadata = stream_data[1]
    
    # ✅ CRITICAL FILTER
    if metadata.get('tags') == ['stream']:
        node_name = metadata.get('langgraph_node')
        
        if node_name and message_chunk.content:
            # ✅ Only sends messages from stream_llm
            yield f"event: delta\ndata: {payload}\n\n"
```

**Result:**
- Router decisions: (filtered out, sent via "updates") ✅
- Plans: (filtered out, sent via "updates") ✅
- Final answer: `H` `e` `r` `e` ` ` `i` `s` ... ✅

## Tag Configuration

### In `/chatagent/config/init.py`

```python
# Non-streaming LLM for structured outputs
llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0,
    api_key=os.getenv("OPENAI_API_KEY"),
    streaming=False,
    tags=["nonstream"],  # ← Tag identifies this LLM
)

# Streaming LLM for final answers
stream_llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0,
    api_key=os.getenv("OPENAI_API_KEY"),
    streaming=True,
    tags=["stream"],  # ← Tag identifies this LLM
)
```

## Metadata Structure

When a message arrives at the router:

```python
# From llm (non-streaming)
metadata = {
    'langgraph_node': 'planner_node',
    'langgraph_triggers': [...],
    'langgraph_path': [...],
    'tags': ['nonstream'],  # ← Filter checks this
    ...
}
# ❌ Filtered out: tags != ['stream']

# From stream_llm (streaming)
metadata = {
    'langgraph_node': 'final_answer_node',
    'langgraph_triggers': [...],
    'langgraph_path': [...],
    'tags': ['stream'],  # ← Filter checks this
    ...
}
# ✅ Passed: tags == ['stream']
```

## Benefits of Tag Filtering

1. **Precise Control**: Only messages you want streamed will stream
2. **No Accidental Streaming**: Structured outputs can't leak through
3. **Future-Proof**: Can add more tags for different behaviors
4. **Debugging**: Easy to identify which LLM produced which message
5. **Performance**: Frontend doesn't waste time on filtered messages

## Testing the Filter

Run this to see tag filtering in action:

```python
# This will NOT stream (filtered by tags)
result = await llm.ainvoke([HumanMessage(content="test")])

# This WILL stream (tags == ['stream'])
async for chunk in stream_llm.astream([HumanMessage(content="test")]):
    print(chunk.content, end="")
```

## Summary

The tag filter is the **critical piece** that makes selective streaming work:

```python
if metadata.get('tags') == ['stream']:
    # Stream it! ✅
else:
    # Filter it out! ❌
```

Without this filter, even with `streaming=False`, some messages might still attempt to stream through the "messages" stream mode. The tag filter ensures **only** `stream_llm` outputs reach the frontend as token streams.
