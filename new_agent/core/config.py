"""
Configuration management for the New Agent Framework
"""

import os
from dataclasses import dataclass
from typing import Dict, Any, List, Optional
from pathlib import Path

# Try to load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # dotenv not available, just use system environment variables
    pass


@dataclass
class DatabaseConfig:
    """Database configuration"""
    type: str = "sqlite"  # sqlite, json, memory
    connection_string: str = "new_agent.db"
    enable_logging: bool = True
    backup_enabled: bool = True
    backup_interval_hours: int = 24


@dataclass
class LLMConfig:
    """LLM configuration for OpenAI GPT-4o Mini"""
    provider: str = "openai"  # openai for agentic operations
    model: str = "gpt-4o-mini"
    api_key: str = ""  # OpenAI API key (set via environment)
    temperature: float = 0.1
    max_tokens: int = 4000
    timeout_seconds: int = 60
    enable_token_tracking: bool = True
    cost_alert_threshold: float = 5.0  # Alert if cost exceeds $5
    max_cost_per_session: float = 10.0  # Maximum cost per session


@dataclass
class StreamingConfig:
    """Real-time streaming configuration"""
    enabled: bool = True
    buffer_size: int = 1000
    flush_interval_ms: int = 100
    show_tool_lifecycle: bool = True
    show_node_transitions: bool = True
    token_by_token: bool = True


@dataclass
class ExecutionConfig:
    """Execution engine configuration"""
    max_parallel_agents: int = 5
    default_timeout_seconds: int = 300
    max_retries: int = 3
    enable_checkpoints: bool = True
    checkpoint_interval_steps: int = 5
    recovery_enabled: bool = True


@dataclass
class CLIConfig:
    """CLI interface configuration"""
    output_format: str = "rich"  # rich, json, plain
    show_progress: bool = True
    show_metadata: bool = True
    verbose: bool = True
    colors_enabled: bool = True
    interactive_mode: bool = False


class FrameworkConfig:
    """Main configuration class for the New Agent Framework"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or self._get_default_config_path()
        
        # Core configurations
        self.database = DatabaseConfig()
        self.llm = LLMConfig()
        self.streaming = StreamingConfig()
        self.execution = ExecutionConfig()
        self.cli = CLIConfig()
        
        # Load OpenAI API key from environment
        self.llm.api_key = os.getenv("OPENAI_API_KEY", "")
        
        # Framework settings
        self.framework_name = "New Agent Framework"
        self.version = "1.0.0"
        self.data_dir = self._get_data_dir()
        self.logs_dir = self._get_logs_dir()
        
        # Agent limits and scaling
        self.max_agents = 200
        self.default_active_agents = 50
        self.agent_registry_size = 1000
        
        # Load configuration if exists
        self._load_config()
    
    def _get_default_config_path(self) -> str:
        """Get default configuration file path"""
        return os.path.join(os.path.dirname(__file__), "config.json")
    
    def _get_data_dir(self) -> str:
        """Get data directory path"""
        data_dir = os.path.join(os.path.dirname(__file__), "..", "data")
        os.makedirs(data_dir, exist_ok=True)
        return data_dir
    
    def _get_logs_dir(self) -> str:
        """Get logs directory path"""
        logs_dir = os.path.join(os.path.dirname(__file__), "..", "logs")
        os.makedirs(logs_dir, exist_ok=True)
        return logs_dir
    
    def _load_config(self):
        """Load configuration from file if exists"""
        if os.path.exists(self.config_path):
            try:
                import json
                with open(self.config_path, 'r') as f:
                    config_data = json.load(f)
                self._update_from_dict(config_data)
            except Exception as e:
                print(f"Warning: Could not load config from {self.config_path}: {e}")
    
    def _update_from_dict(self, config_data: Dict[str, Any]):
        """Update configuration from dictionary"""
        for section, values in config_data.items():
            if hasattr(self, section) and isinstance(values, dict):
                section_config = getattr(self, section)
                for key, value in values.items():
                    if hasattr(section_config, key):
                        setattr(section_config, key, value)
    
    def save_config(self):
        """Save current configuration to file"""
        try:
            import json
            config_data = {
                "database": self.database.__dict__,
                "llm": self.llm.__dict__,
                "streaming": self.streaming.__dict__,
                "execution": self.execution.__dict__,
                "cli": self.cli.__dict__
            }
            
            with open(self.config_path, 'w') as f:
                json.dump(config_data, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save config to {self.config_path}: {e}")
    
    def get_database_path(self) -> str:
        """Get full database file path"""
        return os.path.join(self.data_dir, self.database.connection_string)
    
    def get_log_file_path(self, log_type: str = "main") -> str:
        """Get log file path for specific log type"""
        return os.path.join(self.logs_dir, f"{log_type}.log")
    
    def validate(self) -> List[str]:
        """Validate configuration and return list of issues"""
        issues = []
        
        # Validate database settings
        if self.database.type not in ["sqlite", "json", "memory"]:
            issues.append(f"Invalid database type: {self.database.type}")
        
        # Validate execution limits
        if self.execution.max_parallel_agents < 1:
            issues.append("max_parallel_agents must be at least 1")
        
        if self.max_agents < self.default_active_agents:
            issues.append("max_agents must be >= default_active_agents")
        
        # Validate paths
        try:
            os.makedirs(self.data_dir, exist_ok=True)
            os.makedirs(self.logs_dir, exist_ok=True)
        except Exception as e:
            issues.append(f"Cannot create directories: {e}")
        
        return issues
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary"""
        return {
            "framework_name": self.framework_name,
            "version": self.version,
            "data_dir": self.data_dir,
            "logs_dir": self.logs_dir,
            "max_agents": self.max_agents,
            "default_active_agents": self.default_active_agents,
            "database": self.database.__dict__,
            "llm": self.llm.__dict__,
            "streaming": self.streaming.__dict__,
            "execution": self.execution.__dict__,
            "cli": self.cli.__dict__
        }


# Global configuration instance
config = FrameworkConfig()


# Environment variable overrides
def load_env_overrides():
    """Load configuration overrides from environment variables"""
    
    # Database overrides
    if os.getenv("NEW_AGENT_DB_TYPE"):
        config.database.type = os.getenv("NEW_AGENT_DB_TYPE")
    
    if os.getenv("NEW_AGENT_DB_CONNECTION"):
        config.database.connection_string = os.getenv("NEW_AGENT_DB_CONNECTION")
    
    # Execution overrides
    if os.getenv("NEW_AGENT_MAX_AGENTS"):
        try:
            config.max_agents = int(os.getenv("NEW_AGENT_MAX_AGENTS"))
        except ValueError:
            pass
    
    if os.getenv("NEW_AGENT_PARALLEL_LIMIT"):
        try:
            config.execution.max_parallel_agents = int(os.getenv("NEW_AGENT_PARALLEL_LIMIT"))
        except ValueError:
            pass
    
    # CLI overrides
    if os.getenv("NEW_AGENT_VERBOSE"):
        config.cli.verbose = os.getenv("NEW_AGENT_VERBOSE").lower() == "true"
    
    if os.getenv("NEW_AGENT_OUTPUT_FORMAT"):
        config.cli.output_format = os.getenv("NEW_AGENT_OUTPUT_FORMAT")


# Load environment overrides on import
load_env_overrides()