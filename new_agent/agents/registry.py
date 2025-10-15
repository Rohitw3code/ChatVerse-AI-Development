"""
Agent registry and management system for the New Agent Framework
"""

from typing import Dict, List, Optional, Set, Any
from dataclasses import dataclass, field
from datetime import datetime
import json

from ..core.state import AgentMetadata, AgentType
from ..core.config import config
from ..llm.openai_llm import get_llm_instance
from .enhanced_agents import (
    LinkedInAgent, InstagramAgent, GmailAgent, 
    ResearchAgent, SummarizerAgent, OrchestratorAgent
)


@dataclass
class AgentCapability:
    """Represents a specific capability of an agent"""
    name: str
    description: str
    tools_required: List[str] = field(default_factory=list)
    complexity_level: int = 1  # 1-5 scale
    estimated_time_seconds: int = 30


class AgentRegistry:
    """Central registry for all available agents in the framework"""
    
    def __init__(self):
        self.agents: Dict[str, AgentMetadata] = {}
        self.agent_capabilities: Dict[str, List[AgentCapability]] = {}
        self.agent_usage_stats: Dict[str, Dict[str, Any]] = {}
        self.llm = get_llm_instance()
        
        # Initialize enhanced agents with LLM capabilities
        self.enhanced_agents = {}
        self._initialize_enhanced_agents()
    
    def _initialize_enhanced_agents(self):
        """Initialize the registry with enhanced LLM-powered agents"""
        
        # Create enhanced agent instances
        self.enhanced_agents = {
            "LinkedInAgent": LinkedInAgent(),
            "InstagramAgent": InstagramAgent(),
            "GmailAgent": GmailAgent(),
            "ResearchAgent": ResearchAgent(),
            "SummarizerAgent": SummarizerAgent(),
            "OrchestratorAgent": OrchestratorAgent()
        }
        
        # Register each enhanced agent
        for agent_name, agent_instance in self.enhanced_agents.items():
            agent_info = agent_instance.get_agent_info()
            
            # Create AgentMetadata from enhanced agent info
            agent_metadata = AgentMetadata(
                name=agent_info["name"],
                description=agent_info["description"],
                agent_type="executor" if agent_name != "OrchestratorAgent" else "orchestrator",
                tools=agent_info["available_tools"],
                capabilities=agent_info["capabilities"],
                max_retries=3,
                timeout_seconds=300
            )
            
            self.register_agent(agent_metadata)
            
            # Create capabilities from agent capabilities
            capabilities = []
            for capability in agent_info["capabilities"]:
                capabilities.append(AgentCapability(
                    name=capability,
                    description=f"{agent_info['specialization']} - {capability}",
                    tools_required=agent_info["available_tools"],
                    complexity_level=3,
                    estimated_time_seconds=90
                ))
            
            self.agent_capabilities[agent_name] = capabilities
    
    def register_agent(self, agent: AgentMetadata) -> bool:
        """Register a new agent in the registry"""
        if agent.name in self.agents:
            return False  # Agent already exists
        
        self.agents[agent.name] = agent
        self.agent_usage_stats[agent.name] = {
            "total_executions": 0,
            "successful_executions": 0,
            "failed_executions": 0,
            "average_execution_time": 0,
            "last_executed": None,
            "created_at": datetime.now().isoformat()
        }
        
        return True
    
    def get_agent(self, agent_name: str) -> Optional[AgentMetadata]:
        """Get agent metadata by name"""
        return self.agents.get(agent_name)
    
    def list_agents(self, agent_type: Optional[AgentType] = None, active_only: bool = True) -> List[AgentMetadata]:
        """List agents with optional filtering"""
        agents = list(self.agents.values())
        
        if agent_type:
            agents = [a for a in agents if a.agent_type == agent_type]
        
        if active_only:
            agents = [a for a in agents if a.is_active]
        
        return agents
    
    def find_agents_by_capability(self, capability: str) -> List[str]:
        """Find agents that have a specific capability"""
        matching_agents = []
        
        for agent_name, agent in self.agents.items():
            if capability in agent.capabilities:
                matching_agents.append(agent_name)
        
        return matching_agents
    
    def find_agents_for_tools(self, required_tools: List[str]) -> List[str]:
        """Find agents that can use the required tools"""
        matching_agents = []
        
        for agent_name, agent in self.agents.items():
            if all(tool in agent.tools for tool in required_tools):
                matching_agents.append(agent_name)
        
        return matching_agents
    
    def get_agent_capabilities(self, agent_name: str) -> List[AgentCapability]:
        """Get detailed capabilities for an agent"""
        return self.agent_capabilities.get(agent_name, [])
    
    def suggest_agents_for_query(self, query: str) -> List[tuple[str, float]]:
        """Suggest the best agents for a given query with confidence scores"""
        query_lower = query.lower()
        suggestions = []
        
        # Keyword-based matching
        keywords_to_agents = {
            "linkedin": ["LinkedInAgent"],
            "job": ["LinkedInAgent"],
            "jobs": ["LinkedInAgent"],
            "career": ["LinkedInAgent"],
            "instagram": ["InstagramAgent"],
            "social": ["InstagramAgent"],
            "analytics": ["InstagramAgent"],
            "email": ["GmailAgent"],
            "gmail": ["GmailAgent"],
            "send": ["GmailAgent"],
            "research": ["ResearchAgent"],
            "search": ["ResearchAgent"],
            "find": ["ResearchAgent"],
            "summarize": ["SummarizerAgent"],
            "summary": ["SummarizerAgent"],
            "combine": ["SummarizerAgent"]
        }
        
        agent_scores = {}
        
        # Calculate scores based on keyword matches
        for keyword, agents in keywords_to_agents.items():
            if keyword in query_lower:
                for agent in agents:
                    agent_scores[agent] = agent_scores.get(agent, 0) + 0.3
        
        # Boost scores for exact capability matches
        for agent_name, capabilities in self.agent_capabilities.items():
            for capability in capabilities:
                if any(word in query_lower for word in capability.name.split('_')):
                    agent_scores[agent_name] = agent_scores.get(agent_name, 0) + 0.5
        
        # Convert to suggestions with confidence scores
        for agent_name, score in agent_scores.items():
            if agent_name in self.agents and self.agents[agent_name].is_active:
                confidence = min(1.0, score)  # Cap at 1.0
                suggestions.append((agent_name, confidence))
        
        # Sort by confidence (highest first)
        suggestions.sort(key=lambda x: x[1], reverse=True)
        
        # If no specific matches, suggest orchestrator for complex queries
        if not suggestions and len(query.split()) > 10:
            suggestions.append(("OrchestratorAgent", 0.6))
        
        return suggestions
    
    def update_agent_stats(self, agent_name: str, execution_time: int, success: bool):
        """Update agent execution statistics"""
        if agent_name not in self.agent_usage_stats:
            return
        
        stats = self.agent_usage_stats[agent_name]
        stats["total_executions"] += 1
        stats["last_executed"] = datetime.now().isoformat()
        
        if success:
            stats["successful_executions"] += 1
        else:
            stats["failed_executions"] += 1
        
        # Update average execution time
        total_time = stats["average_execution_time"] * (stats["total_executions"] - 1) + execution_time
        stats["average_execution_time"] = total_time / stats["total_executions"]
    
    def get_agent_stats(self, agent_name: str) -> Optional[Dict[str, Any]]:
        """Get statistics for a specific agent"""
        return self.agent_usage_stats.get(agent_name)
    
    def get_all_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get statistics for all agents"""
        return self.agent_usage_stats.copy()
    
    def deactivate_agent(self, agent_name: str) -> bool:
        """Deactivate an agent"""
        if agent_name in self.agents:
            self.agents[agent_name].is_active = False
            return True
        return False
    
    def activate_agent(self, agent_name: str) -> bool:
        """Activate an agent"""
        if agent_name in self.agents:
            self.agents[agent_name].is_active = True
            return True
        return False
    
    def export_registry(self) -> Dict[str, Any]:
        """Export the entire registry to a dictionary"""
        return {
            "agents": {name: {
                "name": agent.name,
                "description": agent.description,
                "agent_type": agent.agent_type,
                "tools": agent.tools,
                "capabilities": agent.capabilities,
                "max_retries": agent.max_retries,
                "timeout_seconds": agent.timeout_seconds,
                "is_active": agent.is_active
            } for name, agent in self.agents.items()},
            "capabilities": {name: [
                {
                    "name": cap.name,
                    "description": cap.description,
                    "tools_required": cap.tools_required,
                    "complexity_level": cap.complexity_level,
                    "estimated_time_seconds": cap.estimated_time_seconds
                } for cap in caps
            ] for name, caps in self.agent_capabilities.items()},
            "stats": self.agent_usage_stats,
            "exported_at": datetime.now().isoformat()
        }
    
    def get_agent_instance(self, agent_name: str):
        """Get the enhanced agent instance for execution"""
        return self.enhanced_agents.get(agent_name)
    
    def route_to_best_agent(self, task: str, context: str = "") -> Optional[str]:
        """Use LLM to determine the best agent for a task"""
        try:
            available_agents = []
            for agent_name, agent_instance in self.enhanced_agents.items():
                agent_info = agent_instance.get_agent_info()
                available_agents.append({
                    "name": agent_name,
                    "description": agent_info["description"]
                })
            
            routing_decision = self.llm.route_to_agent(task, available_agents, context)
            return routing_decision.selected_agent
        except Exception as e:
            print(f"Warning: LLM routing failed, using fallback: {e}")
            # Fallback to keyword-based routing
            task_lower = task.lower()
            if "linkedin" in task_lower or "job" in task_lower:
                return "LinkedInAgent"
            elif "instagram" in task_lower:
                return "InstagramAgent"
            elif "email" in task_lower or "gmail" in task_lower:
                return "GmailAgent"
            elif "research" in task_lower:
                return "ResearchAgent"
            elif "summary" in task_lower or "summarize" in task_lower:
                return "SummarizerAgent"
            else:
                return "OrchestratorAgent"
    
    def import_registry(self, data: Dict[str, Any]) -> bool:
        """Import registry data from a dictionary"""
        try:
            # Clear existing data
            self.agents.clear()
            self.agent_capabilities.clear()
            self.agent_usage_stats.clear()
            
            # Import agents
            for name, agent_data in data.get("agents", {}).items():
                agent = AgentMetadata(**agent_data)
                self.agents[name] = agent
            
            # Import capabilities
            for agent_name, caps_data in data.get("capabilities", {}).items():
                capabilities = []
                for cap_data in caps_data:
                    capability = AgentCapability(**cap_data)
                    capabilities.append(capability)
                self.agent_capabilities[agent_name] = capabilities
            
            # Import stats
            self.agent_usage_stats.update(data.get("stats", {}))
            
            return True
        except Exception as e:
            print(f"Error importing registry: {e}")
            return False


# Global agent registry instance
agent_registry = AgentRegistry()