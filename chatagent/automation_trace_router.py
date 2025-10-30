from fastapi import APIRouter, Query, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid

from chatagent.db.automation_trace_db import AutomationTraceDB

automation_trace_router = APIRouter(
    prefix="/automation",
    tags=["Automation Trace"]
)

automation_db = AutomationTraceDB()


class SaveTracePayload(BaseModel):
    user_id: str
    provider_id: str
    thread_id: str
    trace_data: List[Dict[str, Any]]
    name: Optional[str] = None


class UpdateTracePayload(BaseModel):
    trace_id: str
    name: Optional[str] = None
    trace_data: Optional[List[Dict[str, Any]]] = None


class DeployAutomationPayload(BaseModel):
    trace_id: str
    schedule_type: str  # 'daily', 'weekly', 'monthly', 'custom'
    schedule_time: str  # Time or schedule string (e.g., "09:00", "Monday at 3pm")
    schedule_config: Optional[Dict[str, Any]] = None  # Additional config (days, intervals, etc.)
    name: Optional[str] = None  # Optional name for the automation


@automation_trace_router.post("/traces")
async def save_automation_trace(payload: SaveTracePayload):
    """
    Save a new automation trace to the database.
    
    Args:
        payload: Contains user_id, provider_id, thread_id, trace_data, and optional name
    
    Returns:
        JSON response with the created trace ID
    """
    try:
        trace_id = await automation_db.save_trace(
            user_id=payload.user_id,
            provider_id=payload.provider_id,
            thread_id=payload.thread_id,
            trace_data=payload.trace_data,
            name=payload.name
        )
        
        return JSONResponse(
            content={
                "success": True,
                "trace_id": str(trace_id),
                "message": "Automation trace saved successfully"
            },
            status_code=201
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save trace: {str(e)}")


@automation_trace_router.get("/traces/{trace_id}")
async def get_automation_trace(trace_id: str):
    """
    Load an automation trace by its ID.
    
    Args:
        trace_id: UUID of the trace to load
    
    Returns:
        JSON response with the complete trace data
    """
    try:
        trace = await automation_db.load_trace_by_id(trace_id)
        
        if not trace:
            raise HTTPException(status_code=404, detail="Trace not found")
        
        return JSONResponse(content={
            "success": True,
            "trace": trace
        })
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load trace: {str(e)}")


@automation_trace_router.get("/traces/thread/{thread_id}")
async def get_trace_by_thread(thread_id: str):
    """
    Load the most recent automation trace for a given thread_id.
    
    Args:
        thread_id: Thread ID to search for
    
    Returns:
        JSON response with the trace data
    """
    try:
        trace = await automation_db.load_trace_by_thread(thread_id)
        
        if not trace:
            raise HTTPException(status_code=404, detail="No trace found for this thread")
        
        return JSONResponse(content={
            "success": True,
            "trace": trace
        })
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load trace: {str(e)}")


@automation_trace_router.get("/traces")
async def get_user_traces(
    user_id: str = Query(..., description="User ID"),
    provider_id: Optional[str] = Query(None, description="Optional provider ID filter"),
    limit: int = Query(50, description="Number of traces to return", ge=1, le=100),
    offset: int = Query(0, description="Offset for pagination", ge=0)
):
    """
    Get all automation traces for a user with optional filtering and pagination.
    
    Args:
        user_id: User ID to filter by
        provider_id: Optional provider ID to further filter
        limit: Maximum number of results to return (1-100)
        offset: Number of results to skip for pagination
    
    Returns:
        JSON response with list of traces
    """
    try:
        traces = await automation_db.get_user_traces(
            user_id=user_id,
            provider_id=provider_id,
            limit=limit,
            offset=offset
        )
        
        return JSONResponse(content={
            "success": True,
            "traces": traces,
            "count": len(traces)
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch traces: {str(e)}")


@automation_trace_router.patch("/traces/{trace_id}")
async def update_automation_trace(trace_id: str, payload: UpdateTracePayload):
    """
    Update an automation trace (name or trace data).
    
    Args:
        trace_id: UUID of the trace to update
        payload: Contains optional name and/or trace_data to update
    
    Returns:
        JSON response with success message
    """
    try:
        if not payload.name and not payload.trace_data:
            raise HTTPException(status_code=400, detail="No update data provided")
        
        success = await automation_db.update_trace(
            trace_id=trace_id,
            name=payload.name,
            trace_data=payload.trace_data
        )
        
        if not success:
            raise HTTPException(status_code=404, detail="Trace not found")
        
        return JSONResponse(content={
            "success": True,
            "message": "Trace updated successfully"
        })
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update trace: {str(e)}")


@automation_trace_router.delete("/traces/{trace_id}")
async def delete_automation_trace(trace_id: str):
    """
    Delete an automation trace by its ID.
    
    Args:
        trace_id: UUID of the trace to delete
    
    Returns:
        JSON response with success message
    """
    try:
        success = await automation_db.delete_trace(trace_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Trace not found")
        
        return JSONResponse(content={
            "success": True,
            "message": "Trace deleted successfully"
        })
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete trace: {str(e)}")


@automation_trace_router.post("/deploy")
async def deploy_automation(payload: DeployAutomationPayload):
    """
    Deploy an automation with schedule information.
    Updates the trace with deployment status and schedule configuration.
    
    Args:
        payload: Contains trace_id, schedule_type, schedule_time, optional schedule_config and name
    
    Returns:
        JSON response with success message
    """
    try:
        success = await automation_db.deploy_automation(
            trace_id=payload.trace_id,
            schedule_type=payload.schedule_type,
            schedule_time=payload.schedule_time,
            schedule_config=payload.schedule_config,
            name=payload.name
        )
        
        if not success:
            raise HTTPException(status_code=404, detail="Trace not found")
        
        return JSONResponse(content={
            "success": True,
            "message": "Automation deployed successfully",
            "deployment_status": "deployed"
        })
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to deploy automation: {str(e)}")


@automation_trace_router.patch("/deployment-status/{trace_id}")
async def update_deployment_status(trace_id: str, status: str = Query(..., description="New status (draft, deployed, paused, failed)")):
    """
    Update the deployment status of an automation.
    
    Args:
        trace_id: UUID of the trace
        status: New deployment status
    
    Returns:
        JSON response with success message
    """
    try:
        valid_statuses = ['draft', 'deployed', 'paused', 'failed']
        if status not in valid_statuses:
            raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}")
        
        success = await automation_db.update_deployment_status(trace_id, status)
        
        if not success:
            raise HTTPException(status_code=404, detail="Trace not found")
        
        return JSONResponse(content={
            "success": True,
            "message": f"Deployment status updated to '{status}'"
        })
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update deployment status: {str(e)}")
