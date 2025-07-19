# Big Data Exam Project - Academic Year 2022/2023 - Student ID VR457811

#### Note
This project was originally a university assignment, but extended with real-world benchmarks and analysis. Original language it is written with was italian.

## Introduction and Context

This document presents a performance comparison between two different types of databases, PostgreSQL and InfluxDB, focusing on their ability to handle large amounts of data. The analysis is based on real-world usage scenarios, as described below.

Since the two databases are fundamentally different — and InfluxDB is relatively unknown — this report also includes an overview of its main architecture and functionalities.

The implementation and analysis focus on storing and processing time-series data, specifically related to public transportation stop events in a medium-sized Italian city. This project originated as a hypothetical extension of the features of an Automatic Vehicle Monitoring (AVM) system I developed in a professional context. That system receives raw data from GPS devices installed on board each bus and provides the following functionalities:

- verifies that the vehicle is following its assigned route
- detects stop calls, meaning the action of passing by or stopping at designated bus stops to pick up or drop off passengers
- calculates delays or early arrivals relative to the scheduled timetable
- stores various types of data:
  - raw signals received from the vehicle
  - processed signals enriched with information such as assigned trip, next stop, delay/early status, number of passengers on board, etc.
  - stop call records for reporting purposes, used to generate monthly reports that the company must submit to the municipality to receive compensation based on service quality

Each of these last records represents a _stop call_, a term commonly used in public transportation to describe a specific stop made by a vehicle while operating a certain trip on a specific route. These records are crucial for reporting since the company uses them to calculate reimbursement from the municipality, which varies according to service quality. Reports are typically generated monthly, but data must be retained for several years for legal compliance (e.g., in case of incidents requiring judicial investigation) or for internal service analysis.

A critical aspect of the existing system is the storage and post-processing of reporting data, due to the large volume of records that must be read, written, and analyzed. For context: in a small city, there are approximately 400 trips per day, each with an average of 30 stops, resulting in around 12,000 stop calls per day. Spread over 20 hours of service, that’s one stop call every six seconds on average, and roughly one million records every three months.

Currently, performance limitations with the PostgreSQL database have been partially mitigated by saving not only raw data but also short-term pre-aggregated statistics, relying on in-memory data caching.

A feature missing in the current system, which I considered interesting for this comparative study, is the analysis of archived data to identify recurring discrepancies between scheduled stop times and actual arrival times. Such analysis requires the post-processing of a large dataset.

## Query Objectives

The goal is to generate statistics that could be useful for the client company — if this were implemented in the original system — to help optimize bus stop scheduling.

The project analyzes the performance of both databases in terms of write speed and query speed. Obviously, performance depends on many factors, and since the databases serve different use cases by design, every effort was made to create comparable test conditions.

## Limitations of This Performance Analysis

The two databases differ not only in data structure (relational vs. time-series) and intended use case (general-purpose vs. time-series) but also in system architecture. PostgreSQL typically runs as a local, single-instance service, either on the same machine as other services or on a dedicated server. InfluxDB, on the other hand, was designed with a cloud-oriented, distributed architecture in mind.

However, for the purposes of this project, I used the local installation of InfluxDB to ensure comparable hardware and a controlled environment, which also removes some of InfluxDB’s advantages in distributed scenarios.

## Theoretical Background on InfluxDB
Let’s start with a brief explanation of InfluxDB, as it is less widely known compared to PostgreSQL.

InfluxDB is a DBMS written primarily in Go that uses Time-Structured Merge Trees (TSM) to efficiently store time-series data. Data is compressed and organized into _shards_, which group records by time range. Queries are executed using a language called _Flux_, which works as a pipeline of data operations, where each command processes the output of the previous one.

Unlike most databases, InfluxDB allows you to perform aggregations without losing data granularity and to expand or re-group results after initial aggregations. It also provides useful time-based functions, such as windowing aggregations.

