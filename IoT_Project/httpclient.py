import json
from flask import Flask, request, jsonify
import influx

app = Flask(__name__)

@app.route('/sensordata/ESP32-EC79D2A3C9C8/(44.494716644287111,11.349454879760743)', methods=['POST'])
def read_data():
    data = request.get_json()
    print(data)
    gps = "(44.494716644287111,11.349454879760743)"
    id = "ESP32-EC79D2A3C9C8"
    sensor_types = ["temperature", "humidity", "gas", "aqi", "wifi"]
    for key, value in data.items():
        if key not in sensor_types:
            return jsonify({"Error": "This sensor type is not valid: " + key})
        influx.InfluxClient(id, gps, key, float(value))
    print("HTTP to InfluxDB")
    return data, 200


if __name__ == '__main__':
    app.run(debug=True, use_reloader=False, host='0.0.0.0', port=105 or 5000)

