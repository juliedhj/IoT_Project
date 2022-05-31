import pandas as pd
import time
from datetime import datetime
from fbprophet import Prophet

from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

import os
from dotenv import load_dotenv

load_dotenv()


token = os.getenv('INFLUX_TOKEN')
bucket = os.getenv('INFLUX_BUCKET')
org = os.getenv('INFLUX_ORG')
client = InfluxDBClient(url="http://localhost:9999", token=token, org=org)
query_api = client.query_api()
write_api = client.write_api(write_options=SYNCHRONOUS)