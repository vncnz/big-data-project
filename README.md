# big-data-project
Progetto d'esame per Big Data AA 2022/2023 - Matricola VR457811

## Contesto ed introduzione

Quella che segue è una relazione che prova a confrontare le prestazioni nella gestione di un numeri significativo di dati in due diversi tipi di database: PostgreSQL e InfluxDB; e lo fa basandosi in parte su un confronto nell'utilizzo reale degli stessi nel contesto di seguito descritto ed in parte su letteratura già esistente.
Trattandosi di due database profondamente diversi vedremo anche le differenze in termini di architettura, implementazione ed interrogazione.
La parte implementativa e di analisi diretta del progetto si concentra sul salvataggio e sulla rielaborazione di dati di tipo temporale e più nello specifico dati relativi alla registrazione dei passaggi a fermata dei mezzi di trasporto pubblico di una città italiana di medie dimensioni. L'idea nasce come ipotetica estensione delle funzionalità di un sistema AVM (Automatic Vehicle Monitoring) realizzato dal sottoscritto in ambito lavorativo. Tale sistema riceve i dati grezzi da un sistema gps presente a bordo di ogni autobus e fornisce le seguenti funzionalità:
- verifica che il mezzo sia correttamente sul percorso a lui assegnato
- riconosce il passaggio a fermata, ovvero l'azione di passaggio accanto ad ogni fermata designata e con eventuale fermata del mezzo per far salire e scendere i passeggeri
- calcola il ritardo/anticipo del mezzo rispetto alla tabella di marcia per la corsa a cui è assegnato
- memorizza una serie di dati:
  - i segnali grezzi ricevuti dal mezzo
  - i segnali rielaborati con l'aggiunta di indicazioni sullo stato del mezzo (corsa assegnata, prossima fermata, anticipo/ritardo, passeggeri a bordo, eccetera)
  - i dati di passaggio per la reportistica, ovvero per la produzione di report mensili che l'azienda deve consegnare al comune per ricevere una compensazione economica dipendente dalla qualità del servizio effettuato

Uno dei punti critici del sistema sviluppato riguarda il salvataggio e la rielaborazione dei dati di reportistica in quanto si tratta di una grandissima quantità di dati da leggere, scrivere e rielaborare; attualmente i limiti riscontrati a livello di prestazioni del database PostgreSQL utilizzato per tale sistema sono stati parzialmente aggirati salvando oltre ai dati dettagliati delle statistiche pre-calcolate sul breve periodo basandosi su dati che vengono tenuti in RAM.
Una funzionalità che **non** è presente nel sistema e che ho ritenuto interessante per il progetto da realizzare per questo esame è l'analisi dei dati memorizzati per l'individuazione di deviazioni tra i passaggi a fermata previsti secondo la pianificazione ed i passaggi registrati nella realtà di ogni giorno. Un'analisi di questo tipo richiede la rielaborazione di un grande numero di record. Per dare una prima idea dell'ordine di grandezza, i passaggi a fermata registrati per la sola domenica 2/07/2023 sono 6258 mentre per il lunedì seguente sono 43960. Effettuare delle analisi statistiche su un periodo che può coprire mesi significa quindi lavorare su milioni di record.

## Obiettivo della parte implementativa del progetto

L'obiettivo è la creazione di statistiche che sarebbero utili all'azienda cliente, in un'ipotetica messa in produzione del codice qui sviluppato, per correggere e migliorare le tabelle di passaggi a fermata che gli autobus devono rispettare. Vengono analizzate le prestazioni dei due database sia in fase di salvataggio che di interrogazione. Le prestazioni dipendono chiaramente da un grande numero di variabili e da una natura diversa dei database stessi ma si cerca di essere il più omogenei possibile.

## Limiti di questa analisi prestazionale

I due database confrontati non differiscono solo nella struttura (relazionale vs buckets) e nell'obiettivo (dati generici vs serie temporali) ma anche nell'architettura di base. Mentre PostgreSQL viene eseguito solitamente come mono-istanza in locale, sulla macchina che ospita anche gli altri servizi o al massimo su una macchina dedicata, InfluxDB nasce come sistema di memorizzazione in cloud ed è fortemente orientato a tale scenario di utilizzo. Per questo progetto, tuttavia, è stata utilizzata una versione installabile in locale per poter confrontare le prestazioni a parità di risorse hardware ed in un ambiente controllato.

