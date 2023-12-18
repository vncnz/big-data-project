import time, pickle
from datetime import datetime, timedelta

from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS

from utilities import progressBar

pickle_time_start = time.perf_counter()
with open('records', 'rb') as file:
    records = pickle.load(file)
pickle_time_end = time.perf_counter()
print(f"The loading time for {len(records)} records in python is: {timedelta(seconds = (pickle_time_end - pickle_time_start))}")

records = [rec for rec in records if rec['field'] == 'delay']# rec['delay'] is not None]


org = 'vncnz'
bucket = 'bigdata_project'

# client = InfluxDBClient(
#   url="https://europe-west1-1.gcp.cloud2.influxdata.com",
#   token="Taiju5w8TEteVMjU4bt6emM3L0NpgnWAinolzSEYfB4JCVphV9DjebNRvQASWXzKSOqkKO4TvthcB74N1ICCPw=="
# )
client = InfluxDBClient(
    url="http://localhost:8086",
    token='DA FARE'
)

write_api = client.write_api()
query_api = client.query_api()

path_linux = '/home/vncnz/TODO'
path_windows = 'TODO'

records = records[:10]

i = 0
for record in records:
    point = Point("StopCalls") \
            .tag("day_of_service", record['day_of_service']) \
            .tag("route_id", record['route_id']) \
            .tag("trip_id", record['trip_id']) \
            .tag("stop_id", record['stop_id']) \
            ...
            .field("delay", record['delay']) \
            .time(record['...datetime'].isoformat(), WritePrecision.S)

    write_api.write(bucket, org, point)
    i += 1
    progressBar(i, len(records), 40)
print('')