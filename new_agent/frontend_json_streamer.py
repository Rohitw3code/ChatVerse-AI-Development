"""
Frontend JSON Streaming Handler for Enhanced Main Agent
Provides clean JSON output for web frontend integration
"""

import asyncio
import json
import sys
from typing import Dict, Any, Optional
from datetime import datetime

from new_agent.execution.enhanced_main_engine import enhanced_main_engine
from new_agent.core.langgraph_state import StreamingEvent


class FrontendJSONStreamer:
    """
    JSON streamer for frontend integration
    Outputs structured JSON events that can be easily consumed by web frontends
    """
    
    def __init__(self):
        self.engine = enhanced_main_engine
        self.session_data = {}
    
    def format_json_event(self, event: StreamingEvent) -> Dict[str, Any]:
        """Convert StreamingEvent to JSON-friendly format"""
        
        event_data = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event.event_type,
            "content": event.content,
            "metadata": event.metadata or {}
        }
        
        # Add specific fields based on event type
        if hasattr(event, 'token') and event.token:
            event_data["token"] = event.token
        
        if hasattr(event, 'agent_name') and event.agent_name:
            event_data["agent_name"] = event.agent_name
        
        if hasattr(event, 'tool_name') and event.tool_name:
            event_data["tool_name"] = event.tool_name
        
        if hasattr(event, 'tool_input') and event.tool_input:
            event_data["tool_input"] = event.tool_input
        
        if hasattr(event, 'tool_output') and event.tool_output:
            event_data["tool_output"] = str(event.tool_output)
        
        return event_data
    
    async def stream_query_json(self, query: str, user_id: str = "default_user"):
        """Stream query execution as JSON events"""
        
        session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        try:
            # Initialize session
            session_init = {
                "event_type": "session_init",
                "session_id": session_id,
                "user_id": user_id,
                "query": query,
                "timestamp": datetime.now().isoformat()
            }
            print(json.dumps(session_init), flush=True)
            
            # Stream execution events
            async for event in self.engine.execute_query(query, user_id):
                json_event = self.format_json_event(event)
                json_event["session_id"] = session_id
                
                # Output JSON event
                print(json.dumps(json_event), flush=True)
            
            # Session complete
            session_complete = {
                "event_type": "session_complete",
                "session_id": session_id,
                "timestamp": datetime.now().isoformat()
            }
            print(json.dumps(session_complete), flush=True)
            
        except Exception as e:
            # Error event
            error_event = {
                "event_type": "session_error",
                "session_id": session_id,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
            print(json.dumps(error_event), flush=True)
    
    async def get_conversation_history_json(self, user_id: str = "default_user") -> str:
        """Get conversation history as JSON"""
        
        try:
            history = await self.engine.get_conversation_history(user_id)
            return json.dumps(history, indent=2)
        except Exception as e:
            error_response = {
                "error": f"Failed to get conversation history: {str(e)}",
                "user_id": user_id,
                "timestamp": datetime.now().isoformat()
            }
            return json.dumps(error_response, indent=2)
    
    async def get_available_tools_json(self) -> str:
        """Get available tools as JSON"""
        
        try:
            tools_info = self.engine.get_available_tools()
            return json.dumps(tools_info, indent=2)
        except Exception as e:
            error_response = {
                "error": f"Failed to get available tools: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
            return json.dumps(error_response, indent=2)
    
    async def get_system_status_json(self) -> str:
        """Get system status as JSON"""
        
        try:
            status = self.engine.get_system_status()
            return json.dumps(status, indent=2)
        except Exception as e:
            error_response = {
                "error": f"Failed to get system status: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
            return json.dumps(error_response, indent=2)


class TokenStreamHandler:
    """
    Specialized handler for token-by-token streaming
    Optimized for real-time frontend text streaming
    """
    
    def __init__(self):
        self.engine = enhanced_main_engine
    
    async def stream_tokens_only(self, query: str, user_id: str = "default_user"):
        """Stream only tokens for real-time text display with detailed workflow"""
        
        try:
            async for event in self.engine.execute_query(query, user_id):
                if event.event_type == "main_agent_token" and hasattr(event, 'token'):
                    # Output just the token for real-time streaming
                    print(event.token, end='', flush=True)
                    
                elif event.event_type == "agents_analysis":
                    print(f"\n\n📋 AVAILABLE AGENTS ANALYSIS:", flush=True)
                    
                elif event.event_type == "agent_capability":
                    print(f"\n{event.content}", flush=True)
                    
                elif event.event_type == "plan_created":
                    print(f"\n\n🧠 EXECUTION PLAN CREATED:", flush=True)
                    
                elif event.event_type == "plan_step":
                    print(f"\n{event.content}", flush=True)
                    
                elif event.event_type == "research_phase_start":
                    print(f"\n\n🔍 RESEARCH PHASE STARTING:", flush=True)
                    
                elif event.event_type == "internet_search":
                    print(f"\n{event.content}", flush=True)
                    
                elif event.event_type == "data_analysis":
                    print(f"\n{event.content}", flush=True)
                    
                elif event.event_type == "research_complete":
                    print(f"\n{event.content}", flush=True)
                    
                elif event.event_type == "data_gathering_start":
                    print(f"\n\n{event.content}", flush=True)
                    
                elif event.event_type == "tool_start":
                    tool_params = event.tool_input if hasattr(event, 'tool_input') else {}
                    print(f"\n[TOOL_START:{event.tool_name}] with params: {tool_params}", flush=True)
                    
                elif event.event_type == "data_gathered":
                    print(f"\n{event.content}", flush=True)
                    
                elif event.event_type == "tool_end":
                    print(f"[TOOL_END:{event.tool_name}] - Operation completed", flush=True)
                    
                elif event.event_type in ["execution_complete", "main_agent_execution_complete"]:
                    print(f"\n\n✅ ALL STEPS COMPLETED SUCCESSFULLY\n", flush=True)
        
        except Exception as e:
            print(f"\n[ERROR:{str(e)}]", flush=True)


async def main():
    """Main entry point for JSON streaming"""
    
    import argparse
    
    parser = argparse.ArgumentParser(description="Frontend JSON Streamer")
    parser.add_argument("command", choices=["stream", "history", "tools", "status", "tokens"], help="Command to execute")
    parser.add_argument("--query", help="Query to process (for stream/tokens commands)")
    parser.add_argument("--user-id", default="default_user", help="User ID")
    
    args = parser.parse_args()
    
    if args.command == "stream":
        if not args.query:
            error = {"error": "Query required for stream command", "timestamp": datetime.now().isoformat()}
            print(json.dumps(error))
            return
        
        streamer = FrontendJSONStreamer()
        await streamer.stream_query_json(args.query, args.user_id)
    
    elif args.command == "tokens":
        if not args.query:
            print("[ERROR:Query required for tokens command]")
            return
        
        handler = TokenStreamHandler()
        await handler.stream_tokens_only(args.query, args.user_id)
    
    elif args.command == "history":
        streamer = FrontendJSONStreamer()
        history_json = await streamer.get_conversation_history_json(args.user_id)
        print(history_json)
    
    elif args.command == "tools":
        streamer = FrontendJSONStreamer()
        tools_json = await streamer.get_available_tools_json()
        print(tools_json)
    
    elif args.command == "status":
        streamer = FrontendJSONStreamer()
        status_json = await streamer.get_system_status_json()
        print(status_json)


if __name__ == "__main__":
    asyncio.run(main())