The user interface is web-based, providing RESTful APIs for programmatic access and a modern web dashboard for direct user interaction. The dashboard includes a graphical query builder and built-in visualization tools. However, in this project, all queries and interactions were handled via Python scripts.

InfluxDB uses a two-phase write process: first, data is written to Write-Ahead Log (WAL) files acting as a buffer, and then it is flushed into the main database storage. For production systems with high throughput, InfluxDB’s authors recommend storing WAL files and database files on separate physical volumes to maximize disk I/O performance.

Since version 2.x, InfluxDB uses the TSM engine to store data in a columnar format, combining data and indexes within the same files to optimize query performance.

A key distinction of InfluxDB: there is no “update” operation. Data is always appended, which aligns with its time-series focus.

# Comparison Project

## Technologies Used

The project is developed in Python 3.x and uses the python-influxdb and psycopg2 libraries to handle data insertion and querying in InfluxDB and PostgreSQL, respectively.
The data comes from a real-world database used by a small Italian city. The data was exported by generating SQL dump files, which were then processed and imported into the target databases using two separate Python scripts. These scripts share most of the codebase and differ only in the portions related to the specifics of the target database.

## Software/Hardware Configuration and Performance Disclaimer

All performance-related data in this document refers to execution within a VirtualBox virtual machine configured with 4 cores and 8 GB RAM.
The host machine is equipped with an AMD Ryzen 7 4800U CPU, with PAE/NX enabled, allowing four cores to be directly assigned to the VM. The virtual disk uses dynamic allocation storage and is physically located on an NVMe M.2 SSD connected via USB 3.1.

Performance will naturally vary depending on hardware and system configurations; the goal of the timing data provided here is solely to compare the two databases under the same conditions and should not be considered absolute performance metrics.

The operating system used is GNU/Linux, specifically Arch Linux.

## Data Organization Overview

Since InfluxDB is designed to handle time-series data and not general-purpose data storage, most non-time-series data should be stored in a secondary relational database, such as PostgreSQL. While PostgreSQL alone is capable of storing and handling all the required data, in an architecture involving InfluxDB, both databases coexist: one for time-series data and one for general-purpose data. There is no strict limitation preventing the storage of reference data (e.g., stop details) within InfluxDB, but relational databases are far more suitable for that purpose.

For this project, it is assumed that reference data such as stops, routes, and other static datasets are stored in dedicated PostgreSQL tables. However, these tables were not implemented to avoid interference with the queries under analysis and because they are irrelevant to the scope of this performance comparison.

The original PostgreSQL database structure used for data extraction contains the following columns:

- [ ] schedule_id: active schedule ID
- [x] block_id: vehicle block ID
- [x] trip_id: trip ID
- [ ] arrival_time: scheduled arrival time
- [ ] real_time: actual arrival time
- [x] stop_id: ID of the served stop
- [ ] stop_sequence: incremental stop sequence within vehicle block
- [ ] shape_dist_traveled: scheduled distance of the stop from trip start
- [ ] real_dist_traveled: actual distance of the stop from trip start
- [x] day_of_service: service day
- [x] psg_up: passeggeri passengers boarding at the stop
- [x] psg_down: passengers alighting at the stop
- [ ] creation_timestamp: record creation timestamp
- [x] update_timestamp: record update timestamp
- [ ] vehicle_id: ID of the vehicle that served the stop
- [x] delay: delay compared to scheduled stop time
- [ ] reported: whether the stop was registered
- [x] route_id: route ID
- [ ] quality: service quality based on delay
- [ ] served: unused field
- [ ] fake: boolean flag indicating if the stop was real or post-processed

Fields marked with a checkmark were included and migrated in this project, while the others were excluded, as they were not considered relevant for the performance comparison between the databases.

The excluded fields are mainly tied to the logic of the original production system (e.g., _served_ and _fake_), used for internal debugging (_creation\_timestamp_), or related to business rules and contractual agreements (such as _quality_, _shape\_dist\_traveled_, etc.).