# Parte teorica

## Database model
InfluxDB è un "timeseries database", cioè un database orientato al salvataggio di dati temporali
## Architetura
## Licenza
## Use cases
## Scalability


# Parte pratica

## [Tecnologie usate]

Il progetto è realizzato in Python, utilizza Flask per la creazione di un servizio web ed apposite librerie per l'esecuzione dei salvataggi e delle interrogazioni. I dati provengono da un database utilizzato realmente in una città italiana di piccole dimensioni, sono stati esportati tramite la creazione di file sql che sono stati letti da uno script in python e travasati, tramite due script separati, in influxdb ed in postgresql. I due script condividono la maggior parte del codice e differiscono per la sola parte legata allo specifico database di destinazione.

## Descrizione dell'organizzazione dei dati
Siccome InfluxDB nasce per gestire serie temporali e non altro, la maggior parte dei dati richiedono il salvataggio in un database di appoggio che può essere proprio PostgreSQL. Mentre PostgreSQL può essere l'unico database utilizzato per raggiungere l'obiettivo nel caso di InfluxDB si avrà invece la coesistenza dei due database, uno utilizzato per la memorizzazione di tutti i dati non temporali ed uno utilizzato per questi ultimi. Non esistono vincoli specifici che impediscono il salvataggio di anagrafiche in InfluxDB ma è un tipo di dati perfetto per un database relazionale e non timeseries-oriented.
In questo progetto si immagina quindi di avere le anagrafiche di fermate, linee e quant'altro residenti in tabelle PostgreSQL dedicate che non viene però implementate per evitare che ciò interferisca con le query in esame e perché superfluo ai fini dell'analisi. La struttura del database PostgreSQL da cui sono stati estratti i dati ha le seguenti colonne:

- [ ] schedule_id: id della pianificazione attiva
- [x] block_id: id del turno macchina
- [x] trip_id: id della corsa
- [ ] arrival_time: orario di arrivo previsto
- [ ] real_time: orario di arrivo reale
- [x] stop_id: id della fermata servita
- [ ] stop_sequence: autoincrementale della fermata all'interno del turno macchina
- [ ] shape_dist_traveled: distanza prevista della fermata dalla partenza della corsa
- [ ] real_dist_traveled distanza percorsa dal mezzo dalla partenza della corsa
- [x] day_of_service: giorno di servizio
- [x] psg_up: passeggeri saliti alla fermata
- [x] psg_down: passeggeri scesi alla fermata
- [ ] creation_timestamp: timestamp di creazione del record
- [x] update_timestamp: timestamp di aggiornamento del record
- [ ] vehicle_id: id del veicolo che ha effettuato la fermata
- [x] delay: ritardo rispetto al passaggio previsto
- [ ] reported: fermata recistrata
- [x] route_id: id della linea
- [ ] quality: qualità del servizio in base al ritardo
- [ ] served: non usato
- [ ] fake: boolean che indica se la registrazione della fermata è reale o calcolata a posteriori

I dati marcati con un check sono stati implementati in questo progetto e quindi travasati, gli altri dati sono stati esclusi perché considerati non utili ai fini del confronto prestazionale tra i database. Alcuni di questi ultimi sono strettamente legati al funzionamento del sistema di provenienza (ad esempio i flag _served_ e _fake_), allo studio di eventuali bug (ad esempio _creation_timestamp_) e/o a politiche economiche legate al cliente per cui il sistema è stato implementato (i campi _quality_, _shape_dist_traveled_ ed altri).

### [Descrizione della base dati postgres]
Per l'implementazione in PostgreSQL è stata creata una tabella con i dati sopra indicati. Per ciascuna stop call [TODO: spiegare cos'è] sono presenti in un unico record delay, psg_up e psg_down (se esistenti).
Sono stati creati degli indici per le colonne relative a trip, stop, block, day_of_service, route.

