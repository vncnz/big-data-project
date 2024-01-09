import time, pickle
from datetime import datetime, timedelta
import traceback

import psycopg2

from utilities import countRows, dataGenerator, progressBar

# sudo systemctl start postgresql.service

host = 'localhost'
org = 'vncnz'
bucket = 'bigdata_cfr'
pwd = 'bigdata_project'
erase_all = False
skip_write = False

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
        values ('{record['day_of_service']}', {record['route_id']}, {record['trip_id']}, {record['stop_id']}, {record['block_id'] or 'NULL'}, '{record['datetime']}'::timestamp, {record['delay'] or 'NULL'}, {record['psg_up'] or 'NULL'}, {record['psg_down'] or 'NULL'});"

write_time_start = time.perf_counter()

stopcalls_path = "rpt_stop_details_202312221311.sql"
stops_path = "sch_gtfs_stops_202312071735.sql"
total_rows = countRows(stopcalls_path)

i = 0
err = 0
ok = 0
for record in dataGenerator(stopcalls_path, stops_path, False):
    query = recordToInsertQuery(record)
    if not skip_write:
        try:
            cursor.execute(query)
            conn.commit()
            ok += 1
        except Exception as exc:
            err += 1
            print(exc)
            print(query)
            traceback.print_exc()
    i += 1
    progressBar(i, total_rows, 40)
print('')
print(f'{err} errori, {ok} record inseriti con successo')

write_time_end = time.perf_counter()

conn.close()

diff = write_time_end - write_time_start
# print(f"The written time for {len(records)} records in influxdb is: {timedelta(seconds = diff)}")
print(f"The written time for {i} records in postgresql is: {timedelta(seconds = diff)} ({(i / diff):.2f} records per second)")