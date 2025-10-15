"""
Execution engine for the New Agent Framework
Coordinates agents, manages tool calls, and handles real-time streaming
"""

import asyncio
import time
import threading
from typing import Dict, Any, List, Optional, Generator
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import queue

from ..core.state import (
    AgentState, ExecutionPlan, TaskStep, ToolCall, TaskStatus, 
    StreamingEvent, advance_to_next_step, log_execution_event, EventType
)
from ..core.config import config
from ..agents.registry import agent_registry
from ..tools.dummy_tools import dummy_tool_registry
from ..llm.openai_llm import get_llm_instance


class ExecutionEngine:
    """
    Core execution engine that orchestrates agent workflows,
    manages tool calls, and provides real-time streaming output
    """
    
    def __init__(self):
        self.llm = get_llm_instance()
        self.agent_registry = agent_registry
        self.tool_registry = dummy_tool_registry
        self.is_running = False
        self.current_execution = None
        self.streaming_queue = queue.Queue()
        self.executor = ThreadPoolExecutor(max_workers=config.execution.max_parallel_agents)
        
        # Execution metrics
        self.execution_metrics = {
            "total_executions": 0,
            "successful_executions": 0,
            "failed_executions": 0,
            "average_execution_time": 0,
            "total_tools_called": 0
        }
    
    def execute_plan(self, state: AgentState) -> Generator[StreamingEvent, None, AgentState]:
        """
        Execute a complete plan with real-time streaming
        """
        self.is_running = True
        self.current_execution = state["session_id"]
        start_time = time.time()
        
        try:
            # Emit start event
            yield StreamingEvent(
                event_type="status",
                content="🚀 Starting execution...",
                metadata={"plan_id": state["execution_plan"].plan_id}
            )
            
            # Update state
            state = log_execution_event(state, "execution_started", {
                "plan_id": state["execution_plan"].plan_id,
                "total_steps": len(state["execution_plan"].steps)
            })
            
            # Execute steps based on execution mode
            execution_mode = state["execution_plan"].execution_mode
            
            if execution_mode == "sequential":
                yield from self._execute_sequential(state)
            elif execution_mode == "parallel":
                yield from self._execute_parallel(state)
            else:  # conditional
                yield from self._execute_conditional(state)
            
            # Final completion
            execution_time = int((time.time() - start_time) * 1000)
            
            yield StreamingEvent(
                event_type="status",
                content="✅ Execution completed successfully!",
                metadata={
                    "execution_time_ms": execution_time,
                    "steps_completed": state["current_step_index"],
                    "final_status": state["status"]
                }
            )
            
            # Update metrics
            self._update_execution_metrics(execution_time, True)
            
            return state
            
        except Exception as e:
            execution_time = int((time.time() - start_time) * 1000)
            
            yield StreamingEvent(
                event_type="error",
                content=f"❌ Execution failed: {str(e)}",
                metadata={"error": str(e), "execution_time_ms": execution_time}
            )
            
            state["status"] = "failed"
            state["error_log"].append(f"Execution failed: {str(e)}")
            
            self._update_execution_metrics(execution_time, False)
            
            return state
            
        finally:
            self.is_running = False
            self.current_execution = None
    
    def _execute_sequential(self, state: AgentState) -> Generator[StreamingEvent, None, None]:
        """Execute steps sequentially"""
        
        plan = state["execution_plan"]
        
        for step_index, step in enumerate(plan.steps):
            state["current_step_index"] = step_index
            state["current_step"] = step
            
            # Check dependencies
            if not self._check_dependencies(step, state):
                yield StreamingEvent(
                    event_type="error",
                    content=f"⚠️ Dependencies not met for step: {step.description}",
                    metadata={"step_id": step.step_id}
                )
                continue
            
            # Execute step
            yield from self._execute_step(step, state)
            
            # Update progress
            plan.completed_steps += 1
    
    def _execute_parallel(self, state: AgentState) -> Generator[StreamingEvent, None, None]:
        """Execute steps in parallel where possible"""
        
        plan = state["execution_plan"]
        
        # Group steps by dependency level
        dependency_levels = self._group_by_dependencies(plan.steps)
        
        for level, steps in dependency_levels.items():
            yield StreamingEvent(
                event_type="status",
                content=f"🔄 Executing {len(steps)} steps in parallel (level {level})",
                metadata={"level": level, "steps_count": len(steps)}
            )
            
            # Execute all steps in this level simultaneously
            futures = []
            for step in steps:
                future = self.executor.submit(self._execute_step_sync, step, state)
                futures.append((future, step))
            
            # Collect results as they complete
            for future, step in futures:
                try:
                    events = future.result(timeout=step.timeout_seconds if hasattr(step, 'timeout_seconds') else 300)
                    for event in events:
                        yield event
                except Exception as e:
                    yield StreamingEvent(
                        event_type="error",
                        content=f"❌ Step failed: {step.description} - {str(e)}",
                        metadata={"step_id": step.step_id, "error": str(e)}
                    )
            
            plan.completed_steps += len(steps)
    
    def _execute_conditional(self, state: AgentState) -> Generator[StreamingEvent, None, None]:
        """Execute steps with conditional logic"""
        
        plan = state["execution_plan"]
        
        for step_index, step in enumerate(plan.steps):
            state["current_step_index"] = step_index
            state["current_step"] = step
            
            # Evaluate conditions for this step
            should_execute = self._evaluate_step_conditions(step, state)
            
            if not should_execute:
                yield StreamingEvent(
                    event_type="status",
                    content=f"⏭️ Skipping step: {step.description} (conditions not met)",
                    metadata={"step_id": step.step_id, "reason": "conditions_not_met"}
                )
                step.status = "skipped"
                continue
            
            # Execute step
            yield from self._execute_step(step, state)
            plan.completed_steps += 1
    
    def _execute_step(self, step: TaskStep, state: AgentState) -> Generator[StreamingEvent, None, None]:
        """Execute a single step using enhanced LLM-powered agents"""
        
        step.status = "in_progress"
        step.started_at = datetime.now()
        
        yield StreamingEvent(
            event_type="node_start",
            content=f"🔵 Starting: {step.description}",
            node_name=step.agent_name,
            metadata={
                "step_id": step.step_id,
                "agent": step.agent_name,
                "description": step.description
            }
        )
        
        try:
            # Get enhanced agent instance
            agent_instance = self.agent_registry.get_agent_instance(step.agent_name)
            if not agent_instance:
                raise ValueError(f"Enhanced agent {step.agent_name} not found")
            
            # Prepare context for agent
            context = {
                "state": state,
                "previous_results": getattr(step, 'output', {}),
                "data_sources": []
            }
            
            # Collect results from previous steps as data sources
            for prev_step in state["execution_plan"].steps:
                if (prev_step.status == "completed" and 
                    hasattr(prev_step, 'output') and 
                    prev_step.output):
                    context["data_sources"].append({
                        "source_name": f"{prev_step.agent_name}_output",
                        "data": prev_step.output
                    })
            
            # Execute agent step with streaming using thread pool to avoid event loop conflicts
            import concurrent.futures
            
            def run_async_agent():
                """Run agent in a separate thread with its own event loop"""
                import asyncio
                
                async def collect_events():
                    events = []
                    async for event in agent_instance.execute_step(
                        task=step.description,
                        context=context
                    ):
                        events.append(event)
                    return events
                
                # Create new event loop for this thread
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    return loop.run_until_complete(collect_events())
                finally:
                    loop.close()
            
            # Execute in thread pool
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(run_async_agent)
                events = future.result(timeout=300)  # 5 minute timeout
                
                # Yield all collected events
                for event in events:
                    # Convert agent events to execution events
                    if hasattr(event, 'type') and event.type == EventType.AGENT_START:
                        yield StreamingEvent(
                            event_type="agent_thinking",
                            content=f"🧠 {step.agent_name} analyzing task...",
                            node_name=step.agent_name,
                            metadata=event.data if hasattr(event, 'data') else {}
                        )
                    elif hasattr(event, 'type') and event.type == EventType.AGENT_THINKING:
                        yield StreamingEvent(
                            event_type="agent_thinking",
                            content=f"💭 {event.data.get('reasoning', 'Processing...')}",
                            node_name=step.agent_name,
                            metadata={
                                "action_type": event.data.get('action_type'),
                                "confidence": event.data.get('confidence')
                            }
                        )
                    elif hasattr(event, 'type') and event.type == EventType.TOOL_START:
                        yield StreamingEvent(
                            event_type="tool_start",
                            content=f"🔧 Using {event.data.get('tool_name', 'tool')}...",
                            tool_name=event.data.get('tool_name'),
                            metadata=event.data
                        )
                    elif hasattr(event, 'type') and event.type == EventType.TOOL_END:
                        yield StreamingEvent(
                            event_type="tool_end",
                            content=f"✅ Tool completed: {event.data.get('tool_name')}",
                            tool_name=event.data.get('tool_name'),
                            metadata=event.data
                        )
                    elif hasattr(event, 'type') and event.type == EventType.AGENT_COMPLETE:
                        if hasattr(event, 'data'):
                            step.output = event.data.get('result', {})
                        yield StreamingEvent(
                            event_type="agent_complete",
                            content=f"✅ {step.agent_name} completed",
                            node_name=step.agent_name,
                            metadata=event.data if hasattr(event, 'data') else {}
                        )
                    elif hasattr(event, 'type') and event.type == EventType.ERROR:
                        error_msg = event.data.get('error', 'Unknown error') if hasattr(event, 'data') else 'Unknown error'
                        raise Exception(f"Agent error: {error_msg}")
            
            # Mark step as completed
            step.status = "completed"
            step.completed_at = datetime.now()
            
            # Update statistics
            execution_time = int((step.completed_at - step.started_at).total_seconds() * 1000)
            self.agent_registry.update_agent_stats(step.agent_name, execution_time, True)
            
            yield StreamingEvent(
                event_type="node_end",
                content=f"✅ Completed: {step.description}",
                node_name=step.agent_name,
                metadata={
                    "step_id": step.step_id,
                    "execution_time_ms": execution_time,
                    "token_usage": agent_instance.execution_stats,
                    "results": step.output
                }
            )
            
        except Exception as e:
            step.status = "failed"
            step.error = str(e)
            step.completed_at = datetime.now()
            
            # Update agent statistics
            if step.started_at:
                execution_time = int((step.completed_at - step.started_at).total_seconds() * 1000)
                agent_registry.update_agent_stats(step.agent_name, execution_time, False)
            
            yield StreamingEvent(
                event_type="error",
                content=f"❌ Failed: {step.description} - {str(e)}",
                node_name=step.agent_name,
                metadata={
                    "step_id": step.step_id,
                    "error": str(e)
                }
            )
            
            # Handle retries if configured
            if hasattr(step, 'retry_count') and step.retry_count < 3:  # Max 3 retries
                step.retry_count += 1
                yield StreamingEvent(
                    event_type="status",
                    content=f"🔄 Retrying step: {step.description} (attempt {step.retry_count + 1})",
                    metadata={"step_id": step.step_id, "retry_attempt": step.retry_count + 1}
                )
                yield from self._execute_step(step, state)
            else:
                # Mark step as failed
                step.status = "failed"
                step.completed_at = datetime.now()
                self.agent_registry.update_agent_stats(step.agent_name, 0, False)
    
    def _execute_tool_call(self, tool_call: ToolCall, state: AgentState) -> Generator[StreamingEvent, None, None]:
        """Execute a single tool call with streaming"""
        
        tool_call.status = "in_progress"
        tool_call.started_at = datetime.now()
        
        yield StreamingEvent(
            event_type="tool_start",
            content=f"🔧 Started calling tool {tool_call.tool_name}",
            tool_name=tool_call.tool_name,
            metadata={
                "tool_call_id": tool_call.call_id,
                "parameters": tool_call.parameters
            }
        )
        
        # Stream tool-specific tokens
        yield StreamingEvent(
            event_type="token",
            content=f"with params {tool_call.parameters}",
            metadata={"tool_call_id": tool_call.call_id}
        )
        
        try:
            # Execute the tool
            result = self.tool_registry.execute_tool(tool_call.tool_name, **tool_call.parameters)
            
            tool_call.result = result.result
            tool_call.status = "completed" if result.success else "failed"
            tool_call.completed_at = datetime.now()
            tool_call.error = result.error
            
            # Update metrics
            self.execution_metrics["total_tools_called"] += 1
            
            # Store result in state
            state["tool_outputs"][tool_call.call_id] = result.result
            
            yield StreamingEvent(
                event_type="tool_end",
                content=f"🔧 Completed calling tool {tool_call.tool_name}",
                tool_name=tool_call.tool_name,
                metadata={
                    "tool_call_id": tool_call.call_id,
                    "success": result.success,
                    "execution_time_ms": result.execution_time_ms,
                    "result_preview": str(result.result)[:100] + "..." if len(str(result.result)) > 100 else str(result.result)
                }
            )
            
        except Exception as e:
            tool_call.status = "failed"
            tool_call.error = str(e)
            tool_call.completed_at = datetime.now()
            
            yield StreamingEvent(
                event_type="error",
                content=f"❌ Tool {tool_call.tool_name} failed: {str(e)}",
                tool_name=tool_call.tool_name,
                metadata={
                    "tool_call_id": tool_call.call_id,
                    "error": str(e)
                }
            )
    
    def _execute_step_sync(self, step: TaskStep, state: AgentState) -> List[StreamingEvent]:
        """Synchronous version of step execution for parallel processing"""
        events = []
        
        # Convert generator to list for parallel execution
        for event in self._execute_step(step, state):
            events.append(event)
        
        return events
    
    def _check_dependencies(self, step: TaskStep, state: AgentState) -> bool:
        """Check if step dependencies are satisfied"""
        
        if not step.dependencies:
            return True
        
        plan = state["execution_plan"]
        
        # Check if all dependency steps are completed
        for dep_step_id in step.dependencies:
            dep_step = next((s for s in plan.steps if s.step_id == dep_step_id), None)
            if not dep_step or dep_step.status != "completed":
                return False
        
        return True
    
    def _group_by_dependencies(self, steps: List[TaskStep]) -> Dict[int, List[TaskStep]]:
        """Group steps by dependency level for parallel execution"""
        
        levels = {}
        step_levels = {}
        
        def get_step_level(step):
            if step.step_id in step_levels:
                return step_levels[step.step_id]
            
            if not step.dependencies:
                level = 0
            else:
                # Find steps that this depends on
                dep_steps = [s for s in steps if s.step_id in step.dependencies]
                max_dep_level = max((get_step_level(dep_step) for dep_step in dep_steps), default=-1)
                level = max_dep_level + 1
            
            step_levels[step.step_id] = level
            return level
        
        # Assign levels to all steps
        for step in steps:
            level = get_step_level(step)
            if level not in levels:
                levels[level] = []
            levels[level].append(step)
        
        return levels
    
    def _evaluate_step_conditions(self, step: TaskStep, state: AgentState) -> bool:
        """Evaluate whether a step should be executed based on conditions"""
        
        # For now, execute all steps unless explicitly marked to skip
        # Future: Add more sophisticated condition evaluation
        
        # Check if previous steps failed and this step requires their output
        if step.dependencies:
            plan = state["execution_plan"]
            for dep_step_id in step.dependencies:
                dep_step = next((s for s in plan.steps if s.step_id == dep_step_id), None)
                if dep_step and dep_step.status == "failed":
                    # Skip this step if critical dependencies failed
                    return False
        
        return True
    
    def _update_execution_metrics(self, execution_time_ms: int, success: bool):
        """Update execution metrics"""
        
        self.execution_metrics["total_executions"] += 1
        
        if success:
            self.execution_metrics["successful_executions"] += 1
        else:
            self.execution_metrics["failed_executions"] += 1
        
        # Update average execution time
        total_execs = self.execution_metrics["total_executions"]
        current_avg = self.execution_metrics["average_execution_time"]
        new_avg = ((current_avg * (total_execs - 1)) + execution_time_ms) / total_execs
        self.execution_metrics["average_execution_time"] = new_avg
    
    def get_execution_status(self) -> Dict[str, Any]:
        """Get current execution status"""
        return {
            "is_running": self.is_running,
            "current_execution": self.current_execution,
            "metrics": self.execution_metrics.copy()
        }
    
    def stop_execution(self):
        """Stop current execution"""
        self.is_running = False
        
        # Cancel any pending futures
        self.executor.shutdown(wait=False)
        self.executor = ThreadPoolExecutor(max_workers=config.execution.max_parallel_agents)
    
    def cleanup(self):
        """Cleanup resources"""
        self.executor.shutdown(wait=True)


# Global execution engine instance
execution_engine = ExecutionEngine()