"""
Planning module for the Enhanced Agent Framework
"""

from .planner import PlanningEngine

# Create global instance
planning_engine = PlanningEngine()

__all__ = ['PlanningEngine', 'planning_engine']