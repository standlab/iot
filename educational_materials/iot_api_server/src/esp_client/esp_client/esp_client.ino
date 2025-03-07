#include "Config.h"
#include "WiFi.h"
#include "RegistrationClient.h"
#include "MQTT.h"

void setup() {
  Serial.begin(9600);
  pinMode(LED_PIN, OUTPUT);
  bool wifiConnected = initWIFI(WIFI_CLIENT_MODE); 
  if ( !wifiConnected) {
    return;
  }
  registerDevice();
  initMQTT();
}

void loop() {
  if(Serial.available()) {
    char cmd = Serial.read();
    if(cmd == REGISTER_ON_API) {
      registerDevice();
    } else if(cmd == GET_INFO_ON_API) {
      updateDeviceInfo();
    }
  }
  int sensor_val = analogRead(SENSOR_PIN);
  mqttClient.publish(mqtt_topic.c_str(), String(sensor_val).c_str());
  delay(1000); // replace with scheduler
}
