from datetime import datetime, timedelta
import psycopg2
import time

host = 'localhost'
org = 'vncnz'
bucket = 'bigdata_project'
pwd = 'bigdata_project'

conn = psycopg2.connect(database='postgres',
                        host=host,
                        user="postgres",
                        password=pwd,
                        port=5432)
cursor = conn.cursor()



query = '''
select DATE_TRUNC('month', datetime) AS month, extract(dow from datetime) as weekday, stop_id, avg(psg_up) from bigdata_project
where day_of_service > '2020-09-10' and day_of_service < '2020-10-12' and psg_up is not null
group by month, weekday, stop_id
-- limit 100
'''

queryy = '''
select route_id, trip_id, stop_id, avg(delay) from bigdata_project
where day_of_service > '2020-09-10' and day_of_service < '2020-10-12' and delay is not null
group by route_id, trip_id, stop_id
-- limit 100
'''

# query = 'select * from bigdata_project limit 1'

def executeQuery (query):
    cursor.execute(query)
    rows = cursor.fetchall()
    return rows

write_time_start = time.perf_counter()
results = executeQuery(query)
write_time_end = time.perf_counter()
diff = write_time_end - write_time_start

def countResults(results):
    return { 'results': len(results), 'cols': 0, 'tables': 1 }

def printResultTables(results, cols, max_records):

    lengths = []
    for col in cols:
        # l = col.label in ['_time', '_stop', '_start'] and 18 or 10
        l = (col == 'datetime' or col == 'month') and 25 or max(10, len(col))
        lengths.append(l)
        print(col.rjust(l), end='  ')
    print('')
    for record in results[:max_records]:
        # for col in cols:
        #     dt = record.values.get(col.label)
        #     if col.data_type == 'dateTime:RFC3339':
        #         dt = dt.strftime('%Y%m%d@%H:%M:%S')
        #     if col.label in ['_time', '_stop', '_start']:
        #         print('%18s' % dt, end='  ')
        #     else:
        #         print('%10s' % dt, end='  ')
        # print('')
        # print(record)
        for idx, val in enumerate(record):
            print(f'{val}'.rjust(lengths[idx]), end='  ')
        print('')

printResultTables(results, [desc[0] for desc in cursor.description], 5)
print(countResults(results))
print(f"Query executed in : {timedelta(seconds = diff)} seconds")