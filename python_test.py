import re

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

small = True

def fileToDict (filename) -> dict:

  with open(filename, 'r') as file:
    
    ltables = {}
    print(f'File {filename} caricato', end='')
    cmds = file.read().split(';')
    print(f'\rFile {filename} letto, sono {len(cmds)} comandi')

    if small: cmds = cmds[:1000]

    for cmd_idx, cmd in enumerate(cmds):
      now_perc = int((cmd_idx + 1) / len(cmds) * 100)
      prev_perc = int(cmd_idx / len(cmds) * 100)
      if now_perc != prev_perc: print(f'\rSto parsando la riga {cmd_idx + 1}/{len(cmds)} ({now_perc}%)', end='')
      if not cmd: continue
      cmd = cmd.strip()
      if not cmd or len(cmd) < 20: continue
      cmd = cmd[19:]
      table, data = cmd.split(' ', 1)

      if not table in ltables:
        ltables[table] = {
          'records': [],
          'legend': None
        }

      rows = re.findall(r'\((.*?)\)', data)
      legend = rows[0].split(',')
      ltables[table]['legend'] = legend
      for row in rows[1:]:
        record = {}
        for idx, el in enumerate(row.split(',')):
          if el == 'NULL': el = None
          elif el == 'false': el = False
          elif el == 'true': el = True
          else: el = eval(el)
          record[legend[idx]] = el
        ltables[table]['records'].append(record)
  print()
  return ltables

rpt_stop_details = fileToDict("rpt_stop_details_202308080948.sql")
prev_stop_details = fileToDict("prev_stop_details_202308080953.sql")
rpt_trips = fileToDict("rpt_trips_202308080953.sql")

all_data = { **rpt_stop_details, **prev_stop_details, **rpt_trips }

stops = {}
routes = {}
for rec in all_data['prev_stop_details']['records']:
  stops[rec['stop_id']] = rec['stop_name']
  routes[rec['route_id']] = rec['route_name']

for t,v in all_data.items():
  # media_delay = sum([rec['delay'] for rec in v['records'] if rec['delay']]) / len(v['records'])
  # print(t, media_delay)
  print(t, len(v['records']))




# print(tables)
exit(0)

with open('rpt_stop_details_202308080948.sql') as f:
  txt = f.read()
  # print(txt.count('2023-07-03'))
  res = re.split("(?:[^;]|(?:'.*?'))*", txt)
  print(len(res))