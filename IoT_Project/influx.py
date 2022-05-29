from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS


#user = juliedhj
#pwd = iotproject
#org = iotunibo
#buket = measures


def InfluxClient(id, gps, field, value): 
    token = "JAIXEbfN95UtK9j0JgWY25q4pRxzXIuF0VcObkFawsWmJ_01C6OlCwHhz3LfTK5Lq42DRbPB_qVIAFe2VaqhTQ=="
    org = "iotunibo"
    bucket = "sensordata"


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