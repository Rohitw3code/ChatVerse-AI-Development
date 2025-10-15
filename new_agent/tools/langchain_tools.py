"""
LangChain-compatible tool wrappers for dummy tools
Bridges dummy tools to LangChain tool interface
"""

from typing import Dict, Any, List, Optional, Type
from pydantic import BaseModel, Field
from langchain_core.tools import BaseTool

from new_agent.tools.dummy_tools import dummy_tool_registry


class LinkedInJobSearchInput(BaseModel):
    """Input schema for LinkedIn job search"""
    query: str = Field(description="Job search query (e.g., 'Python developer')")
    location: str = Field(default="Remote", description="Job location")
    experience_level: str = Field(default="mid", description="Experience level: entry, mid, senior")


class LinkedInJobSearchTool(BaseTool):
    """LinkedIn job search tool"""
    name: str = "linkedin_job_search"
    description: str = "Search for jobs on LinkedIn with specified criteria"
    args_schema: Type[BaseModel] = LinkedInJobSearchInput
    
    def _run(self, query: str, location: str = "Remote", experience_level: str = "mid") -> str:
        """Execute LinkedIn job search"""
        result = dummy_tool_registry.execute_tool(
            "linkedin_job_search",
            query=query,
            location=location,
            experience_level=experience_level
        )
        return str(result.result) if result.success else f"Error: {result.error}"


class InstagramInsightsInput(BaseModel):
    """Input schema for Instagram insights"""
    account: str = Field(description="Instagram account username")
    metric: str = Field(default="engagement", description="Metric to analyze")


class InstagramInsightsTool(BaseTool):
    """Instagram insights analysis tool"""
    name: str = "instagram_insights"
    description: str = "Get insights and analytics for Instagram accounts"
    args_schema: Type[BaseModel] = InstagramInsightsInput
    
    def _run(self, account: str, metric: str = "engagement") -> str:
        """Execute Instagram insights analysis"""
        result = dummy_tool_registry.execute_tool(
            "instagram_insights",
            account=account,
            metric=metric
        )
        return str(result.result) if result.success else f"Error: {result.error}"


class GmailSendInput(BaseModel):
    """Input schema for Gmail send"""
    to: str = Field(description="Recipient email address")
    subject: str = Field(description="Email subject")
    body: str = Field(description="Email body content")


class GmailSendTool(BaseTool):
    """Gmail email sending tool"""
    name: str = "gmail_send"
    description: str = "Send emails via Gmail"
    args_schema: Type[BaseModel] = GmailSendInput
    
    def _run(self, to: str, subject: str, body: str) -> str:
        """Execute Gmail send"""
        result = dummy_tool_registry.execute_tool(
            "gmail_send",
            to=to,
            subject=subject,
            body=body
        )
        return str(result.result) if result.success else f"Error: {result.error}"


class ContentSummarizerInput(BaseModel):
    """Input schema for content summarizer"""
    content: str = Field(description="Content to summarize")
    max_length: int = Field(default=200, description="Maximum summary length")


class ContentSummarizerTool(BaseTool):
    """Content summarization tool"""
    name: str = "content_summarizer"
    description: str = "Summarize long content into concise summaries"
    args_schema: Type[BaseModel] = ContentSummarizerInput
    
    def _run(self, content: str, max_length: int = 200) -> str:
        """Execute content summarization"""
        result = dummy_tool_registry.execute_tool(
            "content_summarizer",
            content=content,
            max_length=max_length
        )
        return str(result.result) if result.success else f"Error: {result.error}"


class WebResearchInput(BaseModel):
    """Input schema for web research"""
    topic: str = Field(description="Research topic or query")
    depth: str = Field(default="medium", description="Research depth: shallow, medium, deep")


class WebResearchTool(BaseTool):
    """Web research tool"""
    name: str = "web_research"
    description: str = "Research topics on the web and gather information"
    args_schema: Type[BaseModel] = WebResearchInput
    
    def _run(self, topic: str, depth: str = "medium") -> str:
        """Execute web research"""
        result = dummy_tool_registry.execute_tool(
            "web_research",
            topic=topic,
            depth=depth
        )
        return str(result.result) if result.success else f"Error: {result.error}"


class DataProcessorInput(BaseModel):
    """Input schema for data processor"""
    data: str = Field(description="Data to process (JSON string or text)")
    operation: str = Field(default="analyze", description="Processing operation")


class DataProcessorTool(BaseTool):
    """Data processing tool"""
    name: str = "data_processor"
    description: str = "Process and analyze various types of data"
    args_schema: Type[BaseModel] = DataProcessorInput
    
    def _run(self, data: str, operation: str = "analyze") -> str:
        """Execute data processing"""
        result = dummy_tool_registry.execute_tool(
            "data_processor",
            data=data,
            operation=operation
        )
        return str(result.result) if result.success else f"Error: {result.error}"


class LangChainToolRegistry:
    """Registry of LangChain-compatible tools"""
    
    def __init__(self):
        self.tools = {
            "linkedin_search": LinkedInJobSearchTool(),
            "linkedin_profile_analysis": LinkedInJobSearchTool(),  # Alias
            "job_analyzer": LinkedInJobSearchTool(),  # Related tool
            
            "instagram_insights": InstagramInsightsTool(),
            "instagram_analytics": InstagramInsightsTool(),  # Alias
            "content_analyzer": ContentSummarizerTool(),  # Related tool
            
            "gmail_send": GmailSendTool(),
            "gmail_compose": GmailSendTool(),  # Alias
            "email_formatter": GmailSendTool(),  # Related tool
            
            "web_search": WebResearchTool(),
            "data_analyzer": DataProcessorTool(),
            "fact_checker": WebResearchTool(),  # Related tool
            
            "summarizer": ContentSummarizerTool(),
            "report_generator": ContentSummarizerTool(),  # Related tool
            "content_synthesizer": ContentSummarizerTool(),  # Related tool
        }
    
    def get_tool(self, tool_name: str) -> Optional[BaseTool]:
        """Get a tool by name"""
        return self.tools.get(tool_name)
    
    def list_tools(self) -> List[str]:
        """List all available tool names"""
        return list(self.tools.keys())
    
    def get_all_tools(self) -> List[BaseTool]:
        """Get all tools as a list"""
        return list(self.tools.values())


# Global instance
langchain_tool_registry = LangChainToolRegistry()