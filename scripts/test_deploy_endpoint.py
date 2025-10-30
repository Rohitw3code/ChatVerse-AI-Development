"""
Quick test script to verify the deployment endpoint is working.
Run this to test if the backend deployment API is accessible.
"""

import requests
import json

# Configuration
BASE_URL = "http://localhost:8000"  # Change if your backend runs on a different port
DEPLOY_ENDPOINT = f"{BASE_URL}/automation/deploy"

# Test data
test_payload = {
    "trace_id": "test-trace-id-12345",  # Replace with actual trace ID
    "schedule_type": "daily",
    "schedule_time": "09:00",
    "schedule_config": {
        "timezone": "UTC"
    },
    "name": "Test Deployment"
}

print("=" * 80)
print("Testing Automation Deployment Endpoint")
print("=" * 80)
print(f"\nEndpoint: {DEPLOY_ENDPOINT}")
print(f"Payload: {json.dumps(test_payload, indent=2)}")
print("\n" + "=" * 80)

try:
    # Send POST request
    response = requests.post(
        DEPLOY_ENDPOINT,
        json=test_payload,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"\n✅ Request sent successfully!")
    print(f"Status Code: {response.status_code}")
    print(f"Response Headers: {dict(response.headers)}")
    print(f"\nResponse Body:")
    print("-" * 80)
    
    try:
        response_json = response.json()
        print(json.dumps(response_json, indent=2))
    except:
        print(response.text)
    
    print("-" * 80)
    
    if response.ok:
        print("\n✅ SUCCESS! Deployment endpoint is working!")
    else:
        print(f"\n❌ FAILED! Status code: {response.status_code}")
        print("Check the error message above for details.")
        
except requests.exceptions.ConnectionError:
    print("\n❌ CONNECTION ERROR!")
    print("Could not connect to the backend server.")
    print(f"Make sure the server is running at: {BASE_URL}")
    print("\nTo start the backend:")
    print("  1. cd /home/bittu/Desktop/chatverse/ChatVerse-AI-Development")
    print("  2. source venv/bin/activate")
    print("  3. python main.py")
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)
