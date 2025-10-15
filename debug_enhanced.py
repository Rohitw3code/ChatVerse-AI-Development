"""
Debug script for enhanced LangGraph system
"""

import asyncio
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

async def test_enhanced_system():
    """Test the enhanced system step by step"""
    
    from new_agent.execution.enhanced_langgraph_engine import enhanced_langgraph_engine
    
    try:
        print("🔍 Testing Enhanced LangGraph System")
        print("=" * 50)
        
        # Test 1: Check agents initialization
        print("1. Testing agent initialization...")
        agents_info = enhanced_langgraph_engine.get_available_agents()
        print(f"   ✅ Found {len(agents_info)} agents: {list(agents_info.keys())}")
        
        # Test 2: Test simple streaming
        print("\n2. Testing streaming execution...")
        query = "Hello world test"
        user_id = "test_user"
        
        event_count = 0
        async for event in enhanced_langgraph_engine.execute_query_with_streaming(query, user_id):
            event_count += 1
            print(f"   Event {event_count}: {event.event_type} - {event.content[:80]}...")
            
            # Stop after reasonable number of events for debugging
            if event_count >= 20:
                print("   📝 Stopping after 20 events...")
                break
        
        print(f"   ✅ Received {event_count} events")
        print("\n✅ Enhanced system test completed!")
        
    except Exception as e:
        import traceback
        print(f"❌ Test failed: {e}")
        print("Full traceback:")
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_enhanced_system())