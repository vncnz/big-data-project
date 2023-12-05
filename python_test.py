import re, datetime, random

from utilities import fileToDict

# txt = """INSERT INTO public.rpt_stop_details (schedule_id,block_id,trip_id,arrival_time,real_time,stop_id,stop_sequence,shape_dist_traveled,real_dist_traveled,day_of_service,psg_up,psg_down,creation_timestamp,update_timestamp,vehicle_id,delay,reported,route_id,quality,served,fake) VALUES
# 	 (958,'606','104','15:10:00',NULL,'255',1,0.0,NULL,'2023-07-01',NULL,NULL,'2023-07-01 08:40:05.827817+02',NULL,NULL,NULL,NULL,'10',NULL,NULL,false),
# 	 (958,'604','670','07:25:00','2023-07-01 07:22:32','89',18,5.545000076293945,NULL,'2023-07-01',NULL,NULL,'2023-07-01 08:40:05.827817+02','2023-07-01 07:22:40+02',105,-148,true,'8',NULL,false,false),
# 	 (958,'611','86','08:01:00','2023-07-01 07:55:01','209',18,6.898000240325928,NULL,'2023-07-01',1,0,'2023-07-01 08:40:05.827817+02','2023-07-01 07:55:14+02',205,-359,true,'2',NULL,false,false),
# 	 (958,'611','86','08:04:00','2023-07-01 07:58:04','213',21,9.273000717163086,NULL,'2023-07-01',1,0,'2023-07-01 08:40:05.827817+02','2023-07-01 07:58:09+02',205,-356,true,'2',NULL,false,false),
# 	 (958,'611','86','08:05:00','2023-07-01 07:59:02','214',22,9.770000457763672,NULL,'2023-07-01',NULL,NULL,'2023-07-01 08:40:05.827817+02','2023-07-01 07:59:10+02',205,-358,true,'2',NULL,false,false),
# 	 (958,'611','86','08:06:00','2023-07-01 07:59:46','542',23,10.158000946044922,NULL,'2023-07-01',NULL,NULL,'2023-07-01 08:40:05.827817+02','2023-07-01 07:59:51+02',205,-374,true,'2',NULL,false,false),
# 	 (958,'611','86','08:07:00','2023-07-01 08:00:18','543',24,10.593000411987305,NULL,'2023-07-01',0,1,'2023-07-01 08:40:05.827817+02','2023-07-01 08:00:22+02',205,-402,true,'2',NULL,false,false),
# 	 (958,'611','86','08:08:00',NULL,'512',25,10.904000282287598,NULL,'2023-07-01',NULL,NULL,'2023-07-01 08:40:05.827817+02',NULL,NULL,NULL,NULL,'2',NULL,NULL,false),
# 	 (958,'611','86','08:09:00',NULL,'510',26,11.285000801086426,NULL,'2023-07-01',NULL,NULL,'2023-07-01 08:40:05.827817+02',NULL,NULL,NULL,NULL,'2',NULL,NULL,false),
# 	 (958,'611','86','08:10:00',NULL,'507',27,11.48900032043457,NULL,'2023-07-01',NULL,NULL,'2023-07-01 08:40:05.827817+02',NULL,NULL,NULL,NULL,'2',NULL,NULL,false);
# INSERT INTO public.rpt_stop_details (schedule_id,block_id,trip_id,arrival_time,real_time,stop_id,stop_sequence,shape_dist_traveled,real_dist_traveled,day_of_service,psg_up,psg_down,creation_timestamp,update_timestamp,vehicle_id,delay,reported,route_id,quality,served,fake) VALUES
# 	 (958,'611','86','08:11:00','2023-07-01 08:02:05','505',28,11.796000480651855,NULL,'2023-07-01',NULL,NULL,'2023-07-01 08:40:05.827817+02','2023-07-01 08:02:15+02',205,-535,true,'2',NULL,false,false),
# 	 (958,'611','86','08:12:00','2023-07-01 08:03:29','202',29,12.165000915527344,NULL,'2023-07-01',NULL,NULL,'2023-07-01 08:40:05.827817+02','2023-07-01 08:03:37+02',205,-511,true,'2',NULL,false,false),
# 	 (958,'611','86','08:13:00','2023-07-01 08:03:51','503',30,12.370000839233398,NULL,'2023-07-01',NULL,NULL,'2023-07-01 08:40:05.827817+02','2023-07-01 08:03:57+02',205,-549,true,'2',NULL,false,false),
# 	 (958,'611','86','08:13:00','2023-07-01 08:04:11','263',31,12.515000343322754,NULL,'2023-07-01',NULL,NULL,'2023-07-01 08:40:05.827817+02','2023-07-01 08:04:18+02',205,-529,true,'2',NULL,false,false),
# 	 (958,'611','86','08:13:00','2023-07-01 08:04:31','261',32,12.749000549316406,NULL,'2023-07-01',NULL,NULL,'2023-07-01 08:40:05.827817+02','2023-07-01 08:04:38+02',205,-509,true,'2',NULL,false,false),
# 	 (958,'611','86','08:14:00','2023-07-01 08:04:47','259',33,12.91300106048584,NULL,'2023-07-01',NULL,NULL,'2023-07-01 08:40:05.827817+02','2023-07-01 08:04:59+02',205,-553,true,'2',NULL,false,false),
# 	 (958,'611','86','08:14:00','2023-07-01 08:05:06','281',34,13.224000930786133,NULL,'2023-07-01',NULL,NULL,'2023-07-01 08:40:05.827817+02','2023-07-01 08:05:19+02',205,-534,true,'2',NULL,false,false),
# 	 (958,'611','86','08:15:00','2023-07-01 08:05:40','412',35,13.540000915527344,NULL,'2023-07-01',0,2,'2023-07-01 08:40:05.827817+02','2023-07-01 08:05:50+02',205,-560,true,'2',NULL,false,false),
# 	 (958,'611','86','08:16:00','2023-07-01 08:07:00','436',36,13.903000831604004,NULL,'2023-07-01',NULL,NULL,'2023-07-01 08:40:05.827817+02','2023-07-01 08:07:12+02',205,-540,true,'2',NULL,false,false),
# 	 (958,'611','86','08:17:00','2023-07-01 08:08:12','255',37,14.194000244140625,NULL,'2023-07-01',0,0,'2023-07-01 08:40:05.827817+02','2023-07-01 08:08:23+02',205,-528,true,'2',NULL,false,false);"""

