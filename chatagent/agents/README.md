# Agents Directory Structure

This directory contains all agent implementations for the ChatVerse AI system. Each agent is organized in its own folder with a consistent structure.

## 📁 Directory Structure

```
chatagent/agents/
├── agents_config.py          # Centralized configuration for all agents
├── agent_db.py               # Agent registry for semantic search
├── agent_retrieval.py        # Agent retrieval logic
├── agent_search_node.py      # Agent search functionality
├── create_agent_tool.py      # Agent creation utilities
├── final_node.py             # Final answer node
├── inputer_agent.py          # Input handler agent
├── planner_agent.py          # Planning agent
├── supervisor_agent.py       # Supervisor agent
├── task_dispatcher.py        # Task distribution logic
├── task_selection.py         # Task selection logic
│
├── gmail/                    # Gmail Agent
│   ├── __init__.py
│   ├── gmail_agent.py        # Agent logic
│   └── gmail_tools.py        # Gmail-related tools
│
├── instagram/                # Instagram Agent
│   ├── __init__.py
│   ├── instagram_agent.py    # Agent logic
│   └── instagram_tools.py    # Instagram-related tools
│
├── youtube/                  # YouTube Agent
│   ├── __init__.py
│   ├── youtube_agent.py      # Agent logic
│   └── youtube_tools.py      # YouTube-related tools
│
└── research/                 # Research Agent
    ├── __init__.py
    ├── research_agent.py     # Agent logic
    └── research_tools.py     # Research-related tools
```

## 🎯 Design Principles

### 1. **No Hardcoded Prompts or Names**
- All agent prompts are centralized in `agents_config.py`
- Agent names, descriptions, and configurations are defined in one place
- Easy to update and maintain without touching individual files

### 2. **Separation of Concerns**
- **Agent files** (`*_agent.py`): Contains agent initialization logic
- **Tool files** (`*_tools.py`): Contains all tool implementations
- **Config file** (`agents_config.py`): Contains all configurations

### 3. **Consistent Structure**
Each agent folder follows the same pattern:
```
agent_name/
├── __init__.py              # Exports agent_node and create functions
├── agent_name_agent.py      # Agent initialization
└── agent_name_tools.py      # Tool implementations
```

## 📝 Agent Configuration

All agent configurations are defined in `agents_config.py`:

```python
AGENTS_CONFIG = [
    {
        "name": "gmail_agent_node",
        "description": "Email agent: draft emails, send emails, read Gmail messages...",
        "prompt": "You are a Gmail Manager Agent...",
        "module_path": "chatagent.agents.gmail.gmail_agent",
        "node_function": "gmail_agent_node"
    },
    # ... other agents
]
```

### Configuration Fields:
- **name**: Unique identifier for the agent
- **description**: Used for semantic search and agent selection
- **prompt**: System prompt for the agent (no hardcoding!)
- **module_path**: Python import path to the agent module
- **node_function**: Function name to import

## 🔧 Adding a New Agent

### Step 1: Create Agent Folder
```bash
mkdir -p chatagent/agents/new_agent
```

### Step 2: Create `__init__.py`
```python
"""New Agent Module"""
from .new_agent_agent import new_agent_node, create_new_agent_node

__all__ = ["new_agent_node", "create_new_agent_node"]
```

### Step 3: Create `new_agent_tools.py`
```python
"""
New Agent Tools Module
Contains all new agent-related tools.
"""

from chatagent.node_registry import NodeRegistry
from langchain_core.tools import tool
from pydantic import BaseModel, Field

@tool("example_tool")
def example_tool(param: str) -> str:
    \"\"\"Example tool description.\"\"\"
    # Tool implementation
    return "result"

def get_new_agent_tool_registry() -> NodeRegistry:
    \"\"\"Returns a NodeRegistry containing all New Agent tools.\"\"\"
    registry = NodeRegistry()
    registry.add("example_tool", example_tool, "tool")
    return registry
```

