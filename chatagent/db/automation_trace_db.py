from chatagent.db.database_manager import DatabaseManager
from typing import Optional, List, Dict, Any
import json
import uuid


class AutomationTraceDB:
    """Database operations for automation traces."""

    def __init__(self):
        self.db_manager = DatabaseManager()

    async def save_trace(
        self,
        user_id: str,
        provider_id: str,
        thread_id: str,
        trace_data: List[Dict[str, Any]],
        name: Optional[str] = None
    ) -> str:
        """
        Save a new automation trace to the database.
        
        Args:
            user_id: User identifier
            provider_id: Provider identifier
            thread_id: Thread identifier
            trace_data: List of trace entries
            name: Optional name for the trace
        
        Returns:
            UUID of the created trace
        """
        pool = await self.db_manager.get_pool()
        async with pool.connection() as conn:
            result = await conn.execute(
                """
                INSERT INTO automation_traces (
                    user_id, provider_id, thread_id, name, trace_data
                ) VALUES (%s, %s, %s, %s, %s)
                RETURNING id
                """,
                (user_id, provider_id, thread_id, name, json.dumps(trace_data))
            )
            row = await result.fetchone()
            return str(row["id"])

    async def load_trace_by_id(self, trace_id: str) -> Optional[Dict[str, Any]]:
        """
        Load an automation trace by its ID.
        
        Args:
            trace_id: UUID of the trace
        
        Returns:
            Dictionary with trace information or None if not found
        """
        pool = await self.db_manager.get_pool()
        async with pool.connection() as conn:
            result = await conn.execute(
                """
                SELECT id, user_id, provider_id, thread_id, name, trace_data, 
                       deployment_status, schedule_type, schedule_time, schedule_config,
                       deployed_at, created_at, updated_at
                FROM automation_traces
                WHERE id = %s
                """,
                (trace_id,)
            )
            row = await result.fetchone()
            
            if not row:
                return None
            
            return {
                "id": str(row["id"]),
                "user_id": row["user_id"],
                "provider_id": row["provider_id"],
                "thread_id": row["thread_id"],
                "name": row["name"],
                "trace_data": row["trace_data"],
                "deployment_status": row["deployment_status"],
                "schedule_type": row["schedule_type"],
                "schedule_time": row["schedule_time"],
                "schedule_config": row["schedule_config"],
                "deployed_at": row["deployed_at"].isoformat() if row["deployed_at"] else None,
                "created_at": row["created_at"].isoformat() if row["created_at"] else None,
                "updated_at": row["updated_at"].isoformat() if row["updated_at"] else None
            }

    async def load_trace_by_thread(self, thread_id: str) -> Optional[Dict[str, Any]]:
        """
        Load the most recent automation trace for a given thread_id.
        
        Args:
            thread_id: Thread identifier
        
        Returns:
            Dictionary with trace information or None if not found
        """
        pool = await self.db_manager.get_pool()
        async with pool.connection() as conn:
            result = await conn.execute(
                """
                SELECT id, user_id, provider_id, thread_id, name, trace_data, 
                       deployment_status, schedule_type, schedule_time, schedule_config,
                       deployed_at, created_at, updated_at
                FROM automation_traces
                WHERE thread_id = %s
                ORDER BY created_at DESC
                LIMIT 1
                """,
                (thread_id,)
            )
            row = await result.fetchone()
            
            if not row:
                return None
            
            return {
                "id": str(row["id"]),
                "user_id": row["user_id"],
                "provider_id": row["provider_id"],
                "thread_id": row["thread_id"],
                "name": row["name"],
                "trace_data": row["trace_data"],
                "deployment_status": row["deployment_status"],
                "schedule_type": row["schedule_type"],
                "schedule_time": row["schedule_time"],
                "schedule_config": row["schedule_config"],
                "deployed_at": row["deployed_at"].isoformat() if row["deployed_at"] else None,
                "created_at": row["created_at"].isoformat() if row["created_at"] else None,
                "updated_at": row["updated_at"].isoformat() if row["updated_at"] else None
            }

    async def get_user_traces(
        self,
        user_id: str,
        provider_id: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Get all automation traces for a user with optional filtering.
        
        Args:
            user_id: User identifier
            provider_id: Optional provider identifier filter
            limit: Maximum number of results
            offset: Number of results to skip
        
        Returns:
            List of trace dictionaries
        """
        pool = await self.db_manager.get_pool()
        async with pool.connection() as conn:
            if provider_id:
                query = """
                    SELECT id, user_id, provider_id, thread_id, name, 
                           deployment_status, schedule_type, schedule_time,
                           deployed_at, created_at, updated_at,
                           jsonb_array_length(trace_data) as entry_count
                    FROM automation_traces
                    WHERE user_id = %s AND provider_id = %s
                    ORDER BY created_at DESC
                    LIMIT %s OFFSET %s
                """
                params = (user_id, provider_id, limit, offset)
            else:
                query = """
                    SELECT id, user_id, provider_id, thread_id, name, 
                           deployment_status, schedule_type, schedule_time,
                           deployed_at, created_at, updated_at,
                           jsonb_array_length(trace_data) as entry_count
                    FROM automation_traces
                    WHERE user_id = %s
                    ORDER BY created_at DESC
                    LIMIT %s OFFSET %s
                """
                params = (user_id, limit, offset)
            
            result = await conn.execute(query, params)
            rows = await result.fetchall()
            
            traces = []
            for row in rows:
                traces.append({
                    "id": str(row["id"]),
                    "user_id": row["user_id"],
                    "provider_id": row["provider_id"],
                    "thread_id": row["thread_id"],
                    "name": row["name"],
                    "deployment_status": row["deployment_status"],
                    "schedule_type": row["schedule_type"],
                    "schedule_time": row["schedule_time"],
                    "deployed_at": row["deployed_at"].isoformat() if row["deployed_at"] else None,
                    "created_at": row["created_at"].isoformat() if row["created_at"] else None,
                    "updated_at": row["updated_at"].isoformat() if row["updated_at"] else None,
                    "entry_count": row["entry_count"]
                })
            
            return traces

    async def update_trace(
        self,
        trace_id: str,
        name: Optional[str] = None,
        trace_data: Optional[List[Dict[str, Any]]] = None
    ) -> bool:
        """
        Update an automation trace.
        
        Args:
            trace_id: UUID of the trace
            name: Optional new name
            trace_data: Optional new trace data
        
        Returns:
            True if updated, False if not found
        """
        pool = await self.db_manager.get_pool()
        async with pool.connection() as conn:
            update_parts = []
            params = []
            
            if name is not None:
                update_parts.append("name = %s")
                params.append(name)
            
            if trace_data is not None:
                update_parts.append("trace_data = %s")
                params.append(json.dumps(trace_data))
            
            if not update_parts:
                return False
            
            params.append(trace_id)
            
            query = f"""
                UPDATE automation_traces
                SET {', '.join(update_parts)}
                WHERE id = %s
                RETURNING id
            """
            
            result = await conn.execute(query, tuple(params))
            row = await result.fetchone()
            
            return row is not None

    async def delete_trace(self, trace_id: str) -> bool:
        """
        Delete an automation trace.
        
        Args:
            trace_id: UUID of the trace
        
        Returns:
            True if deleted, False if not found
        """
        pool = await self.db_manager.get_pool()
        async with pool.connection() as conn:
            result = await conn.execute(
                """
                DELETE FROM automation_traces
                WHERE id = %s
                RETURNING id
                """,
                (trace_id,)
            )
            row = await result.fetchone()
            
            return row is not None

    async def upsert_trace_by_thread(
        self,
        user_id: str,
        provider_id: str,
        thread_id: str,
        trace_data: List[Dict[str, Any]],
        name: Optional[str] = None
    ) -> str:
        """
        Insert or update automation trace for a thread.
        Creates new trace if none exists for the thread, otherwise updates existing.
        
        Args:
            user_id: User identifier
            provider_id: Provider identifier
            thread_id: Thread identifier
            trace_data: Complete list of trace entries
            name: Optional name for the trace
        
        Returns:
            UUID of the trace (created or updated)
        """
        pool = await self.db_manager.get_pool()
        async with pool.connection() as conn:
            # Check if trace exists for this thread
            result = await conn.execute(
                """
                SELECT id FROM automation_traces
                WHERE thread_id = %s AND provider_id = %s
                ORDER BY created_at DESC
                LIMIT 1
                """,
                (thread_id, provider_id)
            )
            row = await result.fetchone()
            
            if row:
                # Update existing trace
                trace_id = str(row["id"])
                await conn.execute(
                    """
                    UPDATE automation_traces
                    SET trace_data = %s, updated_at = NOW()
                    WHERE id = %s
                    """,
                    (json.dumps(trace_data), trace_id)
                )
                return trace_id
            else:
                # Create new trace
                result = await conn.execute(
                    """
                    INSERT INTO automation_traces (
                        user_id, provider_id, thread_id, name, trace_data
                    ) VALUES (%s, %s, %s, %s, %s)
                    RETURNING id
                    """,
                    (user_id, provider_id, thread_id, name, json.dumps(trace_data))
                )
                row = await result.fetchone()
                return str(row["id"])

    async def deploy_automation(
        self,
        trace_id: str,
        schedule_type: str,
        schedule_time: str,
        schedule_config: Optional[Dict[str, Any]] = None,
        name: Optional[str] = None
    ) -> bool:
        """
        Deploy an automation by updating its deployment status and schedule information.
        
        Args:
            trace_id: UUID of the trace to deploy
            schedule_type: Type of schedule (daily, weekly, monthly, custom)
            schedule_time: Time or schedule configuration
            schedule_config: Additional schedule configuration (days, intervals, etc.)
            name: Optional name for the automation
        
        Returns:
            True if deployed successfully, False if not found
        """
        pool = await self.db_manager.get_pool()
        async with pool.connection() as conn:
            update_parts = [
                "deployment_status = %s",
                "schedule_type = %s",
                "schedule_time = %s",
                "schedule_config = %s",
                "deployed_at = NOW()"
            ]
            params = [
                "deployed",
                schedule_type,
                schedule_time,
                json.dumps(schedule_config) if schedule_config else None
            ]
            
            if name is not None:
                update_parts.append("name = %s")
                params.append(name)
            
            params.append(trace_id)
            
            query = f"""
                UPDATE automation_traces
                SET {', '.join(update_parts)}
                WHERE id = %s
                RETURNING id
            """
            
            result = await conn.execute(query, tuple(params))
            row = await result.fetchone()
            
            return row is not None

    async def update_deployment_status(
        self,
        trace_id: str,
        status: str
    ) -> bool:
        """
        Update the deployment status of an automation.
        
        Args:
            trace_id: UUID of the trace
            status: New status (draft, deployed, paused, failed)
        
        Returns:
            True if updated, False if not found
        """
        pool = await self.db_manager.get_pool()
        async with pool.connection() as conn:
            result = await conn.execute(
                """
                UPDATE automation_traces
                SET deployment_status = %s
                WHERE id = %s
                RETURNING id
                """,
                (status, trace_id)
            )
            row = await result.fetchone()
            
            return row is not None
