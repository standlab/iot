#include <ESP8266WiFi.h>
#include <WiFiClient.h>
#include <ESP8266WiFiMulti.h>

ESP8266WiFiMulti wifiMulti;    
WiFiClient wifiClient;

String ip = "(IP unset)"; 

String macAdress = "00:00:00:00:00:00";
bool macSetted = false;

String getMAC() {
  if (macSetted == true) {
    return macAdress;
  }
  uint8_t mac[WL_MAC_ADDR_LENGTH];
  WiFi.softAPmacAddress(mac);
  String __mac = String(mac[0], HEX);
  for(int i=1; i < WL_MAC_ADDR_LENGTH; i++) {
    __mac =  __mac + ":" + String(mac[i], HEX);
  }
  __mac.toUpperCase();
  Serial.print("Device mac address: ");
  Serial.println(__mac.c_str());
  macAdress = __mac;
  macSetted = true;
  return macAdress;
}

String id(){
  uint8_t mac[WL_MAC_ADDR_LENGTH];
  WiFi.softAPmacAddress(mac);
  String macID = (
    String(mac[WL_MAC_ADDR_LENGTH - 2], HEX) + 
    String(mac[WL_MAC_ADDR_LENGTH - 1], HEX) 
  );
  macID.toUpperCase();
  return macID;
}

bool startAPMode() {
  IPAddress apIP(192, 168, 4, 1);
  WiFi.disconnect();
  WiFi.mode(WIFI_AP);
  WiFi.softAPConfig(apIP, apIP, IPAddress(255, 255, 255, 0));
  WiFi.softAP((ssidAP + " " + id()).c_str(), passwordAP.c_str());
  Serial.println("");
  Serial.println("WiFi up in AP mode with name: "+ ssidAP + " " + id());
  return true;
}

bool startClientMode() {
  Serial.println("Connecting to router as Client...");
  wifiMulti.addAP(ssidCLI, passwordCLI);
  //it is possible to add more networks to connect
  while(wifiMulti.run() != WL_CONNECTED) {
       
  }
  return true;
}

bool initWIFI(int mode) {
    if (mode == WIFI_AP_MODE) {
      startAPMode();
      ip = WiFi.softAPIP().toString();
    } else if (mode == WIFI_CLIENT_MODE) {
      startClientMode();
      ip = WiFi.localIP().toString();
    } else {
      Serial.println("Unkonown WIFI mode");  
      return false;
    }
    Serial.println("IP address: ");
    Serial.println(ip);  
    return true;
}