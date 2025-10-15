"""
Execution engine module for the Enhanced Agent Framework
"""

from .engine import ExecutionEngine

# Create global instance
execution_engine = ExecutionEngine()

__all__ = ['ExecutionEngine', 'execution_engine']