### Descrizione della base dati PostgreSQL
Per l'implementazione in PostgreSQL è stata creata una tabella con i dati sopra indicati. Per ciascuna _stop call_ sono presenti in un unico record delay, psg_up e psg_down (se esistenti, NULL altrimenti).
Sono stati creati degli indici per le colonne relative a trip, stop, block, day_of_service, route.

### Descrizione della base dati InfluxDB
Per l'implementazione in InfluxDB è stato utilizzato un bucket con i seguenti elementi:
- (_time) timestamp: ora del passaggio o dell'orario previsto
- (_measurement) measurement: "psg_up" (passeggeri saliti) / "psg_down" (passeggeri scesi) / "delay" (ritardo)
- (tag) schedule_id
- (tag) block_id
- (tag) trip_id
- (tag) stop_id
- (tag) day_of_service
- (tag) route_id
- (_field) "psg_up" (passeggeri saliti) / "psg_down" (passeggeri scesi) / "delay" (ritardo)
- (_value) numero relativo a _field

E' importante ricordare che in InfluxDB solo i tag vengono indicizzati, i valori (_field e _value) non sono indicizzati. Si è scelto quindi di utilizzare il numero di passeggeri saliti/scesi ed il mezzo che ha effettuato la fermata come valori memorizzati ed i vari identificatori della fermata (la fermata fisica, la linea, la corsa, eccetera) come tag.

