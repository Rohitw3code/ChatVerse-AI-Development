"""
Enhanced Execution Engine for Main Agent with Direct Response and Tool Execution
Handles both streaming responses and structured tool execution
"""

import asyncio
import json
from typing import Dict, Any, Optional, AsyncGenerator
from datetime import datetime

from new_agent.core.langgraph_state import StreamingEvent
from new_agent.agents.enhanced_main_agent import enhanced_main_agent


class EnhancedMainExecutionEngine:
    """
    Execution engine for the enhanced main agent
    Handles both direct responses and tool-based execution
    """
    
    def __init__(self):
        self.main_agent = enhanced_main_agent
        self.current_session = None
        
    async def execute_query(
        self, 
        query: str, 
        user_id: str = "default_user"
    ) -> AsyncGenerator[StreamingEvent, None]:
        """
        Execute a query through the enhanced main agent
        Yields streaming events for real-time feedback
        """
        
        session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.current_session = session_id
        
        try:
            # Start execution
            yield StreamingEvent(
                event_type="execution_start",
                content=f"🚀 Processing query: {query[:100]}{'...' if len(query) > 100 else ''}",
                metadata={
                    "session_id": session_id,
                    "user_id": user_id,
                    "query": query,
                    "start_time": datetime.now().isoformat()
                }
            )
            
            # Process through main agent
            async for event in self.main_agent.process_query(query, user_id):
                # Add session metadata to all events
                if hasattr(event, 'metadata') and event.metadata:
                    event.metadata["session_id"] = session_id
                    event.metadata["user_id"] = user_id
                else:
                    event.metadata = {"session_id": session_id, "user_id": user_id}
                
                yield event
            
            # Execution complete
            yield StreamingEvent(
                event_type="execution_complete",
                content="✅ Query execution completed successfully",
                metadata={
                    "session_id": session_id,
                    "user_id": user_id,
                    "end_time": datetime.now().isoformat()
                }
            )
            
        except Exception as e:
            yield StreamingEvent(
                event_type="execution_error",
                content=f"❌ Execution failed: {str(e)}",
                metadata={
                    "session_id": session_id,
                    "user_id": user_id,
                    "error": str(e),
                    "error_time": datetime.now().isoformat()
                }
            )
    
    async def get_conversation_history(self, user_id: str = "default_user") -> Dict[str, Any]:
        """Get conversation history for a user"""
        
        try:
            messages = self.main_agent.conversation_history.get_messages()
            execution_history = self.main_agent.conversation_history.execution_history
            
            return {
                "user_id": user_id,
                "conversation_messages": [
                    {
                        "type": type(msg).__name__,
                        "content": msg.content,
                        "timestamp": getattr(msg, 'timestamp', None)
                    } for msg in messages
                ],
                "execution_history": execution_history,
                "total_messages": len(messages),
                "total_executions": len(execution_history)
            }
            
        except Exception as e:
            return {
                "error": f"Failed to get conversation history: {str(e)}",
                "user_id": user_id
            }
    
    async def clear_conversation_history(self, user_id: str = "default_user") -> Dict[str, Any]:
        """Clear conversation history for a user"""
        
        try:
            # Reset conversation history
            self.main_agent.conversation_history = self.main_agent.conversation_history.__class__()
            
            # Re-add system message
            from langchain_core.messages import SystemMessage
            system_prompt = self.main_agent._create_system_prompt()
            self.main_agent.conversation_history.add_message(SystemMessage(content=system_prompt))
            
            return {
                "success": True,
                "message": f"Conversation history cleared for user {user_id}",
                "user_id": user_id,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to clear conversation history: {str(e)}",
                "user_id": user_id
            }
    
    def get_available_tools(self) -> Dict[str, Any]:
        """Get information about available tools"""
        
        try:
            tool_registry = self.main_agent.semantic_matcher.tool_registry
            
            tools_info = {}
            tool_names = tool_registry.list_tools()
            
            for tool_name in tool_names:
                tool = tool_registry.get_tool(tool_name)
                if tool:
                    tools_info[tool_name] = {
                        "name": tool_name,
                        "description": tool.description,
                        "args_schema": str(tool.args_schema) if hasattr(tool, 'args_schema') else None
                    }
            
            return {
                "available_tools": tools_info,
                "total_tools": len(tools_info),
                "categories": list(self.main_agent.semantic_matcher.semantic_keywords.keys())
            }
            
        except Exception as e:
            return {
                "error": f"Failed to get available tools: {str(e)}",
                "available_tools": {},
                "total_tools": 0
            }
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get current system status"""
        
        try:
            return {
                "status": "operational",
                "main_agent_ready": True,
                "conversation_history_size": len(self.main_agent.conversation_history.messages),
                "execution_history_size": len(self.main_agent.conversation_history.execution_history),
                "current_session": self.current_session,
                "system_time": datetime.now().isoformat(),
                "capabilities": {
                    "direct_response": True,
                    "tool_execution": True,
                    "semantic_search": True,
                    "conversation_history": True,
                    "streaming_response": True
                }
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "system_time": datetime.now().isoformat()
            }


# Global instance
enhanced_main_engine = EnhancedMainExecutionEngine()