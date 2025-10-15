"""
Dummy LLM implementation for local, no-API operation
"""

import time
import random
from typing import List, Dict, Any, Generator, Optional
from datetime import datetime
import json
import re

from ..core.config import config
from ..core.state import StreamingEvent


class DummyLLM:
    """
    A dummy LLM that simulates intelligent responses for planning, routing,
    and coordination without requiring external API calls.
    """
    
    def __init__(self, model_name: str = "dummy-gpt-4"):
        self.model_name = model_name
        self.temperature = config.llm.temperature
        self.max_tokens = config.llm.max_tokens
        
        # Response templates for different contexts
        self.response_templates = {
            "planning": [
                "I'll analyze your request and create a structured plan.",
                "Let me break down this task into executable steps.",
                "Based on your query, here's what I'll plan to do:",
                "I'm creating a comprehensive plan for your request."
            ],
            "routing": [
                "Routing to the appropriate agent for this task.",
                "I'll direct this to the most suitable agent.",
                "Selecting the optimal agent for execution.",
                "Coordinating with the right specialist."
            ],
            "execution": [
                "Executing the requested action now.",
                "Processing your request with the selected tools.",
                "Working on this task step by step.",
                "Implementing the planned approach."
            ],
            "completion": [
                "Task completed successfully.",
                "I've finished processing your request.",
                "All steps have been executed as planned.",
                "The requested work is now complete."
            ]
        }
        
        # Simulated response delays for realism
        self.typing_delays = {
            "fast": (0.01, 0.03),
            "normal": (0.02, 0.05), 
            "slow": (0.03, 0.08)
        }
    
    def generate_planning_response(self, query: str, available_agents: List[Dict]) -> Dict[str, Any]:
        """Generate a dummy planning response"""
        
        # Analyze query keywords to determine plan complexity
        query_lower = query.lower()
        
        # Extract key actions and entities
        actions = self._extract_actions(query_lower)
        entities = self._extract_entities(query_lower)
        
        # Generate steps based on detected patterns
        plan_steps = []
        
        # LinkedIn job search pattern
        if any(word in query_lower for word in ["linkedin", "job", "jobs"]):
            plan_steps.append("Search for AI/ML engineer positions on LinkedIn in India")
            
        # Instagram insights pattern  
        if any(word in query_lower for word in ["instagram", "insight", "analytics"]):
            plan_steps.append("Fetch Instagram account insights and analytics")
        
        # Email/Gmail pattern
        if any(word in query_lower for word in ["email", "gmail", "send"]):
            if "summary" in query_lower or "summarize" in query_lower:
                plan_steps.append("Compose and send summary email")
            else:
                plan_steps.append("Handle email-related task")
        
        # Research/search pattern
        if any(word in query_lower for word in ["research", "search", "find", "look"]):
            plan_steps.append("Conduct research and gather information")
        
        # Summarization pattern
        if any(word in query_lower for word in ["summarize", "summary", "combine"]):
            if len(plan_steps) > 1:
                plan_steps.append("Summarize and combine all gathered information")
        
        # Fallback for unmatched queries
        if not plan_steps:
            plan_steps = [
                "Analyze the user request",
                "Execute appropriate actions",
                "Provide comprehensive results"
            ]
        
        return {
            "plan_id": f"plan_{int(time.time())}",
            "query": query,
            "steps": plan_steps,
            "estimated_duration": len(plan_steps) * 30,  # 30 seconds per step
            "confidence": 0.85 + random.uniform(0, 0.15)
        }
    
    def generate_routing_decision(self, current_step: str, available_agents: List[str]) -> Dict[str, Any]:
        """Generate a dummy routing decision"""
        
        step_lower = current_step.lower()
        
        # Agent routing logic based on step content
        selected_agent = "GenericAgent"  # fallback
        confidence = 0.7
        
        if any(word in step_lower for word in ["linkedin", "job"]):
            selected_agent = "LinkedInAgent"
            confidence = 0.95
        elif any(word in step_lower for word in ["instagram", "social"]):
            selected_agent = "InstagramAgent"
            confidence = 0.92
        elif any(word in step_lower for word in ["email", "gmail", "send"]):
            selected_agent = "GmailAgent"
            confidence = 0.90
        elif any(word in step_lower for word in ["research", "search"]):
            selected_agent = "ResearchAgent" 
            confidence = 0.88
        elif any(word in step_lower for word in ["summary", "summarize"]):
            selected_agent = "SummarizerAgent"
            confidence = 0.85
        
        # Ensure selected agent is in available agents
        if selected_agent not in available_agents and available_agents:
            selected_agent = available_agents[0]
            confidence = 0.6
        
        return {
            "selected_agent": selected_agent,
            "confidence": confidence,
            "reasoning": f"Selected {selected_agent} based on step content analysis",
            "alternatives": [agent for agent in available_agents if agent != selected_agent][:2]
        }
    
    def generate_tool_parameters(self, tool_name: str, context: str) -> Dict[str, Any]:
        """Generate realistic dummy parameters for tool calls"""
        
        tool_lower = tool_name.lower()
        context_lower = context.lower()
        
        if "linkedin" in tool_lower and "search" in tool_lower:
            return {
                "role": "AI/ML Engineer",
                "location": "India",
                "experience_level": "mid-senior",
                "company_size": "any",
                "limit": 50
            }
        
        elif "instagram" in tool_lower and "insight" in tool_lower:
            return {
                "account_id": "dummy_account",
                "metrics": ["followers", "engagement", "reach", "impressions"],
                "time_period": "30_days"
            }
        
        elif "email" in tool_lower or "gmail" in tool_lower:
            # Extract email from context
            email_match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', context)
            recipient = email_match.group(0) if email_match else "rohit@gmail.com"
            
            return {
                "to": recipient,
                "subject": "AI Agent Task Summary",
                "body": "Generated summary content will be inserted here"
            }
        
        elif "summary" in tool_lower or "summarize" in tool_lower:
            return {
                "content_sources": ["linkedin_results", "instagram_insights"],
                "summary_type": "comprehensive",
                "max_length": 500
            }
        
        else:
            return {
                "operation": "process",
                "context": context,
                "options": {"detailed": True}
            }
    
    def stream_response(self, prompt: str, context: str = "general") -> Generator[StreamingEvent, None, None]:
        """Generate streaming response tokens"""
        
        response_type = self._determine_response_type(prompt)
        template = random.choice(self.response_templates.get(response_type, self.response_templates["execution"]))
        
        # Add context-specific content
        if "plan" in prompt.lower():
            full_response = f"{template} Let me create a detailed execution plan for your request."
        elif "route" in prompt.lower() or "select" in prompt.lower():
            full_response = f"{template} I'll coordinate with the most appropriate specialist."
        else:
            full_response = f"{template} Processing your request now."
        
        # Stream word by word with realistic delays
        words = full_response.split()
        for i, word in enumerate(words):
            delay = random.uniform(*self.typing_delays["normal"])
            time.sleep(delay)
            
            yield StreamingEvent(
                event_type="token",
                content=word + (" " if i < len(words) - 1 else ""),
                metadata={
                    "token_index": i,
                    "total_tokens": len(words),
                    "model": self.model_name,
                    "response_type": response_type
                }
            )
    
    def _extract_actions(self, query: str) -> List[str]:
        """Extract action words from query"""
        action_words = [
            "search", "find", "fetch", "get", "send", "email", "summarize",
            "combine", "analyze", "research", "look", "gather", "collect"
        ]
        return [word for word in action_words if word in query]
    
    def _extract_entities(self, query: str) -> List[str]:
        """Extract entity mentions from query"""
        entities = []
        
        # Platform mentions
        platforms = ["linkedin", "instagram", "gmail", "email", "youtube", "twitter"]
        entities.extend([p for p in platforms if p in query])
        
        # Job-related entities
        if any(word in query for word in ["job", "engineer", "developer"]):
            entities.extend(["jobs", "career", "employment"])
        
        # Location entities
        if "india" in query:
            entities.append("india")
        
        return entities
    
    def _determine_response_type(self, prompt: str) -> str:
        """Determine the type of response needed"""
        prompt_lower = prompt.lower()
        
        if any(word in prompt_lower for word in ["plan", "steps", "break down"]):
            return "planning"
        elif any(word in prompt_lower for word in ["route", "select", "choose", "agent"]):
            return "routing"
        elif any(word in prompt_lower for word in ["complete", "done", "finished"]):
            return "completion"
        else:
            return "execution"


