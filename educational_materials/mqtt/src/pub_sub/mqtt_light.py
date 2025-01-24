import time
from paho.mqtt.client import Client, MQTTMessage
from paho.mqtt.enums import CallbackAPIVersion
import random

broker = "broker.emqx.io"
luminosity_topic = "laboratory/greenhouse/luminosity"
light_status_topic = "laboratory/greenhouse/light"
light_state = "off"

def set_light_on() -> str:
    # do stuff
    light_state = "on"
    return light_state

def set_light_off() -> str:
    # do stuff
    light_state = "off"
    return light_state

def process_luminosity_data(data: bytes, client: Client):
    global light_state
    data = str(data)
    if float(data) < 500 and light_state == "on":
        print("Setting light off")
        light_state = set_light_off()
        client.publish(light_status_topic, light_state)
        print(f"Published status {light_state} to {light_status_topic}")
    elif float(data) > 500 and light_state == "off":
        print("Setting light on")
        light_state = set_light_on()
        client.publish(light_status_topic, light_state)
        print(f"Published status {light_state} to {light_status_topic}")
    else:
        print("Light state remains the same")

def on_connect(client: Client, userdata, flags, reason_code, properties):
    if reason_code == 0:
        print("Connected to MQTT Broker!")
    else:
        print("Failed to connect, return code %d\n", reason_code)

def on_message(client: Client, userdata, message: MQTTMessage):
    data = str(message.payload.decode("utf-8"))
    topic = message.topic
    print(f"Received message {data} from topic {topic}")
    if topic == luminosity_topic:
        process_luminosity_data(data, client)

# ID is important to broker make sure it is unique. 
if __name__ == "__main__":
    client= Client(
        callback_api_version=CallbackAPIVersion.VERSION2,
        client_id = f'MY_CLIENT_ID_{random.randint(10000, 99999)}'
    )
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(broker) 

    client.connect(broker) 
    client.loop_start() 
    print(f"Subcribing to {luminosity_topic}")
    client.subscribe(luminosity_topic)
    client.publish(light_status_topic, light_state)
    time.sleep(1800)
    client.disconnect()
    client.loop_stop()