import requests
import json

print("=== Testing Neo Runtime Gateway ===")

# Test 1: Health Check
print("\n1. Health Check")
try:
    response = requests.get("http://localhost:7777/health")
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.text}")
except Exception as e:
    print(f"   Error: {e}")

# Test 2: Create Session
print("\n2. Create Session")
try:
    payload = {
        "project_path": "res://test/",
        "mode": "default",
        "budget_usd": 10.0,
        "selected_models": []
    }
    response = requests.post("http://localhost:7777/v1/sessions", json=payload)
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        session_id = data["session_id"]
        print(f"   Session ID: {session_id}")
    else:
        print(f"   Response: {response.text}")
except Exception as e:
    print(f"   Error: {e}")

# Test 3: Create Plan
print("\n3. Create Plan")
try:
    payload = {
        "session_id": session_id,
        "goal": "Create a 2D platformer game",
        "context": "Game development with Godot",
        "constraints": {},
        "existing_artifacts": []
    }
    response = requests.post("http://localhost:7777/v1/plan", json=payload)
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   Plan ID: {data['plan_id']}")
        print(f"   Tasks: {len(data['tasks'])}")
        for task in data['tasks'][:3]:
            print(f"     - {task['kind']}: {task['description']}")
except Exception as e:
    print(f"   Error: {e}")

# Test 4: List Sessions
print("\n4. List Sessions")
try:
    response = requests.get("http://localhost:7777/v1/sessions")
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   Sessions: {len(data)}")
except Exception as e:
    print(f"   Error: {e}")

print("\n=== All tests completed ===")