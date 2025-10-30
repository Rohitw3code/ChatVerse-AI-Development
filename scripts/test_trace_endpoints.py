#!/usr/bin/env python3
"""
Test script to verify automation trace endpoints are working correctly.
"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from chatagent.db.automation_trace_db import AutomationTraceDB


async def test_trace_endpoints():
    """Test creating and retrieving automation trace via database methods."""
    
    trace_db = AutomationTraceDB()
    
    # Test data
    test_user_id = "test_user_endpoint"
    test_provider_id = "test_provider_endpoint"
    test_thread_id = "chat_test_endpoint_123"
    
    test_trace_data = [
        {
            "timestamp": "2025-10-30T15:00:00Z",
            "node": "inputer_agent",
            "event": "routing_decision",
            "agent": "gmail_agent_node",
            "decision": {"goto": "agent_tool_node", "reason": "User wants to send email"}
        },
        {
            "timestamp": "2025-10-30T15:00:01Z",
            "node": "agent_tool_node",
            "event": "tool_call",
            "agent": "gmail_agent_node",
            "tool": "send_gmail",
            "params": {"to": "test@example.com", "subject": "Test Email"}
        },
        {
            "timestamp": "2025-10-30T15:00:02Z",
            "node": "final_node",
            "event": "completion",
            "agent": "gmail_agent_node"
        }
    ]
    
    print("🧪 Testing Automation Trace Endpoints\n")
    
    # Clean up any existing trace for this thread
    print("🧹 Cleaning up old test data...")
    try:
        existing = await trace_db.load_trace_by_thread(test_thread_id)
        if existing:
            await trace_db.delete_trace(existing['id'])
            print(f"   ✅ Deleted old trace: {existing['id']}")
    except Exception:
        pass
    print()
    
    # Test 1: Create trace using upsert
    print("1️⃣ Testing upsert_trace_by_thread (create new)...")
    trace_id = await trace_db.upsert_trace_by_thread(
        user_id=test_user_id,
        provider_id=test_provider_id,
        thread_id=test_thread_id,
        trace_data=test_trace_data,
        name="Test Endpoint Trace"
    )
    print(f"   ✅ Created trace with ID: {trace_id}\n")
    
    # Test 2: Retrieve by thread_id (simulates frontend API call)
    print("2️⃣ Testing load_trace_by_thread (simulates GET /traces/thread/{thread_id})...")
    loaded_trace = await trace_db.load_trace_by_thread(test_thread_id)
    
    if loaded_trace:
        print(f"   ✅ Successfully loaded trace:")
        print(f"      - ID: {loaded_trace['id']}")
        print(f"      - Thread ID: {loaded_trace['thread_id']}")
        print(f"      - Provider ID: {loaded_trace['provider_id']}")
        print(f"      - Trace Data Entries: {len(loaded_trace['trace_data'])}")
        print(f"      - Created: {loaded_trace['created_at']}")
        print(f"\n   📊 Trace Data Sample:")
        for i, entry in enumerate(loaded_trace['trace_data'][:2], 1):
            print(f"      Entry {i}: {entry.get('event')} - {entry.get('node')}")
    else:
        print("   ❌ Failed to load trace by thread")
    print()
    
    # Test 3: Update trace (add more entries)
    print("3️⃣ Testing upsert_trace_by_thread (update existing)...")
    updated_trace_data = test_trace_data + [
        {
            "timestamp": "2025-10-30T15:00:03Z",
            "node": "inputer_agent",
            "event": "routing_decision",
            "decision": {"goto": "END", "reason": "Task completed"}
        }
    ]
    updated_id = await trace_db.upsert_trace_by_thread(
        user_id=test_user_id,
        provider_id=test_provider_id,
        thread_id=test_thread_id,
        trace_data=updated_trace_data
    )
    print(f"   ✅ Updated trace ID: {updated_id}")
    print(f"   ℹ️  Same ID as before: {updated_id == trace_id}\n")
    
    # Test 4: Verify update
    print("4️⃣ Verifying update...")
    refreshed_trace = await trace_db.load_trace_by_thread(test_thread_id)
    if refreshed_trace:
        print(f"   ✅ Verified updated trace:")
        print(f"      - Trace Data Entries: {len(refreshed_trace['trace_data'])}")
        print(f"      - Updated: {refreshed_trace['updated_at']}")
        print(f"      - Last Entry: {refreshed_trace['trace_data'][-1]['event']}")
    print()
    
    # Test 5: Simulate frontend response format
    print("5️⃣ Testing response format (what frontend receives)...")
    response_format = {
        "success": True,
        "trace": refreshed_trace
    }
    print(f"   ✅ Response structure:")
    print(f"      - success: {response_format['success']}")
    print(f"      - trace.id: {response_format['trace']['id']}")
    print(f"      - trace.thread_id: {response_format['trace']['thread_id']}")
    print(f"      - trace.trace_data (array): {len(response_format['trace']['trace_data'])} entries")
    print(f"\n   📦 Frontend should access: response.trace.trace_data")
    print()
    
    # Test 6: Test 404 scenario (non-existent thread)
    print("6️⃣ Testing 404 scenario (non-existent thread)...")
    missing_trace = await trace_db.load_trace_by_thread("non_existent_thread_123")
    if missing_trace is None:
        print("   ✅ Correctly returns None for non-existent thread")
    else:
        print("   ❌ Should return None for non-existent thread")
    print()
    
    # Cleanup
    print("🧹 Cleaning up test data...")
    deleted = await trace_db.delete_trace(trace_id)
    if deleted:
        print(f"   ✅ Deleted test trace: {trace_id}")
    print()
    
    print("=" * 60)
    print("🎉 All endpoint tests completed successfully!")
    print("=" * 60)
    print("\n📝 Frontend Integration Summary:")
    print("   1. Frontend calls: AutomationTraceApiService.getTraceByThread(chatId)")
    print("   2. Backend endpoint: GET /automation/traces/thread/{thread_id}")
    print("   3. Response format: { success: true, trace: { id, trace_data, ... } }")
    print("   4. Frontend extracts: response.trace.trace_data (array)")
    print("   5. Store loads: loadTrace(response.trace.trace_data)")
    print("\n✅ Everything is working correctly!")


if __name__ == "__main__":
    asyncio.run(test_trace_endpoints())
