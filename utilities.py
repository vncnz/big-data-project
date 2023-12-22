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
                'day_of_service': rec['day_of_service'],
                'datetime': rec['update_timestamp']
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







last_percent = -1
def progressBar(current, total, barLength = 20):
    global last_percent
    percent = int((float(current) * 100 / total) + 0.5)
    if last_percent != percent:
      arrow   = '-' * int(percent/100 * barLength - 1) + '>'
      spaces  = ' ' * (barLength - len(arrow))

      print(percent >= 100 and '  ✅' or '  ⏳', 'Progress: [%s%s] %d %%' % (arrow, spaces, percent), end='\r')
      last_percent = percent





def separateRecords (rec):
  if rec['delay'] is not None or rec['psg_up'] or rec['psg_down']:
    newrec = {
      'schedule_id': rec['schedule_id'],
      'route_id': rec['route_id'],
      'trip_id': rec['trip_id'],
      'block_id': rec['block_id'],
      'stop_id': rec['stop_id'],
      'stop_sequence': rec['stop_sequence'],
      'day_of_service': rec['day_of_service'],
      'datetime': rec['update_timestamp']
    }

    # Le separo perché in campo arrivano separatamente!
    if rec['psg_up'] is not None:
      yield { **newrec, 'field': 'psg_up', 'value': rec['psg_up'] }

    if rec['psg_down'] is not None:
      yield { **newrec, 'field': 'psg_down', 'value': rec['psg_down'] }

    if rec['delay'] is not None:
      yield { **newrec, 'field': 'delay', 'value': rec['delay'] }

import sqlite3
def parse (line):
  conn = sqlite3.connect(":memory:")
  conn.execute('''CREATE TABLE rpt_stop_details (
                        schedule_id int8 NOT NULL,
                        block_id varchar NULL,
                        trip_id varchar NOT NULL,
                        arrival_time varchar NULL,
                        real_time varchar NULL,
                        stop_id varchar NULL,
                        stop_sequence int4 NOT NULL,
                        shape_dist_traveled float8 NULL,
                        real_dist_traveled float8 NULL,
                        day_of_service text NOT NULL,
                        psg_up int4 NULL,
                        psg_down int4 NULL,
                        creation_timestamp timestamptz NULL,
                        update_timestamp timestamptz NULL,
                        vehicle_id int4 NULL,
                        delay int4 NULL,
                        reported bool NULL,
                        route_id varchar NULL,
                        quality int2 NULL,
                        served bool NULL,
                        fake bool NOT NULL DEFAULT false,
                        count int8 NULL
                      );''')
  conn.execute(line.replace('public.', ''))
  parsed_rows = list(conn.execute("select * from rpt_stop_details"))
  conn.close()
  return parsed_rows

def recordGeneratorFromFile (filename, onlySample=False) -> dict:

  # max_ram = 0

  with open(filename, 'r') as file:

    # print(f'File {filename} caricato', end='')

    cumulative_row = ''
    line_idx = -1
    for line in file:

      line = line.strip()
      # cmds = file.read().split(';')
      # print(f'\rFile {filename} letto, sono {len(cmds)} comandi')

      if line.startswith('INSERT'):
         cumulative_row = line
      else:
         cumulative_row += line
      
      if cumulative_row.endswith(');'):
        if onlySample and line_idx > 10: break
        line_idx += 1
        res = parse(cumulative_row)
        for rec in res:
          yield rec

legend = 'schedule_id, block_id, trip_id, arrival_time, real_time, stop_id, stop_sequence, shape_dist_traveled, real_dist_traveled, day_of_service, psg_up, psg_down, creation_timestamp, update_timestamp, vehicle_id, delay, reported, route_id, quality, served, fake, count'.split(', ')
def dataGenerator (stopcalls_path, stops_path, onlySample=False):
  stops_map = createStopMap(stops_path, onlySample)

  i = 0
  for rec in recordGeneratorFromFile(stopcalls_path, onlySample):
    rec = dict(zip(legend, rec))
    # print(i, rec)
    i += 1

    k = str(rec['schedule_id']) + '_' + rec['stop_id']
    if k in stops_map:
      rec['stop_code'] = stops_map[k]

    # Filtro record incompleti
    if rec['update_timestamp'] and rec['stop_id']:

      # pulizia valori sballati
      if rec['delay'] and abs(rec['delay']) > 6*60*60*1000: rec['delay'] = None
      if rec['psg_up'] and rec['psg_up'] > 200: rec['psg_up'] = None
      if rec['psg_down'] and rec['psg_down'] > 200: rec['psg_down'] = None

      # rinomino qualche campo
      rec['datetime'] = rec['update_timestamp']
      # del rec['update_timestamp']
      # del rec['creation_timestamp']
      yield rec

def _count_generator(reader):
    b = reader(1024 * 1024)
    while b:
        yield b
        b = reader(1024 * 1024)

def countRows (filepath):
  with open(filepath, 'rb') as fp:
    c_generator = _count_generator(fp.raw.read)
    count = sum(buffer.count(b'\n') for buffer in c_generator)
    return count + 1

if __name__ == '__main__':
  stopcalls_path = "rpt_stop_details_202312221216.sql"
  stops_path = "sch_gtfs_stops_202312071735.sql"

  total_rows = countRows(stopcalls_path)
  rows = 0
  for row in dataGenerator(stopcalls_path, stops_path, False):
    # print(row)
    rows += 1
    # print(f'\rCaricamento stop call {rows:,} su {total_rows:,}             ', end='')
    progressBar(rows, total_rows, 40)
  print()