# Simulated intelligent responses for specific agent contexts
class AgentResponseGenerator:
    """Generate contextual responses for different agent types"""
    
    @staticmethod
    def generate_linkedin_response(query: str) -> Dict[str, Any]:
        """Generate LinkedIn search results"""
        return {
            "jobs_found": random.randint(15, 45),
            "sample_jobs": [
                {
                    "title": "Senior AI/ML Engineer",
                    "company": "TechCorp India",
                    "location": "Bangalore, India",
                    "experience": "3-5 years",
                    "posted": "2 days ago"
                },
                {
                    "title": "Machine Learning Engineer", 
                    "company": "InnovateAI",
                    "location": "Mumbai, India",
                    "experience": "2-4 years", 
                    "posted": "1 week ago"
                },
                {
                    "title": "AI Research Scientist",
                    "company": "DataSci Solutions",
                    "location": "Hyderabad, India",
                    "experience": "4-6 years",
                    "posted": "3 days ago"
                }
            ],
            "search_metadata": {
                "query_processed": "AI/ML Engineer jobs in India",
                "total_results": random.randint(100, 500),
                "search_time_ms": random.randint(150, 800)
            }
        }
    
    @staticmethod
    def generate_instagram_response(query: str) -> Dict[str, Any]:
        """Generate Instagram insights data"""
        return {
            "account_metrics": {
                "followers": random.randint(1000, 50000),
                "following": random.randint(500, 2000),
                "posts": random.randint(50, 500),
                "engagement_rate": round(random.uniform(1.5, 8.5), 2)
            },
            "recent_performance": {
                "avg_likes": random.randint(50, 1000),
                "avg_comments": random.randint(5, 100),
                "reach_last_30_days": random.randint(5000, 100000),
                "impressions_last_30_days": random.randint(8000, 150000)
            },
            "top_content": [
                {
                    "post_id": "post_001",
                    "likes": random.randint(100, 2000),
                    "comments": random.randint(10, 200),
                    "type": "carousel"
                },
                {
                    "post_id": "post_002", 
                    "likes": random.randint(80, 1500),
                    "comments": random.randint(8, 150),
                    "type": "reel"
                }
            ],
            "insights_period": "Last 30 days",
            "generated_at": datetime.now().isoformat()
        }
    
    @staticmethod
    def generate_email_response(recipient: str, subject: str, content: str) -> Dict[str, Any]:
        """Generate email send confirmation"""
        return {
            "email_sent": True,
            "message_id": f"msg_{int(time.time())}_{random.randint(1000, 9999)}",
            "recipient": recipient,
            "subject": subject,
            "sent_at": datetime.now().isoformat(),
            "delivery_status": "delivered",
            "content_length": len(content),
            "estimated_read_time": f"{max(1, len(content.split()) // 200)} minutes"
        }
    
    @staticmethod
    def generate_summary_response(data_sources: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate summarized content from multiple sources"""
        
        summary_parts = []
        
        # Process LinkedIn data
        linkedin_data = next((d for d in data_sources if "linkedin" in str(d).lower()), None)
        if linkedin_data:
            job_count = linkedin_data.get("jobs_found", 0)
            summary_parts.append(f"LinkedIn Search: Found {job_count} AI/ML engineer positions in India")
        
        # Process Instagram data
        instagram_data = next((d for d in data_sources if "instagram" in str(d).lower()), None)
        if instagram_data:
            metrics = instagram_data.get("account_metrics", {})
            followers = metrics.get("followers", 0)
            engagement = metrics.get("engagement_rate", 0)
            summary_parts.append(f"Instagram Insights: {followers:,} followers with {engagement}% engagement rate")
        
        full_summary = "## Task Completion Summary\\n\\n" + "\\n".join(f"• {part}" for part in summary_parts)
        
        if not summary_parts:
            full_summary = "## Task Summary\\n\\nCompleted the requested analysis and data gathering operations."
        
        return {
            "summary": full_summary,
            "data_sources_processed": len(data_sources),
            "summary_length": len(full_summary),
            "generated_at": datetime.now().isoformat(),
            "key_insights": summary_parts
        }