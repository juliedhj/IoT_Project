# IoT_Project

This project consists of an ESP-32 board who collects temperature and humidity values from a DHT22 sensor, and gas values from an MQ-5 sensor. In addition the sensor send the WIFI RSSI signal, the ID of the ESP device, the GPS position and a computed AQI value. The sensor values are being sent to a remote back-end via MQTT or HTTP protocol upon your choice. The values are stored in the InfluxDB and used to show a dashboard in Grafana with graphs for each value. 

* InfluxDB is running from Docker. 
* Grafana dashboard is installed locally. 

<img width="1379" alt="Skjermbilde 2022-06-08 kl  12 49 17" src="https://user-images.githubusercontent.com/71122987/172598701-31ba40fb-d22d-4b2e-a1f5-fc1522396874.png">