## Riempimento dei dati e prestazioni di inserimento
Per entrambi i database c'è la necessità di leggere i dati dai file sql per effettuare poi l'inserimento nel database di destinazione. Siccome i file da cui i dati provengono sono di grandi dimensioni (mediamente 500MB l'uno) il caricamento da file e la scrittura nel database devono avvenire di pari passo.

La preparazione dei dati per InfluxDB prevede la creazione, per ogni punto, di un'istanza di una classe fornita dalla libreria, la lettura e preparazione di tutti i dati impiega circa un minuto e venti secondi. La preparazione dei dati per PostgreSQL prevede invece la creazione di query tramite interpolazione di stringhe ed questo invece impiega circa un minuto e dieci secondi. In entrambi i casi questi tempi sono stati presi senza l'inserimento reale dei dati nel rispettivo database ai fini di capirne l'influenza sulle tempistiche totali misurate ma la creazione nella versione finale del codice avviene contestualmente all'inserimento, record per record, non occupando così un quantitativo di RAM degno di nota. Questo è reso necessario dal fatto che volendo testare l'inserimento di un alto numero di record lo spazio occupato dall'esplosione dei dati in RAM non è accettabile.

La quantità di record da inserire cambia in base al database, questo è dovuto al fatto che per ogni passaggio a fermata effettuato possono esistere da uno a tre dati raccolti:
- ritardo/anticipo
- passeggeri saliti
- passeggeri scesi

In PostgreSQL questi (eventualmente) tre dati vengono inseriti in un unico record mentre in InfluxDB vengono inseriti come tre diversi datapoints. Già in questo vediamo una differenza sostanziale relativa allo scenario di utilizzo in real time di uno e dell'altro database: con InfluxDB ogni dato che arriva dal campo si trasforma in un punto da inserire, con PostgreSQL ogni dato si trasforma invece in una _insert or update_. L'alternativa, per quanto riguarda PostgreSQL, è scegliere un momento in cui il sistema è scarico e preparare preventivamente tutti i record che dovranno ospitare i dati in arrivo durante la giornata, così da evitare le _insert or update_ ed effettuare solo degli _update_. Naturalmente è possibile strutturare la tabella in PostgreSQL in modo che ospiti una colonna _field_ ed una _value_ assumendo un aspetto più simile al bucket in InfluxDB ma questo sembra meno naturale per un database relazionale.

I dati provengono da sei diversi file con estensione .sql di circa 500mb ciascuno, le tempistiche di inserimento sono state le seguenti. Qualunque tempistica in questa relazione è espressa nel formato h:mm:ss.sss

<table style="border-spacing: 3px;border-collapse: separate">
  <thead>
    <tr>
      <th style="border-bottom-color: transparent"></th>
      <th colspan="3" style="border-bottom-color: red">PostgreSQL</th>
      <th colspan="3" style="border-bottom-color: green">Influxdb</th>
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

## Estrazione dei dati e prestazioni di select

## Prima query: Ritardo medio fermata
La prima query per testare e confrontare le prestazioni tra i due database in esame riguarda il calcolo del ritardo medio per ciascuna corsa in ciascuna fermata in un certo periodo di tempo.

Questa query è stata creata in due versioni diverse e lanciata in entrambe le versioni su periodi di uno, tre e sei mesi. Le due versioni differiscono tra loro per l'assenza o la presenza di un raggruppamento su base mensile.

Le query eseguite in PostgreSQL per ottenere i dati sono le seguenti:

(Con raggruppamento)
```sql
select DATE_TRUNC('month', datetime) AS month, route_id, trip_id, stop_id, avg(delay) from bigdata_project
where day_of_service > '2020-09-10' and day_of_service < '2022-03-12' and delay is not null
group by month, route_id, trip_id, stop_id
```

(Senza raggruppamento)
```sql
select route_id, trip_id, stop_id, avg(delay) from bigdata_project
where day_of_service > '2020-09-10' and day_of_service < '2021-10-12' and delay is not null
group by route_id, trip_id, stop_id
```

Per quanto riguarda InfluxDB invece sono le seguenti:

(Con raggruppamento)
```js
from(bucket:"bigdata_project2")
|> range(start: 2020-09-11T00:00:00Z, stop: 2021-03-11T23:59:59Z)
|> filter(fn:(r) => r._measurement == "de")
|> drop(columns: ["_start", "_stop"])
|> group(columns: ["route_id", "trip_id", "stop_id"])
|> aggregateWindow(every: 1mo, fn: mean)
|> group()
|> keep(columns: ["_time", "route_id", "trip_id", "stop_id", "_value"])
```

(Senza raggruppamento)
```js
from(bucket:"bigdata_project2")
|> range(start: 2020-09-11T00:00:00Z, stop: 2020-10-11T23:59:59Z)
|> filter(fn:(r) => r._measurement == "de")
|> drop(columns: ["_start", "_stop"])
|> group(columns: ["route_id", "trip_id", "stop_id"])
|> mean()
|> group()
|> keep(columns: ["_time", "route_id", "trip_id", "stop_id", "_value"])
```

I tempi perché il processo in Python ottenesse la lista completa di risultati sono i seguenti e sono stati ottenuti dopo l'inserimento nei database del primo file di dati:

<table style="border-spacing: 3px;border-collapse: separate">
  <thead>
    <tr>
      <th></th>
      <th colspan="3" style="border-bottom:1px solid red">PostgreSQL</th>
      <th colspan="3" style="border-bottom:1px solid green">Influxdb</th>
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

Vediamo che la situazione per quanto riguarda il recupero dei dati si è molto differente rispetto all'inserimento. In fase di lettura dei dati è presente infatti una fortissima disparità che vede PostgreSQL estremamente più veloce rispetto ad InfluxDB nella lettura. Parleremo in seguito di come questo può non essere un problema per l'utilizzatore di InfluxDB.

Seguono i tempi per le stesse query nelle stesse modalità ma con tutti i dati inseriti:

<table style="border-spacing: 3px;border-collapse: separate">
  <thead>
    <tr>
      <th style="border-bottom:none"></th>
      <th colspan="3" style="border-bottom:1px solid green">PostgreSQL</th>
      <th colspan="3" style="border-bottom:1px solid red">InfluxDB</th>
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
      <td>0:00:01.187149</td><td>0:00:01.292565</td><td>0:00:02.221006</td>
      <td>0:00:08.133967</td><td>0:00:12.281949</td><td>0:00:42.795060</td>
    </tr>
    <tr>
      <td>Con</td>
      <td>0:00:01.431923</td><td>0:00:01.574078</td><td>0:00:02.353574</td>
      <td>0:00:18.449262</td><td>0:00:30.584004</td><td>0:01:30.440092</td>
    </tr>
  </tbody>
</table>

## Una questione di cardinalità
La cardinalità è un concetto importante in InfluxDB v2 ed inficia pesantemente le prestazioni ed i requisiti, tanto che si può mettere in relazione la cardinalità con il quantitativo di RAM occupata.

Nella versione 3 di InfluxDB gli autori promettono di aver modificato la gestione dei tag impedendo ora all'elevata cardinalità di diventare un problema, tuttavia questa nuova versione è disponibile solo come servizio a pagamento in cloud ed è closed source, non prendiamo quindi in considerazione la sua esistenza e continuiamo a parlare di InfluxDB v2.

Per studiare a fondo le prestazioni di InfluxDB nei vari casi è stato usato un set di dati più ristretto del precedente e sono stati creati diversi buckets con una diversa configurazione di tags:
1) stop_call
2) Route, Trip, Stop, Block
3) Route, Trip, Stop, stop_call, Block
4) Block, route % 5, trip % 5, stop % 5
5) Block

