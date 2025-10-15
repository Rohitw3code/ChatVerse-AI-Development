"""
Dummy tool implementations for local development and testing
"""

import time
import random
import json
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass

from ..core.state import ToolCall, TaskStatus
from ..llm.dummy_llm import AgentResponseGenerator


@dataclass
class ToolResult:
    """Result of a tool execution"""
    success: bool
    result: Any
    error: Optional[str] = None
    execution_time_ms: int = 0
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class BaseDummyTool:
    """Base class for all dummy tools"""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.call_count = 0
        self.total_execution_time = 0
    
    def execute(self, **params) -> ToolResult:
        """Execute the tool with given parameters"""
        start_time = time.time()
        self.call_count += 1
        
        try:
            # Simulate processing time
            processing_time = self._get_processing_time()
            time.sleep(processing_time)
            
            # Execute tool logic
            result = self._execute_impl(**params)
            
            # Calculate execution time
            execution_time_ms = int((time.time() - start_time) * 1000)
            self.total_execution_time += execution_time_ms
            
            return ToolResult(
                success=True,
                result=result,
                execution_time_ms=execution_time_ms,
                metadata={
                    "tool_name": self.name,
                    "call_count": self.call_count,
                    "parameters": params,
                    "simulated": True
                }
            )
            
        except Exception as e:
            execution_time_ms = int((time.time() - start_time) * 1000)
            return ToolResult(
                success=False,
                result=None,
                error=str(e),
                execution_time_ms=execution_time_ms,
                metadata={
                    "tool_name": self.name,
                    "error_type": type(e).__name__,
                    "parameters": params
                }
            )
    
    def _execute_impl(self, **params) -> Any:
        """Override this method in subclasses"""
        raise NotImplementedError("Subclasses must implement _execute_impl")
    
    def _get_processing_time(self) -> float:
        """Get simulated processing time in seconds"""
        return random.uniform(0.5, 2.0)  # 500ms to 2s
    
    def get_stats(self) -> Dict[str, Any]:
        """Get tool usage statistics"""
        avg_time = self.total_execution_time / self.call_count if self.call_count > 0 else 0
        return {
            "name": self.name,
            "call_count": self.call_count,
            "total_execution_time_ms": self.total_execution_time,
            "average_execution_time_ms": avg_time
        }


class DummyLinkedInSearchTool(BaseDummyTool):
    """Dummy LinkedIn job search tool"""
    
    def __init__(self):
        super().__init__(
            name="linkedin_job_search",
            description="Search for job postings on LinkedIn with specified criteria"
        )
    
    def _execute_impl(self, **params) -> Dict[str, Any]:
        """Simulate LinkedIn job search"""
        role = params.get("role", "Software Engineer")
        location = params.get("location", "India")
        experience_level = params.get("experience_level", "mid-senior")
        limit = params.get("limit", 25)
        
        # Generate realistic dummy data
        result = AgentResponseGenerator.generate_linkedin_response(f"{role} jobs in {location}")
        
        # Adjust based on parameters
        result["search_parameters"] = {
            "role": role,
            "location": location,
            "experience_level": experience_level,
            "limit": limit
        }
        
        result["jobs_found"] = min(result["jobs_found"], limit)
        
        return result
    
    def _get_processing_time(self) -> float:
        return random.uniform(1.0, 3.5)  # LinkedIn searches take longer


class DummyInstagramInsightsTool(BaseDummyTool):
    """Dummy Instagram insights and analytics tool"""
    
    def __init__(self):
        super().__init__(
            name="instagram_insights",
            description="Fetch Instagram account insights, analytics, and performance metrics"
        )
    
    def _execute_impl(self, **params) -> Dict[str, Any]:
        """Simulate Instagram insights retrieval"""
        account_id = params.get("account_id", "dummy_account")
        metrics = params.get("metrics", ["followers", "engagement", "reach"])
        time_period = params.get("time_period", "30_days")
        
        result = AgentResponseGenerator.generate_instagram_response("instagram insights")
        
        # Add parameter context
        result["request_parameters"] = {
            "account_id": account_id,
            "requested_metrics": metrics,
            "time_period": time_period
        }
        
        return result
    
    def _get_processing_time(self) -> float:
        return random.uniform(0.8, 2.2)


class DummyGmailSendTool(BaseDummyTool):
    """Dummy Gmail email sending tool"""
    
    def __init__(self):
        super().__init__(
            name="gmail_send",
            description="Send emails via Gmail with specified recipient, subject, and content"
        )
    
    def _execute_impl(self, **params) -> Dict[str, Any]:
        """Simulate email sending"""
        to = params.get("to", "recipient@example.com")
        subject = params.get("subject", "No Subject")
        body = params.get("body", "")
        
        # Validate required parameters
        if not to or not body:
            raise ValueError("Both 'to' and 'body' parameters are required")
        
        result = AgentResponseGenerator.generate_email_response(to, subject, body)
        
        return result
    
    def _get_processing_time(self) -> float:
        return random.uniform(0.3, 1.0)  # Email sending is relatively fast


