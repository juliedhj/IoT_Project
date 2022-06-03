from nbformat import write
import pandas as pd
import time
from datetime import datetime
from fbprophet import Prophet
import numpy as np

from influxdb_client import InfluxDBClient, Point, WriteOptions
from influxdb_client.client.write_api import SYNCHRONOUS
from influx import getClient

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

def query_data_process(measurement, bucket):
   query = f'from(bucket:"{bucket}")' \
        ' |> range(start:-1h, stop: 0h)'\
        ' |> filter(fn: (r) => r._measurement == "measures")' \
        f' |> filter(fn: (r) => r._field == "{measurement}")'\
        ' |> aggregateWindow (every: 1m, fn: mean, createEmpty: false)'

   result = client.query_api().query(org=org, query=query)

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

def query_data_process_forecast(measurement, bucket):
   query = f'from(bucket:"{bucket}")' \
        ' |> range(start:-1h, stop: 0h)'\
        ' |> filter(fn: (r) => r._measurement == "{measurement}")' \
        ' |> aggregateWindow (every: 1m, fn: mean, createEmpty: false)'

   result = client.query_api().query(org=org, query=query)

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
   

def prophet_forecast(dataframe):
   m = Prophet()
   m.fit(dataframe)

   future = m.make_future_dataframe(periods=48)
   forecast = m.predict(future)
   forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail()

   return forecast 

def process_forecast(forecast, measurement):
   forecast['measurement'] = measurement 
   copy = forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper','measurement']].copy()
   lines = [str(copy["measurement"][d]) 
         + ",type=forecast" 
         + " " 
         + "yhat=" + str(copy["yhat"][d]) + ","
         + "yhat_lower=" + str(copy["yhat_lower"][d]) + ","
         + "yhat_upper=" + str(copy["yhat_upper"][d])
         + " " + str(int(time.mktime(copy['ds'][d].timetuple()))) + "000000000" for d in range(len(copy))]

   return lines 

def publish_forecast(lines):
   write_api.write(forecast_bucket, org, lines)

def forcasting_data(measurement):
   dataframe = query_data_process(measurement, bucket)
   forecast = prophet_forecast(dataframe)
   lines = process_forecast(forecast, measurement)
   publish_forecast(lines)

def compute_mse(y_true, y_pred):
   return np.square(np.subtract(y_true, y_pred)).mean()

def drop_duplicates(dataframe):
   dataframe.drop_duplicates(subset='ds', keep='last', inplace=True)
   dataframe.set_index('ds', inplace=True)
   return dataframe

def timeseries_mse(measurement):
   dataframe_sensor = query_data_process(measurement, bucket)
   dataframe_forecast = query_data_process_forecast(measurement, forecast_bucket)

   dataframe_sensor = drop_duplicates(dataframe_sensor)
   dataframe_forecast = drop_duplicates(dataframe_forecast)

   mse_ts = compute_mse(dataframe_sensor, dataframe_forecast)

   return mse_ts 

def compute_all_mse():
   measurements = ["temperature", "humidity", "gas"]
   for measure in measurements: 
        mse = timeseries_mse(measure)
        print(f"{measure} : {mse}")

forcasting_data("temperature")
forcasting_data("humidity")
forcasting_data("gas")
#compute_all_mse()