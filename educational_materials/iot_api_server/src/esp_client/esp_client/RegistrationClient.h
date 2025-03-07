#include <ESP8266HTTPClient.h>
#include <ArduinoJson.h>

String device_id;
String mqtt_topic;

bool registerDevice() {
    HTTPClient http;
    String mac = getMAC(); // defined in WiFi.h
    http.begin(wifiClient, String(registration_server) + "/register/");
    http.addHeader("Content-Type", "application/json");
    
    StaticJsonDocument<256> json;
    json["mac_address"] = String(mac);
    json["location"]["lat"] = 52.0;
    json["location"]["lon"] = 104.0;
    json["city"] = "Irkutsk";
    json["owner"] = "IoTSchool";
    json["measurement_type"] = "temperature";
    json["sensor_model"] = "T1000";

    String payload;
    serializeJson(json, payload);
    Serial.println("Trying to register device with info:");
    Serial.println(payload);
    
    int httpResponseCode = http.POST(payload);
    if (httpResponseCode < 0) {
      Serial.println("Failed to make request. Check the server is available. ");
      return false;
    }
    if (httpResponseCode == 200) {
      StaticJsonDocument<256> response;
      deserializeJson(response, http.getString());
      device_id = response["device_id"].as<String>();
      mqtt_topic = response["topic"].as<String>();
      Serial.println("Device is registered with ID and MQTT topic:");
      Serial.println(device_id);
      Serial.println(mqtt_topic);
      http.end();
      return true;
    } else if (httpResponseCode == 400){
      StaticJsonDocument<256> response;
      deserializeJson(response, http.getString());
      Serial.println("Device is probably registered. See details:");
      Serial.println(response["detail"].as<String>());
    } else {
      Serial.print("Failed to register device with code:");
      Serial.println(httpResponseCode);

    }

    http.end();
    return false;
}


bool updateDeviceInfo() {
    HTTPClient http;
    String mac = getMAC(); // defined in WiFi.h
    http.begin(wifiClient, String(registration_server) + "/device_by_mac/");
    http.addHeader("Content-Type", "application/json");
    
    StaticJsonDocument<256> json;
    json["mac_address"] = String(mac);

    String payload;
    serializeJson(json, payload);
    Serial.println("Trying to query device info with:");
    Serial.println(payload);
    
    int httpResponseCode = http.POST(payload);
    if (httpResponseCode < 0) {
      Serial.println("Failed to make request. Check the server is available. ");
      return false;
    }
    if (httpResponseCode == 200) {
      StaticJsonDocument<256> response;
      deserializeJson(response, http.getString());
      device_id = response["device_id"].as<String>();
      mqtt_topic = response["topic"].as<String>();
      Serial.println("Got device with ID and MQTT topic:");
      Serial.println(device_id);
      Serial.println(mqtt_topic);
      http.end();
      return true;
    } else if (httpResponseCode == 404){
      StaticJsonDocument<256> response;
      Serial.println("Device is not found in the system.");
    } else {
      Serial.print("Failed to get device with code:");
      Serial.println(httpResponseCode);
    }

    http.end();
    return false;
}