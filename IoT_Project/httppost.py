import requests
import json

url = 'http://192.168.1.247:105/sensordata/'

data = {"temperature":29.10,"humidity":67.00,"gas":41.25,"aqi":1.00,"wifi":-57,"chip_id":"ESP32-EC79D2A3C9C8","gps":"(44.494716644287111,11.349454879760743)"}
headers = {'Content-type': 'application/json'}
r = requests.post(url, data=json.dumps(data), headers=headers)

print(r.text)