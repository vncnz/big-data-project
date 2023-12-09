from utilities import fileToDict

def produceSeparateRecords (tableData):

    records = []
    blocks = set()
    trips = set()
    routes = set()
    stops = set()
    dos = set()

    for rec in tableData['records']:
        # schedule_id, block_id, trip_id, arrival_time, real_time, stop_id, stop_sequence, shape_dist_traveled, real_dist_traveled, day_of_service,
        # psg_up, psg_down, creation_timestamp, update_timestamp, vehicle_id, delay, reported, route_id, quality, served, fake, count
        if rec['delay'] is not None or rec['psg_up'] or rec['psg_down']:
            newrec = {
                'schedule_id': rec['schedule_id'],
                'route_id': rec['route_id'],
                'trip_id': rec['trip_id'],
                'block_id': rec['block_id'],
                'stop_id': rec['stop_id'],
                'stop_sequence': rec['stop_sequence'],
                'day_of_service': rec['day_of_service']
            }

            # Le separo perché in campo arrivano separatamente!
            if rec['psg_up'] is not None:
                newrec1 = { **newrec, 'field': 'psg_up', 'value': rec['psg_up'] }
                records.append(newrec1)

            if rec['psg_down'] is not None:
                newrec2 = { **newrec, 'field': 'psg_down', 'value': rec['psg_down'] }
                records.append(newrec2)
            
            if rec['delay'] is not None:
                newrec3 = { **newrec, 'field': 'delay', 'value': rec['delay'] }
                records.append(newrec3)

            routes.add(rec['route_id'])
            trips.add(rec['trip_id'])
            blocks.add(rec['block_id'])
            stops.add(rec['stop_id'])
            dos.add(rec['day_of_service'])
    return records

def createStopMap(filename, onlySample=False):
    stops_table = fileToDict(filename, onlySample)
    stops_list = stops_table['sch_gtfs_stops']['records']
    # stops_list = list(filter(lambda x: x['stop_code'] == '648', stops_list))
    m = {}
    for stop in stops_list:
        m[f"{stop['schedule_id']}_{stop['stop_id']}"] = stop['stop_code']
    return m

# for el in stops_map:
#     if el['stop_code'] in m: m[el['stop_code']] += 1
#     else: m[el['stop_code']] = 1

# for k,v in m.items():
#     print(f'{k}: {v} occorrenze')
stops_map = createStopMap("sch_gtfs_stops_202312071735.sql", onlySample=False)

rpt_stop_details = fileToDict("rpt_stop_details_202312041753.sql", onlySample=False)
records = produceSeparateRecords(rpt_stop_details['rpt_stop_details'])

def addStopCodes (records, stops_map):
    for rec in records:
        k = str(rec['schedule_id']) + '_' + rec['stop_id']
        if k in stops_map:
            rec['stop_code'] = stops_map[k]

def groupBy (records, keys):
    key = lambda rec: '_'.join([rec[k] for k in keys])
    groups = {}
    for rec in records:
        k = key(rec)
        if not k in groups: groups[k] = [rec]
        else: groups[k].append(rec)
    return groups

addStopCodes(records, stops_map)

records = [rec for rec in records if rec['field'] == 'delay']# rec['delay'] is not None]

groups_trip = groupBy(records, ['trip_id'])
groups_trip_and_stop = {}
for trip_id, group in groups_trip.items():
    groups_trip_and_stop[trip_id] = groupBy(group, ['trip_id', 'stop_id'])

for k,v in list(groups_trip.items())[:1]:
    print(v)

a_random_trip = list(groups_trip_and_stop.values())[4]
# all = [item for sublist in a_random_trip.values() for item in sublist if item['delay'] is not None]
for all in sorted(list(a_random_trip.values()), key = lambda recs: len(recs), reverse = True)[:10]:
    delays = list(map(lambda s: s['value'], all))
    avg = sum(delays) / len(delays)
    print(len(delays), avg)

exit(0)





records = []
blocks = set()
trips = set()
routes = set()
stops = set()
dos = set()



numToPrint = 30
for rec in records[:numToPrint]:
    print(rec)
print(f'{len(records) - numToPrint} records omessi')