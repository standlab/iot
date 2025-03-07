from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, Field
from enum import Enum
import hashlib
import os
import json
import tempfile

app = FastAPI()

DATA_FILE = os.path.join(tempfile.gettempdir(), "devices.json")
CONFIG_FILE = os.path.join(tempfile.gettempdir(), "configs.json")

def load_data(file_path):
    if os.path.exists(file_path):
        with open(file_path, "r") as file:
            return json.load(file)
    return {}

def save_data(file_path, data):
    with open(file_path, "w") as file:
        json.dump(data, file, indent=4)

def data_file():
    return DATA_FILE

def config_file():
    return CONFIG_FILE

devices = load_data(DATA_FILE)
configs = load_data(CONFIG_FILE)

def hash_mac(mac: str) -> str:
    return hashlib.sha256(mac.encode()).hexdigest()[:16]

class MeasurementType(str, Enum):
    TEMPERATURE = "temperature"
    LUMINOCITY = "luminocity"
    
class DeviceRegistration(BaseModel):
    mac_address: str = Field("00:00:00:00:00:00")
    longitude: float = Field(101.7121)
    latitude: float = Field(56.2928)
    height: float = Field(428)
    city: str = Field("Bratsk")
    owner: str = Field("Lyceum")
    measurement_type: str = Field(
        MeasurementType.TEMPERATURE, 
        description=f"Measurements types: {[e.value for e in MeasurementType]}"
    )
    sensor_model: str = Field(..., description="Put particular sensor model name here")

class DeviceRetrieveByMac(BaseModel):
    mac_address: str = Field("00:00:00:00:00:00")

class ConfigSettings(BaseModel):
    data_cadence: int = Field(60, description="Data transmission interval in seconds")
    qos: int = Field(0, description="MQTT Quality of Service level")
    last_updated: str = Field(..., description="Timestamp of last update")

@app.post("/register/", response_model=dict)
def register_device(device: DeviceRegistration):
    device_id = hash_mac(device.mac_address)
    topic = f"{device.owner}/{device.city}/{device.measurement_type}/{device_id}"
    
    if device_id in devices:
        raise HTTPException(status_code=400, detail="Device already registered")
    
    devices[device_id] = {"device_id": device_id, "topic": topic, **device.model_dump()}
    save_data(DATA_FILE, devices)
    return {"device_id": device_id, "topic": topic}

@app.get("/devices", response_model=dict)
def get_all_devices(owner: str):
    result = {}
    for device in devices.values():
        if device["owner"] == owner:
            result[device["device_id"]] = device                

    if not result:
        raise HTTPException(status_code=404, detail="No devices found for owner")
    return result

@app.get("/device/{device_id}", response_model=dict)
def get_device(device_id: str):
    if device_id not in devices:
        raise HTTPException(status_code=404, detail="Device not found")
    return devices[device_id]

@app.post("/device_by_mac/", response_model=dict)
def get_device_by_mac(device: DeviceRetrieveByMac):
    device_id = hash_mac(device.mac_address)
    if device_id not in devices:
        raise HTTPException(status_code=404, detail="Device not found")
    return devices[device_id]

@app.delete("/device/{device_id}")
def delete_device(device_id: str):
    if device_id not in devices:
        raise HTTPException(status_code=404, detail="Device not found")
    del devices[device_id]
    save_data(DATA_FILE, devices)
    return {"message": "Device deleted"}

@app.put("/device/{device_id}", response_model=dict)
def update_device(device_id: str, updated_data: DeviceRegistration):
    if device_id not in devices:
        raise HTTPException(status_code=404, detail="Device not found")
    
    topic = f"{updated_data.owner}/{updated_data.city}/{updated_data.measurement_type}/{device_id}"
    devices[device_id] = {"device_id": device_id, "topic": topic, **updated_data.model_dump()}
    save_data(DATA_FILE, devices)
    return devices[device_id]

@app.get("/topics/{device_id}", response_model=dict)
def get_mqtt_topic(device_id: str):
    if device_id not in devices:
        raise HTTPException(status_code=404, detail="Device not found")
    return {"topic": devices[device_id]["topic"]}

@app.get("/configs/{device_id}", response_model=ConfigSettings)
def get_device_config(device_id: str):
    if device_id not in configs:
        raise HTTPException(status_code=404, detail="Config not found for device")
    return configs[device_id]

@app.post("/configs/{device_id}", response_model=ConfigSettings)
def set_device_config(device_id: str, config: ConfigSettings):
    if device_id not in devices:
        raise HTTPException(status_code=404, detail="Device not found")
    configs[device_id] = {"device_id": device_id, **config.model_dump()}
    save_data(CONFIG_FILE, configs)
    return config
