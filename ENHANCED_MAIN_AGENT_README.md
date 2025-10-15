# Enhanced Main Agent System

## Overview

The Enhanced Main Agent System is a sophisticated AI framework that intelligently handles both direct conversational responses and agentic tool execution based on semantic query analysis. Built with OpenAI GPT-4o Mini and LangGraph, it provides seamless streaming capabilities for frontend integration.

## Key Features

### 🤖 Intelligent Query Processing
- **Direct Response Mode**: For general questions and conversations that don't require external actions
- **Tool Execution Mode**: For queries requiring specific actions (job searches, emails, research, etc.)
- **Semantic Tool Discovery**: Automatically finds relevant tools based on query analysis with query reconstruction for better matching

### 🔧 Tool Execution Framework
- **LinkedIn Job Search**: Search for jobs with criteria filtering
- **Instagram Analytics**: Get insights and engagement metrics
- **Gmail Integration**: Send and compose emails
- **Web Research**: Research topics and gather information
- **Content Processing**: Summarize and analyze content
- **Data Analysis**: Process various data formats

### 📡 Advanced Streaming
- **Token-by-Token Streaming**: Real-time text streaming for main agent responses
- **Tool Lifecycle Tracking**: Detailed progress of tool executions with start/end events
- **JSON Event Streaming**: Structured events for frontend integration
- **Rich CLI Interface**: Multi-panel display with live updates

### 💾 Conversation Management
- **Persistent History**: Maintains complete conversation context
- **Automatic Cropping**: Intelligently manages memory by keeping last 20 messages
- **Execution Tracking**: Records all tool executions and their results

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   Enhanced Main Agent                       │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐ │
│  │ Semantic Tool   │  │ Conversation    │  │ OpenAI       │ │
│  │ Matcher         │  │ History         │  │ GPT-4o Mini  │ │
│  └─────────────────┘  └─────────────────┘  └──────────────┘ │
├─────────────────────────────────────────────────────────────┤
│                 LangGraph ReAct Framework                   │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌────────┐ │
│  │ LinkedIn    │ │ Instagram   │ │ Gmail       │ │ Web    │ │
│  │ Tools       │ │ Tools       │ │ Tools       │ │ Tools  │ │
│  └─────────────┘ └─────────────┘ └─────────────┘ └────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## Installation & Setup

### Prerequisites
- Python 3.8+
- OpenAI API Key
- Required dependencies (see requirements.txt)

### Installation
```bash
# Clone the repository
git clone <repository-url>
cd ChatVerse-AI-Dev

# Install dependencies
pip install -r requirements.txt

# Set up OpenAI API key in config
export OPENAI_API_KEY="your-api-key-here"
```

## Usage

### Basic Command Line Interface

```bash
# Direct query execution
python -m new_agent "Find Python developer jobs on LinkedIn"

# Interactive mode
python -m new_agent
```

### JSON Streaming for Frontend Integration

```bash
# Stream structured JSON events
python -m new_agent.frontend_json_streamer stream --query "Send an email about job search results"

# Token-only streaming for real-time text display
python -m new_agent.frontend_json_streamer tokens --query "What are the best Python frameworks?"

# Get system information
python -m new_agent.frontend_json_streamer status
python -m new_agent.frontend_json_streamer tools
python -m new_agent.frontend_json_streamer history
```

## Streaming Events

### JSON Event Types

```json
{
  "event_type": "session_init",
  "session_id": "session_20251016_003016",
  "user_id": "default_user",
  "query": "Find Python jobs",
  "timestamp": "2025-10-16T00:30:16.695910"
}
```

#### Main Event Types:
- `session_init` - Session started
- `tool_discovery_start` - Searching for relevant tools
- `tool_discovery_complete` - Tools found and selected
- `direct_response_start` - Starting direct LLM response
- `tool_execution_mode` - Starting tool-based execution
- `main_agent_token` - Real-time token streaming
- `tool_start` - Tool execution begins
- `tool_end` - Tool execution completes
- `execution_complete` - Full query processing complete

### Token Streaming
For real-time text display, use the token streaming mode:
```bash
python -m new_agent.frontend_json_streamer tokens --query "Your query here"
```

Outputs clean token stream:
```
There are several excellent Python frameworks for web development...
[TOOL_START:linkedin_job_search]
[TOOL_END:linkedin_job_search]
```

## System Behavior

### Direct Response Queries
Examples that trigger direct responses:
- "Hello, how are you?"
- "What are the best Python frameworks?"
- "Explain machine learning concepts"
- "Tell me a joke"

