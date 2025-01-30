import time
from paho.mqtt.client import Client
from paho.mqtt.enums import CallbackAPIVersion
import random

broker="broker.emqx.io"
luminosity_topic = "laboratory/greenhouse/luminosity"

# ID is important to broker make sure it is unique. 
if __name__ == "__main__":
    client= Client(
        callback_api_version = CallbackAPIVersion.VERSION2,
        client_id = f'MY_CLIENT_ID_{random.randint(10000, 99999)}'
    )
    client.connect(broker) 

    for itteration in range(10):
        val = str(random.randint(100, 999))
        client.publish(luminosity_topic, val, qos=2)
        print(f"Itteration {itteration} publish luminosity - {val} to {luminosity_topic}")
        time.sleep(10)
        
    client.disconnect()
