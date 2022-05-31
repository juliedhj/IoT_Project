import requests
import json

url = 'http://192.168.1.151:105/sensordata/ESP32-EC79D2A3C9C8/(44.494716644287111,11.349454879760743)'

data = {'sender': 'Julie', 'receiver': 'Frida', 'message': 'Test'}
headers = {'Content-type': 'application/json'}
r = requests.post(url, data=json.dumps(data), headers=headers)

print(r.text)