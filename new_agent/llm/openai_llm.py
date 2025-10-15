"""
OpenAI LLM integration for the New Agent Framework
Uses GPT-4o Mini for all agentic operations with token and cost tracking
"""

import openai
import time
import json
from typing import List, Dict, Any, Generator, Optional, Union
from datetime import datetime
from pydantic import BaseModel, Field
import tiktoken

from ..core.config import config


class TokenUsage(BaseModel):
    """Token usage tracking"""
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    estimated_cost: float = 0.0


class LLMResponse(BaseModel):
    """Standardized LLM response with tracking"""
    content: str
    usage: TokenUsage
    model: str
    response_time_ms: int
    timestamp: datetime = Field(default_factory=datetime.now)


class PlanStep(BaseModel):
    """Individual step in execution plan"""
    step_number: int
    description: str
    agent_name: str
    reasoning: str
    estimated_duration_seconds: int = 60
    dependencies: List[int] = Field(default_factory=list)


class ExecutionPlan(BaseModel):
    """Complete execution plan from LLM"""
    query_analysis: str
    total_steps: int
    execution_mode: str = Field(description="sequential, parallel, or conditional")
    estimated_total_duration_seconds: int
    steps: List[PlanStep]
    selected_agents: List[str]
    confidence_score: float = Field(ge=0.0, le=1.0)


class AgentAction(BaseModel):
    """Agent's decision on what action to take"""
    action_type: str = Field(description="tool_call, delegate, complete, or error")
    tool_name: Optional[str] = None
    tool_parameters: Dict[str, Any] = Field(default_factory=dict)
    reasoning: str
    next_agent: Optional[str] = None
    completion_message: Optional[str] = None
    confidence: float = Field(ge=0.0, le=1.0)


class RouterDecision(BaseModel):
    """Routing decision between agents"""
    selected_agent: str
    reasoning: str
    confidence: float = Field(ge=0.0, le=1.0)
    alternative_agents: List[str] = Field(default_factory=list)


class SummaryContent(BaseModel):
    """Structured summary content"""
    title: str
    key_findings: List[str]
    detailed_summary: str
    data_sources: List[str]
    recommendations: List[str] = Field(default_factory=list)
    confidence_score: float = Field(ge=0.0, le=1.0)