La seconda combinazione è quella più naturale mentre la prima e la terza sono state create per valutarne gli impatti sulle prestazioni. La quarta e la quinta non hanno utilità pratica ma sono state create solo per analizzare la situazione in cui si hanno tag con cardinalità ridotta oppure un unico tag.
stop_call é generato dalla concatenazione tra tre diversi tag e la sua cardinalità é pari alla moltiplicazione tra le cardinalità di tali tag.

Per la quarta combinazione i tag con cardinalità maggiore sono stati inseriti dopo un'operazione di modulo 5 in modo da abbassarne la cardinalità ma avere comunque lo stesso quantitativo di informazioni inserite nel bucket.

Sono infine state create, per confronto, due tabelle in Postgres partendo dagli stessi set di dati:
1) Route, Trip, Stop, Block
2) Block

### Prestazioni in inserimento

Per i tag fare riferimento all'elenco qui sopra. Il tempo è sempre nel formato h:mm:ss.sss mentre rec/sec indica il numero di record inseriti al secondo.
|Tags|         Tempo|rec/sec|
|----|--------------|-------|
| IN1|0:07:12.722923|5139.89|
| IN2|0:07:38.987807|4845.77|
| IN3|0:08:09.947025|4539.57|
| IN4|0:06:42.864470|5520.83|
| IN5|0:06:07.548264|6051.31|
| PG1|0:33:23.441024| 790.37|
| PG2|0:33:49.539156| 780.21|

All'aumentare del numero di tag diminuisce in maniera non rilevante la velocità di inserimento dei records. In ogni caso è evidente anche da questa prova come la velocità di inserimento dei dati in InfluxDB sia un punto forte dello stesso rispetto a PostgreSQL.

### Prestazioni di lettura
Per confrontare le varie configurazioni possiamo fare tre query che differiscono solo per il raggruppamento:
- una raggruppa per la combinazione route, trip e stop
- una raggruppa per stop_call, che ricordo essere il prodotto cartesiano di route, trip e stop
- l'ultima raggruppa per block

