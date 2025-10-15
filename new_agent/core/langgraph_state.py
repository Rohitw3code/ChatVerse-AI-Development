"""
LangGraph State Management for Enhanced Agent Framework
Provides proper state management with streaming events and tool call tracking
"""

from typing import Annotated, Dict, Any, List, Optional, TypedDict
from typing_extensions import NotRequired
from dataclasses import dataclass, field
from datetime import datetime
import uuid

from langgraph.graph.message import AnyMessage, add_messages
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, ToolMessage
from langchain_core.tools import BaseTool


class AgentState(TypedDict):
    """LangGraph State for the Enhanced Agent Framework"""
    
    # Core query and execution
    query: str
    user_id: str
    session_id: str
    
    # Message history for LangGraph
    messages: Annotated[List[AnyMessage], add_messages]
    
    # Current execution state
    current_step: int
    total_steps: int
    current_agent: Optional[str]
    
    # Agent and tool tracking
    available_agents: List[str]
    active_tools: List[str]
    tool_results: Dict[str, Any]
    
    # Execution plan and results
    execution_plan: Optional[Dict[str, Any]]
    step_results: List[Dict[str, Any]]
    final_output: Optional[Dict[str, Any]]
    
    # Cost and token tracking
    total_tokens: int
    total_cost: float
    llm_calls: int
    
    # Status and metadata
    status: str  # pending, in_progress, completed, failed
    error: Optional[str]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    metadata: Dict[str, Any]


@dataclass
class StreamingEvent:
    """Enhanced streaming event with LangGraph compatibility"""
    event_type: str  # "token", "tool_start", "tool_end", "agent_start", "agent_end", "error"
    content: str
    timestamp: datetime = field(default_factory=datetime.now)
    
    # Agent information
    agent_name: Optional[str] = None
    step_number: Optional[int] = None
    
    # Tool information
    tool_name: Optional[str] = None
    tool_input: Optional[Dict[str, Any]] = None
    tool_output: Optional[Any] = None
    
    # Token streaming
    token: Optional[str] = None
    is_complete: bool = False
    
    # Cost tracking
    tokens_used: int = 0
    cost_incurred: float = 0.0
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)


class ToolCallEvent:
    """Represents a tool call with streaming support"""
    
    def __init__(self, tool_name: str, tool_input: Dict[str, Any]):
        self.tool_name = tool_name
        self.tool_input = tool_input
        self.call_id = str(uuid.uuid4())
        self.started_at = datetime.now()
        self.completed_at: Optional[datetime] = None
        self.result: Optional[Any] = None
        self.error: Optional[str] = None
        self.status = "started"
    
    def complete(self, result: Any):
        """Mark tool call as completed"""
        self.result = result
        self.completed_at = datetime.now()
        self.status = "completed"
    
    def fail(self, error: str):
        """Mark tool call as failed"""
        self.error = error
        self.completed_at = datetime.now()
        self.status = "failed"
    
    def get_duration(self) -> float:
        """Get execution duration in seconds"""
        if self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return (datetime.now() - self.started_at).total_seconds()


def create_initial_state(query: str, user_id: str = "default") -> AgentState:
    """Create initial LangGraph state"""
    return AgentState(
        query=query,
        user_id=user_id,
        session_id=str(uuid.uuid4()),
        messages=[HumanMessage(content=query)],
        current_step=0,
        total_steps=0,
        current_agent=None,
        available_agents=[],
        active_tools=[],
        tool_results={},
        execution_plan=None,
        step_results=[],
        final_output=None,
        total_tokens=0,
        total_cost=0.0,
        llm_calls=0,
        status="pending",
        error=None,
        started_at=datetime.now(),
        completed_at=None,
        metadata={}
    )


def update_state_with_message(state: AgentState, message: BaseMessage) -> AgentState:
    """Update state with new message"""
    state["messages"].append(message)
    return state


def update_state_with_tool_result(
    state: AgentState, 
    tool_name: str, 
    result: Any,
    tokens_used: int = 0,
    cost: float = 0.0
) -> AgentState:
    """Update state with tool execution result"""
    state["tool_results"][tool_name] = result
    state["total_tokens"] += tokens_used
    state["total_cost"] += cost
    return state


def update_state_with_llm_usage(
    state: AgentState,
    tokens_used: int,
    cost: float
) -> AgentState:
    """Update state with LLM usage statistics"""
    state["total_tokens"] += tokens_used
    state["total_cost"] += cost
    state["llm_calls"] += 1
    return state


def finalize_state(state: AgentState, final_output: Dict[str, Any]) -> AgentState:
    """Mark state as completed with final output"""
    state["final_output"] = final_output
    state["status"] = "completed"
    state["completed_at"] = datetime.now()
    return state


