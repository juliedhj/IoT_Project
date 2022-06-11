#include "DHTesp.h"
#include "WiFi.h"
#include <PubSubClient.h>
#include <WiFiClient.h>
#include <HTTPClient.h>
#include <Arduino_JSON.h>
#include <list>
DHTesp dht;
WiFiClient clientWiFi;
PubSubClient clientMQTT;
HTTPClient clientHTTP; 
using namespace std;

//Variables
char packetBuffer[255];
char  ReplyBuffer[] = "ACK";
int SAMPLE_FREQUENCY = 5000;
int MAX_GAS_VALUE = 100;
int MIN_GAS_VALUE = 0;
list<float> gasValues(true);
int Gas_analog = 35;  
long gasAverage;
float AQI;
int useMQTT = 1;
boolean resultMQTT;
float latitude = 44.494716552360245;
float longitude = 11.349454942271755;
int mqttPackets;
int httpPacketsSent;
int httpPacketsReceived;
unsigned long timesentHttp; 
unsigned long timereceivedHttp;
unsigned long timesentMqtt; 
unsigned long timereceivedMqtt;
list<long> delayHttp;
list<long> delayMqtt;

//Network related variables
char* SSID = "FASTWEB-7847FA";
char* PASS = "9H7GPMPFZ2";
const IPAddress ipadd(192,168,0,132);
char id[23];
const char* MQTT_USER = "iot2020";
const char* MQTT_PASSWD = "mqtt2020*";
const char* IP_MQTT_SERVER ="130.136.2.70";
const char* serverName = "http://192.168.1.151:105/sensordata";

//Topics for sending
const char* TOPIC_0="temperature";
const char* TOPIC_1="humidity";
const char* TOPIC_2="gas";
const char* TOPIC_3="wifi";
const char* TOPIC_4="aqi";

//Topics for receiving
const char* TOPIC_ALL = "hjsensor/incoming/#";
const char* TOPIC_5 = "hjsensor/incoming/changeProtocol";
const char* TOPIC_6 = "hjsensor/incoming/samplefreq";
const char* TOPIC_7 = "hjsensor/incoming/min_gas";
const char* TOPIC_8 = "hjsensor/incoming/max_gas";

//Functions for MQTT handling
void callback_MQTT(char* topic, byte* payload, unsigned int length){
  String payloadMessage;
  Serial.print("Message received in callback, to topic ");
  Serial.println(topic);

  Serial.print("[LOG] Message payload: ");
  for (int i = 0; i < length; i++){
    Serial.print((char)payload[i]);
    payloadMessage += (char)payload[i];
  }
   if (strcmp(topic, TOPIC_5) == 0){
    String protocol = payloadMessage;
    if (protocol.compareTo("http") == 0) {
      useMQTT = 0; 
      Serial.println("[LOG] HTTP protocol in use");
    }
    if (protocol.compareTo("mqtt") == 0){
      useMQTT = 1; 
      Serial.println("[LOG] MQTT protocol in use");
    }
  }
  if (strcmp(topic, TOPIC_6)==0){
      SAMPLE_FREQUENCY = payloadMessage.toInt();
      Serial.println("Changed sample frequency to: "); 
      Serial.print(payloadMessage);
  }
  if (strcmp(topic, TOPIC_7)==0){
      MIN_GAS_VALUE = payloadMessage.toInt();
      Serial.println("Changed min gas value to: "); 
      Serial.print(payloadMessage);
  }
  if (strcmp(topic, TOPIC_8)==0){
      MAX_GAS_VALUE = payloadMessage.toInt();
      Serial.println("Changed max gas value to: "); 
      Serial.print(payloadMessage);
  }
   
  Serial.println();
}

const char *create_topic(String sensor, char * id, String gps) {
  String topic;
  topic += "hjsensor/" + String(id) + "/" +
           gps + "/" + sensor;
  return topic.c_str();
}

boolean publishData(int channel, float value, char * id, String gps) {
  bool result=false;
  boolean connected=clientMQTT.connected();
  
  if (!connected) 
    connected=clientMQTT.connect("MYesp32",MQTT_USER,MQTT_PASSWD);
  if (connected) {
      String message=String(value);
      const char* payload=message.c_str();
      if (channel==0) 
        result=clientMQTT.publish(create_topic(TOPIC_0, id, gps), payload);
      if (channel==1) 
        result=clientMQTT.publish(create_topic(TOPIC_1, id, gps),payload);
      if (channel==2)
        result=clientMQTT.publish(create_topic(TOPIC_2, id, gps), payload);
      if (channel==3)
        result=clientMQTT.publish(create_topic(TOPIC_3, id, gps),payload);
      if (channel==4)
        result=clientMQTT.publish(create_topic(TOPIC_4, id, gps),payload);
      clientMQTT.loop();
      return result;
  } else return(false);  
}

void subscribe_MQTT(){
  boolean subscribe = clientMQTT.subscribe(TOPIC_ALL, 1); 
  if (!subscribe) {
    Serial.print("Failed to subscribe to topic.");
  }
}