### [Descrizione della base dati influxdb]
Per l'implementazione in InfluxDB è stato utilizzato un bucket con i seguenti elementi:
- (_time) timestamp: ora del passaggio o dell'orario previsto
[TODO: ricontrollare e/o eliminare] - (_measurement) measurement: "R" per passaggio reale, "P" per l'orario previsto
- (tag) schedule_id
- (tag) block_id
- (tag) trip_id
- (tag) stop_id
- (tag) day_of_service
- (tag) route_id
- (_field) "psg_up" (passeggeri saliti) / "psg_down" (passeggeri scesi) / "delay" (ritardo)
- (_value) numero relativo a _field

E' importante ricordare che in InfluxDB solo i tag vengono indicizzati, i valori (_field e _value) non sono indicizzati. Si è scelto quindi di utilizzare il numero di passeggeri saliti/scesi ed il mezzo che ha effettuato la fermata come valori memorizzati ed i vari identificatori della fermata (la fermata fisica, la linea, la corsa, eccetera) come tag. Questi sono anche quei campi tendenzialmente ripetitivi (una corsa ha molte fermate, da una fermata passano molte corse, eccetera) e questo assicura di non far esplodere la cardinalità della serie temporale, anche se essa sarà comunque relativamente alta in particolare per colpa dell'id fermata.

## Configurazione software/hardware e nota sulle prestazioni

Qualunque dato prestazionale presente in questo documento si riferisce all'esecuzione su una macchina virtuale VirtualBox con 4 core e 6gb di RAM. La CPU fisica è una AMD Ryzen 7 4800U e grazie all'opzione PAE/NX attiva 4 dei suoi core sono esposti direttamente alla VM. Il disco virtuale è del tipo "dynamic allocation storage" e si trova fisicamente su un disco NVME M2 connesso tramite USB3.1. Su macchine o configurazioni differenti le prestazioni possono chiaramente differire ma lo scopo dei tempi qui riportati è fine al confronto tra i due database e non devono essere presi in senso assoluto.
Il sistema operativo è GNU/Linux, per maggior precisione una distro Arch.
Il software è scritto in python 3.x, la gestione di influxdb è effettuata tramite la libreria ufficiale influxdb_client mentre per postgres ho usato la libreria psycopg2.

## Riempimento dei dati e prestazioni di inserimento
Per entrambi i database c'è la necessità di leggere i dati dai file sql per effettuare poi l'inserimento nel database di destinazione. Siccome i file da cui i dati provengono sono di grandi dimensioni (giga) il caricamento da file e la scrittura nel database devono avvenire di pari passo.
La preparazione dei dati per InfluxDB prevede la creazione, per ogni punto, di un'istanza di una classe fornita dalla libreria, la lettura e preparazione di tutti i dati impiega circa un minuto e venti secondi. La preparazione dei dati per PostgreSQL prevede invece la creazione di query tramite interpolazione di stringhe ed questo invece impiega circa un minuto e dieci secondi. In entrambi i casi questi tempi sono stati presi senza l'inserimento reale dei dati nel rispettivo database ai fini di capirne l'influenza sulle tempistiche totali misurate ma la creazione nella versione finale del codice avviene contestualmente all'inserimento, record per record, non occupando così un quantitativo di RAM degno di nota. Questo è reso necessario dal fatto che volendo testare l'inserimento di un alto numero di record lo spazio occupato dai dati in RAM non è accettabile.
La quantità di record da inserire cambia in base al database, questo è dovuto al fatto che per ogni passaggio a fermata effettuato possono esistere da uno a tre dati raccolti:
- ritardo/anticipo
- passeggeri saliti
- passeggeri scesi
In PostgreSQL questi (eventualmente) tre dati vengono inseriti in un unico record mentre in InfluxDB vengono inseriti come tre diversi datapoints. Già in questo vediamo una differenza sostanziale in uno scenario di utilizzo in real time di uno e dell'altro database: con InfluxDB ogni dato che arriva dal campo si trasforma in un punto da inserire, con PostgreSQL ogni dato si trasforma invece in una _insert or update_. L'alternativa, per quanto riguarda PostgreSQL, è scegliere un momento in cui il sistema è scarico e preparare preventivamente tutti i record che dovranno ospitare i dati in arrivo durante la giornata, così da evitare le _insert or update_ ed effettuare solo degli _update_. Naturalmente è possibile strutturare la tabella in PostgreSQL in modo che ospiti una colonna _field_ ed una _value_ assumendo un aspetto più simile al bucket in InfluxDB ma questo sembra meno naturale per un database relazionale.

