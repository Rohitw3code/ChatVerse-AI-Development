"""
Database module for the Enhanced Agent Framework
"""

from .simple_db import SimpleLocalDatabase

# Create global instance
database = SimpleLocalDatabase()

__all__ = ['SimpleLocalDatabase', 'database']