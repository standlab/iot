import pytest
from fastapi.testclient import TestClient
from src.iot_regestration_server.main import app, hash_mac
import json

client = TestClient(app)

@pytest.fixture(scope="session")
def temp_files(tmp_path):
    data_file = tmp_path / "devices.json"
    config_file = tmp_path / "configs.json"
    data_file.write_text(json.dumps({}))
    config_file.write_text(json.dumps({}))
    return str(data_file), str(config_file)

def test_register_device():
    device_data = {
        "mac_address": "00:1A:2B:3C:4D:5E",
        "location": {"lat": 12.34, "lon": 56.78},
        "city": "TestCity",
        "owner": "TestCompany",
        "measurement_type": "temperature",
        "sensor_model": "T1000"
    }
    response = client.post("/register/", json=device_data)
    assert response.status_code == 200
    data = response.json()
    assert "device_id" in data
    assert "topic" in data

def test_register_duplicate_device(temp_files):
    test_register_device(temp_files)
    device_data = {
        "mac_address": "00:1A:2B:3C:4D:5E",
        "location": {"lat": 12.34, "lon": 56.78},
        "city": "TestCity",
        "owner": "TestCompany",
        "measurement_type": "temperature",
        "sensor_model": "T1000"
    }
    response = client.post("/register/", json=device_data)
    assert response.status_code == 400

def test_get_device(temp_files):
    test_register_device(temp_files)
    device_id = hash_mac("00:1A:2B:3C:4D:5E")
    response = client.get(f"/devices/{device_id}")
    assert response.status_code == 200
    assert response.json()["device_id"] == device_id

def test_get_nonexistent_device():
    response = client.get("/devices/nonexistent_id")
    assert response.status_code == 404

def test_delete_device(temp_files):
    test_register_device(temp_files)
    device_id = hash_mac("00:1A:2B:3C:4D:5E")
    response = client.delete(f"/devices/{device_id}")
    assert response.status_code == 200
    assert response.json() == {"message": "Device deleted"}

def test_update_device(temp_files):
    test_register_device(temp_files)
    device_id = hash_mac("00:1A:2B:3C:4D:5E")
    update_data = {
        "mac_address": "00:1A:2B:3C:4D:5E",
        "location": {"lat": 98.76, "lon": 54.32},
        "city": "NewCity",
        "owner": "NewCompany",
        "measurement_type": "pressure",
        "sensor_model": "P2000"
    }
    response = client.put(f"/devices/{device_id}", json=update_data)
    assert response.status_code == 200
    assert response.json()["city"] == "NewCity"

def test_get_mqtt_topic(temp_files):
    test_register_device(temp_files)
    device_id = hash_mac("00:1A:2B:3C:4D:5E")
    response = client.get(f"/topics/{device_id}")
    assert response.status_code == 200
    assert "topic" in response.json()

def test_set_and_get_config(temp_files):
    device_id = hash_mac("00:1A:2B:3C:4D:5E")
    config_data = {
        "data_cadence": 30,
        "retention_policy": "14d",
        "qos": 1,
        "last_updated": "2025-02-20T12:00:00Z"
    }
    response = client.post(f"/configs/{device_id}", json=config_data)
    assert response.status_code == 200
    response = client.get(f"/configs/{device_id}")
    assert response.status_code == 200
    assert response.json()["data_cadence"] == 30

def test_get_nonexistent_config():
    response = client.get("/configs/nonexistent_id")
    assert response.status_code == 404
