from utilities import fileToDict


pt_stop_details = fileToDict("rpt_stop_details_202312041753.sql", onlySample=True)

records = []
blocks = set()
trips = set()
routes = set()
stops = set()
dos = set()


for rec in pt_stop_details['rpt_stop_details']['records']:
    # schedule_id, block_id, trip_id, arrival_time, real_time, stop_id, stop_sequence, shape_dist_traveled, real_dist_traveled, day_of_service,
    # psg_up, psg_down, creation_timestamp, update_timestamp, vehicle_id, delay, reported, route_id, quality, served, fake, count
    if rec['served'] or rec['psg_up'] or rec['psg_down']:
        newrec = {
            'route': rec['route_id'],
            'trip': rec['trip_id'],
            'block': rec['block_id'],
            'stop': rec['stop_id'],
            'sequence': rec['stop_sequence'],
            'day_of_service': rec['day_of_service']
        }

        # Le separo perché in campo arrivano separatamente!
        newrec1 = { **newrec, 'field': 'psg_up', 'value': rec['psg_up'] }
        newrec2 = { **newrec, 'field': 'psg_down', 'value': rec['psg_down'] }
        newrec3 = { **newrec, 'field': 'delay', 'value': rec['delay'] }
        records.append(newrec1)
        records.append(newrec2)
        records.append(newrec3)

        routes.add(rec['route_id'])
        trips.add(rec['trip_id'])
        blocks.add(rec['block_id'])
        stops.add(rec['stop_id'])
        dos.add(rec['day_of_service'])

for rec in records[:30]:
    print(rec)