from utilities import fileToDict


pt_stop_details = fileToDict("rpt_stop_details_202312041753.sql", onlySample=True)

records = []

for rec in pt_stop_details['rpt_stop_details']['records']:
    # schedule_id, block_id, trip_id, arrival_time, real_time, stop_id, stop_sequence, shape_dist_traveled, real_dist_traveled, day_of_service,
    # psg_up, psg_down, creation_timestamp, update_timestamp, vehicle_id, delay, reported, route_id, quality, served, fake, count
    if rec['served']:
        newrec = {
            'route': rec['route_id'],
            'trip': rec['trip_id'],
            'block': rec['block_id'],
            'stop': rec['stop_id'],
            'sequence': rec['stop_sequence'],
            'day_of_service': rec['day_of_service'],
            'psg_up': rec['psg_up'],
            'psg_down': rec['psg_down'],
            'delay': rec['delay']
        }
        records.append(newrec)

print(len(records))