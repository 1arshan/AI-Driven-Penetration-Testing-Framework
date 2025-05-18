import pytest
from fastapi.testclient import TestClient
from src.mcp_server.app import app

client = TestClient(app)

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()

def test_create_task_unauthorized():
    response = client.post(
        "/api/task/create",
        headers={"Authorization": "Bearer invalid_token"},
        json={
            "type": "reconnaissance",
            "target": "192.168.1.1",
            "scope": {"ip_range": "192.168.1.0/24"},
            "description": "Test reconnaissance"
        }
    )
    assert response.status_code == 401

def test_create_task_authorized():
    response = client.post(
        "/api/task/create",
        headers={"Authorization": "Bearer dev_token"},
        json={
            "type": "reconnaissance",
            "target": "192.168.1.1",
            "scope": {"ip_range": "192.168.1.0/24"},
            "description": "Test reconnaissance"
        }
    )
    assert response.status_code == 200
    assert "task_id" in response.json()
    assert response.json()["status"] == "created"