|Bucket|Tempo         |Numero risultati|Raggruppamento    |
|------|--------------|----------------|------------------|
|  IN2 |0:00:24.026554|           41350| Route, trip, stop|
|  IN3 |0:00:24.578068|           41350| Route, trip, stop|
|  IN1 |0:00:19.925843|           41350| stop_call        |
|  IN3 |0:00:23.553541|           41350| stop_call        |
|  IN2 |0:00:18.239343|              39| block            |
|  IN3 |0:00:19.068654|              39| block            |
|  IN4 |0:00:01.648853|              39| block            |
|  IN5 |0:00:00.153695|              39| block            |
|  PG1 |0:00:00.909779|              39| block            |
|  PG2 |0:00:00.780086|              39| block            |

Da questa tabella possiamo dedurre diverse cose:
- guardando le query con raggruppamento su route, trip e stop nel bucket IN2 e nel bucket IN3, filtrando per tre tag separati (route, trip e stop) su una tabella il fatto che essa abbia o meno un tag che ne sia la combinazione (stop_call) non è influente
- guardando le query sul bucket IN3, utilizzare un solo tag dato dalla combinazione di tre tag diversi non sembra dare un chiaro vantaggio rispetto alla combinazione di più tag con la stessa cardinalità risultante
- una query che lavora sullo stesso numero di dati nello stesso periodo ma utilizza solo un tag con cardinalità minore impiega un tempo decisamente minore, come si vede confrontando i raggruppamenti per block e per route, trip e stop su IN2 o su IN3
- una query che lavora sullo stesso numero di dati nello stesso periodo ma su un bucket che non possiede un'elevata cardinalità è estremamente più performante, come si vede dalle query per block su IN4 e IN5 rispetto a IN2 e IN3

In particolare, la query su IN5 è l'unica query in InfluxDB più performante delle query su PostgreSQL, a parità di dati memorizzati. Nel caso non siano presenti molti tag e la cardinalità sia limitata, InfluxDB riesce ad essere più performante di PostgreSQL anche in lettura mentre quando i tag e/o la loro cardinalità aumentano le prestazioni in lettura di InfluxDB degradano molto più velocemente di quelle di PostgreSQL.

### Occupazione spazio su disco

