import re

def fileToDict (filename, onlySample=False) -> dict:

  with open(filename, 'r') as file:
    
    ltables = {}
    print(f'File {filename} caricato', end='')
    cmds = file.read().split(';')
    print(f'\rFile {filename} letto, sono {len(cmds)} comandi')

    if onlySample: cmds = cmds[:1000]

    for cmd_idx, cmd in enumerate(cmds):
      now_perc = int((cmd_idx + 1) / len(cmds) * 100)
      prev_perc = int(cmd_idx / len(cmds) * 100)
      if now_perc != prev_perc: print(f'\rSto parsando la riga {cmd_idx + 1}/{len(cmds)} ({now_perc}%)', end='')
      if not cmd: continue
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