### Tool Execution Queries
Examples that trigger tool execution:
- "Find Python developer jobs on LinkedIn"
- "Send an email about the job search results"
- "Get Instagram insights for my account"
- "Research the latest AI trends"
- "Summarize this document content"

## Console Output for Frontend Integration

The system provides structured console output specifically designed for frontend consumption:

```bash
# Tool lifecycle tracking
TOOL_START: linkedin_job_search with params: {'query': 'Python developer'}
TOOL_END: linkedin_job_search - Output: {'jobs_found': 18, 'sample_jobs': [...]}

# Token streaming
TOKEN: I
TOKEN:  found
TOKEN:  several
TOKEN:  Python
TOKEN:  developer
TOKEN:  jobs
```

## Configuration

### Core Configuration (`config.py`)
```python
class Config:
    llm = LLMConfig(
        provider="openai",
        model="gpt-4o-mini",
        api_key=os.getenv("OPENAI_API_KEY"),
        temperature=0.1
    )
```

### Tool Registry
Tools are automatically registered and discoverable through semantic matching:
```python
semantic_keywords = {
    "linkedin_search": ["job", "linkedin", "career", "position", "employment"],
    "gmail_send": ["email", "gmail", "send", "mail", "message"],
    "web_search": ["search", "research", "find", "web", "information"]
}
```

## API Reference

### Main Agent Methods
```python
# Process a query with streaming
async for event in enhanced_main_agent.process_query(query, user_id):
    # Handle streaming events
    process_event(event)

# Get conversation history
history = await engine.get_conversation_history(user_id)

# Get available tools
tools = engine.get_available_tools()

# Get system status
status = engine.get_system_status()
```

### Streaming Event Structure
```python
@dataclass
class StreamingEvent:
    event_type: str
    content: str
    metadata: Dict[str, Any]
    token: Optional[str] = None
    agent_name: Optional[str] = None
    tool_name: Optional[str] = None
    tool_input: Optional[Dict] = None
    tool_output: Optional[Any] = None
```

## Frontend Integration Examples

### React.js Streaming Component
```javascript
// Stream JSON events
const response = await fetch('/api/stream', {
  method: 'POST',
  body: JSON.stringify({ query: 'Find Python jobs' })
});

const reader = response.body.getReader();
while (true) {
  const { done, value } = await reader.read();
  if (done) break;
  
  const event = JSON.parse(new TextDecoder().decode(value));
  handleStreamingEvent(event);
}
```

### Real-time Token Display
```javascript
// Handle token streaming for real-time text
if (event.event_type === 'main_agent_token') {
  appendToDisplay(event.token);
}

// Handle tool events
if (event.event_type === 'tool_start') {
  showToolProgress(event.tool_name, 'running');
}
```

## Performance Characteristics

### Typical Performance Metrics
- **Direct Response**: 2-4 seconds average
- **Tool Execution**: 5-15 seconds depending on tool complexity
- **Token Streaming**: Real-time, <100ms latency
- **Memory Usage**: Efficient with automatic history management
- **Cost**: Optimized with GPT-4o Mini (~$0.0003-0.002 per query)

### Scalability Features
- Conversation history auto-cropping (20 messages)
- Execution history management (10 recent executions)
- Efficient tool discovery with semantic caching
- Asynchronous processing for concurrent requests

## Troubleshooting

### Common Issues
1. **No tools found**: Check semantic keywords match your query intent
2. **API errors**: Verify OpenAI API key is set correctly
3. **Streaming issues**: Ensure async/await syntax is used properly
4. **JSON parsing errors**: Check event structure matches expected format

### Debug Commands
```bash
# Check system status
python -m new_agent.frontend_json_streamer status

# List available tools
python -m new_agent.frontend_json_streamer tools

# Interactive mode for testing
python -m new_agent
```

## Contributing

### Adding New Tools
1. Create tool class extending `BaseTool`
2. Add to `langchain_tools.py`
3. Update semantic keywords in `enhanced_main_agent.py`
4. Test with sample queries

### Extending Event Types
1. Add new event type to `StreamingEvent`
2. Update JSON streaming handler
3. Document in API reference
4. Add frontend examples

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support, please:
1. Check the troubleshooting section
2. Review the API reference
3. Test with debug commands
4. Submit issues with detailed logs

---

*Built with ❤️ using OpenAI GPT-4o Mini and LangGraph*