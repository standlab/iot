#include <PubSubClient.h>

PubSubClient mqttClient(wifiClient); // wifiClient is defined in WIFI.h

void initMQTT(){
  mqttClient.setServer(mqttBroker, mqttPort);
  while (!mqttClient.connected()) {
      String client_id = "esp8266-" + device_id;
      Serial.println("Connecting to MQTT broker with client_id: " + client_id);
      if (mqttClient.connect(client_id.c_str())){
          Serial.println("MQTT Connected");
      } else {
          Serial.print("Failed to connect to MQTT with state: ");
          Serial.println(mqttClient.state());
          delay(2000);
      }
  }  
}