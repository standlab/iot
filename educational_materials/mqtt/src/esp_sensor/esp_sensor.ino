#include "Config.h"
#include "WIFI.h"
#include "MQTT.h"

long int last_send = 0;

void setup(void){
  Serial.begin(115200);
  pinMode(led_pin, OUTPUT);
  Serial.println("Starting WiFi....");
  WIFI_init(false);
  Serial.println("Starting MQTT....");
  MQTT_init();
}

void loop(void){
  if(last_send + SEND_INTERVAL < millis()) {
    int sensor_val = analogRead(sensor_pin);
    // convert to char* since it required by publish method
    mqtt_client.publish(SENSOR_TOPIC, String(sensor_val).c_str());
    Serial.print("Sent value to the broker:");
    Serial.print(String(sensor_val).c_str());
    last_send = millis();
  }
}
