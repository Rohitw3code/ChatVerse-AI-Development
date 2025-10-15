"""
Streaming interface module for the Enhanced Agent Framework
"""

from .interface import StreamingInterface

# Create global instance
cli_streamer = StreamingInterface()

__all__ = ['StreamingInterface', 'cli_streamer']