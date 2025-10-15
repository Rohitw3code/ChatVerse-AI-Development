"""
JSON Stream Output for Frontend Integration
Provides structured JSON events for frontend consumption
"""

import asyncio
import json
import sys
from datetime import datetime
from typing import Dict, Any

from new_agent.execution.enhanced_langgraph_engine import enhanced_langgraph_engine


class JSONStreamProcessor:
    """Process streaming events and output structured JSON for frontend"""
    
    def __init__(self):
        self.event_count = 0
        self.session_start = datetime.now()
    
    async def stream_to_json(self, query: str, user_id: str = "default"):
        """Stream execution events as JSON objects"""
        
        try:
            async for event in enhanced_langgraph_engine.execute_query_with_streaming(query, user_id):
                self.event_count += 1
                
                # Convert streaming event to JSON structure
                json_event = {
                    "event_id": self.event_count,
                    "timestamp": datetime.now().isoformat(),
                    "session_start": self.session_start.isoformat(),
                    "event_type": event.event_type,
                    "content": event.content,
                    "agent_name": getattr(event, 'agent_name', None),
                    "step_number": getattr(event, 'step_number', None),
                    "tool_name": getattr(event, 'tool_name', None),
                    "tool_input": getattr(event, 'tool_input', None),
                    "tool_output": getattr(event, 'tool_output', None),
                    "token": getattr(event, 'token', None),
                    "metadata": getattr(event, 'metadata', {})
                }
                
                # Output JSON event
                print(json.dumps(json_event, default=str, ensure_ascii=False))
                sys.stdout.flush()
                
        except Exception as e:
            # Output error as JSON
            error_event = {
                "event_id": self.event_count + 1,
                "timestamp": datetime.now().isoformat(),
                "session_start": self.session_start.isoformat(),
                "event_type": "system_error",
                "content": f"System error: {str(e)}",
                "error": str(e),
                "metadata": {}
            }
            print(json.dumps(error_event, default=str, ensure_ascii=False))
            sys.stdout.flush()


async def main():
    """Main function for JSON streaming"""
    if len(sys.argv) < 2:
        print(json.dumps({
            "event_type": "error",
            "content": "Usage: python json_stream.py 'Your query here'",
            "timestamp": datetime.now().isoformat()
        }))
        return
    
    query = sys.argv[1]
    user_id = sys.argv[2] if len(sys.argv) > 2 else "default"
    
    processor = JSONStreamProcessor()
    await processor.stream_to_json(query, user_id)


if __name__ == "__main__":
    asyncio.run(main())