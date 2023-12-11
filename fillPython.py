from datetime import timedelta
from utilities import groupBy, produceData
import itertools, time

stopcalls_path = "rpt_stop_details_202312041753.sql"
stops_path = "sch_gtfs_stops_202312071735.sql"
records = produceData(stopcalls_path, stops_path)

start_time = time.perf_counter()

records = [rec for rec in records if rec['field'] == 'delay']# rec['delay'] is not None]

groups_trip = groupBy(records, ['trip_id'])
# groups_trip_and_stop = {}
# for trip_id, group in groups_trip.items():
#    groups_trip_and_stop[trip_id] = groupBy(group, ['trip_id', 'stop_id'])

results = []
for k,v in groups_trip.items():
    # print(v)
    v = sorted(v, key = lambda x: x['stop_sequence'])
    trip = [k, v]
    for kk,vv in itertools.groupby(v, lambda x: x['stop_sequence']):
        # print(kk, vv)
        delays = list(map(lambda s: s['value'], vv))
        avg = sum(delays) / len(delays)
        trip.append(avg)
        # print(f'trip:{k}, seq:{kk:>2}, cnt:{len(delays)}, avg:{avg}')
    results.append(trip)

end_time = time.perf_counter()
execution_time = end_time - start_time
print(f"The computation time for {len(results)} trips in python is: {timedelta(seconds = execution_time)}")