String ssidAP = "ESP_WIFI"; // имя контроллера и точки доступа
String passwordAP = "ESP8266123"; // пароль точки доступа

const char* ssidCLI = "enet";
const char* passwordCLI = "hzrx9585+";

const char* mqtt_broker = "broker.emqx.io";

const int mqtt_port = 1883;

const int led_pin = LED_BUILTIN;
const int sensor_pin = A0;

const int SEND_INTERVAL = 1000;
const char* SENSOR_TOPIC = "laboratory/greenhouse/luminosity";