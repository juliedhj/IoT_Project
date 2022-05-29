import requests
import json

url = 'http://192.168.1.151:105/sensordatatest'

data = {'sender': 'Julie', 'receiver': 'Helene', 'message': 'We did it!'}
headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
r = requests.post(url, data=json.dumps(data), headers=headers)

print(r.text)