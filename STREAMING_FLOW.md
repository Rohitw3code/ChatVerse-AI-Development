# Streaming Architecture Flow

## Request Flow with New Configuration

```
User Request
    ↓
┌───────────────────────────────────────────────────────────┐
│ inputer_node (Router)                                      │
│ LLM: llm (non-streaming)                                   │
│ Output: RouterDecision (Pydantic)                          │
│ Returns: Complete JSON immediately                         │
└───────────────────────────────────────────────────────────┘
    ↓
┌───────────────────────────────────────────────────────────┐
│ search_agent_node                                          │
│ LLM: llm (non-streaming)                                   │
│ Output: AgentCheck (Pydantic)                              │
│ Returns: Complete JSON immediately                         │
└───────────────────────────────────────────────────────────┘
    ↓
┌───────────────────────────────────────────────────────────┐
│ planner_node                                               │
│ LLM: llm (non-streaming)                                   │
│ Output: Plan (Pydantic with steps)                         │
│ Returns: Complete JSON immediately                         │
└───────────────────────────────────────────────────────────┘
    ↓
┌───────────────────────────────────────────────────────────┐
│ task_dispatcher_node                                       │
│ LLM: llm (non-streaming)                                   │
│ Output: Router (Pydantic)                                  │
│ Returns: Complete JSON immediately                         │
└───────────────────────────────────────────────────────────┘
    ↓
┌───────────────────────────────────────────────────────────┐
│ supervisor_node (if needed)                                │
│ LLM: llm (non-streaming)                                   │
│ Output: Router (Pydantic)                                  │
│ Returns: Complete JSON immediately                         │
└───────────────────────────────────────────────────────────┘
    ↓
┌───────────────────────────────────────────────────────────┐
│ Agent Execution (gmail/instagram/youtube/research)         │
│ LLM: llm (non-streaming)                                   │
│ Output: Tool calls & structured data                       │
│ Returns: Complete JSON immediately                         │
└───────────────────────────────────────────────────────────┘
    ↓
┌───────────────────────────────────────────────────────────┐
│ final_answer_node                                          │
│ LLM: stream_llm (STREAMING ✨)                             │
│ Output: Natural language response                          │
│ Returns: Token-by-token stream                             │
└───────────────────────────────────────────────────────────┘
    ↓
User sees streaming response
```

## Frontend Receives

### During Workflow (non-streaming nodes)
```json
{
  "stream_type": "updates",
  "event": "delta",
  "data": {
    "node": "planner_node",
    "status": "success",
    "next_node": "task_dispatcher_node",
    "message": "Complete message here",
    "plans": ["Step 1", "Step 2"]
  }
}
```
✅ **Complete JSON objects** - No character-by-character assembly needed!

### Final Answer (streaming node)
```
event: delta
data: {"stream_type": "messages", "message": "Here"}

event: delta
data: {"stream_type": "messages", "message": " is"}

event: delta
data: {"stream_type": "messages", "message": " your"}

event: delta
data: {"stream_type": "messages", "message": " answer"}
```
✅ **Token-by-token streaming** - Natural typing effect!

## Key Differences

| Aspect | Old Behavior | New Behavior |
|--------|--------------|--------------|
| Router decisions | Streamed char-by-char | Complete JSON |
| Plan generation | Streamed char-by-char | Complete JSON |
| Agent responses | Streamed char-by-char | Complete JSON |
| Final answer | Streamed char-by-char | ✅ Still streams |
| Frontend parsing | Complex reassembly | Direct JSON parse |
| Performance | Slower (many small msgs) | Faster (fewer msgs) |

## Code Examples

### Old Way (Everything Streams)
```python
# ❌ Problem: JSON streams character by character
llm = init_chat_model("openai:gpt-4o-mini")  # Default streaming
decision = llm.with_structured_output(Router).invoke(messages)
# Frontend receives: { " n " e " x " t " : ...
```

### New Way (Selective Streaming)
```python
# ✅ Structured output: Complete JSON
llm = ChatOpenAI(streaming=False)  # Non-streaming
decision = llm.with_structured_output(Router).invoke(messages)
# Frontend receives: {"next": "agent_name", "reason": "..."}

# ✅ Final answer: Token streaming
stream_llm = ChatOpenAI(streaming=True)  # Streaming
final = stream_llm.invoke(messages)
# Frontend receives: Token ... by ... token
```

## Benefits Summary

1. 🎯 **Cleaner API**: Structured data as complete objects
2. ⚡ **Better Performance**: Fewer network messages
3. 🔍 **Easier Debugging**: Can log complete decisions
4. 🎨 **Better UX**: Final answers still stream naturally
5. 🛡️ **Type Safety**: Pydantic validation works correctly
6. 📊 **Predictable**: Know exactly when data is complete
