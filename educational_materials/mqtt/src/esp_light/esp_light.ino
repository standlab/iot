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
  mqtt_client.subscribe(SENSOR_TOPIC);
}

void loop(void){
  mqtt_client.loop();
}