I dati provengono da sei diversi file con estensione .sql di circa 500mb ciascuno [TODO: controllare il peso], le tempistiche di inserimento sono state le seguenti:

<table>
  <thead>
    <tr>
      <th></th>
      <th colspan="3">PostgreSQL</th>
      <th colspan="3">Influxdb</th>
    </tr>
    <tr>
      <th>File</th>
      <th># records</th>
      <th>Tempo</th>
      <th>rec/sec</th>
      <th># records</th>
      <th>Tempo</th>
      <th>rec/sec</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>1</td>
      <td>1490706</td>
      <td>0:30:16.069264</td>
      <td>820.84</td>
      <td>2067108</td>
      <td>0:07:05.215808</td>
      <td>4861.32</td>
    </tr>
    <tr>
      <td>2</td>
      <td>1881493</td>
      <td>0:37:18.237019</td>
      <td>840.61</td>
      <td>2640835</td>
      <td>0:08:39.005862</td>
      <td>5088.26</td>
    </tr>
    <tr>
      <td>3</td>
      <td>2021527</td>
      <td>0:40:13.353439</td>
      <td>837.64</td>
      <td>2882403</td>
      <td>0:09:25.619937</td>
      <td>5096.01</td>
    </tr>
    <tr>
      <td>4</td>
      <td>2075451</td>
      <td>0:42:30.483643</td>
      <td>813.75</td>
      <td>2978935</td>
      <td>0:10:08.921629</td>
      <td>4892.15</td>
    </tr>
    <tr>
      <td>5</td>
      <td>2079754</td>
      <td>0:42:12.619232</td>
      <td>821.19</td>
      <td>2934493</td>
      <td>0:10:44.535332</td>
      <td>4552.88</td>
    </tr>
    <tr>
      <td>6</td>
      <td>886979</td>
      <td>0:13:02.482605</td>
      <td>1133.54</td>
      <td>1288200</td>
      <td>0:04:39.054345</td>
      <td>4616.31</td>
    </tr>
  </tbody>
</table>

```
[TODO: rimuovere, esempio inserimento per copia-incolla della tilda]
```

## Estrazione dei dati e prestazioni di select

## Ritardo medio fermata
La prima query per testare e confrontare le prestazioni tra i due database in esame riguarda il calcolo del ritardo medio per ciascuna corsa in ciascuna fermata in un certo periodo di tempo.

Questa query è stata creata in due versioni diverse e lanciata in entrambe le versioni su periodi di uno, tre e sei mesi. Le due versioni differiscono tra loro per l'assenza o la presenza di un raggruppamento su base mensile.

Le query eseguite in PostgreSQL per ottenere i dati sono le seguenti:
(Con raggruppamento)
```
select DATE_TRUNC('month', datetime) AS month, route_id, trip_id, stop_id, avg(delay) from bigdata_project
where day_of_service > '2020-09-10' and day_of_service < '2022-03-12' and delay is not null
group by month, route_id, trip_id, stop_id
```

(Senza raggruppamento)
```
select route_id, trip_id, stop_id, avg(delay) from bigdata_project
where day_of_service > '2020-09-10' and day_of_service < '2021-10-12' and delay is not null
group by route_id, trip_id, stop_id
```

Per quanto riguarda InfluxDB invece sono le seguenti:
(Con raggruppamento)
```
from(bucket:"bigdata_project2")
|> range(start: 2020-09-11T00:00:00Z, stop: 2021-03-11T23:59:59Z)
|> filter(fn:(r) => r._measurement == "de")
// |> drop(columns: ["_start", "_stop"])
|> group(columns: ["route_id", "trip_id", "stop_id"])
|> aggregateWindow(every: 1mo, fn: mean)
// |> group()
|> keep(columns: ["_time", "route_id", "trip_id", "stop_id", "_value"])
```

