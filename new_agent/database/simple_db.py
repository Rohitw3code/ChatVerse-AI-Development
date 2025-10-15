"""
Simplified local database implementation for the New Agent Framework
Uses synchronous SQLite and JSON storage for complete local operation
"""

import sqlite3
import json
import os
from typing import Dict, Any, List, Optional
from datetime import datetime
from threading import Lock

from ..core.config import config
from ..core.state import ExecutionPlan, TaskStep, AgentState


class SimpleLocalDatabase:
    """
    Simplified local database with synchronous operations
    """
    
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or config.get_database_path()
        self.db_type = config.database.type
        self.is_initialized = False
        self._lock = Lock()  # Thread safety
        
        # Ensure database directory exists
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
    
    def initialize(self):
        """Initialize the database and create tables"""
        
        if self.is_initialized:
            return
        
        with self._lock:
            if self.db_type == "sqlite":
                self._initialize_sqlite()
            elif self.db_type == "json":
                self._initialize_json()
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
    
    def _initialize_sqlite(self):
        """Initialize SQLite database with required tables"""
        
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
                    metadata TEXT
                )
            """)
            
            # Create indexes
            db.execute("CREATE INDEX IF NOT EXISTS idx_executions_user_id ON executions (user_id)")
            db.execute("CREATE INDEX IF NOT EXISTS idx_plans_execution_id ON plans (execution_id)")
            
            db.commit()
    
    def _initialize_json(self):
        """Initialize JSON-based storage"""
        
        self.json_files = {
            "executions": os.path.join(os.path.dirname(self.db_path), "executions.json"),
            "plans": os.path.join(os.path.dirname(self.db_path), "plans.json"),
            "logs": os.path.join(os.path.dirname(self.db_path), "logs.json")
        }
        
        # Initialize empty files if they don't exist
        for file_path in self.json_files.values():
            if not os.path.exists(file_path):
                with open(file_path, 'w') as f:
                    json.dump({}, f)
    
    def save_execution(self, state: AgentState) -> bool:
        """Save execution state to database"""
        
        self.initialize()
        
        execution_data = {
            "id": state["session_id"],
            "session_id": state["session_id"],
            "user_id": state.get("user_id", "default"),
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
            with self._lock:
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
                    self._save_to_json("executions", state["session_id"], execution_data)
                
                else:  # memory
                    self.data["executions"][state["session_id"]] = execution_data
            
            return True
            
        except Exception as e:
            self.log_error(f"Failed to save execution: {e}", {"execution_id": state["session_id"]})
            return False
    
    def save_plan(self, plan: ExecutionPlan, execution_id: str) -> bool:
        """Save execution plan to database"""
        
        self.initialize()
        
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
                "step_count": len(plan.steps),
                "step_descriptions": [step.description for step in plan.steps]
            })
        }
        
        try:
            with self._lock:
                if self.db_type == "sqlite":
                    with sqlite3.connect(self.db_path) as db:
                        db.execute("""
                            INSERT OR REPLACE INTO plans 
                            (id, execution_id, query, total_steps, completed_steps, failed_steps, status, execution_mode, estimated_duration, created_at, metadata)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            plan_data["id"], plan_data["execution_id"], plan_data["query"],
                            plan_data["total_steps"], plan_data["completed_steps"], plan_data["failed_steps"],
                            plan_data["status"], plan_data["execution_mode"], plan_data["estimated_duration"],
                            plan_data["created_at"], plan_data["metadata"]
                        ))
                        db.commit()
                
                elif self.db_type == "json":
                    self._save_to_json("plans", plan.plan_id, plan_data)
                
                else:  # memory
                    self.data["plans"][plan.plan_id] = plan_data
            
            return True
            
        except Exception as e:
            self.log_error(f"Failed to save plan: {e}", {"plan_id": plan.plan_id})
            return False
    
    def get_execution_history(self, user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get execution history for a user"""
        
        self.initialize()
        
        try:
            with self._lock:
                if self.db_type == "sqlite":
                    with sqlite3.connect(self.db_path) as db:
                        cursor = db.execute("""
                            SELECT * FROM executions 
                            WHERE user_id = ? 
                            ORDER BY created_at DESC 
                            LIMIT ?
                        """, (user_id, limit))
                        columns = [description[0] for description in cursor.description]
                        rows = cursor.fetchall()
                        return [dict(zip(columns, row)) for row in rows]
                
                elif self.db_type == "json":
                    data = self._load_from_json("executions")
                    filtered = [exec_data for exec_data in data.values() if exec_data.get("user_id") == user_id]
                    sorted_data = sorted(filtered, key=lambda x: x["created_at"], reverse=True)
                    return sorted_data[:limit]
                
                else:  # memory
                    filtered = [exec_data for exec_data in self.data["executions"].values() if exec_data.get("user_id") == user_id]
                    sorted_data = sorted(filtered, key=lambda x: x["created_at"], reverse=True)
                    return sorted_data[:limit]
                    
        except Exception as e:
            self.log_error(f"Failed to get execution history: {e}", {"user_id": user_id})
            return []
    
    def get_plan_details(self, plan_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed plan information"""
        
        self.initialize()
        
        try:
            with self._lock:
                if self.db_type == "sqlite":
                    with sqlite3.connect(self.db_path) as db:
                        cursor = db.execute("SELECT * FROM plans WHERE id = ?", (plan_id,))
                        row = cursor.fetchone()
                        if not row:
                            return None
                        
                        columns = [description[0] for description in cursor.description]
                        return dict(zip(columns, row))
                
                elif self.db_type == "json":
                    plans = self._load_from_json("plans")
                    return plans.get(plan_id)
                
                else:  # memory
                    return self.data["plans"].get(plan_id)
                
        except Exception as e:
            self.log_error(f"Failed to get plan details: {e}", {"plan_id": plan_id})
            return None
    
    def log_event(self, level: str, source: str, message: str, metadata: Dict[str, Any] = None, execution_id: str = None):
        """Log an event to the database"""
        
        self.initialize()
        
        log_data = {
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "source": source,
            "message": message,
            "metadata": json.dumps(metadata or {}),
            "execution_id": execution_id
        }
        
        try:
            with self._lock:
                if self.db_type == "json":
                    logs = self._load_from_json("logs")
                    if not isinstance(logs, list):
                        logs = []
                    logs.append(log_data)
                    # Keep only last 1000 logs
                    if len(logs) > 1000:
                        logs = logs[-1000:]
                    self._save_json_file("logs", logs)
                
                else:  # memory or sqlite fallback
                    if not hasattr(self, 'data'):
                        self.data = {"logs": []}
                    if "logs" not in self.data:
                        self.data["logs"] = []
                    self.data["logs"].append(log_data)
                    # Keep only last 1000 logs
                    if len(self.data["logs"]) > 1000:
                        self.data["logs"] = self.data["logs"][-1000:]
                    
        except Exception as e:
            print(f"Failed to log event: {e}")  # Fallback logging
    
    def log_error(self, message: str, metadata: Dict[str, Any] = None, execution_id: str = None):
        """Log an error event"""
        self.log_event("ERROR", "database", message, metadata, execution_id)
    
    def _save_to_json(self, table_name: str, key: str, data: Dict[str, Any]):
        """Save data to JSON file"""
        existing_data = self._load_from_json(table_name)
        existing_data[key] = data
        self._save_json_file(table_name, existing_data)
    
    def _load_from_json(self, table_name: str) -> Dict[str, Any]:
        """Load data from JSON file"""
        file_path = self.json_files[table_name]
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
    
    def _save_json_file(self, table_name: str, data):
        """Save data to JSON file"""
        file_path = self.json_files[table_name]
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2, default=str)
    
    def cleanup(self):
        """Cleanup database resources (no-op for this implementation)"""
        pass


# Global database instance
database = SimpleLocalDatabase()