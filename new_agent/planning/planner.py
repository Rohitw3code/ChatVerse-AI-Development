"""
Planning engine for the New Agent Framework
Analyzes queries and creates structured execution plans
"""

import re
import time
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta

from ..core.state import ExecutionPlan, TaskStep, ExecutionMode, AgentState
from ..agents.registry import agent_registry
from ..llm.openai_llm import get_llm_instance
from ..core.config import config


class PlanningEngine:
    """
    Intelligent planning engine that analyzes user queries and creates
    structured execution plans with appropriate agent assignments
    """
    
    def __init__(self):
        self.llm = get_llm_instance()
        self.agent_registry = agent_registry
    
    def _initialize_planning_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Initialize patterns for recognizing different types of tasks"""
        return {
            "linkedin_job_search": {
                "keywords": ["linkedin", "job", "jobs", "career", "position", "hiring"],
                "required_agents": ["LinkedInAgent"],
                "typical_tools": ["linkedin_job_search"],
                "estimated_duration": 60,
                "complexity": 2
            },
            "instagram_analytics": {
                "keywords": ["instagram", "insight", "analytics", "engagement", "followers"],
                "required_agents": ["InstagramAgent"],
                "typical_tools": ["instagram_insights"],
                "estimated_duration": 45,
                "complexity": 2
            },
            "email_operations": {
                "keywords": ["email", "gmail", "send", "mail"],
                "required_agents": ["GmailAgent"],
                "typical_tools": ["gmail_send"],
                "estimated_duration": 30,
                "complexity": 1
            },
            "content_summarization": {
                "keywords": ["summarize", "summary", "combine", "merge"],
                "required_agents": ["SummarizerAgent"],
                "typical_tools": ["content_summarizer"],
                "estimated_duration": 90,
                "complexity": 3
            },
            "research_tasks": {
                "keywords": ["research", "search", "find", "look", "investigate"],
                "required_agents": ["ResearchAgent"],
                "typical_tools": ["web_research"],
                "estimated_duration": 120,
                "complexity": 3
            },
            "multi_platform": {
                "keywords": ["and", "also", "both", "multiple"],
                "required_agents": ["OrchestratorAgent"],
                "typical_tools": ["data_processor"],
                "estimated_duration": 300,
                "complexity": 5
            }
        }
    
    def _initialize_dependency_rules(self) -> Dict[str, List[str]]:
        """Initialize rules for task dependencies"""
        return {
            # Tasks that must complete before summarization
            "content_summarizer": ["linkedin_job_search", "instagram_insights", "web_research"],
            # Tasks that must complete before email sending  
            "gmail_send": ["content_summarizer", "data_processor"],
            # General data processing dependencies
            "data_processor": ["linkedin_job_search", "instagram_insights", "web_research"]
        }
    
    def create_plan(self, query: str, user_id: str = "default") -> ExecutionPlan:
        """
        Create a structured execution plan from a user query using LLM reasoning
        """
        print(f"🧠 Planning Engine: Analyzing query with OpenAI - '{query}'")
        
        # Get available agents from registry
        available_agents = []
        for agent_name, agent_metadata in self.agent_registry.agents.items():
            available_agents.append({
                "name": agent_name,
                "description": agent_metadata.description,
                "capabilities": agent_metadata.capabilities
            })
        
        try:
            # Use LLM to create execution plan
            llm_plan = self.llm.create_execution_plan(query, available_agents)
            
            # Convert LLM plan to our ExecutionPlan format
            steps = []
            for llm_step in llm_plan.steps:
                step = TaskStep(
                    step_id=f"step_{llm_step.step_number}",
                    description=llm_step.description,
                    agent_name=llm_step.agent_name,
                    tool_calls=[],  # Will be populated during execution
                    dependencies=llm_step.dependencies,
                    status="pending",
                    estimated_time_seconds=llm_step.estimated_duration_seconds,
                    metadata={
                        "reasoning": llm_step.reasoning,
                        "confidence": getattr(llm_plan, 'confidence_score', 0.8)
                    }
                )
                steps.append(step)
            
            # Determine execution mode from LLM decision
            if llm_plan.execution_mode.lower() == "parallel":
                execution_mode = "parallel"
            elif llm_plan.execution_mode.lower() == "conditional":
                execution_mode = "conditional"
            else:
                execution_mode = "sequential"
            
            plan = ExecutionPlan(
                query=query,
                steps=steps,
                total_steps=len(steps),
                execution_mode=execution_mode,
                estimated_duration=llm_plan.estimated_total_duration_seconds,
                metadata={
                    "query_analysis": llm_plan.query_analysis,
                    "selected_agents": llm_plan.selected_agents,
                    "confidence_score": llm_plan.confidence_score,
                    "llm_usage": self.llm.get_usage_stats()
                }
            )
            
            print(f"✅ LLM Plan created: {len(steps)} steps, estimated {plan.estimated_duration}s")
            print(f"💡 Analysis: {llm_plan.query_analysis}")
            print(f"🎯 Confidence: {llm_plan.confidence_score:.2f}")
            
            return plan
            
        except Exception as e:
            print(f"❌ Error creating LLM plan: {e}")
            # Fallback to simple plan if LLM fails
            return self._create_fallback_plan(query, available_agents)
    
    def _create_fallback_plan(self, query: str, available_agents: List[Dict]) -> ExecutionPlan:
        """Create a basic fallback plan if LLM fails"""
        print("🔄 Creating fallback plan...")
        
        # Simple agent selection based on keywords
        query_lower = query.lower()
        selected_agent = "GenericAgent"
        
        # Basic keyword matching
        if "linkedin" in query_lower or "job" in query_lower:
            selected_agent = "LinkedInAgent"
        elif "instagram" in query_lower or "social" in query_lower:
            selected_agent = "InstagramAgent"
        elif "email" in query_lower or "send" in query_lower:
            selected_agent = "GmailAgent"
        elif "research" in query_lower or "analyze" in query_lower:
            selected_agent = "ResearchAgent"
        elif "summary" in query_lower or "summarize" in query_lower:
            selected_agent = "SummarizerAgent"
        
        step = TaskStep(
            step_id="fallback_step_1",
            description=f"Execute query using {selected_agent}",
            agent_name=selected_agent,
            tool_calls=[],
            dependencies=[],
            status="pending",
            estimated_time_seconds=120,
            metadata={"fallback": True}
        )
        
        return ExecutionPlan(
            query=query,
            steps=[step],
            total_steps=1,
            execution_mode="sequential",
            estimated_duration=120,
            metadata={"fallback_plan": True}
        )
    
    def _analyze_query(self, query: str) -> List[Dict[str, Any]]:
        """Analyze query to identify different task types"""
        query_lower = query.lower()
        identified_tasks = []
        
        # Check each planning pattern
        for task_type, pattern in self.planning_patterns.items():
            keyword_matches = sum(1 for keyword in pattern["keywords"] if keyword in query_lower)
            
            if keyword_matches > 0:
                confidence = min(1.0, keyword_matches / len(pattern["keywords"]) * 2)
                
                identified_tasks.append({
                    "type": task_type,
                    "confidence": confidence,
                    "pattern": pattern,
                    "keyword_matches": keyword_matches
                })
        
        # Sort by confidence
        identified_tasks.sort(key=lambda x: x["confidence"], reverse=True)
        
        # Handle complex multi-task queries
        if len(identified_tasks) > 1 and not any(t["type"] == "multi_platform" for t in identified_tasks):
            # Add orchestration task for complex workflows
            identified_tasks.append({
                "type": "multi_platform",
                "confidence": 0.8,
                "pattern": self.planning_patterns["multi_platform"],
                "keyword_matches": 0
            })
        
        return identified_tasks
    
    def _generate_steps(self, identified_tasks: List[Dict[str, Any]], query: str) -> List[TaskStep]:
        """Generate execution steps from identified tasks"""
        steps = []
        step_counter = 1
        
        # Extract specific parameters from query
        extracted_params = self._extract_query_parameters(query)
        
        for task_info in identified_tasks:
            task_type = task_info["type"]
            pattern = task_info["pattern"]
            
            # Skip multi-platform orchestration if it's the only task
            if task_type == "multi_platform" and len(identified_tasks) == 1:
                continue
            
            # Create step for this task
            step = TaskStep(
                description=self._generate_step_description(task_type, query, extracted_params),
                agent_name=pattern["required_agents"][0],  # Use primary agent
                execution_mode="sequential"
            )
            
            # Add tool calls for this step
            for tool_name in pattern["typical_tools"]:
                tool_params = self._generate_tool_parameters(tool_name, query, extracted_params)
                step.tool_calls.append(self._create_tool_call(tool_name, tool_params))
            
            # Set estimated time
            step.estimated_time_seconds = pattern["estimated_duration"]
            
            steps.append(step)
            step_counter += 1
        
        return steps
    
    def _extract_query_parameters(self, query: str) -> Dict[str, Any]:
        """Extract specific parameters from the query text"""
        params = {}
        
        # Extract email addresses
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, query, re.IGNORECASE)
        if emails:
            params["email_recipients"] = emails
        
        # Extract job roles/titles
        job_keywords = ["engineer", "developer", "scientist", "analyst", "manager", "designer"]
        for keyword in job_keywords:
            if keyword in query.lower():
                # Try to extract full job title
                pattern = rf'([A-Za-z/\s]*{keyword}[A-Za-z/\s]*)'
                matches = re.findall(pattern, query, re.IGNORECASE)
                if matches:
                    params["job_role"] = matches[0].strip()
                    break
        
        # Extract locations
        location_keywords = ["india", "bangalore", "mumbai", "delhi", "hyderabad", "pune", "chennai"]
        for location in location_keywords:
            if location in query.lower():
                params["location"] = location.title()
                break
        
        # Extract platforms
        platforms = ["linkedin", "instagram", "gmail", "youtube", "twitter"]
        params["platforms"] = [p for p in platforms if p in query.lower()]
        
        return params
    
    def _generate_step_description(self, task_type: str, query: str, params: Dict[str, Any]) -> str:
        """Generate a human-readable description for a step"""
        descriptions = {
            "linkedin_job_search": f"Search for {params.get('job_role', 'AI/ML engineer')} positions on LinkedIn in {params.get('location', 'India')}",
            "instagram_analytics": "Fetch Instagram account insights and analytics data",
            "email_operations": f"Send email to {params.get('email_recipients', ['specified recipient'])[0] if params.get('email_recipients') else 'recipient'}",
            "content_summarization": "Summarize and combine results from all data sources",
            "research_tasks": "Conduct research and gather relevant information",
            "multi_platform": "Coordinate multi-platform data gathering and processing"
        }
        
        return descriptions.get(task_type, f"Execute {task_type} task")
    
    def _generate_tool_parameters(self, tool_name: str, query: str, extracted_params: Dict[str, Any]) -> Dict[str, Any]:
        """Generate appropriate parameters for tool calls"""
        
        if tool_name == "linkedin_job_search":
            return {
                "role": extracted_params.get("job_role", "AI/ML Engineer"),
                "location": extracted_params.get("location", "India"),
                "experience_level": "mid-senior",
                "limit": 50
            }
        
        elif tool_name == "instagram_insights":
            return {
                "account_id": "target_account",
                "metrics": ["followers", "engagement", "reach", "impressions"],
                "time_period": "30_days"
            }
        
        elif tool_name == "gmail_send":
            recipients = extracted_params.get("email_recipients", ["rohit@gmail.com"])
            return {
                "to": recipients[0] if recipients else "rohit@gmail.com",
                "subject": "AI Agent Task Summary",
                "body": "Summary content will be generated from previous steps"
            }
        
        elif tool_name == "content_summarizer":
            return {
                "content_sources": ["linkedin_results", "instagram_insights"],
                "summary_type": "comprehensive",
                "max_length": 500
            }
        
        elif tool_name == "web_research":
            return {
                "query": query,
                "sources": ["web", "news"],
                "limit": 10
            }
        
        elif tool_name == "data_processor":
            return {
                "operation": "process",
                "options": {"detailed": True}
            }
        
        else:
            return {"query": query}
    
    def _create_tool_call(self, tool_name: str, parameters: Dict[str, Any]):
        """Create a tool call object"""
        from ..core.state import ToolCall
        return ToolCall(
            tool_name=tool_name,
            parameters=parameters
        )
    
    def _optimize_step_order(self, steps: List[TaskStep]) -> List[TaskStep]:
        """Optimize the order of steps based on dependencies"""
        
        # Create dependency map
        step_dependencies = {}
        
        for i, step in enumerate(steps):
            step_dependencies[i] = []
            
            # Check tool-based dependencies
            for tool_call in step.tool_calls:
                tool_name = tool_call.tool_name
                
                # If this tool has dependencies, find steps that provide them
                if tool_name in self.dependency_rules:
                    required_tools = self.dependency_rules[tool_name]
                    
                    for j, other_step in enumerate(steps):
                        if j != i:
                            for other_tool_call in other_step.tool_calls:
                                if other_tool_call.tool_name in required_tools:
                                    step_dependencies[i].append(j)
        
        # Topological sort to order steps
        ordered_indices = self._topological_sort(step_dependencies)
        
        # Reorder steps and update dependencies
        ordered_steps = []
        for idx in ordered_indices:
            step = steps[idx]
            # Update step dependencies with step IDs
            dependent_step_ids = [steps[dep_idx].step_id for dep_idx in step_dependencies[idx]]
            step.dependencies = dependent_step_ids
            ordered_steps.append(step)
        
        return ordered_steps
    
    def _topological_sort(self, dependencies: Dict[int, List[int]]) -> List[int]:
        """Perform topological sort on step dependencies"""
        # Simple topological sort implementation
        visited = set()
        result = []
        
        def visit(node):
            if node in visited:
                return
            visited.add(node)
            
            # Visit dependencies first
            for dep in dependencies.get(node, []):
                visit(dep)
            
            result.append(node)
        
        # Visit all nodes
        for node in dependencies.keys():
            visit(node)
        
        return result
    
    def _determine_execution_mode(self, steps: List[TaskStep]) -> ExecutionMode:
        """Determine the best execution mode for the plan"""
        
        # Check if steps have dependencies
        has_dependencies = any(step.dependencies for step in steps)
        
        # Check complexity
        total_complexity = sum(1 for step in steps)
        
        if has_dependencies or total_complexity > 3:
            return "sequential"  # Use sequential for complex workflows
        elif total_complexity <= 2:
            return "parallel"    # Simple tasks can run in parallel
        else:
            return "conditional" # Use conditional for moderate complexity
    
    def validate_plan(self, plan: ExecutionPlan) -> List[str]:
        """Validate a plan and return any issues found"""
        issues = []
        
        # Check if all agents exist
        for step in plan.steps:
            agent = agent_registry.get_agent(step.agent_name)
            if not agent:
                issues.append(f"Agent '{step.agent_name}' not found in registry")
            elif not agent.is_active:
                issues.append(f"Agent '{step.agent_name}' is not active")
        
        # Check circular dependencies
        if self._has_circular_dependencies(plan.steps):
            issues.append("Circular dependencies detected in plan")
        
        # Check tool availability
        from ..tools.dummy_tools import tool_registry
        for step in plan.steps:
            for tool_call in step.tool_calls:
                if not tool_registry.get_tool(tool_call.tool_name):
                    issues.append(f"Tool '{tool_call.tool_name}' not available")
        
        return issues
    
    def _has_circular_dependencies(self, steps: List[TaskStep]) -> bool:
        """Check for circular dependencies in the plan"""
        # Create adjacency list
        step_map = {step.step_id: step for step in steps}
        
        def has_cycle(step_id, visited, rec_stack):
            visited.add(step_id)
            rec_stack.add(step_id)
            
            step = step_map.get(step_id)
            if step:
                for dep_id in step.dependencies:
                    if dep_id not in visited:
                        if has_cycle(dep_id, visited, rec_stack):
                            return True
                    elif dep_id in rec_stack:
                        return True
            
            rec_stack.remove(step_id)
            return False
        
        visited = set()
        for step in steps:
            if step.step_id not in visited:
                if has_cycle(step.step_id, visited, set()):
                    return True
        
        return False
    
    def estimate_execution_time(self, plan: ExecutionPlan) -> int:
        """Estimate total execution time for a plan in seconds"""
        
        if plan.execution_mode == "parallel":
            # Parallel execution - time is max of all steps
            return max((getattr(step, 'estimated_time_seconds', 60) for step in plan.steps), default=60)
        
        elif plan.execution_mode == "sequential":
            # Sequential execution - sum of all steps
            return sum(getattr(step, 'estimated_time_seconds', 60) for step in plan.steps)
        
        else:  # conditional
            # Conditional execution - assume 70% of sequential time
            sequential_time = sum(getattr(step, 'estimated_time_seconds', 60) for step in plan.steps)
            return int(sequential_time * 0.7)


# Global planning engine instance
planning_engine = PlanningEngine()