(Senza raggruppamento)
```
from(bucket:"bigdata_project2")
|> range(start: 2020-09-11T00:00:00Z, stop: 2020-10-11T23:59:59Z)
|> filter(fn:(r) => r._measurement == "de")
|> drop(columns: ["_start", "_stop"])
|> group(columns: ["route_id", "trip_id", "stop_id"])
|> mean()
|> group()
|> keep(columns: ["_time", "route_id", "trip_id", "stop_id", "_value"])
```

I tempi perché il processo in Python ottenesse la lista completa di risultati sono espressi nel formato h:mm:ss.sss. Queste tempistiche sono state ottenute dopo l'inserimento nei database del solo file 1 di dati:

<table>
  <thead>
    <tr>
      <th></th>
      <th colspan="3">PostgreSQL</th>
      <th colspan="3">Influxdb</th>
    </tr>
    <tr>
      <th>Raggruppamento</th>
      <th>Un mese</th>
      <th>Tre mesi</th>
      <th>Sei mesi</th>
      <th>Un mese</th>
      <th>Tre mesi</th>
      <th>Sei mesi</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Senza</td>
      <td>0:00:00.369832</td><td>0:00:00.472875</td><td>0:00:01.141519</td>
      <td>0:00:07.040072</td><td>0:00:07.864913</td><td>0:00:54.924719</td>
    </tr>
    <tr>
      <td>Con</td>
      <td>0:00:00.564010</td><td>0:00:00.640163</td><td>0:00:01.854010</td>
      <td>0:00:09.885804</td><td>0:00:19.470520</td><td>0:01:27.276970</td>
    </tr>
  </tbody>
</table>

Vediamo che la situazione per quanto riguarda il recupero dei dati si è ribaltata. In fase di lettura dei dati è presente infatti una fortissima disparità che vede PostgreSQL estremamente più veloce rispetto ad InfluxDB nella lettura. Parleremo in seguito di come questo può non essere un problema per l'utilizzatore di InfluxDB.

Seguono i tempi per le stesse query nelle stesse modalità ma con tutti i dati inseriti:
[TODO]

## Una questione di cardinalità
La cardinalità è un concetto importante in InfluxDB ed inficia pesantemente le prestazioni ed i requisiti, tanto che si può mettere in relazione la cardinalità con il quantitativo di RAM occupata.

Per studiare a fondo le prestazioni di InfluxDB è stato usato un set di dati più ristretto del precedente e sono stati creati tre diversi buckets con un diverso numero di tags:
1) Route_trip_stop, Block
2) Route, Trip, Stop, Block
3) Route, Trip, Stop, Route_trip_stop, Block
4) Block

La seconda combinazione è quella più naturale mentre la prima e la terza sono state create per valutarne gli impatti sulle prestazioni. La quarta non ha utilità pratica ma è stata creata solo per analizzare la situazione in cui si ha un unico tag con cardinalità ridotta.
Da notare come Route_trip_stop sia dato dalla combinazione tra tre diversi tag e la sua cardinalità sia pari alla moltiplicazione tra le cardinalità di tali tag.

### Prestazioni in inserimento

Per i tag fare riferimento all'elenco qui sopra. Il tempo è sempre nel formato h:mm:ss.sss mentre rec/sec sta per records inseriti al secondo.
|Tags|         Tempo|rec/sec|
|----|--------------|-------|
|   1|0:07:12.722923|5139.89|
|   2|0:07:38.987807|4845.77|
|   3|0:08:09.947025|4539.57|
|   4|0:06:15.663339|5920.59|

All'aumentare del numero di tag diminuisce in maniera non rilevante la velocità di inserimento dei records.

### Prestazioni di lettura: uno o più tags con stessa cardinalità risultante
Per confrontare la modalità 2 con la modalità 3 possiamo fare due query che differiscono solo per il raggruppamento: una raggruppa per la combinazione route, trip e stop (modalità 2) e l'altra per route_trip_stop (modalità 3):

