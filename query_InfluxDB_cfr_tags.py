# from influxdb import InfluxDBClient
# client = InfluxDBClient(host='localhost', port=8086)

# from datetime import datetime

from influxdb_client import InfluxDBClient #, Point, WritePrecision
import time
from datetime import timedelta
# from influxdb_client.client.write_api import SYNCHRONOUS

org = 'vncnz'

client = InfluxDBClient(
    url="http://localhost:8086",
    token='w1vABiIPJ28ixch-pz-DyDDjTlnOpLsxSY8yrUT5dvMi9Xn_wsnDUAU-E4oyTVFhfVHGtqskQRAUm_6LHbZQYA=='
)

# write_api = client.write_api()
query_api = client.query_api()
client.api_client.configuration.timeout = 5*60*1000

query = '''
from(bucket:"bigdata_cfr5")
|> range(start: 2023-10-01T00:00:00Z, stop: 2023-10-30T23:59:59Z)
|> filter(fn:(r) => r._measurement == "de")
|> drop(columns: ["_start", "_stop"])
|> group(columns: ["block_id"])
|> aggregateWindow(every: 1mo, fn: mean, createEmpty: false)
|> group()
|> keep(columns: ["_time", "block_id", "_value"])
'''
query = '''
from(bucket:"bigdata_cfr5")
|> range(start: 2023-10-01T00:00:00Z, stop: 2023-10-30T23:59:59Z)
|> filter(fn:(r) => r._measurement == "de")
|> drop(columns: ["_start", "_stop"])
|> keep(columns: ["_time", "block_id", "_value"])
'''
# |> group(columns: ["route_id", "trip_id", "stop_id"])
# |> keep(columns: ["_time", "route_id", "trip_id", "stop_id", "_value"])

write_time_start = time.perf_counter()
results = query_api.query(query=query, org=org)
write_time_end = time.perf_counter()
diff = write_time_end - write_time_start

lst = []

cols = []

def countResults(results):
    t = 0
    c = 0
    r = 0

    for table in results:
        t += 1
        c = len(table.get_group_key())
        r += len(table.records)
    
    return { 'results': r, 'cols': c, 'tables': t }

def printResultTables(results, max_tables, max_records):
    def fltr(lst):
        return [x for x in lst] #if x.label not in ['result', '_start', '_stop', '_field', '_measurement']]

    for table in results[:max_tables]:
        tablecols = fltr(table.get_group_key())
        print('\nTable ', ', '.join(map(lambda c: '%s=%s' % (c.label, table.records[0][c.label]), tablecols)))
        cols = fltr(table.columns)
        for col in cols:
            l = col.label in ['_time', '_stop', '_start'] and 18 or 10
            print(col.label.rjust(l), end='  ')
        print('')
        for record in table.records[:max_records]:
            for col in cols:
                dt = record.values.get(col.label)
                if col.data_type == 'dateTime:RFC3339':
                    dt = dt.strftime('%Y%m%d@%H:%M:%S')
                if col.label in ['_time', '_stop', '_start']:
                    print('%18s' % dt, end='  ')
                else:
                    print('%10s' % dt, end='  ')
            print('')
            # lst.append((record.get_time().isoformat(), str(record.values.get('elapsed')).rjust(8), record.values.get('card'), record.values.get('poi'), record.values.get('dispositivo')))

printResultTables(results, 5, 5)
print(countResults(results))
print(f"Query executed in : {timedelta(seconds = diff)} seconds")

exit(0)
# for el in lst:
#    print(el)

diz = {}
for el in lst:
    if not el[2] in diz:
        diz[el[2]] = []
    diz[el[2]].append(el)

for cardlst in diz.values():
    for el in cardlst:
        print(el)
    print('')

exit(0)

print('Query done. Starting plot...')

import matplotlib.pyplot as plt
import math


cols = 4
figure, axis = plt.subplots(math.ceil(len(results)/cols), cols)
xx = 0
yy = 0

xdata = list(range(0, 366))

for table in results:

    dayofyear = [x.values['dayofyear'] for x in table.records]
    for idx, dt in enumerate(dayofyear):
        if dt[3:5] == '01' or dt[3:5] == '15':
            xdata[idx] = dt
    axis[yy, xx].plot(xdata, [x.values['2019'] for x in table.records], label = "2019")
    axis[yy, xx].plot(xdata, [x.values['2020'] for x in table.records], label = "2020")
    tablecols = fltr(table.get_group_key())
    axis[yy, xx].set_title(', '.join(map(lambda c: '%s=%s' % (c.label, table.records[0][c.label]), tablecols)))
    axis[yy, xx].legend()

    xx += 1
    if xx >= cols:
        xx = 0
        yy += 1

# naming the x axis
plt.xlabel('Giorno')

# naming the y axis
plt.ylabel('Visite')

# giving a title to my graph
#tablecols = fltr(table.get_group_key())
#plt.title(', '.join(map(lambda c: '%s=%s' % (c.label, table.records[0][c.label]), tablecols)))

# show a legend on the plot
plt.legend()

# function to show the plot
plt.show()