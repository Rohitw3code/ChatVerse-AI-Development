# Quick Start Guide - New Agent Framework

## 🚀 Get Started in 3 Steps

### 1. Install Dependencies
```bash
cd new_agent/
pip install rich pydantic
```

### 2. Run Basic Tests
```bash
python test_basic.py
```
You should see all tests pass with a green "🎉 All tests passed!" message.

### 3. Execute Your First Query
```bash
python -m new_agent "Fetch AI/ML engineer jobs from LinkedIn in India and email summary to rohit@gmail.com"
```

## 📋 Essential Commands

### Execute Queries
```bash
# Simple query
python -m new_agent "Get Instagram insights"

# Complex multi-agent workflow
python -m new_agent "Search for Python jobs, analyze results, and email summary"

# With options
python -m new_agent "Research AI trends" --verbose --output-format rich
```

### Information Commands
```bash
# List available agents
python -m new_agent --list-agents

# List available tools
python -m new_agent --list-tools

# Show execution history
python -m new_agent --history

# Get framework statistics
python -m new_agent --stats
```

## 🎯 Example Queries to Try

1. **Simple LinkedIn Search:**
   ```bash
   python -m new_agent "Find machine learning jobs in India"
   ```

2. **Instagram Analytics:**
   ```bash
   python -m new_agent "Get Instagram insights and engagement metrics"
   ```

3. **Email Operations:**
   ```bash
   python -m new_agent "Send a summary email to team@company.com"
   ```

4. **Multi-Agent Workflow:**
   ```bash
   python -m new_agent "Research AI trends, get LinkedIn job data, summarize both, and email results to manager@company.com"
   ```

5. **Complex Coordination:**
   ```bash
   python -m new_agent "Fetch LinkedIn jobs for data scientist roles, analyze Instagram engagement for our company account, combine insights, and email comprehensive report to hiring@company.com"
   ```

## 🔧 What Happens During Execution

When you run a query, you'll see:

1. **🧠 Planning Phase:** AI analyzes your query and creates a structured plan
2. **📋 Plan Display:** Shows the steps, agents, and estimated duration
3. **🔄 Execution Phase:** Real-time streaming of each step
4. **🔧 Tool Calls:** Detailed tool lifecycle with parameters and results
5. **✅ Completion:** Final summary with statistics and outputs

## 📊 Understanding the Output

### Real-time Streaming
- **🔵 Started:** Agent begins working on a step
- **🔧 Tool calls:** "Started calling tool X" → "Completed calling tool X"
- **✅ Completed:** Step finished successfully
- **❌ Error:** If something goes wrong

### Final Summary
- **Session ID:** Unique identifier for this execution
- **Duration:** Total execution time
- **Tools Called:** Number of tool operations
- **Results:** Key outputs from each step

## 🗄️ Data Storage

All execution data is stored locally in:
- **SQLite Database:** `new_agent/data/new_agent.db` (default)
- **JSON Files:** Alternative storage format
- **Logs:** Complete execution history and statistics

## 🎮 Interactive Examples

Try these to see different framework capabilities:

### Basic Agent Coordination
```bash
python -m new_agent "Get Instagram analytics"
```
*Uses: InstagramAgent → instagram_insights tool*

### Multi-Step Planning
```bash
python -m new_agent "Research Python developer market and email findings"
```
*Uses: ResearchAgent → SummarizerAgent → GmailAgent*

### Complex Workflow
```bash
python -m new_agent "Find AI jobs on LinkedIn, get our Instagram metrics, combine data, and email report to hr@company.com"
```
*Uses: LinkedInAgent → InstagramAgent → SummarizerAgent → GmailAgent*

## 🔍 Exploring Results

After running queries, explore the data:

```bash
# See your execution history
python -m new_agent --history --limit 20

# Get detailed statistics
python -m new_agent --stats

# View agent performance
python -m new_agent --list-agents
```

## ⚙️ Configuration

Customize behavior with environment variables:
```bash
export NEW_AGENT_MAX_AGENTS=100
export NEW_AGENT_VERBOSE=true
export NEW_AGENT_OUTPUT_FORMAT=rich
```

Or create a custom config file and use:
```bash
python -m new_agent --config-path my_config.json "Your query"
```

## 🎯 Key Features You'll See

- **🧠 Intelligent Planning:** Automatically breaks complex queries into steps
- **⚡ Real-time Streaming:** See progress as it happens
- **🔧 Tool Integration:** Realistic dummy APIs for LinkedIn, Instagram, Gmail
- **🤖 Multi-Agent Coordination:** Different specialists for different tasks
- **📊 Rich Output:** Beautiful CLI interface with progress tracking
- **🗄️ Complete Logging:** Everything is saved for later review

## 🚀 Ready to Explore!

The framework is completely self-contained and runs locally. Every "API call" is a realistic dummy implementation, so you can see exactly how a production system would work without any external dependencies.

Start with simple queries and work your way up to complex multi-agent workflows!