class DummySummarizerTool(BaseDummyTool):
    """Dummy content summarization tool"""
    
    def __init__(self):
        super().__init__(
            name="content_summarizer", 
            description="Summarize and combine content from multiple data sources"
        )
    
    def _execute_impl(self, **params) -> Dict[str, Any]:
        """Simulate content summarization"""
        content_sources = params.get("content_sources", [])
        summary_type = params.get("summary_type", "comprehensive")
        max_length = params.get("max_length", 500)
        
        # Convert source names to dummy data
        dummy_sources = []
        for source in content_sources:
            if "linkedin" in str(source).lower():
                dummy_sources.append(AgentResponseGenerator.generate_linkedin_response("dummy"))
            elif "instagram" in str(source).lower():
                dummy_sources.append(AgentResponseGenerator.generate_instagram_response("dummy"))
            else:
                dummy_sources.append({"source": source, "data": "processed"})
        
        result = AgentResponseGenerator.generate_summary_response(dummy_sources)
        
        # Add processing parameters
        result["processing_parameters"] = {
            "summary_type": summary_type,
            "max_length": max_length,
            "sources_count": len(content_sources)
        }
        
        return result
    
    def _get_processing_time(self) -> float:
        return random.uniform(1.5, 4.0)  # Summarization takes more processing


class DummyResearchTool(BaseDummyTool):
    """Dummy research and web search tool"""
    
    def __init__(self):
        super().__init__(
            name="web_research",
            description="Conduct research and gather information from web sources"
        )
    
    def _execute_impl(self, **params) -> Dict[str, Any]:
        """Simulate web research"""
        query = params.get("query", "")
        sources = params.get("sources", ["web", "news", "academic"])
        limit = params.get("limit", 10)
        
        # Generate dummy research results
        results = []
        for i in range(min(limit, random.randint(3, 8))):
            results.append({
                "title": f"Research Result {i+1}: {query}",
                "url": f"https://example.com/result-{i+1}",
                "snippet": f"Relevant information about {query} from source {i+1}",
                "source_type": random.choice(sources),
                "relevance_score": round(random.uniform(0.6, 0.98), 2),
                "published_date": (datetime.now() - timedelta(days=random.randint(1, 30))).isoformat()
            })
        
        return {
            "query": query,
            "results": results,
            "total_found": len(results),
            "search_time_ms": random.randint(200, 1500),
            "sources_searched": sources,
            "generated_at": datetime.now().isoformat()
        }
    
    def _get_processing_time(self) -> float:
        return random.uniform(1.0, 3.0)


class DummyDataProcessorTool(BaseDummyTool):
    """Generic dummy data processing tool"""
    
    def __init__(self):
        super().__init__(
            name="data_processor",
            description="Process, transform, and analyze various types of data"
        )
    
    def _execute_impl(self, **params) -> Dict[str, Any]:
        """Simulate data processing"""
        data = params.get("data", {})
        operation = params.get("operation", "process")
        options = params.get("options", {})
        
        # Simulate different processing operations
        if operation == "analyze":
            result = {
                "analysis": {
                    "data_points": random.randint(50, 500),
                    "patterns_found": random.randint(3, 12),
                    "anomalies": random.randint(0, 5),
                    "confidence": round(random.uniform(0.75, 0.95), 2)
                }
            }
        elif operation == "transform":
            result = {
                "transformation": {
                    "input_format": "raw",
                    "output_format": "structured",
                    "records_processed": random.randint(100, 1000),
                    "success_rate": round(random.uniform(0.90, 0.99), 2)
                }
            }
        else:  # default process
            result = {
                "processing": {
                    "status": "completed",
                    "items_processed": random.randint(10, 100),
                    "processing_time_ms": random.randint(500, 5000),
                    "output_size": random.randint(1000, 50000)
                }
            }
        
        result.update({
            "operation": operation,
            "options_applied": options,
            "processed_at": datetime.now().isoformat()
        })
        
        return result
    
    def _get_processing_time(self) -> float:
        return random.uniform(0.5, 2.5)


# Tool Registry
class DummyToolRegistry:
    """Registry for all available dummy tools"""
    
    def __init__(self):
        self.tools = {
            "linkedin_job_search": DummyLinkedInSearchTool(),
            "instagram_insights": DummyInstagramInsightsTool(),
            "gmail_send": DummyGmailSendTool(),
            "content_summarizer": DummySummarizerTool(),
            "web_research": DummyResearchTool(),
            "data_processor": DummyDataProcessorTool()
        }
    
    def get_tool(self, tool_name: str) -> Optional[BaseDummyTool]:
        """Get a tool by name"""
        return self.tools.get(tool_name)
    
    def list_tools(self) -> List[str]:
        """List all available tool names"""
        return list(self.tools.keys())
    
    def get_tool_descriptions(self) -> Dict[str, str]:
        """Get descriptions of all tools"""
        return {name: tool.description for name, tool in self.tools.items()}
    
    def execute_tool(self, tool_name: str, **params) -> ToolResult:
        """Execute a tool by name with parameters"""
        tool = self.get_tool(tool_name)
        if not tool:
            return ToolResult(
                success=False,
                result=None,
                error=f"Tool '{tool_name}' not found",
                metadata={"available_tools": self.list_tools()}
            )
        
        return tool.execute(**params)
    
    def get_all_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get usage statistics for all tools"""
        return {name: tool.get_stats() for name, tool in self.tools.items()}


# Global tool registry instances
tool_registry = DummyToolRegistry()
dummy_tool_registry = tool_registry  # Alias for enhanced framework