"""
Local async database implementation for the New Agent Framework
Supports SQLite and JSON-based storage for complete local operation
"""

import sqlite3
import json
import os
import asyncio
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
from pathlib import Path

from ..core.config import config
from ..core.state import ExecutionPlan, TaskStep, AgentState

# Try to import aiosqlite, fallback to synchronous sqlite3 if not available
try:
    import aiosqlite
    HAS_AIOSQLITE = True
except ImportError:
    HAS_AIOSQLITE = False
    print("⚠️  aiosqlite not available, using synchronous SQLite operations")


class LocalDatabase:
    """
    Async local database for storing execution history, agent data, and logs
    """
    
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or config.get_database_path()
        self.db_type = config.database.type
        self.is_initialized = False
        
        # Ensure database directory exists
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
    
    async def initialize(self):
        """Initialize the database and create tables"""
        
        if self.is_initialized:
            return
        
        if self.db_type == "sqlite":
            await self._initialize_sqlite()
        elif self.db_type == "json":
            await self._initialize_json()
        else:  # memory
            self.data = {
                "executions": {},
                "plans": {},
                "steps": {},
                "tool_calls": {},
                "agent_stats": {},
                "logs": []
            }
        
        self.is_initialized = True
    
    async def _initialize_sqlite(self):
        """Initialize SQLite database with required tables"""
        
        # Use synchronous SQLite since aiosqlite is optional
        with sqlite3.connect(self.db_path) as db:
            # Executions table
            db.execute("""
                CREATE TABLE IF NOT EXISTS executions (
                    id TEXT PRIMARY KEY,
                    session_id TEXT NOT NULL,
                    user_id TEXT NOT NULL,
                    query TEXT NOT NULL,
                    status TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    started_at TEXT,
                    completed_at TEXT,
                    execution_time_ms INTEGER,
                    final_output TEXT,
                    error_log TEXT,
                    metadata TEXT
                )
            """)
            
            # Plans table
            db.execute("""
                CREATE TABLE IF NOT EXISTS plans (
                    id TEXT PRIMARY KEY,
                    execution_id TEXT NOT NULL,
                    query TEXT NOT NULL,
                    total_steps INTEGER NOT NULL,
                    completed_steps INTEGER DEFAULT 0,
                    failed_steps INTEGER DEFAULT 0,
                    status TEXT NOT NULL,
                    execution_mode TEXT NOT NULL,
                    estimated_duration INTEGER,
                    created_at TEXT NOT NULL,
                    metadata TEXT,
                    FOREIGN KEY (execution_id) REFERENCES executions (id)
                )
            """)
            
            # Steps table
            db.execute("""
                CREATE TABLE IF NOT EXISTS steps (
                    id TEXT PRIMARY KEY,
                    plan_id TEXT NOT NULL,
                    description TEXT NOT NULL,
                    agent_name TEXT NOT NULL,
                    status TEXT NOT NULL,
                    execution_mode TEXT NOT NULL,
                    dependencies TEXT,
                    created_at TEXT NOT NULL,
                    started_at TEXT,
                    completed_at TEXT,
                    output TEXT,
                    error TEXT,
                    metadata TEXT,
                    FOREIGN KEY (plan_id) REFERENCES plans (id)
                )
            """)
            
            # Tool calls table
            db.execute("""
                CREATE TABLE IF NOT EXISTS tool_calls (
                    id TEXT PRIMARY KEY,
                    step_id TEXT NOT NULL,
                    tool_name TEXT NOT NULL,
                    parameters TEXT NOT NULL,
                    status TEXT NOT NULL,
                    started_at TEXT,
                    completed_at TEXT,
                    result TEXT,
                    error TEXT,
                    metadata TEXT,
                    FOREIGN KEY (step_id) REFERENCES steps (id)
                )
            """)
            
            # Agent statistics table
            db.execute("""
                CREATE TABLE IF NOT EXISTS agent_stats (
                    agent_name TEXT PRIMARY KEY,
                    total_executions INTEGER DEFAULT 0,
                    successful_executions INTEGER DEFAULT 0,
                    failed_executions INTEGER DEFAULT 0,
                    average_execution_time REAL DEFAULT 0,
                    last_executed TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)
            
            # Logs table
            db.execute("""
                CREATE TABLE IF NOT EXISTS logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    level TEXT NOT NULL,
                    source TEXT NOT NULL,
                    message TEXT NOT NULL,
                    metadata TEXT,
                    execution_id TEXT
                )
            """)
            
            # Create indexes for performance
            db.execute("CREATE INDEX IF NOT EXISTS idx_executions_user_id ON executions (user_id)")
            db.execute("CREATE INDEX IF NOT EXISTS idx_executions_status ON executions (status)")
            db.execute("CREATE INDEX IF NOT EXISTS idx_plans_execution_id ON plans (execution_id)")
            db.execute("CREATE INDEX IF NOT EXISTS idx_steps_plan_id ON steps (plan_id)")
            db.execute("CREATE INDEX IF NOT EXISTS idx_tool_calls_step_id ON tool_calls (step_id)")
            db.execute("CREATE INDEX IF NOT EXISTS idx_logs_execution_id ON logs (execution_id)")
            
            db.commit()
    
    async def _initialize_json(self):
        """Initialize JSON-based storage"""
        
        self.json_files = {
            "executions": os.path.join(os.path.dirname(self.db_path), "executions.json"),
            "plans": os.path.join(os.path.dirname(self.db_path), "plans.json"),
            "steps": os.path.join(os.path.dirname(self.db_path), "steps.json"),
            "tool_calls": os.path.join(os.path.dirname(self.db_path), "tool_calls.json"),
            "agent_stats": os.path.join(os.path.dirname(self.db_path), "agent_stats.json"),
            "logs": os.path.join(os.path.dirname(self.db_path), "logs.json")
        }
        
        # Initialize empty files if they don't exist
        for file_path in self.json_files.values():
            if not os.path.exists(file_path):
                with open(file_path, 'w') as f:
                    json.dump({}, f)
    
    async def save_execution(self, state: AgentState) -> bool:
        """Save execution state to database"""
        
        await self.initialize()
        
        execution_data = {
            "id": state["session_id"],
            "session_id": state["session_id"],
            "user_id": state["user_id"],
            "query": state["query"],
            "status": state["status"],
            "created_at": state["created_at"].isoformat(),
            "started_at": state.get("started_at").isoformat() if state.get("started_at") else None,
            "completed_at": state.get("completed_at").isoformat() if state.get("completed_at") else None,
            "final_output": json.dumps(state.get("final_output", {})),
            "error_log": json.dumps(state.get("error_log", [])),
            "metadata": json.dumps({
                "execution_history": state.get("execution_history", []),
                "performance_metrics": state.get("performance_metrics", {}),
                "tool_outputs": state.get("tool_outputs", {})
            })
        }
        
        try:
            if self.db_type == "sqlite":
                with sqlite3.connect(self.db_path) as db:
                    db.execute("""
                        INSERT OR REPLACE INTO executions 
                        (id, session_id, user_id, query, status, created_at, started_at, completed_at, final_output, error_log, metadata)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        execution_data["id"], execution_data["session_id"], execution_data["user_id"],
                        execution_data["query"], execution_data["status"], execution_data["created_at"],
                        execution_data["started_at"], execution_data["completed_at"],
                        execution_data["final_output"], execution_data["error_log"], execution_data["metadata"]
                    ))
                    db.commit()
            
            elif self.db_type == "json":
                await self._save_to_json("executions", state["session_id"], execution_data)
            
            else:  # memory
                self.data["executions"][state["session_id"]] = execution_data
            
            return True
            
        except Exception as e:
            await self.log_error(f"Failed to save execution: {e}", {"execution_id": state["session_id"]})
            return False
    
    async def save_plan(self, plan: ExecutionPlan, execution_id: str) -> bool:
        """Save execution plan to database"""
        
        await self.initialize()
        
        plan_data = {
            "id": plan.plan_id,
            "execution_id": execution_id,
            "query": plan.query,
            "total_steps": plan.total_steps,
            "completed_steps": plan.completed_steps,
            "failed_steps": plan.failed_steps,
            "status": plan.status,
            "execution_mode": plan.execution_mode,
            "estimated_duration": plan.estimated_duration,
            "created_at": plan.created_at.isoformat(),
            "metadata": json.dumps({
                "step_ids": [step.step_id for step in plan.steps]
            })
        }
        
        try:
            if self.db_type == "sqlite":
                async with aiosqlite.connect(self.db_path) as db:
                    await db.execute("""
                        INSERT OR REPLACE INTO plans 
                        (id, execution_id, query, total_steps, completed_steps, failed_steps, status, execution_mode, estimated_duration, created_at, metadata)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        plan_data["id"], plan_data["execution_id"], plan_data["query"],
                        plan_data["total_steps"], plan_data["completed_steps"], plan_data["failed_steps"],
                        plan_data["status"], plan_data["execution_mode"], plan_data["estimated_duration"],
                        plan_data["created_at"], plan_data["metadata"]
                    ))
                    await db.commit()
            
            elif self.db_type == "json":
                await self._save_to_json("plans", plan.plan_id, plan_data)
            
            else:  # memory
                self.data["plans"][plan.plan_id] = plan_data
            
            # Also save all steps
            for step in plan.steps:
                await self.save_step(step, plan.plan_id)
            
            return True
            
        except Exception as e:
            await self.log_error(f"Failed to save plan: {e}", {"plan_id": plan.plan_id})
            return False
    
    async def save_step(self, step: TaskStep, plan_id: str) -> bool:
        """Save task step to database"""
        
        await self.initialize()
        
        step_data = {
            "id": step.step_id,
            "plan_id": plan_id,
            "description": step.description,
            "agent_name": step.agent_name,
            "status": step.status,
            "execution_mode": step.execution_mode,
            "dependencies": json.dumps(step.dependencies),
            "created_at": step.created_at.isoformat(),
            "started_at": step.started_at.isoformat() if step.started_at else None,
            "completed_at": step.completed_at.isoformat() if step.completed_at else None,
            "output": json.dumps(step.output) if step.output else None,
            "error": step.error,
            "metadata": json.dumps({
                "tool_call_ids": [tc.call_id for tc in step.tool_calls]
            })
        }
        
        try:
            if self.db_type == "sqlite":
                async with aiosqlite.connect(self.db_path) as db:
                    await db.execute("""
                        INSERT OR REPLACE INTO steps 
                        (id, plan_id, description, agent_name, status, execution_mode, dependencies, created_at, started_at, completed_at, output, error, metadata)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        step_data["id"], step_data["plan_id"], step_data["description"],
                        step_data["agent_name"], step_data["status"], step_data["execution_mode"],
                        step_data["dependencies"], step_data["created_at"], step_data["started_at"],
                        step_data["completed_at"], step_data["output"], step_data["error"], step_data["metadata"]
                    ))
                    await db.commit()
            
            elif self.db_type == "json":
                await self._save_to_json("steps", step.step_id, step_data)
            
            else:  # memory
                self.data["steps"][step.step_id] = step_data
            
            # Also save all tool calls
            for tool_call in step.tool_calls:
                await self.save_tool_call(tool_call, step.step_id)
            
            return True
            
        except Exception as e:
            await self.log_error(f"Failed to save step: {e}", {"step_id": step.step_id})
            return False
    
    async def save_tool_call(self, tool_call, step_id: str) -> bool:
        """Save tool call to database"""
        
        await self.initialize()
        
        tool_call_data = {
            "id": tool_call.call_id,
            "step_id": step_id,
            "tool_name": tool_call.tool_name,
            "parameters": json.dumps(tool_call.parameters),
            "status": tool_call.status,
            "started_at": tool_call.started_at.isoformat() if tool_call.started_at else None,
            "completed_at": tool_call.completed_at.isoformat() if tool_call.completed_at else None,
            "result": json.dumps(tool_call.result) if tool_call.result else None,
            "error": tool_call.error,
            "metadata": json.dumps({})
        }
        
        try:
            if self.db_type == "sqlite":
                async with aiosqlite.connect(self.db_path) as db:
                    await db.execute("""
                        INSERT OR REPLACE INTO tool_calls 
                        (id, step_id, tool_name, parameters, status, started_at, completed_at, result, error, metadata)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        tool_call_data["id"], tool_call_data["step_id"], tool_call_data["tool_name"],
                        tool_call_data["parameters"], tool_call_data["status"], tool_call_data["started_at"],
                        tool_call_data["completed_at"], tool_call_data["result"], tool_call_data["error"], tool_call_data["metadata"]
                    ))
                    await db.commit()
            
            elif self.db_type == "json":
                await self._save_to_json("tool_calls", tool_call.call_id, tool_call_data)
            
            else:  # memory
                self.data["tool_calls"][tool_call.call_id] = tool_call_data
            
            return True
            
        except Exception as e:
            await self.log_error(f"Failed to save tool call: {e}", {"tool_call_id": tool_call.call_id})
            return False
    
    async def get_execution_history(self, user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get execution history for a user"""
        
        await self.initialize()
        
        try:
            if self.db_type == "sqlite":
                async with aiosqlite.connect(self.db_path) as db:
                    cursor = await db.execute("""
                        SELECT * FROM executions 
                        WHERE user_id = ? 
                        ORDER BY created_at DESC 
                        LIMIT ?
                    """, (user_id, limit))
                    rows = await cursor.fetchall()
                    columns = [description[0] for description in cursor.description]
                    return [dict(zip(columns, row)) for row in rows]
            
            elif self.db_type == "json":
                data = await self._load_from_json("executions")
                filtered = [exec_data for exec_data in data.values() if exec_data.get("user_id") == user_id]
                sorted_data = sorted(filtered, key=lambda x: x["created_at"], reverse=True)
                return sorted_data[:limit]
            
            else:  # memory
                filtered = [exec_data for exec_data in self.data["executions"].values() if exec_data.get("user_id") == user_id]
                sorted_data = sorted(filtered, key=lambda x: x["created_at"], reverse=True)
                return sorted_data[:limit]
                
        except Exception as e:
            await self.log_error(f"Failed to get execution history: {e}", {"user_id": user_id})
            return []
    
    async def get_plan_details(self, plan_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed plan information including steps and tool calls"""
        
        await self.initialize()
        
        try:
            plan_data = None
            
            if self.db_type == "sqlite":
                async with aiosqlite.connect(self.db_path) as db:
                    # Get plan
                    cursor = await db.execute("SELECT * FROM plans WHERE id = ?", (plan_id,))
                    plan_row = await cursor.fetchone()
                    if not plan_row:
                        return None
                    
                    columns = [description[0] for description in cursor.description]
                    plan_data = dict(zip(columns, plan_row))
                    
                    # Get steps
                    cursor = await db.execute("SELECT * FROM steps WHERE plan_id = ? ORDER BY created_at", (plan_id,))
                    step_rows = await cursor.fetchall()
                    columns = [description[0] for description in cursor.description]
                    plan_data["steps"] = [dict(zip(columns, row)) for row in step_rows]
                    
                    # Get tool calls for each step
                    for step in plan_data["steps"]:
                        cursor = await db.execute("SELECT * FROM tool_calls WHERE step_id = ? ORDER BY started_at", (step["id"],))
                        tool_rows = await cursor.fetchall()
                        columns = [description[0] for description in cursor.description]
                        step["tool_calls"] = [dict(zip(columns, row)) for row in tool_rows]
            
            elif self.db_type == "json":
                plans = await self._load_from_json("plans")
                plan_data = plans.get(plan_id)
                if plan_data:
                    # Add steps and tool calls
                    steps = await self._load_from_json("steps")
                    tool_calls = await self._load_from_json("tool_calls")
                    
                    plan_data["steps"] = [step for step in steps.values() if step["plan_id"] == plan_id]
                    for step in plan_data["steps"]:
                        step["tool_calls"] = [tc for tc in tool_calls.values() if tc["step_id"] == step["id"]]
            
            else:  # memory
                plan_data = self.data["plans"].get(plan_id)
                if plan_data:
                    plan_data["steps"] = [step for step in self.data["steps"].values() if step["plan_id"] == plan_id]
                    for step in plan_data["steps"]:
                        step["tool_calls"] = [tc for tc in self.data["tool_calls"].values() if tc["step_id"] == step["id"]]
            
            return plan_data
            
        except Exception as e:
            await self.log_error(f"Failed to get plan details: {e}", {"plan_id": plan_id})
            return None
    
    async def log_event(self, level: str, source: str, message: str, metadata: Dict[str, Any] = None, execution_id: str = None):
        """Log an event to the database"""
        
        await self.initialize()
        
        log_data = {
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "source": source,
            "message": message,
            "metadata": json.dumps(metadata or {}),
            "execution_id": execution_id
        }
        
        try:
            if self.db_type == "sqlite":
                async with aiosqlite.connect(self.db_path) as db:
                    await db.execute("""
                        INSERT INTO logs (timestamp, level, source, message, metadata, execution_id)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (
                        log_data["timestamp"], log_data["level"], log_data["source"],
                        log_data["message"], log_data["metadata"], log_data["execution_id"]
                    ))
                    await db.commit()
            
            elif self.db_type == "json":
                logs = await self._load_from_json("logs")
                if not isinstance(logs, list):
                    logs = []
                logs.append(log_data)
                await self._save_json_file("logs", logs)
            
            else:  # memory
                if "logs" not in self.data:
                    self.data["logs"] = []
                self.data["logs"].append(log_data)
                
        except Exception as e:
            print(f"Failed to log event: {e}")  # Fallback logging
    
    async def log_error(self, message: str, metadata: Dict[str, Any] = None, execution_id: str = None):
        """Log an error event"""
        await self.log_event("ERROR", "database", message, metadata, execution_id)
    
    async def _save_to_json(self, table_name: str, key: str, data: Dict[str, Any]):
        """Save data to JSON file"""
        existing_data = await self._load_from_json(table_name)
        existing_data[key] = data
        await self._save_json_file(table_name, existing_data)
    
    async def _load_from_json(self, table_name: str) -> Dict[str, Any]:
        """Load data from JSON file"""
        file_path = self.json_files[table_name]
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
    
    async def _save_json_file(self, table_name: str, data: Union[Dict, List]):
        """Save data to JSON file"""
        file_path = self.json_files[table_name]
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2, default=str)
    
    async def cleanup(self):
        """Cleanup database resources"""
        # No cleanup needed for SQLite/JSON, connections are auto-managed
        pass


# Global database instance
database = LocalDatabase()