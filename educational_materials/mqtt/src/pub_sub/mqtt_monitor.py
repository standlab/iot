from paho.mqtt.client import Client, MQTTMessage
from paho.mqtt.enums import CallbackAPIVersion
from datetime import datetime, timedelta
import random

broker = "broker.emqx.io"

luminosity_topic = "laboratory/greenhouse/luminosity"
light_status_topic = "laboratory/greenhouse/light"
topics = [
    luminosity_topic, 
    light_status_topic
]

states = dict(
    light = "off"
)

sensor_data = dict(
    luminosity = 0
)

check_states = dict(
    light = (False, datetime.now())
)

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
        sensor_data["luminosity"] = float(data)
        check_states["light"] = (True, datetime.now() + timedelta(seconds = 5))
    if topic == light_status_topic:
        states["light"] = data

def check_light():
    state = states["light"]
    data =  sensor_data["luminosity"]
    if state == "off" and data < 500:
        print("System work normaly, light off")
    elif state == "on" and data > 500:
        print("System work normaly, light on")
    else:
        print(f"Something went wrong. State {state} and data {data}")
    check_states["light"] = (False, datetime.now())

if __name__ == "__main__":
    # ID is important to broker make sure it is unique. 
    client= Client(
        callback_api_version=CallbackAPIVersion.VERSION2,
        client_id = f'MY_CLIENT_ID_{random.randint(10000, 99999)}'
    )
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(broker) 

    client.connect(broker) 
    client.loop_start() 
    for topic in topics:
        print(f"Subcribing to {topic}")
        client.subscribe(topic)
    while True:
        try:
            for actuator, (need_check, check_time) in check_states.items():
                if need_check and check_time < datetime.now():
                    if actuator == "light":
                        check_light()
                    # other check here
        except KeyboardInterrupt:
            print("Monitoring finisshed....")
            break

    client.disconnect()
    client.loop_stop()