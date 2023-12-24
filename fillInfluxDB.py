import time, pickle
from datetime import datetime, timedelta

from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS

from utilities import countRows, dataGenerator, progressBar, separateRecords

# influxd run
import functools
print = functools.partial(print, flush=True)

# pickle_time_start = time.perf_counter()
# with open('records', 'rb') as file:
#     records = pickle.load(file)
# records = [x for x in records if x['datetime'] and x['stop_id'] and (x['field'] == 'delay' or x['value'] < 200) and (x['field'] != 'delay' or x['value'] < 60*60*2)]
# pickle_time_end = time.perf_counter()
# print(f"The loading time for {len(records)} records in python is: {timedelta(seconds = (pickle_time_end - pickle_time_start))}")

org = 'vncnz'
bucket = 'bigdata_project'
pwd = 'bigdata_project'
erase_all = False
skip_write = False

# client = InfluxDBClient(
#   url="https://europe-west1-1.gcp.cloud2.influxdata.com",
#   token="Taiju5w8TEteVMjU4bt6emM3L0NpgnWAinolzSEYfB4JCVphV9DjebNRvQASWXzKSOqkKO4TvthcB74N1ICCPw=="
# )
client = InfluxDBClient(
    url="http://localhost:8086",
    token='w1vABiIPJ28ixch-pz-DyDDjTlnOpLsxSY8yrUT5dvMi9Xn_wsnDUAU-E4oyTVFhfVHGtqskQRAUm_6LHbZQYA=='
)
client.api_client.configuration.timeout = 30*1000

if erase_all:
    print('Erasing all data in bucket...', end='')
    start = "2023-01-01T00:00:00Z"
    stop = "2025-10-02T00:00:00Z"
    delete_api = client.delete_api()
    delete_api.delete(start, stop, None, bucket=bucket, org=org) # '_measurement="delay"'
    print('\rErased all data in bucket!      ')

write_api = client.write_api()
query_api = client.query_api()

# path_linux = '/home/vncnz/TODO'
# path_windows = 'TODO'

# records = [rec for rec in records if rec['field'] == 'delay']# rec['delay'] is not None]
# records = records[:1000]

def recordToGenericPoint (record):
    return Point(record['field']) \
        .tag("day_of_service", record['day_of_service']) \
        .tag("route_id", record['route_id']) \
        .tag("trip_id", record['trip_id']) \
        .tag("stop_id", record['stop_id']) \
        .tag("block_id", record['block_id']) \
        .time(record['datetime'], WritePrecision.S)

write_time_start = time.perf_counter()

stopcalls_path = "rpt_stop_details_202312221216.sql"
stops_path = "sch_gtfs_stops_202312071735.sql"
total_rows = countRows(stopcalls_path)

i = 0
ii = 0
for fullrec in dataGenerator(stopcalls_path, stops_path, False):
    for record in separateRecords(fullrec):
        point = recordToGenericPoint(record).field(record['field'], record['value']) # .field("delay", record['delay'])
        if not skip_write: write_api.write(bucket, org, point)
        ii += 1
    # print(point)
    i += 1
    progressBar(i, total_rows, 40)
print('')

write_time_end = time.perf_counter()
diff = write_time_end - write_time_start
# print(f"The written time for {len(records)} records in influxdb is: {timedelta(seconds = diff)}")
print(f"The written time for {ii} records in influxdb is: {timedelta(seconds = diff)} ({(ii / diff):.2f} records per second)")