onlySample = False

rpt_stop_details = fileToDict("rpt_stop_details_202312041753.sql", onlySample)
# prev_stop_details = fileToDict("prev_stop_details_202308080953.sql")
rpt_trips = fileToDict("rpt_trips_202312041755.sql", onlySample)

all_data = { **rpt_stop_details, **rpt_trips }
dateformat = "%Y-%m-%d %H:%M:%S"

stop_calls = {}
routes = {}
trips = {}
stops = {}
# prevs = {}
for rec in all_data['rpt_stop_details']['records']:
  if not rec['served']: continue
  s = rec['stop_id']
  r = rec['route_id']
  t = rec['trip_id']
  d = rec['day_of_service']
  routes[r] = True
  trips[t] = True
  stops[s] = True
  k = (r, t, s)
  if not k in stop_calls: stop_calls[k] = [rec]
  else: stop_calls[k].append(rec)

routes = routes.keys()
trips = trips.keys()
stops = stops.keys()

print(f'Caricati {len(routes)} linee, {len(trips)} corse, {len(stops)} fermate, {len(stop_calls.keys())} stop calls grouped by day')

m = sum(map(lambda x: len(x), stop_calls.values())) / len(stop_calls.keys())
f = {}
for v,k in stop_calls.items():
  if len(k) > 1: f[v] = k

print(f'{m} giorni in media per stop_call, {len(f.keys())} stop_calls con più di un passaggio')

for k,v in list(f.items()):
  v = list(filter(lambda x: x['delay'], v))
  if len(v):
    m = sum(map(lambda x: float(x['delay']), v)) / len(v)
    psg_up = sum(map(lambda x: float(x['psg_up'] or 0), v)) / len(v)
    psg_down = sum(map(lambda x: float(x['psg_down'] or 0), v)) / len(v)
    print(f'route: {k[0]}\ttrip: {k[1]}\tstop: {k[2]}\t->\tmedia: {m}\tpsg_up: {psg_up}\tpsg_down: {psg_down}')

exit(0)

# FAKE SERVED_TIME
# dt = datetime.datetime.strptime(rec["aimed_arrival_time"], dateformat)
# r = random.randint(-300, 300)
# rec["served_time"] = (dt + datetime.timedelta(seconds = r)).strftime(dateformat)
# rec["delay"] = r

# prevs[(rec['route_id'], rec['trip_id'], rec['stop_id'], rec['day_of_service'])] = rec

for t,v in all_data.items():
  # media_delay = sum([rec['delay'] for rec in v['records'] if rec['delay']]) / len(v['records'])
  # print(t, media_delay)
  print(t, len(v['records']))

print('\nRoute examples')
for id, name in list(routes.items())[:10]:
  print(f'Route {id:>2}: {name}')

print('\nStop examples')
for id, name in list(stops.items())[:10]:
  print(f'Stop {id[0]:>3} of route {id[1]:>2}: {name}')

onlyServed = False
items = list(onlyServed and filter(lambda x: x[1]['served_time'], prevs.items()) or prevs.items())

prevs = sorted(items, key=lambda x: x[0])

for id, data in prevs[:3]: # list(prevs.items())[:3]:
  print(f'route {id[0]:>2}, trip {id[1]:>3}, stop {id[2]:>3}, dos {id[3]:>10}: {data["aimed_arrival_time"]} / {data["served_time"]}')

# QUI POSSO INIZIARE A RAGGRUPPARE I DATI PER OTTENERE LE STATISTICHE
grouped_by_trip = {}
for id, data in prevs:
  stop, trip, stop, day_of_service = id
  k = (stop, trip, day_of_service)
  if not k in grouped_by_trip: grouped_by_trip[k] = []
  grouped_by_trip[k].append(data)

for k,v in sorted(grouped_by_trip.items(), key = lambda item: item[0][1]):
  print('by trip:', k, len(v))

if False:
  grouped_by_stop = {}
  for id, data in prevs:
    k = id[2]
    if not k in grouped_by_stop: grouped_by_stop[k] = []
    grouped_by_stop[k].append(data)

  for k,v in list(grouped_by_stop.items())[:10]:
    print(f'Ritardo medio fermata {k} {sum(map(lambda x: x["delay"], v))/len(v)} secondi per {len(v)} passaggi')
    # print('by stop:', k, len(v))



# print(tables)
exit(0)

with open('rpt_stop_details_202308080948.sql') as f:
  txt = f.read()
  # print(txt.count('2023-07-03'))
  res = re.split("(?:[^;]|(?:'.*?'))*", txt)
  print(len(res))