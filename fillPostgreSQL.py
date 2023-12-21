import time, pickle
from datetime import datetime, timedelta

import psycopg2

from utilities import progressBar

# sudo systemctl start postgresql.service

pickle_time_start = time.perf_counter()
with open('records', 'rb') as file:
    records = pickle.load(file)
records = [x for x in records if x['datetime'] and x['stop_id'] and (x['field'] != 'psg_up' or x['value'] < 200)]
pickle_time_end = time.perf_counter()
print(f"The loading time for {len(records)} records in python is: {timedelta(seconds = (pickle_time_end - pickle_time_start))}")


host = 'localhost'
org = 'vncnz'
bucket = 'bigdata_project'
pwd = 'bigdata_project'
erase_all = True
skip_write = False

# client = InfluxDBClient(
#   url="https://europe-west1-1.gcp.cloud2.influxdata.com",
#   token="Taiju5w8TEteVMjU4bt6emM3L0NpgnWAinolzSEYfB4JCVphV9DjebNRvQASWXzKSOqkKO4TvthcB74N1ICCPw=="
# )

conn = psycopg2.connect(database='postgres',
                        host=host,
                        user="postgres",
                        password=pwd,
                        port=5432)
cursor = conn.cursor()

if erase_all:
    print('Erasing all data in table...', end='')
    cursor.execute(f"DELETE FROM public.{bucket}")
    # 'create table bigdata_project (day_of_service text, route_id integer, trip_id integer, stop_id integer, block_id integer, datetime timestamp with time zone, delay integer, psg_up smallint, psg_down smallint);'
    print('\rErased all data in table!      ')


# records = [rec for rec in records if rec['field'] == 'delay']# rec['delay'] is not None]
# records = records[:1000]

def recordToInsertQuery (record):
    return f"insert into public.{bucket} (day_of_service, route_id, trip_id, stop_id, block_id, datetime, delay, psg_up, psg_down) \
        values ('{record['day_of_service']}', {record['route_id']}, {record['trip_id']}, {record['stop_id']}, {record['block_id']}, '{record['datetime']}'::timestamp, {record['delay'] or 'NULL'}, {record['psg_up'] or 'NULL'}, {record['psg_down'] or 'NULL'})"

complex_records = {}
i = 0
for record in records:
    k = f"{record['day_of_service']}, {record['route_id']}, {record['trip_id']}, {record['stop_id']}, {record['block_id']}, {record['datetime']}"
    if not k in complex_records:
        complex_records[k] = record
        complex_records[k]['delay'] = None
        complex_records[k]['psg_up'] = None
        complex_records[k]['psg_down'] = None
    complex_records[k][record['field']] = record['value']

records = complex_records.values()

write_time_start = time.perf_counter()

for record in records:
    query = recordToInsertQuery(record)
    if not skip_write: cursor.execute(query)
    i += 1
    progressBar(i, len(records), 40)
print('')

write_time_end = time.perf_counter()
diff = write_time_end - write_time_start
# print(f"The written time for {len(records)} records in influxdb is: {timedelta(seconds = diff)}")
print(f"The written time for {len(records)} records in postgresql is: {timedelta(seconds = diff)} ({(len(records) / diff):.2f} records per second)")