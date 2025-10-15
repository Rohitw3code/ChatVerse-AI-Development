# Enhanced New Agent Framework - OpenAI Powered

A fully agentic, CLI-driven AI Agent Framework that uses **OpenAI GPT-4o Mini** for all intelligent decision-making while maintaining local tool execution.

## 🚀 Key Features

### ✨ **Fully Agentic Operations**
- **LLM-Powered Planning**: GPT-4o Mini creates intelligent execution plans from user queries
- **Dynamic Agent Routing**: AI decides which agents to use based on task requirements  
- **Intelligent Decision Making**: Agents use LLM reasoning for all actions and tool calls
- **Smart Summarization**: AI-generated summaries with structured content analysis
- **Parameter Extraction**: LLM intelligently determines tool parameters from context

### 💰 **Cost & Token Tracking**
- Real-time token usage monitoring
- Cost estimation and alerts
- Per-session expense tracking
- Configurable cost thresholds

### 🛠️ **Architecture**
- **6 Specialized Agents**: LinkedIn, Instagram, Gmail, Research, Summarizer, Orchestrator
- **6 Dummy Tools**: Realistic local simulations for external APIs
- **OpenAI Integration**: GPT-4o Mini for cost-effective intelligence
- **Local Database**: SQLite storage with JSON fallback
- **Rich CLI**: Real-time streaming with progress indicators

## 📋 Prerequisites

1. **Python 3.8+**
2. **OpenAI API Key** - Get from [OpenAI Platform](https://platform.openai.com/api-keys)

## 🔧 Installation & Setup

### 1. Install Dependencies
```bash
cd new_agent
pip install -r requirements.txt
```

### 2. Set OpenAI API Key
```bash
# Windows (Command Prompt)
set OPENAI_API_KEY=your_api_key_here

# Windows (PowerShell)
$env:OPENAI_API_KEY="your_api_key_here"

# Linux/Mac
export OPENAI_API_KEY=your_api_key_here
```

### 3. Verify Installation
```bash
python -m new_agent --help
```

## 🎯 Usage Examples

### Basic Query Execution
```bash
python -m new_agent "Fetch AI/ML engineer jobs from LinkedIn in India and also fetch Instagram insights, summarize both, and email the summary to rohit@gmail.com"
```

### List Available Agents
```bash
python -m new_agent --list-agents
```

### Check Tools
```bash
python -m new_agent --list-tools
```

### View Statistics
```bash
python -m new_agent --stats
```

## 🧠 How It Works

### 1. **Query Analysis** 
- GPT-4o Mini analyzes your natural language request
- Identifies required agents and creates execution plan
- Estimates duration and determines execution mode

### 2. **Agent Selection**
- AI routes tasks to most appropriate specialized agents
- Only relevant agents are selected, not all available agents
- Dynamic routing based on query semantics

### 3. **Execution**
- Each agent uses LLM reasoning to decide actions
- Tools are called with AI-determined parameters
- Real-time streaming shows agent thinking process

### 4. **Cost Tracking**
- Token usage monitored for every LLM call
- Cost estimates displayed after execution
- Alerts if cost exceeds configured thresholds

## 📊 Sample Output

```
🎯 Query: Fetch AI/ML engineer jobs from LinkedIn in India and also fetch Instagram insights, summarize both, and email summary to rohit@gmail.com

🧠 Planning Engine: Analyzing query with OpenAI - 'Fetch AI/ML...'
✅ LLM Plan created: 4 steps, estimated 360s
💡 Analysis: Multi-platform data collection and communication workflow
🎯 Confidence: 0.87

🔄 Executing plan...
🔵 Starting: Search for AI/ML engineer jobs in India
🧠 LinkedInAgent analyzing task...
💭 I need to search for AI/ML engineering positions specifically in India...
🔧 Using DummyLinkedInSearchTool...
✅ Tool completed: DummyLinkedInSearchTool
✅ LinkedInAgent completed
✅ Completed: Search for AI/ML engineer jobs in India

💰 LLM Usage & Cost:
   Model: gpt-4o-mini
   Prompt Tokens: 1,245
   Completion Tokens: 892
   Total Tokens: 2,137
   Estimated Cost: $0.0034
```

## 🔧 Configuration

The framework uses `new_agent/core/config.py` for configuration:

```python
# LLM Configuration
llm:
  api_key: ""  # Loaded from OPENAI_API_KEY env var
  model: "gpt-4o-mini"
  temperature: 0.1
  enable_token_tracking: True
  cost_alert_threshold: 5.0  # Alert if cost > $5
  max_cost_per_session: 10.0  # Max cost per session
```

## 🎯 Agent Specializations

| Agent | Specialization | Tools |
|-------|---------------|--------|
| **LinkedInAgent** | Job searches, professional networking | linkedin_search, profile_analysis |
| **InstagramAgent** | Social media analytics, insights | instagram_insights, analytics |
| **GmailAgent** | Email composition and sending | gmail_send, compose, templates |
| **ResearchAgent** | Web research, data analysis | web_search, data_analyzer |
| **SummarizerAgent** | Content synthesis, reporting | AI-powered summarization |
| **OrchestratorAgent** | Multi-agent workflow coordination | workflow_manager |

## 🛡️ Security & Privacy

- **API Key Security**: OpenAI API key stored in environment variables only
- **Local Processing**: All tool outputs simulated locally (no external API calls)
- **Cost Controls**: Built-in cost monitoring and session limits
- **Data Privacy**: No data sent to external services except OpenAI for LLM operations

## 📈 Cost Optimization

- **GPT-4o Mini**: Most cost-effective OpenAI model ($0.150/1K prompt, $0.600/1K completion)
- **Smart Prompting**: Optimized prompts reduce token usage
- **Selective Agent Use**: AI selects only necessary agents
- **Cost Alerts**: Configurable thresholds prevent overspending

## 🔍 Troubleshooting

### Common Issues

1. **"OpenAI API key is required"**
   - Set `OPENAI_API_KEY` environment variable
   - Verify key is valid on OpenAI platform

2. **High costs**
   - Check `cost_alert_threshold` in config
   - Use simpler queries for testing
   - Monitor token usage in output

3. **Import errors**
   - Install all requirements: `pip install -r requirements.txt`
   - Verify Python 3.8+ is being used

## 📝 Development

### Running Tests
```bash
python test_basic.py
```

### Adding New Agents
1. Create agent class in `agents/enhanced_agents.py`
2. Register in `agents/registry.py`
3. Define specialized tools and capabilities

## 🤝 Support

For issues, questions, or feature requests, please refer to the troubleshooting section or check the code documentation.

---

**Built with ❤️ using OpenAI GPT-4o Mini for intelligent, cost-effective agent operations.**