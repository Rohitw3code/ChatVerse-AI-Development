"""
LLM module for the Enhanced Agent Framework
"""

try:
    from .openai_llm import get_llm_instance, OpenAILLM
    __all__ = ['get_llm_instance', 'OpenAILLM']
except ImportError as e:
    print(f"Warning: OpenAI LLM not available: {e}")
    from .dummy_llm import DummyLLM, AgentResponseGenerator
    __all__ = ['DummyLLM', 'AgentResponseGenerator']