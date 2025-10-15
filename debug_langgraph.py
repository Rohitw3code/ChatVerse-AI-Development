"""
Simple test script to debug the LangGraph issue
"""

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from new_agent.core.langgraph_state import create_initial_state, AgentState
from new_agent.execution.langgraph_engine import langgraph_execution_engine

async def test_simple_execution():
    """Test basic execution"""
    try:
        print("Testing simple query execution...")
        
        query = "Hello world"
        user_id = "test_user"
        
        # Test state creation
        print("Creating initial state...")
        state = create_initial_state(query, user_id)
        print(f"Initial state created: {state['query']}")
        
        # Test streaming execution
        print("Starting streaming execution...")
        event_count = 0
        async for event in langgraph_execution_engine.execute_query_with_streaming(query, user_id):
            event_count += 1
            print(f"Event {event_count}: {event.event_type} - {event.content[:100]}")
            
            if event_count > 50:  # Allow more events to see the error
                print("Completed 50 events successfully!")
                break
                
        print("Test completed successfully!")
        
    except Exception as e:
        import traceback
        print(f"Error in test: {e}")
        print("Full traceback:")
        traceback.print_exc()

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_simple_execution())