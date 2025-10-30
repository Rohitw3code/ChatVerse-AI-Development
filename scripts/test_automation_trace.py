"""
Test script to verify automation trace database operations.
"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from chatagent.db.automation_trace_db import AutomationTraceDB


async def test_automation_trace():
    """Test automation trace save and load operations."""
    
    trace_db = AutomationTraceDB()
    
    # Test data
    test_user_id = "test_user_123"
    test_provider_id = "test_provider_456"
    test_thread_id = "test_thread_789"
    
    test_trace_data = [
        {
            "timestamp": "2025-10-30T12:00:00Z",
            "node": "inputer_agent",
            "event": "routing_decision",
            "agent": "gmail_agent_node",
            "decision": {"goto": "agent_tool_node", "reason": "User wants to send email"}
        },
        {
            "timestamp": "2025-10-30T12:00:01Z",
            "node": "agent_tool_node",
            "event": "tool_call",
            "agent": "gmail_agent_node",
            "tool": "send_gmail",
            "params": {"to": "test@example.com", "subject": "Test Email"}
        }
    ]
    
    print("🧪 Testing Automation Trace Database Operations\n")
    
    # Test 1: Insert new trace
    print("1️⃣ Testing upsert_trace_by_thread (insert)...")
    trace_id = await trace_db.upsert_trace_by_thread(
        user_id=test_user_id,
        provider_id=test_provider_id,
        thread_id=test_thread_id,
        trace_data=test_trace_data,
        name="Test Trace"
    )
    print(f"   ✅ Created trace with ID: {trace_id}\n")
    
    # Test 2: Load trace by ID
    print("2️⃣ Testing load_trace_by_id...")
    loaded_trace = await trace_db.load_trace_by_id(trace_id)
    if loaded_trace:
        print(f"   ✅ Loaded trace:")
        print(f"      - ID: {loaded_trace['id']}")
        print(f"      - Thread ID: {loaded_trace['thread_id']}")
        print(f"      - Entries: {len(loaded_trace['trace_data'])}")
    else:
        print("   ❌ Failed to load trace")
    print()
    
    # Test 3: Update trace with more entries
    print("3️⃣ Testing upsert_trace_by_thread (update)...")
    updated_trace_data = test_trace_data + [
        {
            "timestamp": "2025-10-30T12:00:02Z",
            "node": "final_node",
            "event": "completion",
            "agent": "gmail_agent_node"
        }
    ]
    updated_trace_id = await trace_db.upsert_trace_by_thread(
        user_id=test_user_id,
        provider_id=test_provider_id,
        thread_id=test_thread_id,
        trace_data=updated_trace_data
    )
    print(f"   ✅ Updated trace ID: {updated_trace_id}")
    print(f"   ℹ️  Same ID as before: {updated_trace_id == trace_id}\n")
    
    # Test 4: Load trace by thread
    print("4️⃣ Testing load_trace_by_thread...")
    thread_trace = await trace_db.load_trace_by_thread(test_thread_id)
    if thread_trace:
        print(f"   ✅ Loaded trace from thread:")
        print(f"      - Thread ID: {thread_trace['thread_id']}")
        print(f"      - Entries: {len(thread_trace['trace_data'])}")
        print(f"      - Last entry: {thread_trace['trace_data'][-1]['event']}")
    else:
        print("   ❌ Failed to load trace by thread")
    print()
    
    # Test 5: Get user traces
    print("5️⃣ Testing get_user_traces...")
    user_traces = await trace_db.get_user_traces(
        user_id=test_user_id,
        provider_id=test_provider_id
    )
    print(f"   ✅ Found {len(user_traces)} traces for user")
    for trace in user_traces:
        print(f"      - {trace['id']}: {trace['entry_count']} entries")
    print()
    
    # Test 6: Delete trace
    print("6️⃣ Testing delete_trace...")
    deleted = await trace_db.delete_trace(trace_id)
    if deleted:
        print(f"   ✅ Successfully deleted trace: {trace_id}")
    else:
        print(f"   ❌ Failed to delete trace")
    print()
    
    print("🎉 All tests completed!")


if __name__ == "__main__":
    asyncio.run(test_automation_trace())
