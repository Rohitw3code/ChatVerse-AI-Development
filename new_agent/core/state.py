"""
Core state management and type definitions for the New Agent Framework
"""

from typing import TypedDict, Annotated, List, Dict, Any, Optional, Literal, Union
from typing_extensions import NotRequired
from dataclasses import dataclass, field
from datetime import datetime
import uuid


# Core Types
AgentType = Literal["planner", "supervisor", "executor", "tool_agent", "orchestrator"]
TaskStatus = Literal["pending", "in_progress", "completed", "failed", "skipped"]
NodeType = Literal["input", "planner", "supervisor", "agent", "tool", "final", "error"]
ExecutionMode = Literal["sequential", "parallel", "conditional"]
EventType = Literal["agent_start", "agent_thinking", "agent_complete", "tool_start", "tool_end", "error", "status"]

@dataclass
class ToolCall:
    """Represents a tool call with metadata"""
    tool_name: str
    parameters: Dict[str, Any]
    call_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    status: TaskStatus = "pending"
    result: Optional[Any] = None
    error: Optional[str] = None

@dataclass 
class TaskStep:
    """Represents a single step in a plan"""
    step_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    description: str = ""
    agent_name: str = ""
    tool_calls: List[ToolCall] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)  # step_ids this depends on
    status: TaskStatus = "pending"
    execution_mode: ExecutionMode = "sequential"
    estimated_time_seconds: int = 60  # Added for enhanced planning
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    output: Optional[Any] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)  # Added for enhanced data

@dataclass
class AgentMetadata:
    """Agent definition and capabilities"""
    name: str
    description: str
    agent_type: AgentType
    tools: List[str] = field(default_factory=list)
    capabilities: List[str] = field(default_factory=list) 
    max_retries: int = 3
    timeout_seconds: int = 300
    is_active: bool = True

@dataclass
class ExecutionPlan:
    """Complete execution plan with steps and metadata"""
    plan_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    query: str = ""
    steps: List[TaskStep] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    total_steps: int = 0
    completed_steps: int = 0
    failed_steps: int = 0
    status: TaskStatus = "pending"
    execution_mode: ExecutionMode = "sequential"
    estimated_duration: Optional[int] = None  # seconds
    metadata: Dict[str, Any] = field(default_factory=dict)  # Enhanced metadata

class AgentState(TypedDict, total=False):
    """Enhanced state management for the new agent framework"""
    
    # Core Query & Input
    query: str
    original_query: str
    user_id: str
    session_id: str
    
    # Execution Plan & Progress  
    execution_plan: NotRequired[ExecutionPlan]
    current_step: NotRequired[TaskStep]
    current_step_index: int
    
    # Agent & Tool Management
    available_agents: List[AgentMetadata]
    active_agent: NotRequired[str]
    tool_outputs: Dict[str, Any]
    
    # Streaming & Real-time Updates
    streaming_enabled: bool
    current_node: str
    node_type: NodeType
    streaming_buffer: List[str]
    
    # Execution Context
    execution_mode: ExecutionMode
    retry_count: int
    max_retries: int
    timeout_seconds: int
    
    # Results & Logging
    final_output: NotRequired[Dict[str, Any]]
    execution_history: List[Dict[str, Any]]
    error_log: List[str]
    performance_metrics: Dict[str, Any]
    
    # System State
    status: TaskStatus
    created_at: datetime
    started_at: NotRequired[datetime]
    completed_at: NotRequired[datetime]
    
    # CLI & Output Control
    verbose: bool
    output_format: Literal["json", "text", "rich"]
    show_metadata: bool
    
    # Recovery & Persistence
    checkpoint_data: NotRequired[Dict[str, Any]]
    resume_from_step: NotRequired[int]


@dataclass
class StreamingEvent:
    """Real-time streaming event structure"""
    event_type: Literal["token", "node_start", "node_end", "tool_start", "tool_end", "error", "status"]
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    node_name: Optional[str] = None
    tool_name: Optional[str] = None
    
    # Enhanced fields for new event system
    type: Optional[EventType] = None  # New event type system
    data: Dict[str, Any] = field(default_factory=dict)  # Event data


# Utility functions for state management
def create_initial_state(query: str, user_id: str = "default") -> AgentState:
    """Create initial state for a new execution"""
    return AgentState(
        query=query,
        original_query=query,
        user_id=user_id,
        session_id=str(uuid.uuid4()),
        current_step_index=0,
        available_agents=[],
        streaming_enabled=True,
        current_node="input",
        node_type="input",
        streaming_buffer=[],
        execution_mode="sequential",
        retry_count=0,
        max_retries=3,
        timeout_seconds=300,
        tool_outputs={},
        execution_history=[],
        error_log=[],
        performance_metrics={},
        status="pending",
        created_at=datetime.now(),
        verbose=True,
        output_format="rich",
        show_metadata=True
    )

def update_state_with_plan(state: AgentState, plan: ExecutionPlan) -> AgentState:
    """Update state with a new execution plan"""
    state["execution_plan"] = plan
    state["status"] = "in_progress"
    state["started_at"] = datetime.now()
    return state

def get_current_step(state: AgentState) -> Optional[TaskStep]:
    """Get the current step being executed"""
    if "execution_plan" not in state:
        return None
    
    plan = state["execution_plan"]
    step_index = state["current_step_index"]
    
    if step_index < len(plan.steps):
        return plan.steps[step_index]
    
    return None

def advance_to_next_step(state: AgentState) -> AgentState:
    """Move to the next step in the execution plan"""
    state["current_step_index"] += 1
    
    if "execution_plan" in state:
        plan = state["execution_plan"]
        if state["current_step_index"] >= len(plan.steps):
            state["status"] = "completed"
            state["completed_at"] = datetime.now()
    
    return state

def log_execution_event(state: AgentState, event: str, metadata: Dict[str, Any] = None) -> AgentState:
    """Log an execution event to the history"""
    event_data = {
        "timestamp": datetime.now().isoformat(),
        "event": event,
        "metadata": metadata or {},
        "step_index": state["current_step_index"],
        "node": state["current_node"]
    }
    state["execution_history"].append(event_data)
    return state