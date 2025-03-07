#define WIFI_AP_MODE 0
#define WIFI_CLIENT_MODE 1

#define REGISTER_ON_API 'r'
#define GET_INFO_ON_API 'u'

String ssidAP = "AAAAAAA"; // имя контроллера и точки доступа
String passwordAP = "ESP8266123"; // пароль точки доступа

// Make router is 2.5 GHz band
const char* ssidCLI = "enet"; // имя контроллера и точки доступа
const char* passwordCLI = "juct2647~"; // пароль точки доступа

const char* mqttBroker = "broker.emqx.io";
const int mqttPort = 1883;

const char* registration_server = "http://192.168.212.231:8080";

int LED_PIN = 2;
int SENSOR_PIN = A0;