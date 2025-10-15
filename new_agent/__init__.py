"""
Enhanced New Agent Framework - OpenAI-Powered CLI-Driven AI Agent System

A fully agentic, multi-agent framework that uses OpenAI GPT-4o Mini for intelligent
decision making, planning, routing, and summarization while maintaining local tool execution.
"""

__version__ = "2.0.0"
__author__ = "Enhanced ChatVerse AI Development Team"

# Core imports for enhanced functionality
try:
    from .llm.openai_llm import get_llm_instance
    from .agents.enhanced_agents import (
        LinkedInAgent, InstagramAgent, GmailAgent,
        ResearchAgent, SummarizerAgent, OrchestratorAgent
    )
    from .agents.registry import agent_registry
    from .planning.planner import PlanningEngine
    from .execution.engine import ExecutionEngine
    from .cli import NewAgentCLI
except ImportError as e:
    print(f"Warning: Some enhanced features may not be available: {e}")
    print("Please ensure all requirements are installed: pip install -r requirements.txt")
    print("And set your OpenAI API key: set OPENAI_API_KEY=your_key_here")