"""
Enhanced Agent Base Class with OpenAI LLM Integration
All agents use real LLM for agentic decision making
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, AsyncGenerator
from datetime import datetime
import json

from ..llm.openai_llm import get_llm_instance, AgentAction
from ..core.state import StreamingEvent, EventType
from ..tools.dummy_tools import dummy_tool_registry


class BaseAgent(ABC):
    """
    Base class for all agents with LLM-powered decision making
    """
    
    def __init__(self, name: str, description: str, capabilities: List[str]):
        self.name = name
        self.description = description
        self.capabilities = capabilities
        self.llm = get_llm_instance()
        self.conversation_history = []
        self.execution_stats = {
            "total_calls": 0,
            "successful_calls": 0,
            "failed_calls": 0,
            "total_tokens": 0,
            "total_cost": 0.0
        }
    
    async def execute_step(
        self, 
        task: str, 
        context: Dict[str, Any] = None,
        available_tools: List[str] = None
    ) -> AsyncGenerator[StreamingEvent, None]:
        """
        Execute a task step using LLM reasoning
        """
        context = context or {}
        available_tools = available_tools or self._get_available_tools()
        
        yield StreamingEvent(
            type=EventType.AGENT_START,
            data={
                "agent": self.name,
                "task": task,
                "timestamp": datetime.now().isoformat()
            }
        )
        
        try:
            # Update conversation history
            self.conversation_history.append(f"Task: {task}")
            
            # Get LLM decision on what action to take
            decision = self.llm.make_agent_decision(
                agent_name=self.name,
                agent_description=self.description,
                current_task=task,
                available_tools=available_tools,
                conversation_history=self.conversation_history,
                tool_results=context.get("previous_results")
            )
            
            yield StreamingEvent(
                type=EventType.AGENT_THINKING,
                data={
                    "agent": self.name,
                    "reasoning": decision.reasoning,
                    "action_type": decision.action_type,
                    "confidence": decision.confidence
                }
            )
            
            # Execute the decided action
            result = await self._execute_action(decision, context)
            
            # Update stats
            self.execution_stats["total_calls"] += 1
            if result.get("success", True):
                self.execution_stats["successful_calls"] += 1
            else:
                self.execution_stats["failed_calls"] += 1
            
            # Update token usage
            usage_stats = self.llm.get_usage_stats()
            self.execution_stats["total_tokens"] = usage_stats["total_usage"]["total_tokens"]
            self.execution_stats["total_cost"] = usage_stats["total_usage"]["estimated_cost"]
            
            yield StreamingEvent(
                type=EventType.AGENT_COMPLETE,
                data={
                    "agent": self.name,
                    "result": result,
                    "stats": self.execution_stats
                }
            )
            
        except Exception as e:
            self.execution_stats["failed_calls"] += 1
            yield StreamingEvent(
                type=EventType.ERROR,
                data={
                    "agent": self.name,
                    "error": str(e),
                    "task": task
                }
            )
    
    async def _execute_action(self, decision: AgentAction, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the action decided by the LLM"""
        
        if decision.action_type == "tool_call" and decision.tool_name:
            return await self._execute_tool_call(decision.tool_name, decision.tool_parameters, context)
        
        elif decision.action_type == "delegate":
            return {
                "success": True,
                "action": "delegate",
                "next_agent": decision.next_agent,
                "reasoning": decision.reasoning
            }
        
        elif decision.action_type == "complete":
            return {
                "success": True,
                "action": "complete",
                "message": decision.completion_message,
                "reasoning": decision.reasoning
            }
        
        else:  # error
            return {
                "success": False,
                "action": "error",
                "error": decision.reasoning
            }
    
    async def _execute_tool_call(
        self, 
        tool_name: str, 
        parameters: Dict[str, Any], 
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute a tool call with the given parameters"""
        
        try:
            # Get tool from registry
            tool = dummy_tool_registry.get_tool(tool_name)
            if not tool:
                return {
                    "success": False,
                    "error": f"Tool {tool_name} not found",
                    "available_tools": list(dummy_tool_registry.tools.keys())
                }
            
            # Execute tool
            result = await tool.execute(**parameters)
            
            # Add to conversation history
            self.conversation_history.append(f"Tool {tool_name} result: {json.dumps(result)}")
            
            return {
                "success": True,
                "tool_name": tool_name,
                "parameters": parameters,
                "result": result
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Tool execution failed: {str(e)}",
                "tool_name": tool_name,
                "parameters": parameters
            }
    
    def _get_available_tools(self) -> List[str]:
        """Get list of available tools for this agent"""
        # Override in subclasses to specify agent-specific tools
        return list(dummy_tool_registry.tools.keys())
    
    @abstractmethod
    def get_agent_info(self) -> Dict[str, Any]:
        """Get agent information and statistics"""
        pass


class LinkedInAgent(BaseAgent):
    """Agent specialized for LinkedIn operations"""
    
    def __init__(self):
        super().__init__(
            name="LinkedInAgent",
            description="Specialized agent for LinkedIn job searching, profile analysis, and networking tasks",
            capabilities=["job_search", "profile_analysis", "company_research", "networking"]
        )
    
    def _get_available_tools(self) -> List[str]:
        return ["linkedin_search", "linkedin_profile_analysis", "linkedin_company_info"]
    
    def get_agent_info(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "capabilities": self.capabilities,
            "available_tools": self._get_available_tools(),
            "stats": self.execution_stats,
            "specialization": "LinkedIn operations and job market analysis"
        }


class InstagramAgent(BaseAgent):
    """Agent specialized for Instagram operations"""
    
    def __init__(self):
        super().__init__(
            name="InstagramAgent",
            description="Specialized agent for Instagram analytics, content analysis, and social media insights",
            capabilities=["analytics", "content_analysis", "engagement_tracking", "hashtag_research"]
        )
    
    def _get_available_tools(self) -> List[str]:
        return ["instagram_insights", "instagram_analytics", "instagram_content_analysis"]
    
    def get_agent_info(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "capabilities": self.capabilities,
            "available_tools": self._get_available_tools(),
            "stats": self.execution_stats,
            "specialization": "Instagram analytics and social media insights"
        }


class GmailAgent(BaseAgent):
    """Agent specialized for Gmail operations"""
    
    def __init__(self):
        super().__init__(
            name="GmailAgent",
            description="Specialized agent for email composition, sending, and management tasks",
            capabilities=["email_composition", "email_sending", "contact_management", "email_templates"]
        )
    
    def _get_available_tools(self) -> List[str]:
        return ["gmail_send", "gmail_compose", "gmail_template"]
    
    def get_agent_info(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "capabilities": self.capabilities,
            "available_tools": self._get_available_tools(),
            "stats": self.execution_stats,
            "specialization": "Email communication and management"
        }


class ResearchAgent(BaseAgent):
    """Agent specialized for research and data analysis"""
    
    def __init__(self):
        super().__init__(
            name="ResearchAgent",
            description="Specialized agent for data research, analysis, and information gathering",
            capabilities=["web_research", "data_analysis", "fact_checking", "trend_analysis"]
        )
    
    def _get_available_tools(self) -> List[str]:
        return ["web_search", "data_analyzer", "trend_tracker"]
    
    def get_agent_info(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "capabilities": self.capabilities,
            "available_tools": self._get_available_tools(),
            "stats": self.execution_stats,
            "specialization": "Research and data analysis operations"
        }


class SummarizerAgent(BaseAgent):
    """Agent specialized for summarization and content synthesis"""
    
    def __init__(self):
        super().__init__(
            name="SummarizerAgent",
            description="Specialized agent for summarizing content, synthesizing information, and creating reports",
            capabilities=["text_summarization", "data_synthesis", "report_generation", "content_analysis"]
        )
    
    def _get_available_tools(self) -> List[str]:
        return ["summarizer", "report_generator", "content_analyzer"]
    
    def get_agent_info(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "capabilities": self.capabilities,
            "available_tools": self._get_available_tools(),
            "stats": self.execution_stats,
            "specialization": "Content summarization and synthesis"
        }
    
    async def _execute_action(self, decision: AgentAction, context: Dict[str, Any]) -> Dict[str, Any]:
        """Override to handle summarization with LLM"""
        
        if decision.action_type == "tool_call" and decision.tool_name == "summarizer":
            # Use LLM for intelligent summarization
            data_sources = context.get("data_sources", [])
            if data_sources:
                try:
                    summary = self.llm.generate_summary(
                        data_sources=data_sources,
                        summary_type=decision.tool_parameters.get("type", "comprehensive"),
                        context=context.get("summary_context", "")
                    )
                    
                    return {
                        "success": True,
                        "tool_name": "summarizer",
                        "result": summary.dict(),
                        "llm_generated": True
                    }
                except Exception as e:
                    return {
                        "success": False,
                        "error": f"LLM summarization failed: {str(e)}",
                        "fallback_to_dummy": True
                    }
        
        # Use base implementation for other actions
        return await super()._execute_action(decision, context)


class OrchestratorAgent(BaseAgent):
    """Agent specialized for orchestrating multi-agent workflows"""
    
    def __init__(self):
        super().__init__(
            name="OrchestratorAgent",
            description="Specialized agent for coordinating complex multi-agent workflows and task routing",
            capabilities=["workflow_management", "agent_coordination", "task_routing", "dependency_management"]
        )
    
    def _get_available_tools(self) -> List[str]:
        return ["task_router", "workflow_manager", "dependency_tracker"]
    
    def get_agent_info(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "capabilities": self.capabilities,
            "available_tools": self._get_available_tools(),
            "stats": self.execution_stats,
            "specialization": "Multi-agent workflow orchestration"
        }