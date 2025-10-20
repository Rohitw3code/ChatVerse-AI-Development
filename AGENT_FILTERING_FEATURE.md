# Intelligent Agent Filtering with LLM

## Overview

The agent search node now uses a **two-stage intelligent filtering** approach to select the most relevant agents for each query:

1. **Stage 1: Embedding-based Search** - Fast semantic similarity using embeddings
2. **Stage 2: LLM-based Filtering** - Intelligent selection considering context and conversation history

## Architecture

```
User Query: "Send an email and check Instagram"
           ↓
┌──────────────────────────────────────────────────────────┐
│ Stage 1: Embedding Search (get_relevant_agents)          │
│ - Uses text-embedding-3-small                            │
│ - Returns top_k=5 most similar agents                    │
│ - Fast, but may include irrelevant agents                │
└──────────────────────────────────────────────────────────┘
           ↓
   Result: [gmail_agent_node, instagram_agent_node, 
            youtube_agent_node, research_agent_node, ...]
           ↓
┌──────────────────────────────────────────────────────────┐
│ Stage 2: LLM Filtering (AgentSelection)                  │
│ - Analyzes query + conversation history                  │
│ - Understands user intent                                │
│ - Selects ONLY agents explicitly needed                  │
└──────────────────────────────────────────────────────────┘
           ↓
   Filtered: [gmail_agent_node, instagram_agent_node]
           ↓
┌──────────────────────────────────────────────────────────┐
│ Stage 3: Sufficiency Check (AgentCheck)                  │
│ - Verifies filtered agents can handle the query          │
│ - Routes to planner or retries if insufficient           │
└──────────────────────────────────────────────────────────┘
           ↓
   state['agents'] = [gmail_agent_node, instagram_agent_node]
           ↓
   → Passed to planner_node and task_dispatcher_node
```

## Implementation Details

### 1. AgentSelection Pydantic Model

```python
class AgentSelection(BaseModel):
    """Model for selecting specific agents needed for the query"""
    selected_agent_names: List[str] = Field(
        description="List of exact agent names (from the provided list) that are required to handle the user query based on the current query and conversation history. Only include agents that are explicitly needed."
    )
    reason: str = Field(
        description="Brief explanation of why these specific agents were selected"
    )
```

### 2. LLM Agent Filtering Process

```python
# Build conversation context (last 5 messages)
conversation_history = ""
for msg in state.get("messages", [])[-5:]:
    if isinstance(msg, (HumanMessage, AIMessage)):
        role = "User" if isinstance(msg, HumanMessage) else "Assistant"
        conversation_history += f"{role}: {msg.content}\n"

# Use LLM to intelligently filter agents
agent_selection: AgentSelection = llm.with_structured_output(AgentSelection).invoke([
    SystemMessage(content=AGENT_SELECTION_PROMPT),
    HumanMessage(content=(
        "Available agents:\n"
        + "\n".join([f"- {agent['name']}: {agent['description']}" for agent in all_relevant_agents])
        + f"\n\nConversation History:\n{conversation_history}"
        + f"\n\nCurrent User Query: {state['input']}\n\n"
        "Select ONLY the specific agent names that are needed to handle this query."
    ))
])

# Filter to only selected agents
selected_agents = [
    agent for agent in all_relevant_agents 
    if agent['name'] in agent_selection.selected_agent_names
]
```

### 3. Fallback Mechanism

```python
# If no agents were selected, fall back to all relevant agents
if not selected_agents:
    selected_agents = all_relevant_agents
    print(f"⚠️  No agents selected by LLM, using all relevant agents")
```

## Benefits

### ✅ **Context-Aware Selection**
- Considers conversation history (last 5 messages)
- Understands multi-step requests
- Recognizes follow-up queries

### ✅ **Precise Filtering**
- Only selects agents explicitly needed
- Reduces noise in downstream planning
- Improves routing accuracy

### ✅ **Intelligent Interpretation**
Example queries:
```
Query: "Send an email"
Embedding Search: [gmail_agent_node, instagram_agent_node, youtube_agent_node, ...]
LLM Filter: [gmail_agent_node] ✅ Only email agent selected

Query: "Send an email and post to Instagram"
Embedding Search: [gmail_agent_node, instagram_agent_node, research_agent_node, ...]
LLM Filter: [gmail_agent_node, instagram_agent_node] ✅ Both selected

Query: "What's the weather?" (after discussing Instagram)
Embedding Search: [research_agent_node, instagram_agent_node, ...]
LLM Filter: [research_agent_node] ✅ Ignores Instagram from context
```

