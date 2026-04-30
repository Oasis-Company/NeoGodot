import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy", "service": "neo_runtime_gateway"}

def test_create_session():
    response = client.post(
        "/v1/sessions",
        json={
            "project_path": "res://example_project/",
            "mode": "default",
            "budget_usd": 10.0,
            "selected_models": []
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "session_id" in data
    assert data["project_path"] == "res://example_project/"
    assert data["budget_usd"] == 10.0
    assert data["remaining_budget_usd"] == 10.0

def test_create_plan():
    session_response = client.post(
        "/v1/sessions",
        json={
            "project_path": "res://example_project/",
            "mode": "default",
            "budget_usd": 10.0,
            "selected_models": []
        }
    )
    session_id = session_response.json()["session_id"]
    
    response = client.post(
        "/v1/plan",
        json={
            "session_id": session_id,
            "goal": "Create a 2D platformer level",
            "context": "Game development",
            "constraints": {},
            "existing_artifacts": []
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "plan_id" in data
    assert data["goal"] == "Create a 2D platformer level"
    assert "tasks" in data
    assert len(data["tasks"]) > 0

def test_create_task():
    session_response = client.post(
        "/v1/sessions",
        json={
            "project_path": "res://example_project/",
            "mode": "default",
            "budget_usd": 10.0,
            "selected_models": []
        }
    )
    session_id = session_response.json()["session_id"]
    
    response = client.post(
        "/v1/tasks",
        json={
            "session_id": session_id,
            "kind": "script.generate",
            "priority": "P1",
            "risk_level": "medium",
            "depends_on": [],
            "timeout_ms": 60000,
            "retry_policy": {
                "max_attempts": 3,
                "backoff": "exponential",
                "idempotent": True
            },
            "tool_scope": [],
            "budget": {},
            "success_criteria": [],
            "evidence_refs": [],
            "metadata": {"purpose": "test"}
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "task_id" in data
    assert data["kind"] == "script.generate"

def test_list_sessions():
    client.post(
        "/v1/sessions",
        json={
            "project_path": "res://test_project/",
            "mode": "default",
            "budget_usd": 5.0,
            "selected_models": []
        }
    )
    
    response = client.get("/v1/sessions")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1

if __name__ == "__main__":
    pytest.main([__file__, "-v"])