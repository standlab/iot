#include "Config.h"
#include "WIFI.h"
#include "Server.h"

void setup(void){
  Serial.begin(115200);
  pinMode(led, OUTPUT);
  WIFI_init(false);
  server_init();
}

void loop(void){
  server.handleClient();                   
}