### ✅ **Conversation Continuity**
```
User: "Check my Instagram insights"
→ Selected: [instagram_agent_node]

User: "Now send an email about it"
→ Conversation history helps understand "it" refers to Instagram
→ Selected: [gmail_agent_node]
→ Context from previous message available in state
```

## Debug Output

The system provides detailed logging for transparency:

```
=== AGENT SEARCH DEBUG ===
Step 1 - Agents from embedding search (top_k=5): 
  [gmail_agent_node, instagram_agent_node, youtube_agent_node, research_agent_node, ...]

Step 2 - LLM filtered agents: [gmail_agent_node, instagram_agent_node]
Step 2 - Selection reason: "User needs both email and Instagram functionality"

Step 3 - Agent Sufficiency Check: AgentCheck(recheck=False, reason="sufficient agents found")
Step 3 - Final agents to pass forward: [gmail_agent_node, instagram_agent_node]
=== END AGENT SEARCH DEBUG ===
```

## Flow Integration

### Before (Old System)
```
get_relevant_agents(top_k=5) 
  → state['agents'] = all 5 agents
  → planner sees all 5 agents
  → task_dispatcher sees all 5 agents
  → More confusion, less precision
```

### After (New System)
```
get_relevant_agents(top_k=5)
  → LLM filters to specific needs
  → state['agents'] = only 2 needed agents
  → planner sees only relevant 2 agents
  → task_dispatcher sees only relevant 2 agents
  → Focused, precise, accurate ✅
```

## Key Features

1. **Two-Stage Filtering**
   - Fast embedding search for candidates
   - Smart LLM selection for precision

2. **Conversation-Aware**
   - Uses last 5 messages for context
   - Understands references and continuity

3. **Structured Output**
   - Pydantic models ensure type safety
   - Consistent, validated responses

4. **Fallback Safety**
   - Falls back to all agents if none selected
   - Prevents empty agent lists

5. **Transparent Debugging**
   - Detailed logs at each stage
   - Easy to diagnose issues

## Configuration

### Adjustable Parameters

```python
# Number of agents from embedding search
all_relevant_agents = get_relevant_agents(state["input"], top_k=5)

# Conversation history depth
for msg in state.get("messages", [])[-5:]:  # Last 5 messages
```

### Retry Logic

```python
# Maximum retries if agents are insufficient
agent_search_count = state.get("agent_search_count", 0)
if result.recheck is True and agent_search_count < 3:
    # Retry with new search
```

## Performance Impact

- **Stage 1 (Embedding)**: ~50ms (cached embeddings)
- **Stage 2 (LLM Filter)**: ~500ms (OpenAI API call)
- **Total Added Latency**: ~550ms per query
- **Benefit**: Much better accuracy and focused routing

## Example Scenarios

### Scenario 1: Simple Single-Agent Query
```
Query: "Draft an email to John"
→ Embedding returns 5 agents
→ LLM selects only: gmail_agent_node
→ Planner creates focused email plan
```

### Scenario 2: Multi-Agent Query
```
Query: "Send email and check Instagram insights"
→ Embedding returns 5 agents
→ LLM selects: gmail_agent_node, instagram_agent_node
→ Planner creates multi-step plan
```

### Scenario 3: Context-Aware Follow-up
```
Query 1: "Check my Instagram"
→ Selected: instagram_agent_node

Query 2: "Now send an email about it"
→ Conversation history includes Instagram context
→ Selected: gmail_agent_node
→ Can reference previous Instagram data in email
```

### Scenario 4: Ambiguous Query
```
Query: "Get some information"
→ Embedding returns general agents
→ LLM recognizes ambiguity
→ May select research_agent_node to ask clarifying questions
```

## Testing Recommendations

1. **Test single-agent queries**: Verify only one agent selected
2. **Test multi-agent queries**: Verify all needed agents selected
3. **Test conversation continuity**: Verify context understanding
4. **Test edge cases**: Empty queries, unknown requests
5. **Monitor debug logs**: Check selection reasoning

## Future Enhancements

1. **Dynamic top_k**: Adjust based on query complexity
2. **Agent confidence scores**: LLM provides confidence ratings
3. **Learning from history**: Improve selection over time
4. **User feedback loop**: Learn from successful/failed selections