def mark_state_failed(state: AgentState, error: str) -> AgentState:
    """Mark state as failed with error"""
    state["error"] = error
    state["status"] = "failed"
    state["completed_at"] = datetime.now()
    return state


class TokenStreamCollector:
    """Collects token-by-token streaming from LLM calls"""
    
    def __init__(self):
        self.tokens: List[str] = []
        self.current_content = ""
        self.is_complete = False
    
    def add_token(self, token: str) -> StreamingEvent:
        """Add a token and return streaming event"""
        self.tokens.append(token)
        self.current_content += token
        
        return StreamingEvent(
            event_type="token",
            content=self.current_content,
            token=token,
            is_complete=False
        )
    
    def complete(self) -> StreamingEvent:
        """Mark streaming as complete"""
        self.is_complete = True
        return StreamingEvent(
            event_type="token",
            content=self.current_content,
            token="",
            is_complete=True
        )
    
    def get_full_content(self) -> str:
        """Get complete content"""
        return self.current_content


class LangGraphEventProcessor:
    """Processes LangGraph events and converts to our streaming format"""
    
    def __init__(self):
        self.active_tool_calls: Dict[str, ToolCallEvent] = {}
        self.token_collector = TokenStreamCollector()
    
    def process_event(self, event: Dict[str, Any]) -> Optional[StreamingEvent]:
        """Process a LangGraph event and return streaming event"""
        
        event_type = event.get("event", "")
        
        # Handle different event types
        if event_type == "on_chat_model_start":
            return StreamingEvent(
                event_type="agent_start",
                content="🧠 AI Agent starting to think...",
                agent_name=event.get("name", "Agent"),
                metadata=event.get("data", {})
            )
        
        elif event_type == "on_chat_model_stream":
            # Token-by-token streaming
            chunk = event.get("data", {}).get("chunk", {})
            if hasattr(chunk, 'content') and chunk.content:
                return self.token_collector.add_token(chunk.content)
        
        elif event_type == "on_chat_model_end":
            # Complete token streaming
            usage = event.get("data", {}).get("output", {}).get("usage_metadata", {})
            tokens = usage.get("total_tokens", 0)
            
            return StreamingEvent(
                event_type="agent_end",
                content="✅ AI Agent completed reasoning",
                tokens_used=tokens,
                cost_incurred=self._calculate_cost(tokens),
                metadata={"usage": usage}
            )
        
        elif event_type == "on_tool_start":
            # Tool execution start
            tool_name = event.get("name", "unknown_tool")
            tool_input = event.get("data", {}).get("input", {})
            
            tool_call = ToolCallEvent(tool_name, tool_input)
            self.active_tool_calls[tool_call.call_id] = tool_call
            
            return StreamingEvent(
                event_type="tool_start",
                content=f"🔧 Starting tool: {tool_name}",
                tool_name=tool_name,
                tool_input=tool_input,
                metadata={"call_id": tool_call.call_id}
            )
        
        elif event_type == "on_tool_end":
            # Tool execution end
            tool_name = event.get("name", "unknown_tool")
            output = event.get("data", {}).get("output")
            
            # Find the corresponding tool call
            for call_id, tool_call in self.active_tool_calls.items():
                if tool_call.tool_name == tool_name and tool_call.status == "started":
                    tool_call.complete(output)
                    break
            
            return StreamingEvent(
                event_type="tool_end",
                content=f"✅ Completed tool: {tool_name}",
                tool_name=tool_name,
                tool_output=output,
                metadata={"duration": tool_call.get_duration() if 'tool_call' in locals() else 0}
            )
        
        elif event_type == "on_chain_start":
            return StreamingEvent(
                event_type="agent_start",
                content=f"🚀 Starting: {event.get('name', 'Process')}",
                agent_name=event.get("name"),
                metadata=event.get("data", {})
            )
        
        elif event_type == "on_chain_end":
            return StreamingEvent(
                event_type="agent_end",
                content=f"✅ Completed: {event.get('name', 'Process')}",
                agent_name=event.get("name"),
                metadata=event.get("data", {})
            )
        
        return None
    
    def _calculate_cost(self, tokens: int) -> float:
        """Calculate cost for GPT-4o mini"""
        # GPT-4o mini pricing (approximate)
        prompt_cost = tokens * 0.000150 / 1000  # $0.150 per 1K tokens
        return prompt_cost


def create_streaming_event_generator():
    """Create a generator for processing LangGraph events"""
    processor = LangGraphEventProcessor()
    
    def process_events(event_stream):
        """Process events from LangGraph astream"""
        for event in event_stream:
            streaming_event = processor.process_event(event)
            if streaming_event:
                yield streaming_event
    
    return process_events