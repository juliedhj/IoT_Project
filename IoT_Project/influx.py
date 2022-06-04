from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
import os
from dotenv import load_dotenv

#user = juliedhj
#pwd = iotproject
#org = iotunibo

load_dotenv()

token = os.getenv('INFLUX_TOKEN')
bucket = os.getenv('INFLUX_BUCKET')
org = os.getenv('INFLUX_ORG')

def getClient():
    return InfluxDBClient(url="http://localhost:8086/", token=token, org=org)

def InfluxClient(id, gps, field, value): 
    client = getClient()

    write_api = client.write_api(write_options=SYNCHRONOUS)
    query_api = client.query_api()

    p = Point("measures").tag("ID", id).tag("GPS", gps).field(field, value)

    write_api.write(bucket=bucket, record=p)