### Step 4: Create `new_agent_agent.py`
```python
"""
New Agent Module
Handles all new agent operations without hardcoded prompts.
"""

from chatagent.agents.create_agent_tool import make_agent_tool_node
from chatagent.agents.new_agent.new_agent_tools import get_new_agent_tool_registry

def create_new_agent_node(prompt: str = None):
    \"\"\"Factory function to create New Agent node with dynamic prompt.\"\"\"
    if prompt is None:
        from chatagent.agents.agents_config import get_agent_config
        config = get_agent_config("new_agent_node")
        prompt = config["prompt"]
    
    return make_agent_tool_node(
        members=get_new_agent_tool_registry(),
        prompt=prompt,
        node_name="new_agent_node",
        parent_node="task_dispatcher_node",
    )

# Default instance
new_agent_node = create_new_agent_node()
```

### Step 5: Add to `agents_config.py`
```python
{
    "name": "new_agent_node",
    "description": "New agent: handles X, Y, Z. Keywords: x, y, z",
    "prompt": "You are a New Agent. Your responsibilities are...",
    "module_path": "chatagent.agents.new_agent.new_agent_agent",
    "node_function": "new_agent_node"
}
```

### Step 6: Update `custom_graph.py`
```python
from chatagent.agents.new_agent import new_agent_node

# Add to graph
graph_builder.add_node("new_agent_node", new_agent_node)
```

## 🔍 Current Agents

### 1. **Gmail Agent** (`gmail/`)
**Purpose**: Email management
**Tools**:
- `verify_gmail_connection`: Check Gmail connection status
- `fetch_recent_gmail`: Fetch recent emails
- `fetch_unread_gmail`: Fetch unread emails
- `draft_gmail`: Draft professional emails
- `send_gmail`: Send emails with user approval
- `ask_human`: Request missing information
- `gmail_error`: Handle connection errors

### 2. **Instagram Agent** (`instagram/`)
**Purpose**: Instagram analytics and management
**Tools**:
- `instagram_auth_verification`: Verify Instagram connection
- `profile_insight`: Fetch profile insights and metrics
- `ask_human`: Request clarification
- `instagram_error`: Handle authentication errors

### 3. **YouTube Agent** (`youtube/`)
**Purpose**: YouTube channel management
**Tools**:
- `fetch_youtube_channel_details`: Get channel information

### 4. **Research Agent** (`research/`)
**Purpose**: Web search and LinkedIn research
**Tools**:
- `tavily_search`: General web search
- `linkedin_job_search`: Search LinkedIn jobs
- `linkedin_person_search`: Search LinkedIn profiles

## 🛠️ Utility Functions

### Get Agent Config
```python
from chatagent.agents.agents_config import get_agent_config

config = get_agent_config("gmail_agent_node")
print(config["prompt"])
```

### Get All Agent Names
```python
from chatagent.agents.agents_config import get_all_agent_names

agents = get_all_agent_names()
# ['gmail_agent_node', 'instagram_agent_node', ...]
```

### Create Custom Agent Instance
```python
from chatagent.agents.gmail import create_gmail_agent_node

custom_agent = create_gmail_agent_node(prompt="Custom prompt here")
```

## 📚 Best Practices

1. **Never hardcode prompts** in agent or tool files
2. **Always use `agents_config.py`** for agent configuration
3. **Keep tool logic separate** from agent initialization
4. **Use factory functions** (`create_*_agent_node`) for flexibility
5. **Document all tools** with clear docstrings
6. **Log tool events** for debugging and monitoring
7. **Handle errors gracefully** with appropriate error tools

## 🔄 Migration Notes

If you're migrating from the old structure:
1. Old agent files in `chatagent/agents/*.py` have been moved to folders
2. `social_media_manager/` folder has been removed
3. All imports now use the folder structure: `from chatagent.agents.gmail import gmail_agent_node`
4. `node_prompt.py` is deprecated - use `agents_config.py` instead

## 📖 Related Documentation

- See `agents_config.py` for all agent configurations
- See `AGENT_ARCHITECTURE.md` for system architecture
- See individual tool files for tool-specific documentation

## 🤝 Contributing

When adding new agents:
1. Follow the established folder structure
2. Add configuration to `agents_config.py`
3. Update this README with agent details
4. Write comprehensive docstrings
5. Add logging for all tool operations

---

**Last Updated**: October 21, 2025
**Maintainer**: ChatVerse Team
