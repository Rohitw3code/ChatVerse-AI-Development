# Agent Architecture - Centralized Configuration Guide

## 📋 Overview

This project now uses a **centralized, non-hardcoded architecture** for managing all AI agents. All agent configurations, prompts, and metadata are stored in a single source of truth: `chatagent/agents/agents_config.py`.

## 🎯 Key Benefits

- ✅ **No Hardcoding**: All agent names, prompts, and descriptions in one place
- ✅ **Easy Maintenance**: Update any agent config without touching multiple files
- ✅ **Scalability**: Add new agents by just updating the config file
- ✅ **Consistency**: All agents follow the same pattern
- ✅ **Dynamic Loading**: Agents are loaded dynamically from configuration

## 📁 Project Structure

```
chatagent/
├── agents/
│   ├── README.md               # Agent-specific documentation
│   ├── agents_config.py        # 🔥 MAIN CONFIG - All agent metadata
│   ├── agent_db.py             # Auto-loads from agents_config.py
│   ├── agent_retrival.py       # Semantic search for agents
│   ├── agent_search_node.py    # Agent discovery logic
│   │
│   ├── gmail_agent.py          # Gmail agent (unified location)
│   ├── instagram_agent.py      # Instagram agent (unified location)
│   ├── youtube_agent.py        # YouTube agent (unified location)
│   ├── research_agent.py       # Research agent (unified location)
│   │
│   └── social_media_manager/   # ⚠️ DEPRECATED (kept for legacy imports)
│
├── custom_graph.py             # Main graph - dynamically loads agents
├── prompt/
│   └── node_prompt.py          # ⚠️ DEPRECATED - Use agents_config.py
└── ...
```

## 🔥 Central Configuration File

### `chatagent/agents/agents_config.py`

This is the **single source of truth** for all agents.

```python
AGENTS_CONFIG: List[AgentConfig] = [
    {
        "name": "gmail_agent_node",
        "description": "Email agent: draft, send, read Gmail messages...",
        "prompt": "You are a Gmail Manager Agent. Your responsibility is...",
        "module_path": "chatagent.agents.gmail_agent",
        "node_function": "gmail_agent_node"
    },
    {
        "name": "instagram_agent_node",
        "description": "Instagram agent: profile insights, followers...",
        "prompt": "You are an Instagram Manager Agent...",
        "module_path": "chatagent.agents.instagram_agent",
        "node_function": "instagram_agent_node"
    },
    # ... more agents
]
```

### Configuration Schema

```python
class AgentConfig(TypedDict):
    name: str              # Unique agent identifier
    description: str       # For semantic search & agent discovery
    prompt: str           # System prompt/instructions for the agent
    module_path: str      # Python import path
    node_function: str    # Function name to import
```

## 🔧 How Components Work Together

### 1. Agent Files (e.g., `gmail_agent.py`)

Each agent now uses a **factory pattern**:

```python
# Tools definition
@tool("my_tool")
def my_tool():
    pass

# Tool registry
tool_register = NodeRegistry()
tool_register.add("my_tool", my_tool, "tool")

# Factory function - loads config dynamically
def create_gmail_agent_node(prompt: str = None):
    from chatagent.agents.agents_config import get_agent_config
    
    if prompt is None:
        config = get_agent_config("gmail_agent_node")
        prompt = config["prompt"]  # ← Loaded from config!
    
    return make_agent_tool_node(
        members=tool_register,
        prompt=prompt,
        node_name="gmail_agent_node",
        parent_node="task_dispatcher_node",
    )

# Default instance for backward compatibility
gmail_agent_node = create_gmail_agent_node()
```

### 2. Agent Database (`agent_db.py`)

Automatically loads from config:

```python
from chatagent.agents.agents_config import get_agents_registry_for_db

# No more hardcoded lists!
agents_registry = get_agents_registry_for_db()
```

### 3. Graph Builder (`custom_graph.py`)

Dynamically registers agents:

```python
from chatagent.agents.agents_config import AGENTS_CONFIG

# Import all agents
from chatagent.agents.gmail_agent import gmail_agent_node
from chatagent.agents.instagram_agent import instagram_agent_node
from chatagent.agents.youtube_agent import youtube_agent_node
from chatagent.agents.research_agent import research_agent_node

main_register = NodeRegistry()

# Dynamically add agents from config
for agent_config in AGENTS_CONFIG:
    agent_name = agent_config["name"]
    agent_prompt = agent_config["prompt"]
    
    if agent_name == "gmail_agent_node":
        main_register.add(agent_name, gmail_agent_node, "agent", agent_prompt)
    elif agent_name == "instagram_agent_node":
        main_register.add(agent_name, instagram_agent_node, "agent", agent_prompt)
    # ... etc
```

## 🚀 How to Add a New Agent

### Step 1: Create Agent File

Create `chatagent/agents/twitter_agent.py`:

