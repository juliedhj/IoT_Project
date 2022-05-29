import json
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/sensordatatest/', methods=['POST'])
def read_data():
    data = request.get_json()
    print(data)
    return data, 200


if __name__ == '__main__':
    app.run(debug=True, use_reloader=False, host='0.0.0.0', port=105 or 5000)