|Mode|Tempo         |Numero risultati|
|----|--------------|----------------|
|3su3|0:00:21.358964|          100734|
|3su2|0:00:21.600971|          100734|
|1su3|0:00:18.654712|          100734|
|1su1|0:00:16.935693|          100734|
|Bsu3|0:00:07.488148|             132|
|Bsu4|0:00:00.342538|             132|

Da questa tabella possiamo dedurre diverse cose:
- guardando a 3su3 e 1su3, utilizzare un solo tag dato dalla combinazione di tre tag diversi riduce leggermente le tempistiche ma non sembra dare un vero vantaggio rispetto alla combinazione di più tag con la stessa cardinalità risultante.
- guardando a 3su3 e 3su2, filtrando per tre tag separati (route, trip e stop) su una tabella il fatto che essa abbia o meno un tag che ne sia la combinazione (route_trip_stop)
- una query che lavora sullo stesso numero di dati nello stesso periodo ma utilizza solo un tag con cardinalità minore impiega un tempo decisamente minore
- una query che lavora sullo stesso numero di dati nello stesso periodo ma su un bucket che non possiede un'elevata cardinalità è estremamente più performante

### Occupazione spazio su disco

Per visualizzare in ambiente linux la dimensione dei vari buckets possiamo semplicemente eseguire un comando simile a `du -sh /home/vncnz/.influxdbv2/engine/data/* | sort -hr` ottenendo un output simile al seguente (l'indicazione del bucket è stata aggiunta a posteriori):

```
4,7G	/home/vncnz/.influxdbv2/engine/data/b77778300c262ad4 --> bucket completo
748M	/home/vncnz/.influxdbv2/engine/data/2e65568d31d832e4 --> bucket ridotto per confronto (modalità 3)
658M	/home/vncnz/.influxdbv2/engine/data/f786e5d253b98a85 --> bucket ridotto per confronto (modalità 2)
530M	/home/vncnz/.influxdbv2/engine/data/f7fd809664dfe27c --> bucket ridotto per confronto (modalità 1)
9,6M	/home/vncnz/.influxdbv2/engine/data/0794a0c95d6efca3 --> bucket ridotto per confronto (modalità 4)
160K	/home/vncnz/.influxdbv2/engine/data/394df8c8e6b03e99 --> bucket per utilizzo interno dell'engine
```

Confrontando il bucket modalità 4 con quelli delle altre modalità è evidente come il peso dei dati sia estremamente ridotto e gli indici legati ai tag abbiano un peso molto elevato

Per confronto, eseguendo in postgres la query `SELECT pg_size_pretty( pg_total_relation_size('bigdata_cfr') );` si vede un peso di 144MB.






## La soluzione alla lentezza del recupero dati di InfluxDB: i task

## Considerazioni su PostgreSQL

## Considerazioni su InfluxDB


## Considerazioni finali











``` PostgreSQL (REMOVE ME)
Query executed in : 0:00:00.369832 seconds --> 1 mese senza raggruppamento
Query executed in : 0:00:00.564010 seconds --> 1 mese e raggruppato per mese

Query executed in : 0:00:00.472875 seconds --> 3 mesi senza raggruppamento
Query executed in : 0:00:00.640163 seconds --> 3 mesi e raggruppato per mese

Query executed in : 0:00:01.141519 seconds --> 6 mesi senza raggruppamento
Query executed in : 0:00:01.854010 seconds --> 6 mesi e raggruppato per mese
```





?18 -> 718
;18 -> 318
;07 -> 307
;14 -> 314
57: -> 578

-------------- POSTGRESQL --------------

PRIMO
[vncnz@Julie big-data-project]$ /bin/python /media/sf_NNNNNNNNNNNNNNNNNN/big-data-project/fillPostgreSQL.py
File sch_gtfs_stops_202312071735.sql letto, sono 1053 comandi
Sto parsando la riga 1053/1053 (100%)
MAX RAM: 69.5
  ⏳ Progress: [---------------------->                 ] 58 %
0 errori, 1490706 record inseriti con successo
The written time for 1490706 records in postgresql is: 0:30:16.069264 (820.84 records per second)

SECONDO
[vncnz@Julie big-data-project]$ /bin/python /media/sf_NNNNNNNNNNNNNNNNNN/big-data-project/fillPostgreSQL.py
File sch_gtfs_stops_202312071735.sql letto, sono 1053 comandi
Sto parsando la riga 1053/1053 (100%)
MAX RAM: 59.5
  ⏳ Progress: [----------------------------->          ] 75 %
0 errori, 1881493 record inseriti con successo
The written time for 1881493 records in postgresql is: 0:37:18.237019 (840.61 records per second)

TERZO
[vncnz@Julie big-data-project]$ /bin/python /media/sf_NNNNNNNNNNNNNNNNNN/big-data-project/fillPostgreSQL.py
File sch_gtfs_stops_202312071735.sql letto, sono 1053 comandi
Sto parsando la riga 1053/1053 (100%)
MAX RAM: 60.5
  ⏳ Progress: [------------------------------->        ] 81 %
0 errori, 2021527 record inseriti con successo
The written time for 2021527 records in postgresql is: 0:40:13.353439 (837.64 records per second)

QUERY PER TREDICI MESI RAGGRUPPATI
{'results': 753592, 'cols': 0, 'tables': 1}
Query executed in : 0:00:10.162645 seconds

QUARTO
1894443 errori, 181008 record inseriti con successo
The written time for 2075451 records in postgresql is: 0:18:33.961609 (1863.13 records per second)
--- RIFATTO ---
es/lib/python/debugpy/adapter/../../debugpy/launcher 49453 -- /media/sf_NNNNNNNNNNNNNNNNNN/big-data-project/fillPostgreSQL.py 
File sch_gtfs_stops_202312071735.sql letto, sono 1053 comandi
Sto parsando la riga 1053/1053 (100%)
MAX RAM: 79.9
  ⏳ Progress: [-------------------------------->       ] 84 %
0 errori, 2075451 record inseriti con successo
The written time for 2075451 records in postgresql is: 0:42:30.483643 (813.75 records per second)

QUERY PER TREDICI MESI RAGGRUPPATI (cold start)
{'results': 806881, 'cols': 0, 'tables': 1}
Query executed in : 0:00:15.283426 seconds

QUINTO
[vncnz@Julie big-data-project]$ /bin/python /media/sf_NNNNNNNNNNNNNNNNNN/big-data-project/fillPostgreSQL.py
File sch_gtfs_stops_202312071735.sql letto, sono 1053 comandi
Sto parsando la riga 1053/1053 (100%)
MAX RAM: 39.5
  ⏳ Progress: [-------------------------------->       ] 84 %
0 errori, 2079754 record inseriti con successo
The written time for 2079754 records in postgresql is: 0:42:12.619232 (821.19 records per second)

QUERY PER TREDICI MESI RAGGRUPPATI
{'results': 806881, 'cols': 0, 'tables': 1}
Query executed in : 0:00:11.608005 seconds

QUERY PER TREDICI MESI RAGGRUPPATI (COLD START)
{'results': 816239, 'cols': 0, 'tables': 1}
Query executed in : 0:00:23.493937 seconds

SESTO
File sch_gtfs_stops_202312071735.sql letto, sono 1053 comandi
Sto parsando la riga 1053/1053 (100%)
MAX RAM: 38.6
  ⏳ Progress: [----------------------->                ] 61 %
0 errori, 886979 record inseriti con successo
The written time for 886979 records in postgresql is: 0:13:02.482605 (1133.54 records per second)

QUERY PER TREDICI MESI RAGGRUPPATI (COLD START)
{'results': 848941, 'cols': 0, 'tables': 1}
Query executed in : 0:00:17.925656 seconds



-------------- INFLUX --------------

SECONDO
  ⏳ Progress: [----------------------------->          ] 75 %
The written time for 2641119 records in influxdb is: 0:07:38.219967 (5763.87 records per second)

TERZO
File sch_gtfs_stops_202312071735.sql letto, sono 1053 comandi
Sto parsando la riga 1053/1053 (100%)
MAX RAM: 61.3
  ⏳ Progress: [------------------------------->        ] 81 %
The written time for 2882854 records in influxdb is: 0:10:01.458585 (4793.10 records per second)

CAMBIO QUERY...
VECCHIA: 
from(bucket:"bigdata_project")
|> range(start: 2020-09-11T00:00:00Z, stop: 2020-10-11T23:59:59Z) //-3y)
|> filter(fn:(r) => r._measurement == "delay")
// |> drop(columns: ["_start", "_stop"])
|> keep(columns: ["_time", "route_id", "trip_id", "stop_id", "_value"])
|> group(columns: ["route_id", "trip_id", "stop_id"])
|> aggregateWindow(every: 1mo, fn: mean)
|> group()

NUOVA:
from(bucket:"bigdata_project")
|> range(start: 2020-09-11T00:00:00Z, stop: 2020-10-11T23:59:59Z) //-3y)
|> filter(fn:(r) => r._measurement == "delay")
// |> drop(columns: ["_start", "_stop"])
|> group(columns: ["route_id", "trip_id", "stop_id"])
|> aggregateWindow(every: 1mo, fn: mean)
|> group()
|> keep(columns: ["_time", "route_id", "trip_id", "stop_id", "_value"])

Forse si può ancora migliorare!
... aggiungendo un tag che è l'unione dei tag route, trip, stop (in fondo anche postgres ha una pk indicizzata sull'unione)
Filtrando su un solo tag infatti la query di prova da 10 secondi scende a 3 (con la vecchia query era addirittura 20s)



