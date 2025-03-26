from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, Query
from pydantic import BaseModel, Field
from enum import Enum
import hashlib
import os
import json
import tempfile
import threading

from notifier import send_telegram_notification, start_bot


# Start Telegram bot in a separate thread
threading.Thread(target=start_bot, daemon=True).start()

app = FastAPI()

DATA_FILE = os.path.join(tempfile.gettempdir(), "devices.json")
CONFIG_FILE = os.path.join(tempfile.gettempdir(), "configs.json")
USERS_FILE = os.path.join(tempfile.gettempdir(), "users.json")
USER_DEVICE_LINK_FILE = os.path.join(tempfile.gettempdir(), "user_device_links.json")

def load_data(file_path):
    if os.path.exists(file_path):
        with open(file_path, "r") as file:
            return json.load(file)
    return {}

def load_user_device_links(file_path):
    data = load_data(file_path)
    if not data:
        data = {"devices": {}, "users": {}}
    return data

def save_data(file_path, data):
    with open(file_path, "w") as file:
        json.dump(data, file, indent=4)

def data_file():
    return DATA_FILE

def config_file():
    return CONFIG_FILE

devices = load_data(DATA_FILE)
configs = load_data(CONFIG_FILE)
users = load_data(USERS_FILE)
user_device_links = load_user_device_links(USER_DEVICE_LINK_FILE)

def make_id(key: str) -> str:
    return hashlib.sha256(key.encode()).hexdigest()[:16]

class MeasurementType(str, Enum):
    TEMPERATURE = "temperature"
    LUMINOCITY = "luminocity"


class UserRole(str, Enum):
    MANAGER = "manager"
    ADMINISTRATOR = "administrator"

class Device(BaseModel):
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
    
class DeviceRegistration(Device):
    mac_address: str = Field("00:00:00:00:00:00")

class DeviceRetrieveByMac(BaseModel):
    mac_address: str = Field("00:00:00:00:00:00")

class ConfigSettings(BaseModel):
    data_cadence: int = Field(60, description="Data transmission interval in seconds")
    qos: int = Field(0, description="MQTT Quality of Service level")
    last_updated: str = Field(..., description="Timestamp of last update")

class User(BaseModel):
    username: str = Field(description="User nickname")

class UserRegistration(User):
    chat_id: int = Field(description="User chat id in telegram")

class UserResponse(User):
    user_id: str = Field(description="User ID in service")
    role: str = Field(
        UserRole.MANAGER, 
        description=f"Available roles: {[item.value for item in UserRole]}"
    )

@app.post("/register/", response_model=dict)
def register_device(device: DeviceRegistration, tasks: BackgroundTasks):
    device_id = make_id(device.mac_address)
    topic = f"{device.owner}/{device.city}/{device.measurement_type}/{device_id}"
    
    if device_id in devices:
        raise HTTPException(status_code=400, detail="Device already registered")
    
    devices[device_id] = {"device_id": device_id, "topic": topic, **device.model_dump()}
    save_data(DATA_FILE, devices)

    message = (
        f"New device registered!\n"
        f"ID: {device_id}\n"
        f"Location: ({device.longitude}, {device.latitude})\n"
        f"Owner: {device.owner}\n"
        f"Measurement Type: {device.measurement_type}\n"
        f"Sensor Model: {device.sensor_model}"
    )
    user_device_links["devices"][device_id] = []
    #send_telegram_notification(message)
    tasks.add_task(send_telegram_notification, message)
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
    device_id = make_id(device.mac_address)
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


@app.post("/configs/{device_id}", response_model=ConfigSettings)
def set_device_config(device_id: str, config: ConfigSettings):
    if device_id not in devices:
        raise HTTPException(status_code=404, detail="Device not found")
    configs[device_id] = {"device_id": device_id, **config.model_dump()}
    save_data(CONFIG_FILE, configs)
    return config

@app.post("/register_user", response_model=UserResponse)
def register_user(user: UserRegistration):
    """Performes user registration based on Telegram chat ID

    Default role assigned to a User is manager. It could be letter changed via separate 
    endpoint. An empty device list created for a user. That should be filled via
    'link_device' endpoint.

    Returns 400 HTTP code if user already regestered.
    """
    user_id = make_id(str(user.chat_id))
    if user_id in users:
        raise HTTPException(status_code=400, detail="User already registered")
    users[user_id] = {"user_id": user_id, "role": UserRole.MANAGER, **user.model_dump()}
    save_data(USERS_FILE, users)
    user_device_links["users"][user_id] = []
    save_data(USER_DEVICE_LINK_FILE, user_device_links)
    return users[user_id]


@app.get("/user/{user_id}", response_model=UserResponse)
def get_user(user_id: str):
    if user_id not in users:
        raise HTTPException(status_code=404, detail="User not found")
    return users[user_id]

@app.post("/identify_user/", response_model=UserResponse)
def identify_user(user: UserRegistration):
    user_id = make_id(str(user.chat_id))
    if user_id not in users:
        raise HTTPException(status_code=404, detail="User not found")
    return users[user_id]

@app.delete("/remove_user/{user_id}")
def remove_user(user_id: str):
    if user_id not in users:
        raise HTTPException(status_code=404, detail="User not found")
    del users[user_id]
    save_data(USERS_FILE, users)
    return {"message": "User {user_id} deleted"}

@app.post("/link_device")
def link_device_to_user(
    user_id: str = Query(description="The ID of user as it appears in service"),
    device_id: str = Query(description="The ID of device as it appears in service"),
) -> dict:
    if not user_id in users:
        raise HTTPException(status_code=404, detail="User not found")
    if not device_id in devices:
        raise HTTPException(status_code=404, detail="Device not found")
    
    device_users = user_device_links["devices"][device_id]
    user_devices = user_device_links["users"][user_id]
    if not user_id in device_users:
        device_users.append(user_id)
    if not device_id in user_devices:
        user_devices.append(device_id)

    return {"devices": user_devices}
