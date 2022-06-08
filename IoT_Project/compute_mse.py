from influxdb_client import InfluxDBClient, Point, WriteOptions
from influxdb_client.client.write_api import SYNCHRONOUS
from influx import getClient

import pandas as pd
from sklearn.metrics import mean_squared_error

import os
from dotenv import load_dotenv

load_dotenv()
token = os.getenv('INFLUX_TOKEN')
bucket = os.getenv('INFLUX_BUCKET')
org = os.getenv('INFLUX_ORG')
client = getClient()
query_api = client.query_api()
write_api = client.write_api(write_options=SYNCHRONOUS)
forecast_bucket = "sensor_forecast"


def create_real_query(measurement, bucket):
    query = f'from(bucket:"{bucket}")' \
        ' |> range(start:-1h, stop: 0h)'\
        ' |> filter(fn: (r) => r._measurement == "measures")' \
        f' |> filter(fn: (r) => r._field == "{measurement}")'\
        ' |> aggregateWindow (every: 1m, fn: mean, createEmpty: false)'

    result = client.query_api().query(org=org, query=query)
    return result

def create_forecast_query(measurement, bucket):
    query = f'from(bucket:"{bucket}")' \
        ' |> range(start:-1h, stop: 0h)'\
        f' |> filter(fn: (r) => r._measurement == "{measurement}")' \
        ' |> aggregateWindow (every: 1m, fn: mean, createEmpty: false)'
    result = client.query_api().query(org=org, query=query)
    return result


def create_df(result):
   raw = []
   for table in result:
        for record in table.records:
           raw.append((record.get_value(), record.get_time()))
   
   #Make the raw into a Pandas dataframe 
   print("=== influxdb query into dataframe ===")
   df = pd.DataFrame(raw, columns=['y','ds'], index=None)
   df['ds'] = df['ds'].values.astype('<M8[s]')
   df['ds'] +=  pd.to_timedelta(2, unit='h')
   df['y'] = df['y'].apply(lambda x: round(x, 2))
   df.set_index('ds')
   df.head()
   return df

def compute_mse(df_real, df_forecast):
    metric_df = df_real.join(df_forecast, how='outer', rsuffix='_1')
    metric_df.dropna(inplace=True)
    metric_df.head()
    mse = mean_squared_error(metric_df.y, metric_df.yhat)
    print(mse)

def timeseries_mse(measure):
    query_real = create_real_query(measure, bucket)
    query_forecast = create_forecast_query(measure, forecast_bucket)
    print("real result", query_real)
    print("forecast result", query_forecast)

    df_real = create_df(query_real)
    df_forecast = create_df(query_forecast)
    print(df_forecast)

    mse = compute_mse(df_real, df_forecast)
    return mse

def compute_all_mse():
   measurements = ["temperature", "humidity", "gas"]
   for measure in measurements: 
       mse = timeseries_mse(measure)
       print(f"{measure} : {mse}")

compute_all_mse()