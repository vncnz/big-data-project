import time, pickle
from datetime import datetime, timedelta

from influxdb_client import InfluxDBClient, Point, WritePrecision
# from influxdb_client.client.write_api import SYNCHRONOUS

from utilities import countRows, dataGenerator, progressBar, separateRecords

# influxd run
import functools
print = functools.partial(print, flush=True)

org = 'vncnz'
bucket = 'bigdata_project2'
pwd = 'bigdata_project'
erase_all = False
skip_write = False

client = InfluxDBClient(
    url="http://localhost:8086",
    token='w1vABiIPJ28ixch-pz-DyDDjTlnOpLsxSY8yrUT5dvMi9Xn_wsnDUAU-E4oyTVFhfVHGtqskQRAUm_6LHbZQYA=='
)
client.api_client.configuration.timeout = 60*1000

if erase_all:
    print('Erasing all data in bucket...', end='')
    start = "2020-01-01T00:00:00Z"
    stop = "2020-10-01T00:00:00Z"
    delete_api = client.delete_api()
    delete_api.delete(start, stop, None, bucket=bucket, org=org) # '_measurement="delay"'
    print('\rErased all data in bucket!      ')
    exit(0)

write_api = client.write_api()
query_api = client.query_api()

m = {
    'delay': 'de',
    'psg_up': 'up',
    'psg_down': 'do'
}
def recordToGenericPoint (record):
    return Point(m[record['field']]) \
        .tag("day_of_service", record['day_of_service']) \
        .tag("route_id", record['route_id']) \
        .tag("trip_id", record['trip_id']) \
        .tag("stop_id", record['stop_id']) \
        .tag("block_id", record['block_id']) \
        .tag("stop_call", f"{record['route_id']}_{record['trip_id']}_{record['stop_id']}") \
        .time(record['datetime'], WritePrecision.S)

write_time_start = time.perf_counter()

stopcalls_path = "rpt_stop_details_202312221216_6.sql"
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