//Functions for HTTP handling
void post_HTTP(float temperature, float humidity, float gas, float aqi, int wifi, String id, String gps){
  
    String path; 
    path += String(serverName);
    
    clientHTTP.begin(path.c_str());
    clientHTTP.addHeader("Content-type", "application/json");

    String httpPayload; 
    httpPayload += "{\"temperature\":" + String(temperature) + ",";
    httpPayload += "\"humidity\":" + String(humidity) + ",";
    httpPayload += "\"gas\":" + String(gas) + ",";
    httpPayload += "\"aqi\":" + String(aqi) + ",";
    httpPayload += "\"wifi\":" + String(wifi) + ",";
    httpPayload += "\"id\":" + String(id) + ",";
    httpPayload += "\"gps\":" + String(gps);
    httpPayload += "}";
    httpPayload = String(httpPayload);

    String parsedPayload = httpPayload.c_str();
    Serial.println("Sending HTTP packets");
    timesentHttp = millis();
    int responsecode = clientHTTP.POST(parsedPayload); 
    httpPacketsSent++;
    Serial.print("[LOG]: HTTP packets sent: ");
    Serial.println(httpPacketsSent);


    if (responsecode != 200) {
      Serial.print("[HTTP] Error: ");
      Serial.println(responsecode);
    } else {
      httpPacketsReceived++;
      timereceivedHttp = millis();
      Serial.print("[LOG] Packets received with HTTP: ");
      Serial.println(httpPacketsReceived);
      Serial.print("[LOG] Delay for HTTP: ");
      int delayed = timereceivedHttp - timesentHttp; 
      Serial.println(delayed);
      delayHttp.push_back(delayed);
    }
    clientHTTP.end();
  }

//Compute the AQI value
float computeAQI(float gas) {
   gasValues.push_back(gas); 

  if (gasValues.size() > 5) {
    gasValues.pop_front(); 
  }

  gasAverage = accumulate(gasValues.begin(), gasValues.end(), 0.0) / gasValues.size();
  Serial.print("[LOG] Gas average: "); 
  Serial.println(gasAverage);
  if (gasAverage >= MAX_GAS_VALUE){
    AQI = 0; 
  }
  else if ( MIN_GAS_VALUE <= gasAverage <= MAX_GAS_VALUE){
    AQI = 1;
  }
  else{
    AQI = 2;
  }  
  return AQI;
}

//Compute the average delay for HTTP or MQTT
void averageDelay(list<long> delays){
  if (delays.size() > 15) {
    delays.pop_front();
  }
  long delayAverage = accumulate(delays.begin(), delays.end(), 0.0) / delays.size();
  Serial.print("[LOG] Average delay: ");
  Serial.println(delayAverage);
}
  
//Set up the clients
void setup()
{
  Serial.begin(9600);
  dht.setup(27, DHTesp::DHT11);
  Serial.println();
  delay(1000);
  connect();
  snprintf(id, 23, "ESP32-%llX", ESP.getEfuseMac());
  Serial.println(id);
  clientMQTT.setClient(clientWiFi);
  clientMQTT.setServer(IP_MQTT_SERVER, 1883);
  clientMQTT.setBufferSize(400);
  clientMQTT.setCallback(callback_MQTT);
  subscribe_MQTT();
  resultMQTT=false;
}

//Set up the internet connection
void connect() {
  WiFi.begin(SSID, PASS);
  while (WiFi.status() != WL_CONNECTED) {
    Serial.println("Connection attempt");
    delay(1000);
  }
  Serial.println("WiFi connected");
  // Start the server
  delay(8000);
  Serial.println(WiFi.localIP());
}

//Main logic of the Arduino, the loop to collect sensor values and send them
void loop(){
  if(!clientMQTT.connected()){
    clientMQTT.connect("MYesp32",MQTT_USER,MQTT_PASSWD);
    subscribe_MQTT();
    }
  clientMQTT.loop();
  
  float temperature = dht.getTemperature();
  float humidity = dht.getHumidity();
  float gas_analog_value = analogRead(Gas_analog);
  float gas = ((gas_analog_value/1023)*100);
  int wifiSignal = WiFi.RSSI();
  String gps = "(" + String(latitude, 15) +","+ String(longitude, 15) +")";
  String gps_json = "(" + String(latitude, 15) +","+ String(longitude, 15) +")";
  String gps_http = '"' + gps_json + '"';
  String chip_id = '"' + String(id) + '"';

  AQI = computeAQI(gas);
 
  Serial.print("[LOG] Temperature: ");
  Serial.println(temperature);
  Serial.print("[LOG] Humidity: ");
  Serial.println(humidity);
  Serial.print("[LOG] Gas Sensor: ");
  Serial.println(gas); 
  Serial.print("[LOG] AQI measurement: ");
  Serial.println(AQI);
  Serial.printf("[LOG] RSSI: %d dBm\n", wifiSignal);
  Serial.print("[LOG] Sample Frequency: ");
  Serial.println(SAMPLE_FREQUENCY);

  if (useMQTT) {
    Serial.println("Sending data to the MQTT");
    timesentMqtt = millis();
    resultMQTT=publishData(0, temperature, id, gps);
    resultMQTT=publishData(1, humidity, id, gps);
    resultMQTT=publishData(2, gas, id, gps);
    resultMQTT=publishData(3, wifiSignal, id, gps);
    resultMQTT=publishData(4, AQI, id, gps);
    

    if (resultMQTT) {
      timereceivedMqtt = millis();
      Serial.println("[LOG] Data published to MQTT server");
      mqttPackets++;
      Serial.print("[LOG] Packets sent with MQTT to each channel: ");
      Serial.println(mqttPackets);
      Serial.print("[LOG] Time delay for MQTT: ");
      int delayed = timereceivedMqtt - timesentMqtt;
      Serial.println(delayed);
      delayMqtt.push_back(delayed);
    }
    else 
      Serial.println("[ERROR] MQTT connection failed");
    averageDelay(delayMqtt);
  } 
  else {
    post_HTTP(temperature, humidity, gas, AQI, wifiSignal, chip_id, gps_http); 
    averageDelay(delayHttp);
  }
   delay(SAMPLE_FREQUENCY);
}