class OpenAILLM:
    """
    OpenAI LLM integration with GPT-4o Mini for all agentic operations
    Tracks token usage and costs for complete transparency
    """
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or config.llm.api_key
        if not self.api_key:
            raise ValueError("OpenAI API key is required. Set it in config or pass as parameter.")
        
        openai.api_key = self.api_key
        self.model = "gpt-4o-mini"  # GPT-4o Mini for cost efficiency
        self.encoding = tiktoken.encoding_for_model("gpt-4o-mini")
        
        # Pricing for GPT-4o Mini (as of 2024)
        self.pricing = {
            "prompt_tokens": 0.000150 / 1000,    # $0.150 per 1K prompt tokens
            "completion_tokens": 0.000600 / 1000  # $0.600 per 1K completion tokens
        }
        
        # Total usage tracking
        self.total_usage = TokenUsage()
        self.session_usage = {}
        
    def _count_tokens(self, text: str) -> int:
        """Count tokens in text"""
        return len(self.encoding.encode(text))
    
    def _calculate_cost(self, usage: TokenUsage) -> float:
        """Calculate cost based on token usage"""
        prompt_cost = usage.prompt_tokens * self.pricing["prompt_tokens"]
        completion_cost = usage.completion_tokens * self.pricing["completion_tokens"]
        return prompt_cost + completion_cost
    
    def _make_llm_call(
        self, 
        messages: List[Dict[str, str]], 
        response_format: Optional[Dict] = None,
        temperature: float = 0.1
    ) -> LLMResponse:
        """Make OpenAI API call with tracking"""
        
        start_time = time.time()
        
        try:
            # Prepare API call parameters
            api_params = {
                "model": self.model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": 4000
            }
            
            # Add response format if specified (for structured output)
            if response_format:
                api_params["response_format"] = response_format
            
            # Make API call
            response = openai.chat.completions.create(**api_params)
            
            # Extract usage information
            usage = TokenUsage(
                prompt_tokens=response.usage.prompt_tokens,
                completion_tokens=response.usage.completion_tokens,
                total_tokens=response.usage.total_tokens,
                estimated_cost=self._calculate_cost(TokenUsage(
                    prompt_tokens=response.usage.prompt_tokens,
                    completion_tokens=response.usage.completion_tokens,
                    total_tokens=response.usage.total_tokens
                ))
            )
            
            # Update totals
            self.total_usage.prompt_tokens += usage.prompt_tokens
            self.total_usage.completion_tokens += usage.completion_tokens
            self.total_usage.total_tokens += usage.total_tokens
            self.total_usage.estimated_cost += usage.estimated_cost
            
            response_time = int((time.time() - start_time) * 1000)
            
            return LLMResponse(
                content=response.choices[0].message.content,
                usage=usage,
                model=self.model,
                response_time_ms=response_time
            )
            
        except Exception as e:
            raise Exception(f"OpenAI API call failed: {str(e)}")
    
    def create_execution_plan(
        self, 
        query: str, 
        available_agents: List[Dict[str, Any]]
    ) -> ExecutionPlan:
        """Create execution plan using LLM reasoning"""
        
        # Format available agents for LLM context
        agents_context = []
        for agent in available_agents:
            agent_info = f"- {agent['name']}: {agent['description']}"
            if agent.get('capabilities'):
                agent_info += f" (Capabilities: {', '.join(agent['capabilities'])})"
            agents_context.append(agent_info)
        
        system_prompt = f"""You are an intelligent task planning AI. Analyze the user's query and create a structured execution plan using only the available agents.

Available Agents:
{chr(10).join(agents_context)}

Your task is to:
1. Analyze the query to understand what needs to be done
2. Select only the relevant agents from the available list
3. Create a step-by-step plan that achieves the user's goal
4. Determine dependencies between steps
5. Estimate timing and execution mode

Rules:
- Only use agents from the provided list
- Be specific about what each step accomplishes
- Consider dependencies (e.g., summarization needs data first)
- Choose appropriate execution mode (sequential for dependencies, parallel for independent tasks)
- Provide realistic time estimates

Return a structured JSON response with the execution plan."""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Create an execution plan for: {query}"}
        ]
        
        response = self._make_llm_call(messages, temperature=0.2)
        
        try:
            # Parse JSON response into Pydantic model
            plan_data = json.loads(response.content)
            
            # Create ExecutionPlan object
            execution_plan = ExecutionPlan(**plan_data)
            
            return execution_plan
            
        except Exception as e:
            # Fallback: create basic plan if JSON parsing fails
            print(f"Warning: Could not parse LLM plan response, creating fallback plan: {e}")
            return self._create_fallback_plan(query, available_agents)
    
    def make_agent_decision(
        self, 
        agent_name: str, 
        agent_description: str,
        current_task: str,
        available_tools: List[str],
        conversation_history: List[str],
        tool_results: Dict[str, Any] = None
    ) -> AgentAction:
        """Agent makes decision on what action to take"""
        
        tools_context = "\n".join([f"- {tool}" for tool in available_tools])
        history_context = "\n".join(conversation_history[-5:]) if conversation_history else "No previous context"
        results_context = json.dumps(tool_results, indent=2) if tool_results else "No previous tool results"
        
        system_prompt = f"""You are {agent_name}, a specialized AI agent.

Your role: {agent_description}

Current task: {current_task}

Available tools:
{tools_context}

Recent conversation history:
{history_context}

Previous tool results:
{results_context}

Decide what action to take next. You can:
1. Call a tool with specific parameters
2. Delegate to another agent if the task is outside your expertise
3. Complete the task if you have enough information
4. Report an error if the task cannot be accomplished

Be specific about your reasoning and parameters. Always include confidence score."""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": "What is your next action?"}
        ]
        
        response = self._make_llm_call(messages, temperature=0.1)
        
        try:
            decision_data = json.loads(response.content)
            return AgentAction(**decision_data)
        except Exception as e:
            # Fallback decision
            return AgentAction(
                action_type="error",
                reasoning=f"Failed to parse agent decision: {e}",
                confidence=0.1
            )
    
    def route_to_agent(
        self,
        current_step: str,
        available_agents: List[Dict[str, str]],
        context: str = ""
    ) -> RouterDecision:
        """Decide which agent should handle the current step"""
        
        agents_list = "\n".join([
            f"- {agent['name']}: {agent['description']}" 
            for agent in available_agents
        ])
        
        system_prompt = f"""You are a routing AI that decides which agent should handle specific tasks.

Available agents:
{agents_list}

Current step to route: {current_step}

Additional context: {context}

Select the most appropriate agent for this step. Consider:
1. Agent specialization and capabilities
2. Task requirements
3. Expected outcomes

Provide reasoning for your choice and confidence score."""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": "Which agent should handle this step?"}
        ]
        
        response = self._make_llm_call(messages, temperature=0.1)
        
        try:
            router_data = json.loads(response.content)
            return RouterDecision(**router_data)
        except Exception as e:
            # Fallback to first available agent
            return RouterDecision(
                selected_agent=available_agents[0]["name"] if available_agents else "GenericAgent",
                reasoning=f"Fallback selection due to parsing error: {e}",
                confidence=0.3
            )
    
    def generate_summary(
        self,
        data_sources: List[Dict[str, Any]],
        summary_type: str = "comprehensive",
        context: str = ""
    ) -> SummaryContent:
        """Generate intelligent summary from multiple data sources"""
        
        sources_text = []
        source_names = []
        
        for i, source in enumerate(data_sources, 1):
            source_name = source.get('source_name', f'Source {i}')
            source_names.append(source_name)
            
            # Format source data for LLM
            if isinstance(source.get('data'), dict):
                formatted_data = json.dumps(source['data'], indent=2)
            else:
                formatted_data = str(source.get('data', 'No data available'))
            
            sources_text.append(f"=== {source_name} ===\n{formatted_data}\n")
        
        system_prompt = f"""You are an expert data analyst and report writer. Create a {summary_type} summary from the provided data sources.

Context: {context}

Data Sources:
{chr(10).join(sources_text)}

Create a structured summary that:
1. Provides a clear title
2. Identifies key findings from each source
3. Creates a detailed narrative summary
4. Lists all data sources used
5. Provides actionable recommendations if applicable
6. Includes a confidence score for the analysis

Focus on accuracy, clarity, and actionable insights."""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Create a {summary_type} summary of the provided data."}
        ]
        
        response = self._make_llm_call(messages, temperature=0.2)
        
        try:
            summary_data = json.loads(response.content)
            return SummaryContent(**summary_data)
        except Exception as e:
            # Fallback summary
            return SummaryContent(
                title="Data Summary",
                key_findings=[f"Processed {len(data_sources)} data sources"],
                detailed_summary=response.content,  # Use raw LLM output as fallback
                data_sources=source_names,
                confidence_score=0.7
            )
    
    def determine_tool_parameters(
        self,
        tool_name: str,
        tool_description: str,
        task_context: str,
        user_query: str
    ) -> Dict[str, Any]:
        """Intelligently determine parameters for tool calls"""
        
        system_prompt = f"""You are an intelligent parameter generator. Given a tool and context, determine the appropriate parameters to call the tool.

Tool: {tool_name}
Description: {tool_description}
Task context: {task_context}
Original user query: {user_query}

Analyze the context and query to extract relevant parameters for this tool. Be specific and accurate.
Return only a JSON object with the parameters, no other text."""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": "Generate the tool parameters as JSON."}
        ]
        
        response = self._make_llm_call(messages, temperature=0.1)
        
        try:
            return json.loads(response.content)
        except Exception as e:
            print(f"Warning: Could not parse tool parameters: {e}")
            return {"query": user_query, "context": task_context}
    
    def _create_fallback_plan(self, query: str, available_agents: List[Dict]) -> ExecutionPlan:
        """Create a basic fallback plan if LLM parsing fails"""
        
        # Simple keyword-based agent selection
        query_lower = query.lower()
        selected_agents = []
        
        for agent in available_agents:
            agent_keywords = agent.get('capabilities', []) + [agent['name'].lower()]
            if any(keyword in query_lower for keyword in agent_keywords):
                selected_agents.append(agent['name'])
        
        if not selected_agents and available_agents:
            selected_agents = [available_agents[0]['name']]
        
        # Create basic steps
        steps = []
        for i, agent_name in enumerate(selected_agents):
            steps.append(PlanStep(
                step_number=i + 1,
                description=f"Execute task using {agent_name}",
                agent_name=agent_name,
                reasoning=f"Fallback assignment to {agent_name}",
                estimated_duration_seconds=60
            ))
        
        return ExecutionPlan(
            query_analysis=f"Fallback analysis for: {query}",
            total_steps=len(steps),
            execution_mode="sequential",
            estimated_total_duration_seconds=len(steps) * 60,
            steps=steps,
            selected_agents=selected_agents,
            confidence_score=0.5
        )
    
    def get_usage_stats(self, session_id: str = None) -> Dict[str, Any]:
        """Get token usage and cost statistics"""
        
        stats = {
            "total_usage": self.total_usage.dict(),
            "model": self.model,
            "pricing": self.pricing,
            "timestamp": datetime.now().isoformat()
        }
        
        if session_id and session_id in self.session_usage:
            stats["session_usage"] = self.session_usage[session_id]
        
        return stats
    
    def reset_usage_tracking(self):
        """Reset usage tracking (for testing or new sessions)"""
        self.total_usage = TokenUsage()
        self.session_usage = {}


# Global LLM instance
def get_llm_instance() -> OpenAILLM:
    """Get configured LLM instance"""
    try:
        return OpenAILLM()
    except ValueError as e:
        print(f"Error initializing OpenAI LLM: {e}")
        print("Please set your OpenAI API key in the configuration.")
        raise