Per visualizzare in ambiente linux la dimensione dei vari buckets possiamo semplicemente eseguire un comando simile a `du -sh /home/vncnz/.influxdbv2/engine/data/* | sort -hr` ottenendo un output simile al seguente (l'indicazione del bucket è stata aggiunta a posteriori):

```sql
4,7G    /home/vncnz/.influxdbv2/engine/data/b77778300c262ad4 --> bucket completo
879M    /home/vncnz/.influxdbv2/engine/data/2e65568d31d832e4 --> bucket ridotto(IN3)
697M    /home/vncnz/.influxdbv2/engine/data/f786e5d253b98a85 --> bucket ridotto(IN2)
614M    /home/vncnz/.influxdbv2/engine/data/f7fd809664dfe27c --> bucket ridotto(IN1)
48M	    /home/vncnz/.influxdbv2/engine/data/0794a0c95d6efca3 --> bucket ridotto(IN4)
9,6M    /home/vncnz/.influxdbv2/engine/data/acf8fb1c6410bbe2 --> bucket ridotto(IN5)
160K    /home/vncnz/.influxdbv2/engine/data/394df8c8e6b03e99 --> bucket per utilizzo interno dell'engine
```

Gli indici in InfluxDB sono memorizzati insieme ai dati nei file TSM stessi: i file TSM che vediamo qui contengono sia i dati effettivi delle serie temporali che i metadati e gli indici.

Per confronto, eseguendo in postgres la query `SELECT pg_size_pretty( pg_table_size('NOME_TABELLA') );` si vede un peso di 144MB per PG1 e 101MB per la PG2. A questi dobbiamo sommare la dimensione degli indici, 17M per l'indice sulla tabella PG1 e 10M per l'indice sulla tabella PG2, entrambi i valori sono ottenibili con una query del tipo `select pg_size_pretty(pg_indexes_size('NOME_TABELLA'))`. Avremmo potuto utilizzare la funzione `pg_total_relation_size` perdendo la distinzione tra peso dati e peso indici.

Riassumendo i dati abbiamo quindi la seguente tabella:

|Mode|Spazio|
|----|------|
| IN1|  530M|
| IN2|  658M|
| IN3|  748M|
| IN4|   48M|
| IN5|  9,6M|
| PG1|  128M + 17M|
| PG2|  91M + 10M|

Confrontando il bucket IN4 con quelli delle altre modalità è evidente come il peso dei dati in InfluxDB sia decisamente ridotto e gli indici legati ai tag abbiano un peso molto elevato. E' altrettanto evidente come l'occupazione di spazio dei dati a bassa cardinalità, IN4, sia di circa un terzo rispetto alla corrispondente tabella in PostgreSQL. Confrontando poi IN5 con PG2 vediamo che InfluxDB arriva ad occupare, in queste condizioni, addirittura meno di un decimo dello spazio necessario a PostgreSQL.


## Una soluzione alla lentezza del recupero dati di InfluxDB: i task
Abbiamo visto come in presenza di un'alta cardinalità le query per la lettura e  manipolazione dei dati abbiano tempi di esecuzione non sostenibili. InfluxDB ha però una funzionalità particolare che può essere utile anche (ma non solo) per questo problema. I task sono uno strumento di "ingestione" dei dati, consentono di effettuare calcoli, analisi e/o aggregazioni sui dati di un bucket scrivendo i risultati in un altro bucket in modo che siano già pronti all'uso, senza la necessità di eseguire query di aggregazione on-the-fly. I task possono inoltre attivare automaticamente notifiche al verificarsi di determinate condizioni o interfacciarsi a strumenti esterni, ad esempio convertendo i risultati in json ed inviandoli automaticamente tramite una chiamata http. Vengono eseguiti in modalità automatica in base a tempistiche configurabili, ad esempio ad ogni intervallo temporale prefissato a partire dal primo dato. Tornando alla nostra query di prova "Ritardo medio fermata" un task potrebbe essere eseguito ogni settimana e scrivere su un bucket di destinazione la riga contenente i risultati dell'aggregazione dei dati dell'ultima settimana, query che ci possiamo aspettare impiegare pochi secondi (abbiamo visto i tempi su un mese, un periodo lungo quattro volte tanto). Considerato che come abbiamo potuto vedere InfluxDB soffre quando si lavora su intervalli temporali lunghi ma scala bene al crescere della quantità di dati l'esecuzione periodica di un task non soffre del continuo accumulo di dati sul database e può svolgere un'aggregazione dei dati settimanali in maniera efficiente. I task vengono utilizzati dall'engine stesso anche per la pulizia dei dati obsoleti secondo policy di data retention definibili separatamente sui singoli bucket. Queste operazioni di pulizia sono un'altra funzionalità innata di InfluxDB e viene effettuata in maniera efficiente in quanto i dati sono organizzati in "pacchetti" su base temporale. Nella versione cloud del DBMS questi "pacchetti" vengono anche sparsi su macchine diverse bilanciando il più possibile il carico di lavoro della singola macchina, per cui una query che può risultare eccessivamente lenta per la versione installabile in locale può non creare alcun rallentamento nella versione cloud se i dati provengono da più nodi.

## L'alternativa PostgreSQL ai task di InfluxDB: pgAgent
Anche per PostgreSQL esiste la possibilità di eseguire automaticamente alcune operazioni tramite un'estensione chiamata pgAgent, che offre una configurabilità leggermente inferiore al competitor: manca ad esempio la possibilità di rimandare un'esecuzione se è ancora in corso la precedente o di eseguirla in ritardo ma considerando il datetime precedente al riinvio. pgAgent inoltre, per il contesto di utilizzo visto, non risolve il problema del rallentamento dovuto alla crescita della tabella su cui deve lavorare e rimanda al sistemista la configurazione di un partizionamento orizzontale e quant'altro possa essere necessario per riuscire a gestire i dati.

## Seconda query: Media dei passeggeri saliti per fermata
La seconda query per testare e confrontare le prestazioni tra i due database in esame riguarda il calcolo del numero medio di passeggeri saliti per ciascuna fermata in un certo periodo di tempo.

Le query eseguite in PostgreSQL ed in InfluxDB per ottenere i dati sono le seguenti:

```sql
select DATE_TRUNC('month', datetime) AS month, extract(dow from datetime) as weekday, stop_id, avg(psg_up) from bigdata_project
where day_of_service > '2020-09-10' and day_of_service < '2020-10-12' and psg_up is not null
group by month, weekday, stop_id
```

```js
import "date"

from(bucket:"bigdata_project2")
|> range(start: 2020-09-11T00:00:00Z, stop: 2020-10-11T23:59:59Z)
|> filter(fn:(r) => r._measurement == "up")
|> drop(columns: ["_start", "_stop"])
|> map(fn: (r) => {
      day = date.weekDay(t: r._time)
      return {r with weekday: day}
    })
|> group(columns: ["stop_id", "weekday"])
|> aggregateWindow(every: 1mo, fn: mean)
|> keep(columns: ["_time", "stop_id", "weekday", "_value", "_start", "_stop"])
```

I tempi perché il processo in Python ottenesse la lista completa di risultati sono i seguenti e sono stati ottenuti dopo l'inserimento nei database di tutti i dati a disposizione:

<table style="border-spacing: 3px;border-collapse: separate">
  <thead>
    <tr>
      <th style="border-bottom:1px solid green">PostgreSQL (PG2)</th>
      <th style="border-bottom:1px solid red">InfluxDB (IN2)</th>
      <th style="border-bottom:1px solid orange">InfluxDB (IN4)</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>0:00:01.210025</td><td>0:01:03.521774</td><td>0:00:10.668793</td>
    </tr>
  </tbody>
</table>

Questi risultati sono coerenti con le analisi fatte in maniera approfondita con la prima query. Il bucket IN4 ha infatti una cardinalità molto minore del bucket IN2 e questo si vede nel tempo necessario per ottenere i risultati. PostgreSQL riesce in ogni caso a produrre i risultati in un tempo minore.

## Considerazioni finali

Con questa relazione ed i test svolti si è voluto evidenziare aspetti positivi e negativi di InfluxDB, un DBMS poco conosciuto e con una focalizzazione sulle serie temporali, confrontandolo con un DBMS molto conosciuto e più general-purpose. PostgreSQL è un ottimo DBMS che gestisce una vasta gamma di tipi di dato, può addirittura gestire query spaziali con operazioni di intersezione, inclusione ed altro. Nelle ultime versioni è in grado di lavorare con efficienza anche su dati json, andando in competizione (parziale) anche con sistemi non relazionali come MongoDB. Abbiamo però visto che per determinati contesti ha senso esplorare sistemi alternativi, ad esempio nella gestione di serie temporali che mostrano una crescita rapida e richiedono la conservazione prolungata dei dati a patto che ci sia una bassa cardinalità dei dati correlati a ciascun valore della serie.





<!-- 

FINE

############################################################
############################################################
############################################################
############################################################
############################################################
############################################################

Sistemare il mettere un datetime in PostgreSQL per un confronto migliore (dato che non si usa il day_of_service in InfluxDB ma, appunto, un datetime)

Link che confronta InfluxDB VERSIONE UNO con PostgreSQL, valutare se prenderne spunto: https://portavita.github.io/2018-07-31-blog_influxdb_vs_postgresql

Altre fonti ancora da guardare:

https://www.influxdata.com/comparison/influxdb-vs-postgres/

https://dba.stackexchange.com/questions/275664/is-influxdb-faster-than-postgresql

https://www.postgresql.org/message-id/6b25525b-8c36-620e-5da0-c900a7720c19%40mixmax.com

-->