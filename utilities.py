import re, psutil

def fileToDict (filename, onlySample=False) -> dict:

  max_ram = 0

  with open(filename, 'r') as file:
    
    ltables = {}
    print(f'File {filename} caricato', end='')
    cmds = file.read().split(';')
    print(f'\rFile {filename} letto, sono {len(cmds)} comandi')

    if onlySample: cmds = cmds[:1000]

    cumulative_row = ''

    for cmd_idx, cmd in enumerate(cmds):
      now_perc = int((cmd_idx + 1) / len(cmds) * 100)
      prev_perc = int(cmd_idx / len(cmds) * 100)
      if now_perc != prev_perc: print(f'\rSto parsando la riga {cmd_idx + 1}/{len(cmds)} ({now_perc}%)', end='')
      if not cmd: continue

      if cmd[-1] != ')':
        cumulative_row += cmd
        continue
      elif cumulative_row:
         cmd = cumulative_row + cmd
         cmd = cmd.replace('\n', '').replace('\t', '')
         cumulative_row = ''

      cmd = cmd.strip()
      if not cmd or len(cmd) < 20: continue
      cmd = cmd[12:]
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
        ram = psutil.virtual_memory()[2]
        if ram > max_ram: max_ram = ram
        if ram < 90:
          record = {}
          for idx, el in enumerate(row.split(',')):
            if el == 'NULL': el = None
            elif el == 'false': el = False
            elif el == 'true': el = True
            else: el = eval(el)
            record[legend[idx]] = el
          ltables[table]['records'].append(record)
        else:
           print(f"OUT OF MEMORY after {ltables[table]['records']} records")
           exit(0)
  print()
  print(f'MAX RAM: {max_ram}')
  return ltables

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

def produceData (stopcalls_path, stops_path, onlySample=False):
    stops_map = createStopMap(stops_path, onlySample)
    rpt_stop_details = fileToDict(stopcalls_path, onlySample)
    records = produceSeparateRecords(rpt_stop_details['rpt_stop_details'])
    addStopCodes(records, stops_map)
    return records

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

def progressBar(current, total, barLength = 20):
    percent = float(current) * 100 / total
    arrow   = '-' * int(percent/100 * barLength - 1) + '>'
    spaces  = ' ' * (barLength - len(arrow))

    print(percent >= 100 and '  ✅' or '  ⏳', 'Progress: [%s%s] %d %%' % (arrow, spaces, percent), end='\r')