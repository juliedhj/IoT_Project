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


def InfluxClient(id, gps, field, value): 
    client = InfluxDBClient(url="http://localhost:8086/", token=token, org=org)

    write_api = client.write_api(write_options=SYNCHRONOUS)
    query_api = client.query_api()

    p = Point("measures").tag("ID", id).tag("GPS", gps).field(field, value)

    write_api.write(bucket=bucket, record=p)

#InfluxClient("ESP-ID", "123,456", "humidity", 40)
## using Table structure
#tables = query_api.query('from(bucket:"sensordata") |> range(start: -10m)')

#for table in tables:
#    print(table)
#    for row in table.records:
#        print (row.values)


## using csv library
#csv_result = query_api.query_csv('from(bucket:"sensordata") |> range(start: -10m)')
#val_count = 0
#for row in csv_result:
#    for cell in row:
#        val_count += 1