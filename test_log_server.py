import os
import pytest
from fastapi.testclient import TestClient
from log_server import app

client = TestClient(app)

def test_log_endpoint(monkeypatch):
    # Mock psycopg2.connect to avoid real DB calls
    class DummyCursor:
        def execute(self, *args, **kwargs):
            pass
        def close(self):
            pass
    class DummyConn:
        def cursor(self):
            return DummyCursor()
        def commit(self):
            pass
        def close(self):
            pass
    monkeypatch.setattr("psycopg2.connect", lambda *a, **kw: DummyConn())

    # Prepare a fake log entry
    log_data = {
        "provider": "openai",
        "model": "gpt-4",
        "prompt_tokens": 10,
        "completion_tokens": 20,
        "cost": 0.00123,
        "status": "success",
        "user_id": "testuser",
        "tenant_id": "testtenant",
        "timestamp": "2024-05-25T12:00:00Z"
    }
    response = client.post("/log", json=log_data)
    assert response.status_code == 200
    assert response.json() == {"status": "logged"}

def test_log_missing_required_field(monkeypatch):
    class DummyCursor:
        def execute(self, *args, **kwargs):
            pass
        def close(self):
            pass
    class DummyConn:
        def cursor(self):
            return DummyCursor()
        def commit(self):
            pass
        def close(self):
            pass
    monkeypatch.setattr("psycopg2.connect", lambda *a, **kw: DummyConn())
    # Missing 'provider'
    log_data = {
        "model": "gpt-4",
        "prompt_tokens": 10,
        "completion_tokens": 20,
        "cost": 0.00123,
        "status": "success",
        "user_id": "testuser",
        "tenant_id": "testtenant",
        "timestamp": "2024-05-25T12:00:00Z"
    }
    response = client.post("/log", json=log_data)
    assert response.status_code == 422

def test_log_invalid_data_type(monkeypatch):
    class DummyCursor:
        def execute(self, *args, **kwargs):
            pass
        def close(self):
            pass
    class DummyConn:
        def cursor(self):
            return DummyCursor()
        def commit(self):
            pass
        def close(self):
            pass
    monkeypatch.setattr("psycopg2.connect", lambda *a, **kw: DummyConn())
    # 'prompt_tokens' should be int, not string
    log_data = {
        "provider": "openai",
        "model": "gpt-4",
        "prompt_tokens": "ten",
        "completion_tokens": 20,
        "cost": 0.00123,
        "status": "success",
        "user_id": "testuser",
        "tenant_id": "testtenant",
        "timestamp": "2024-05-25T12:00:00Z"
    }
    response = client.post("/log", json=log_data)
    assert response.status_code == 422

def test_log_db_error(monkeypatch):
    class DummyCursor:
        def execute(self, *args, **kwargs):
            raise Exception("DB error!")
        def close(self):
            pass
    class DummyConn:
        def cursor(self):
            return DummyCursor()
        def commit(self):
            pass
        def close(self):
            pass
    monkeypatch.setattr("psycopg2.connect", lambda *a, **kw: DummyConn())
    log_data = {
        "provider": "openai",
        "model": "gpt-4",
        "prompt_tokens": 10,
        "completion_tokens": 20,
        "cost": 0.00123,
        "status": "success",
        "user_id": "testuser",
        "tenant_id": "testtenant",
        "timestamp": "2024-05-25T12:00:00Z"
    }
    response = client.post("/log", json=log_data)
    assert response.status_code == 500 or response.status_code == 422

# Stubs for future features:
def test_log_unauthorized():
    pass  # Add when API key auth is implemented

def test_health_endpoint():
    pass  # Add when /health endpoint is implemented

def test_rate_limiting():
    pass  # Add when rate limiting is implemented 