# New Agent Framework

A self-contained, CLI-driven AI Agent Framework that runs entirely locally with no external API calls. This framework extends the existing agent architecture with enhanced planning, execution, and real-time streaming capabilities.

## 🚀 Key Features

- **🧠 Intelligent Planning**: Analyzes complex queries and creates structured multi-step execution plans
- **🔧 Multi-Agent Coordination**: Coordinates 50+ agents (expandable to 200+) with specialized capabilities
- **⚡ Real-time Streaming**: Token-by-token output with detailed tool lifecycle and node transition events
- **🗄️ Local Database**: Complete execution history, plans, and logs stored locally (SQLite/JSON)
- **🛠️ Dummy Tool Integration**: Realistic dummy implementations for LinkedIn, Instagram, Gmail, and more
- **📊 Rich CLI Interface**: Beautiful command-line interface with progress tracking and statistics
- **🔄 Flexible Execution**: Sequential, parallel, and conditional execution modes
- **🎯 Zero Dependencies**: No external API calls - completely self-contained operation

## 🏗️ Architecture

The framework consists of several key components:

```
new_agent/
├── core/           # Core state management and configuration
├── planning/       # Intelligent query analysis and plan generation
├── execution/      # Multi-agent workflow orchestration  
├── agents/         # Agent registry and management
├── tools/          # Dummy tool implementations
├── streaming/      # Real-time output streaming
├── database/       # Local async database storage
├── llm/            # Dummy LLM for local operation
└── cli.py          # Main CLI interface
```

## 📋 Example Usage

### Basic Query Execution

```bash
# Execute a complex multi-step query
python -m new_agent "Fetch AI/ML engineer jobs from LinkedIn in India and also fetch Instagram insights, summarize both, and email the summary to rohit@gmail.com"
```

This will automatically:
1. 🔍 **LinkedInAgent** → Search for AI/ML engineer jobs in India
2. 📸 **InstagramAgent** → Fetch Instagram insights and analytics  
3. 📝 **SummarizerAgent** → Combine and summarize results
4. 📧 **GmailAgent** → Send email with summary to rohit@gmail.com

### CLI Commands

```bash
# List available agents
python -m new_agent --list-agents

# List available tools  
python -m new_agent --list-tools

# Show execution history
python -m new_agent --history --user-id default --limit 20

# Get framework statistics
python -m new_agent --stats

# Show detailed plan information
python -m new_agent --plan-details <plan_id>

# Execute with options
python -m new_agent "Research AI trends" --verbose --output-format rich --show-metadata
```

## 🤖 Available Agents

The framework includes several specialized agents:

- **LinkedInAgent**: LinkedIn job searches, profile analysis, professional networking
- **InstagramAgent**: Instagram analytics, insights, content analysis, engagement tracking  
- **GmailAgent**: Email operations including sending, reading, organizing workflows
- **ResearchAgent**: Web research, information gathering, data analysis
- **SummarizerAgent**: Content summarization, data synthesis, report generation
- **OrchestratorAgent**: Complex multi-agent workflow coordination

## 🔧 Available Tools

All tools are dummy implementations that simulate real API interactions:

- **linkedin_job_search**: Search job postings with realistic dummy data
- **instagram_insights**: Fetch account metrics and engagement analytics
- **gmail_send**: Send emails with delivery confirmation simulation
- **content_summarizer**: Combine and summarize content from multiple sources
- **web_research**: Conduct research with simulated web results
- **data_processor**: Generic data processing and analysis

## ⚙️ Configuration

The framework supports flexible configuration through environment variables or config files:

```bash
# Environment variables
export NEW_AGENT_MAX_AGENTS=200
export NEW_AGENT_PARALLEL_LIMIT=10
export NEW_AGENT_VERBOSE=true
export NEW_AGENT_OUTPUT_FORMAT=rich

# Or use a config file
python -m new_agent --config-path custom_config.json "Your query here"
```

## 📊 Real-time Streaming Output

The framework provides rich, real-time streaming with:

