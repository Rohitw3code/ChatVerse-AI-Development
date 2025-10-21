"""
DEPRECATED: This file is deprecated and kept only for backward compatibility.
All agent prompts are now centralized in chatagent/agents/agents_config.py

Please use agents_config.py for all agent configurations.
"""

from dataclasses import dataclass
import warnings

warnings.warn(
    "node_prompt.py is deprecated. Use chatagent.agents.agents_config instead.",
    DeprecationWarning,
    stacklevel=2
)

@dataclass(frozen=True)
class PROMPTS:
    """
    DEPRECATED: Use agents_config.py instead
    """
    
    instagram_manager_node: str = (
        "DEPRECATED: This prompt is no longer used. Check agents_config.py"
    )

    social_media_manager_node: str = (
        "DEPRECATED: This prompt is no longer used. Check agents_config.py"
    )

    gmail_manager_node: str = (
        "DEPRECATED: This prompt is no longer used. Check agents_config.py"
    )

    youtube_manager_node: str = (
        "DEPRECATED: This prompt is no longer used. Check agents_config.py"
    )
