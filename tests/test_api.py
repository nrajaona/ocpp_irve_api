import os
import pytest
import logging
from fastapi.testclient import TestClient
from app.main import app

# Configurer la journalisation
#logging.basicConfig(level=logging.INFO)

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello, World!"}

def test_get_status():
    response = client.get("/status")
    print(f"Réponse de /status: {response.json()}")
    assert response.status_code == 200
    json_response = response.json()
    assert "connectorId" in json_response
    assert "errorCode" in json_response
    assert "status" in json_response
    assert "timestamp" in json_response
    assert "info" in json_response
    assert "vendorId" in json_response
    assert "vendorErrorCode" in json_response

def test_start_charging():
    response = client.post("/start")
    print(f"Réponse de /start: {response.json()}")
    assert response.status_code == 200
    assert "message" in response.json() or "error" in response.json()

def test_stop_charging():
    response = client.post("/stop")
    print(f"Réponse de /stop: {response.json()}")
    assert response.status_code == 200
    assert "message" in response.json() or "error" in response.json()

def test_test_websocket_endpoint():
    response = client.get("/test-websocket")
    print(f"Réponse de /test-websocket: {response.json()}")
    assert response.status_code == 200
    assert "message" in response.json() or "error" in response.json()

def test_heartbeat():
    response = client.get("/heartbeat")
    print(f"Réponse de /heartbeat: {response.json()}")
    assert response.status_code == 200
    assert "current_time" in response.json()

def test_meter_values():
    response = client.post("/meter-values")
    print(f"Réponse de /meter-values: {response.json()}")
    assert response.status_code == 200
    assert "meter_value" in response.json()

def test_authorize():
    response = client.post("/authorize", json={"id_tag": "test_id_tag"})
    print(f"Réponse de /authorize: {response.json()}")
    assert response.status_code == 200
    assert "id_tag_info" in response.json()

def test_unlock_connector():
    response = client.post("/unlock-connector", json={"connector_id": 1})
    print(f"Réponse de /unlock-connector: {response.json()}")
    assert response.status_code == 200
    assert "status" in response.json() or "error" in response.json()

def test_remote_start_transaction():
    response = client.post("/remote-start-transaction", json={"id_tag": "test_id_tag", "connector_id": 1})
    print(f"Réponse de /remote-start-transaction: {response.json()}")
    assert response.status_code == 200
    assert "status" in response.json() or "error" in response.json()

def test_remote_stop_transaction():
    response = client.post("/remote-stop-transaction", json={"transaction_id": 1})
    print(f"Réponse de /remote-stop-transaction: {response.json()}")
    assert response.status_code == 200
    assert "status" in response.json() or "error" in response.json()

def test_get_configuration():
    response = client.post("/get-configuration", json={"key": ["key1", "key2"]})
    print(f"Réponse de /get-configuration: {response.json()}")
    assert response.status_code == 200
    assert "configuration_key" in response.json() or "error" in response.json()

def test_change_configuration():
    response = client.post("/change-configuration", json={"key": "some_key", "value": "some_value"})
    assert response.status_code == 200
    assert "status" in response.json() or "error" in response.json()