PRIMO
  ⏳ Progress: [---------------------->                 ] 58 %
The written time for 2067108 records in influxdb is: 0:07:05.215808 (4861.32 records per second)

SECONDO
  ⏳ Progress: [----------------------------->          ] 75 %
The written time for 2640835 records in influxdb is: 0:08:39.005862 (5088.26 records per second)

TERZO
  ⏳ Progress: [------------------------------->        ] 81 %
The written time for 2882403 records in influxdb is: 0:09:25.619937 (5096.01 records per second)

QUERY PER QUATTRO MESI RAGGRUPPATI
{'results': 188405, 'cols': 3, 'tables': 37681}
Query executed in : 0:00:25.999506 seconds

CINQUE MESI
{'results': 372240, 'cols': 3, 'tables': 62040}
Query executed in : 0:00:51.305029 seconds

SEI MESI
{'results': 444115, 'cols': 3, 'tables': 63445}
Query executed in : 0:01:20.212098 seconds



QUARTO
  ⏳ Progress: [-------------------------------->       ] 84 %
The written time for 2978935 records in influxdb is: 0:10:08.921629 (4892.15 records per second)

QUERY PER TREDICI MESI RAGGRUPPATI (cold start)
SALTATA

QUINTO
  ⏳ Progress: [-------------------------------->       ] 84 %
