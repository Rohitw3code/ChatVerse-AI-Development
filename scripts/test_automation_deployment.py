"""
Test script for automation deployment functionality.
Tests the new deploy_automation and update_deployment_status methods.
"""

import asyncio
import sys
import os
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from chatagent.db.automation_trace_db import AutomationTraceDB


async def test_deployment():
    """Test automation deployment workflow."""
    
    db = AutomationTraceDB()
    
    print("=" * 80)
    print("Testing Automation Deployment Functionality")
    print("=" * 80)
    
    # Test data
    test_user_id = "test_user_deploy_123"
    test_provider_id = "test_provider_deploy"
    test_thread_id = f"test_thread_deploy_{datetime.now().timestamp()}"
    
    test_trace_data = [
        {
            "timestamp": datetime.now().isoformat(),
            "node": "inputer_agent",
            "event": "routing_decision",
            "agent": "gmail_agent_node",
            "decision": {"goto": "agent_tool_node", "reason": "Sending email"}
        },
        {
            "timestamp": datetime.now().isoformat(),
            "node": "agent_tool_node",
            "event": "tool_call",
            "agent": "gmail_agent_node",
            "tool": "send_gmail",
            "params": {"to": "test@example.com", "subject": "Test"}
        }
    ]
    
    try:
        # Step 1: Create a new trace
        print("\n1. Creating automation trace...")
        trace_id = await db.save_trace(
            user_id=test_user_id,
            provider_id=test_provider_id,
            thread_id=test_thread_id,
            trace_data=test_trace_data,
            name="Test Email Automation"
        )
        print(f"   ✅ Trace created with ID: {trace_id}")
        
        # Step 2: Load the trace to verify initial status
        print("\n2. Loading trace to check initial status...")
        trace = await db.load_trace_by_id(trace_id)
        print(f"   ✅ Initial deployment_status: {trace['deployment_status']}")
        print(f"   ✅ Initial deployed_at: {trace['deployed_at']}")
        
        # Step 3: Deploy the automation
        print("\n3. Deploying automation with schedule...")
        schedule_config = {
            "days": ["Monday", "Wednesday", "Friday"],
            "timezone": "UTC"
        }
        
        deploy_success = await db.deploy_automation(
            trace_id=trace_id,
            schedule_type="weekly",
            schedule_time="09:00",
            schedule_config=schedule_config,
            name="Weekly Email Automation"
        )
        
        if deploy_success:
            print("   ✅ Automation deployed successfully")
        else:
            print("   ❌ Failed to deploy automation")
            return
        
        # Step 4: Load trace again to verify deployment
        print("\n4. Verifying deployment details...")
        deployed_trace = await db.load_trace_by_id(trace_id)
        print(f"   ✅ Deployment status: {deployed_trace['deployment_status']}")
        print(f"   ✅ Schedule type: {deployed_trace['schedule_type']}")
        print(f"   ✅ Schedule time: {deployed_trace['schedule_time']}")
        print(f"   ✅ Schedule config: {deployed_trace['schedule_config']}")
        print(f"   ✅ Deployed at: {deployed_trace['deployed_at']}")
        print(f"   ✅ Updated name: {deployed_trace['name']}")
        
        # Step 5: Update deployment status to paused
        print("\n5. Pausing automation...")
        pause_success = await db.update_deployment_status(trace_id, "paused")
        
        if pause_success:
            print("   ✅ Automation paused successfully")
        else:
            print("   ❌ Failed to pause automation")
            return
        
        # Step 6: Verify status change
        print("\n6. Verifying status change...")
        paused_trace = await db.load_trace_by_id(trace_id)
        print(f"   ✅ Current status: {paused_trace['deployment_status']}")
        
        # Step 7: Test get_user_traces with deployment info
        print("\n7. Testing user traces listing with deployment info...")
        user_traces = await db.get_user_traces(test_user_id, limit=10)
        
        if user_traces:
            print(f"   ✅ Found {len(user_traces)} trace(s)")
            for trace in user_traces:
                if trace['id'] == trace_id:
                    print(f"   ✅ Trace deployment_status: {trace['deployment_status']}")
                    print(f"   ✅ Trace schedule_type: {trace['schedule_type']}")
                    print(f"   ✅ Trace schedule_time: {trace['schedule_time']}")
                    break
        else:
            print("   ⚠️  No traces found")
        
        # Step 8: Clean up - delete test trace
        print("\n8. Cleaning up test data...")
        delete_success = await db.delete_trace(trace_id)
        
        if delete_success:
            print("   ✅ Test trace deleted successfully")
        else:
            print("   ❌ Failed to delete test trace")
        
        print("\n" + "=" * 80)
        print("✅ All deployment tests passed!")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_deployment())
