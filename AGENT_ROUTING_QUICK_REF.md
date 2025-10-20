# Agent Name & Dynamic Routing - Quick Reference

## Before vs After

### Agent Names
```
Before (agent_db.py):           After (agent_db.py):
- gmail_agent                   - gmail_agent_node ✅
- instagram_agent               - instagram_agent_node ✅
- youtube_agent                 - youtube_agent_node ✅
- reaserch_agent (typo!)        - research_agent_node ✅
```

### Graph Registry (custom_graph.py)
```python
# Before - INCORRECT:
main_register.add("youtube_agent_node", research_agent_node, ...)  # ❌ Wrong function

# After - CORRECT:
main_register.add("youtube_agent_node", youtube_agent_node, ...)   # ✅ Correct function
```

### Task Dispatcher Prompt (task_dispatcher.py)

#### Before - Static (Hardcoded):
```python
system_prompt = f"""
    <available_nodes>
        {registry.prompt_block("Supervisor")}  # ❌ Always same, hardcoded
    </available_nodes>
"""
```

#### After - Dynamic (State-based):
```python
def build_system_prompt(available_agents: List[dict]) -> str:
    if available_agents:
        # ✅ Uses agents from state (dynamic semantic search)
        agent_lines = [f"- {agent['name']}: {agent['description']}" 
                      for agent in available_agents]
        available_nodes_block = "\n".join(agent_lines)
    else:
        # ✅ Fallback to registry if needed
        available_nodes_block = registry.prompt_block("Supervisor")
    
    return f"""
        <available_nodes>
            {available_nodes_block}  # ✅ Dynamic!
        </available_nodes>
    """

# In task_dispatcher_node:
available_agents = state.get('agents', [])  # ✅ From search_agent_node
system_prompt = build_system_prompt(available_agents)  # ✅ Built dynamically
```

## Data Flow

```
┌─────────────────────────────────────────────────────────────────┐
│ 1. User Query: "Send an email and check Instagram insights"    │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ 2. search_agent_node                                            │
│    - Uses embeddings to find relevant agents                    │
│    - Queries agent_db.py with agent names matching graph nodes  │
│    - Returns: [gmail_agent_node, instagram_agent_node]         │
│    - Stores in: state['agents']                                 │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ 3. planner_node                                                 │
│    - Reads: state['agents']                                     │
│    - Creates plan using ONLY available agents                   │
│    - Stores in: state['plans']                                  │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ 4. task_dispatcher_node                                         │
│    - Reads: state['agents']                                     │
│    - Builds dynamic prompt with available agents                │
│    - Routes to: gmail_agent_node or instagram_agent_node        │
│    - Validates routing against: registry.members()              │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ 5. Specific Agent Node (e.g., gmail_agent_node)                │
│    - Executes the task                                          │
│    - Returns results                                            │
└─────────────────────────────────────────────────────────────────┘
```

## Key Points

### ✅ Consistency
- All agent names match across:
  - agent_db.py (for semantic search)
  - custom_graph.py (graph builder & registry)
  - Individual agent files (node_name parameter)

### ✅ Dynamic Routing
- task_dispatcher now uses `state['agents']` for prompt
- LLM only sees relevant agents for the current query
- Reduces confusion and improves routing accuracy

### ✅ Validation Safety
- Router validator still uses `registry.members()`
- Ensures routing only to registered graph nodes
- Prevents runtime errors from invalid routing

### ✅ Flexibility
- New agents can be added by:
  1. Adding to agent_db.py
  2. Registering in custom_graph.py
  3. Adding node to graph_builder
  - No changes needed in task_dispatcher!

## Example

**Query**: "Draft an email about AI"

**Old Flow**:
```
task_dispatcher sees ALL agents in registry
→ LLM confused by many options
→ May route incorrectly
```

**New Flow**:
```
search_agent finds: [gmail_agent_node]
→ state['agents'] = [gmail_agent_node details]
→ task_dispatcher prompt only shows gmail_agent_node
→ LLM routes directly to gmail_agent_node ✅
```

## Validation

```python
# Prompt uses dynamic agents
system_prompt = build_system_prompt(state.get('agents', []))
# Shows only: gmail_agent_node

# Validator uses all registered nodes
allowed = registry.members() + ["END", "NEXT_TASK"]
# Validates against: [gmail_agent_node, instagram_agent_node, 
#                     youtube_agent_node, research_agent_node, ...]
```

This ensures:
- LLM sees only relevant options (focused decision)
- Validation allows all registered nodes (safe routing)
- Best of both worlds! 🎯