```python
from chatagent.node_registry import NodeRegistry
from langchain_core.tools import tool
from chatagent.agents.create_agent_tool import make_agent_tool_node

@tool("post_tweet")
def post_tweet(content: str):
    """Post a tweet"""
    return f"Posted: {content}"

twitter_tool_register = NodeRegistry()
twitter_tool_register.add("post_tweet", post_tweet, "tool")

def create_twitter_agent_node(prompt: str = None):
    from chatagent.agents.agents_config import get_agent_config
    
    if prompt is None:
        config = get_agent_config("twitter_agent_node")
        prompt = config["prompt"]
    
    return make_agent_tool_node(
        members=twitter_tool_register,
        prompt=prompt,
        node_name="twitter_agent_node",
        parent_node="task_dispatcher_node",
    )

twitter_agent_node = create_twitter_agent_node()
```

### Step 2: Add to Configuration

Edit `chatagent/agents/agents_config.py`:

```python
AGENTS_CONFIG: List[AgentConfig] = [
    # ... existing agents ...
    {
        "name": "twitter_agent_node",
        "description": (
            "Twitter agent: post tweets, read timeline, manage Twitter account. "
            "Keywords: twitter, tweet, post, social media, x"
        ),
        "prompt": (
            "You are a Twitter Manager Agent.\n"
            "Your responsibility is to handle ANY task related to Twitter.\n"
            "Rules:\n"
            "1. Perform the requested Twitter-related action.\n"
            "2. If authentication is missing, instruct the user to connect Twitter.\n"
            "3. After completing or failing the task, END the task."
        ),
        "module_path": "chatagent.agents.twitter_agent",
        "node_function": "twitter_agent_node"
    }
]
```

### Step 3: Update Graph Builder

Edit `chatagent/custom_graph.py`:

```python
# Add import
from chatagent.agents.twitter_agent import twitter_agent_node

# Add to dynamic registration
elif agent_name == "twitter_agent_node":
    main_register.add(agent_name, twitter_agent_node, "agent", agent_prompt)

# Add to graph
graph_builder.add_node("twitter_agent_node", twitter_agent_node)
```

**That's it!** The agent is now:
- ✅ Available for semantic search
- ✅ Registered in the agent database
- ✅ Integrated into the graph
- ✅ Discoverable by users

## 📝 Common Operations

### Update Agent Prompt

**Before (Old Way):**
Edit `chatagent/prompt/node_prompt.py` or the agent file directly

**After (New Way):**
Edit `chatagent/agents/agents_config.py`:

```python
{
    "name": "gmail_agent_node",
    "prompt": "NEW UPDATED PROMPT HERE"
}
```

### Update Agent Description

```python
{
    "name": "gmail_agent_node",
    "description": "NEW DESCRIPTION with better keywords"
}
```

### View All Agents

```python
from chatagent.agents.agents_config import get_all_agent_names, AGENTS_CONFIG

# Get names
names = get_all_agent_names()

# Get full configs
for config in AGENTS_CONFIG:
    print(f"{config['name']}: {config['description']}")
```

## ⚠️ Deprecated Files

These files are deprecated but kept for backward compatibility:

1. **`chatagent/prompt/node_prompt.py`**
   - Old: Hardcoded PROMPTS class
   - New: Use `agents_config.py`

2. **`chatagent/agents/social_media_manager/`**
   - Old: Nested directory structure
   - New: Flat structure in `chatagent/agents/`

## 🧪 Testing Changes

After making changes to `agents_config.py`:

```bash
# 1. Check for import errors
cd /home/bittu/Desktop/chatverse/ChatVerse-AI-Development

# 2. Test agent loading
python3 -c "from chatagent.agents.agents_config import AGENTS_CONFIG; print([a['name'] for a in AGENTS_CONFIG])"

# 3. Test agent database
python3 -c "from chatagent.agents.agent_db import agents_registry; print(agents_registry)"

# 4. Run the application
python3 app.py
```

## 🎓 Best Practices

### ✅ DO:
- Store all agent configs in `agents_config.py`
- Use factory functions for agent creation
- Add detailed descriptions with keywords
- Keep prompts clear and structured
- Update docs when adding new agents

### ❌ DON'T:
- Hardcode agent names in code
- Hardcode prompts in agent files
- Create new nested directories
- Edit deprecated files
- Skip updating the configuration

## 🔍 Troubleshooting

### Agent not found
```python
# Check if agent exists in config
from chatagent.agents.agents_config import get_agent_config
config = get_agent_config("your_agent_node")
```

### Prompt not updating
1. Check `agents_config.py` for typos
2. Restart the application
3. Verify factory function is being used

### Import errors
1. Check module_path in config
2. Verify file exists in correct location
3. Check for circular imports

## 📚 Additional Resources

- **Agent-specific docs**: `chatagent/agents/README.md`
- **Node registry**: `chatagent/node_registry.py`
- **Graph builder**: `chatagent/custom_graph.py`
- **Agent tools**: `chatagent/agents/create_agent_tool.py`

## 🎯 Summary

The new architecture provides:

1. **Single Source of Truth**: `agents_config.py` contains everything
2. **No Hardcoding**: All values loaded dynamically
3. **Easy Maintenance**: Update one file, changes everywhere
4. **Scalability**: Add agents with minimal code changes
5. **Consistency**: All agents follow the same pattern

**Remember**: Always update `agents_config.py` first, then make corresponding changes to the graph builder if needed!