The written time for 2934493 records in influxdb is: 0:10:44.535332 (4552.88 records per second)

QUERY PER TREDICI MESI RAGGRUPPATI
SALTATA

QUERY PER TREDICI MESI RAGGRUPPATI (COLD START)
SALTATA

SESTO
  ⏳ Progress: [----------------------->                ] 61 %
The written time for 1288200 records in influxdb is: 0:04:39.054345 (4616.31 records per second)

QUERY PER SEI MESI RAGGRUPPATI (COLD START)
{'results': 560000, 'cols': 3, 'tables': 80000}
Query executed in : 0:02:22.445360 seconds

##############################################################################################
##############################################################################################

Confronto per numero di tag:

Route, trip, stop, block, route_trip_stop
  ⏳ Progress: [------------------------------->        ] 80 %
The written time for 2224148 records in influxdb is: 0:08:09.947025 (4539.57 records per second)

Route, trip, stop, block
  ⏳ Progress: [------------------------------->        ] 80 %
The written time for 2224148 records in influxdb is: 0:07:38.987807 (4845.77 records per second)

  ⏳ Progress: [------------------------------->        ] 80 %
The written time for 2224148 records in influxdb is: 0:07:12.722923 (5139.89 records per second)

Su postgres la tabella di cfr è
  ⏳ Progress: [------------------------------->        ] 80 %
0 errori, 1583462 record inseriti con successo
The written time for 1583462 records in postgresql is: 0:29:12.295566 (903.65 records per second)