- **Token-by-token generation**: See AI responses as they're generated
- **Tool lifecycle tracking**: "Started calling tool X with params Y" → "Completed calling tool X"
- **Node transitions**: Clear indication of which agent is active
- **Progress indicators**: Visual progress bars and execution statistics
- **Metadata display**: Optional detailed execution information

Example streaming output:
```
🚀 Starting execution session: abc123...
🧠 Creating execution plan...
📋 Execution Plan (ID: plan_456)
   Steps: 4
   Mode: sequential
   Estimated Duration: 180s

🔄 Executing plan...
🔵 Started: Search for AI/ML engineer positions on LinkedIn in India
🔧 Started calling tool linkedin_job_search with params {'role': 'AI/ML Engineer', 'location': 'India'}
🔧 Completed calling tool linkedin_job_search (1247ms)
✅ Completed: Search for AI/ML engineer positions on LinkedIn in India

🔵 Started: Fetch Instagram account insights and analytics data
🔧 Started calling tool instagram_insights with params {'metrics': ['followers', 'engagement']}
🔧 Completed calling tool instagram_insights (987ms)
✅ Completed: Fetch Instagram account insights and analytics data

...
```

## 🗄️ Local Database Storage

All execution data is stored locally with complete traceability:

- **Execution History**: Complete record of all query executions
- **Plan Details**: Structured execution plans with step-by-step breakdowns
- **Tool Logs**: Detailed logs of all tool calls with parameters and results
- **Agent Statistics**: Performance metrics and usage statistics
- **Error Tracking**: Comprehensive error logging and recovery information

## 🎯 Realistic Dummy Data

The framework generates realistic dummy data that simulates real API responses:

**LinkedIn Job Search Results:**
```json
{
  "jobs_found": 23,
  "sample_jobs": [
    {
      "title": "Senior AI/ML Engineer",
      "company": "TechCorp India", 
      "location": "Bangalore, India",
      "experience": "3-5 years",
      "posted": "2 days ago"
    }
  ]
}
```

**Instagram Insights:**
```json
{
  "account_metrics": {
    "followers": 15420,
    "engagement_rate": 4.2,
    "reach_last_30_days": 45000
  }
}
```

## 📈 Scalability

The framework is designed for scalability:

- **Current**: Supports 50+ active agents
- **Expandable**: Up to 200+ agents with proper resource management
- **Parallel Execution**: Multiple agents can run simultaneously
- **Resource Management**: Configurable limits and timeouts
- **Performance Monitoring**: Built-in metrics and statistics

## 🔧 Installation & Setup

1. **Clone and Navigate:**
   ```bash
   cd new_agent/
   ```

2. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run Your First Query:**
   ```bash
   python -m new_agent "Search for Python developer jobs and email results"
   ```

4. **Explore Features:**
   ```bash
   python -m new_agent --list-agents
   python -m new_agent --stats
   ```

## 🎮 Interactive Examples

Try these example queries to see the framework in action:

```bash
# Simple single-agent task
python -m new_agent "Get Instagram insights for my account"

# Multi-agent workflow
python -m new_agent "Research AI trends, summarize findings, and email to team@company.com"

# Complex coordinated task
python -m new_agent "Find machine learning jobs in India, analyze Instagram engagement, combine insights, and email comprehensive report to hiring@company.com"
```

## 🔍 Advanced Features

- **Dependency Management**: Automatic handling of task dependencies
- **Error Recovery**: Automatic retries and graceful error handling  
- **Conditional Execution**: Smart execution based on runtime conditions
- **Checkpoint System**: Save and resume execution states
- **Export Capabilities**: Export execution logs and statistics
- **Custom Agent Registration**: Add new agents and capabilities

## 📝 Development Notes

This framework demonstrates:
- Complete local operation without external dependencies
- Realistic simulation of complex AI agent workflows
- Professional CLI interface with rich formatting
- Comprehensive logging and traceability
- Scalable architecture supporting 200+ agents
- Real-time streaming with detailed metadata
- Flexible execution modes and error handling

The dummy implementations provide a solid foundation that can be easily replaced with real API integrations when needed, while maintaining the same interface and workflow patterns.

---

**Built for the ChatVerse AI Development Team** 🚀