# big-data-project
Progetto d'esame per Big Data AA 2022/2023 - Matricola VR457811

## Introduzione e contesto

Quella che segue è una relazione che confronta le prestazioni nella gestione di un numero significativo di dati in due diversi tipi di database: PostgreSQL e InfluxDB; e lo fa basandosi su un confronto nell'utilizzo reale degli stessi nel contesto di seguito descritto.

Trattandosi di due database profondamente diversi ed essendo InfluxDB poco conosciuto vedremo anche gli aspetti principali della sua architettura e del suo funzionamento.

La parte implementativa e di analisi si concentra sul salvataggio e sulla rielaborazione di dati di tipo temporale e più nello specifico dati relativi alla registrazione dei passaggi a fermata dei mezzi di trasporto pubblico di una città italiana di medie dimensioni. L'idea nasce come ipotetica estensione delle funzionalità di un sistema AVM (Automatic Vehicle Monitoring) realizzato dal sottoscritto in ambito lavorativo. Tale sistema riceve i dati grezzi da un sistema GPS presente a bordo di ogni autobus e fornisce le seguenti funzionalità:
- verifica che il mezzo sia correttamente sul percorso a lui assegnato
- riconosce il passaggio a fermata, ovvero l'azione di passaggio accanto ad ogni fermata designata e con eventuale fermata del mezzo per far salire e scendere i passeggeri
- calcola il ritardo/anticipo del mezzo rispetto alla tabella di marcia per la corsa a cui è assegnato
- memorizza una serie di dati:
  - i segnali grezzi ricevuti dal mezzo
  - i segnali rielaborati con l'aggiunta di indicazioni sullo stato del mezzo (corsa assegnata, prossima fermata, anticipo/ritardo, passeggeri a bordo, eccetera)
  - i dati di passaggio per la reportistica, ovvero per la produzione di report mensili che l'azienda deve consegnare al comune per ricevere una compensazione economica dipendente dalla qualità del servizio effettuato

Ogni record di questo ultimo tipo rappresenta una _stop call_, termine usato nel mondo delle TVM per indicare nello specifico una fermata effettuata da un mezzo che sta servendo una determinata corsa su una determinata linea, si tratta di dati che è importante memorizzare a fini reportistici in quanto l'azienda se ne serve per farsi rimborsare dal Comune in base alla qualità del servizio. Solitamente vengono generati dei report su base mensile ma i dati devono persistere per anni in quanto devono rimanere disponibili in caso di richiesta del sistema giudiziario per analizzare incidenti o per l'azienda stessa per un'analisi del servizio effettuato.

Uno dei punti critici del sistema sviluppato riguarda proprio il salvataggio e la rielaborazione dei dati di reportistica in quanto si tratta di una grandissima quantità di dati da leggere, scrivere e rielaborare. Per dare un'idea più chiara, se in una piccola città sono previste 400 corse al giorno ed ognuna ha mediamente 30 fermate il sistema deve memorizzare 12000 record giornalieri di questo tipo; considerate 20 ore di servizio si tratta di una _stop call_ ogni 6 secondi in media ed un milione di record ogni tre mesi.

Attualmente i limiti riscontrati a livello di prestazioni del database PostgreSQL utilizzato per tale sistema sono stati parzialmente aggirati salvando oltre ai dati dettagliati alcune statistiche pre-calcolate sul breve periodo basandosi su dati che vengono tenuti in RAM.

Una funzionalità che **non** è presente nel sistema e che ho ritenuto interessante come spunto per il confronto soggetto di questo esame è l'analisi dei dati memorizzati per l'individuazione di deviazioni tra i passaggi a fermata previsti secondo la pianificazione ed i passaggi registrati nella realtà di ogni giorno. Un'analisi di questo tipo richiede la rielaborazione di un grande numero di record.

## Obiettivo delle query

L'obiettivo è la creazione di statistiche che sarebbero utili all'azienda cliente, in un'ipotetica messa in produzione del codice qui sviluppato, per correggere e migliorare le tabelle di passaggi a fermata che gli autobus devono rispettare. 

Vengono analizzate le prestazioni dei due database sia in fase di salvataggio che di interrogazione. Le prestazioni dipendono chiaramente da un grande numero di variabili e da una natura diversa dei database stessi ma si è cercato di mettere i due sistemi nelle medesime condizioni di lavoro.

## Limiti di questa analisi prestazionale

I due database confrontati non differiscono solo nella struttura (relazionale vs time-series) e nell'obiettivo (dati generici vs serie temporali) ma anche nell'architettura di base. Mentre PostgreSQL viene eseguito solitamente come mono-istanza in locale, sulla macchina che ospita anche gli altri servizi o al massimo su una macchina dedicata, InfluxDB nasce come sistema di memorizzazione in cloud ed è fortemente orientato a tale scenario di utilizzo. Per questo progetto, tuttavia, è stata utilizzata una versione installabile in locale per poter confrontare le prestazioni a parità di risorse hardware ed in un ambiente il più possibile controllato. Questo toglie ad InfluxDB parte dei suoi vantaggi.

## Cenni teorici su InfluxDB
Iniziamo da una spiegazione del funzionamento di InfluxDB, il sistema meno conosciuto tra i due a confronto.

Si tratta di un DBMS scritto prevalentemente in Go che utilizza i Time Structured Merge Tree per memorizzare in maniera efficiente serie temporali. I dati memorizzati vengono compressi ed organizzati in _shards_, gruppi di dati relativi allo stesso arco temporale. Per eseguire le query si utilizza un linguaggio chiamato _Flux_, organizzato come una specie di pipeline di operazioni sui dati in cui ogni comando lavora sull'output del comando precedente. 

A differenza della maggior parte dei database, in InfluxDB è possibile raggruppare i dati per funzioni di aggregazione senza perderne il dettaglio ed è possibile, dopo un raggruppamento, espandere nuovamente i risultati ed applicare un differente raggruppamento. Offre anche una serie di funzioni comode per la manipolazione temporale dei dati, ad esempio l'aggregazione per finestre temporali.

L'interfaccia tra utilizzatore ed engine è di tipo web tramite delle RESTful API per i programmi ed una pagina di gestione via web per l'accesso diretto degli utenti. Si tratta, quest'ultima, di un'interfaccia molto curata che consente anche la composizione guidata di query e la visualizzazione dei risultati sotto forma di grafici. Per questo progetto tuttavia ho utilizzato un programma in Python.

La memorizzazione di nuovi dati su InfluxDB segue due fasi distinte: la scrittura in file WAL che fungono da buffer e la scrittura nel database vero e proprio. Per questo motivo gli autori di InfluxDB consigliano, per sistemi in produzione e con alti requisiti di performance, di avere la cartella dei database e la cartella degli WAL su due volumi fisici separati ottimizzando così il throughput dei dati sul disco. Con la versione 2.X di InfluxDB l'engine sfrutta come accennato una tecnologia chiamata Time-Structured Merge Tree (TSM) che organizza i dati su disco in un formato colonnare e, negli stessi files, gli indici.

Da sottolineare, in InfluxDB non esiste l'operazione di _update_ dei dati.

# Progetto di confronto

## Tecnologie usate

Il progetto è realizzato in Python 3.x, utilizza python-influxdb e psycopg2 per l'esecuzione dei salvataggi e delle interrogazioni rispettivamente in InfluxDB ed in PostgreSQL. I dati provengono da un database utilizzato realmente in una città italiana di piccole dimensioni, sono stati esportati tramite la creazione di file sql che sono stati letti e travasati, tramite due script separati, nei database di destinazione. I due script condividono la maggior parte del codice e differiscono per la sola parte legata allo specifico database di destinazione.

## Configurazione software/hardware e nota sulle prestazioni

Qualunque dato prestazionale presente in questo documento si riferisce all'esecuzione su una macchina virtuale VirtualBox con 4 core e 8gb di RAM. La CPU fisica è una AMD Ryzen 7 4800U e grazie all'opzione PAE/NX attiva 4 dei suoi core sono esposti direttamente alla VM. Il disco virtuale è del tipo "dynamic allocation storage" e si trova fisicamente su un disco NVME M2 connesso tramite USB3.1. Su macchine o configurazioni differenti le prestazioni possono chiaramente differire ma lo scopo dei tempi qui riportati è fine al confronto tra i due database e non devono essere presi in senso assoluto.

Il sistema operativo è GNU/Linux, per maggior precisione una distro Arch.

## Descrizione dell'organizzazione dei dati
Siccome InfluxDB nasce per gestire serie temporali e non altro, la maggior parte dei dati richiedono il salvataggio in un database di appoggio che può essere proprio PostgreSQL. Mentre PostgreSQL può essere l'unico database utilizzato per raggiungere l'obiettivo nel caso di InfluxDB si avrà invece la coesistenza dei due database, uno utilizzato per la memorizzazione di tutti i dati non temporali ed uno utilizzato per questi ultimi. Non esistono vincoli specifici che impediscono il salvataggio di anagrafiche in InfluxDB ma è un tipo di dati perfetto per un database relazionale e non timeseries-oriented.

In questo progetto si immagina quindi di avere le anagrafiche di fermate, linee e quant'altro residenti in tabelle PostgreSQL dedicate che non vengono però implementate per evitare che ciò interferisca con le query in esame e perché superfluo ai fini dell'analisi. La struttura del database PostgreSQL da cui sono stati estratti i dati ha le seguenti colonne:

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
Per l'implementazione in PostgreSQL è stata creata una tabella con i dati sopra indicati. Per ciascuna _stop call_ sono presenti in un unico record delay, psg_up e psg_down (se esistenti, NULL altrimenti).
Sono stati creati degli indici per le colonne relative a trip, stop, block, day_of_service, route.

### [Descrizione della base dati influxdb]
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

In PostgreSQL questi (eventualmente) tre dati vengono inseriti in un unico record mentre in InfluxDB vengono inseriti come tre diversi datapoints. Già in questo vediamo una differenza sostanziale in uno scenario di utilizzo in real time di uno e dell'altro database: con InfluxDB ogni dato che arriva dal campo si trasforma in un punto da inserire, con PostgreSQL ogni dato si trasforma invece in una _insert or update_. L'alternativa, per quanto riguarda PostgreSQL, è scegliere un momento in cui il sistema è scarico e preparare preventivamente tutti i record che dovranno ospitare i dati in arrivo durante la giornata, così da evitare le _insert or update_ ed effettuare solo degli _update_. Naturalmente è possibile strutturare la tabella in PostgreSQL in modo che ospiti una colonna _field_ ed una _value_ assumendo un aspetto più simile al bucket in InfluxDB ma questo sembra meno naturale per un database relazionale.

I dati provengono da sei diversi file con estensione .sql di circa 500mb ciascuno, le tempistiche di inserimento sono state le seguenti:

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
|> drop(columns: ["_start", "_stop"])
|> group(columns: ["route_id", "trip_id", "stop_id"])
|> aggregateWindow(every: 1mo, fn: mean)
|> group()
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

I tempi perché il processo in Python ottenesse la lista completa di risultati sono espressi nel formato h:mm:ss.sss. Queste tempistiche sono state ottenute dopo l'inserimento nei database del primo file di dati:

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
      <td>0:00:00.622946</td><td>0:00:00.674102</td><td>0:00:02.221006</td>
      <td>0:00:08.133967</td><td>0:00:12.281949</td><td>0:00:42.795060</td>
    </tr>
    <tr>
      <td>Con</td>
      <td>0:00:00.934744</td><td>0:00:01.386777</td><td>0:00:05.111580</td>
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
| PG1|0:29:12.295566| 903.65|
| PG2|0:36:12.246039| 728.95|
[TODO: Ricontrollare PG1 e PG2...]

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

In particolare, la query su IN5 è l'unica query in InfluxDB più performante delle query su PostgreSQL, a parità di dati memorizzati. Nel caso non siano presenti molti tag e la cardinalità sia limitata InfluxDB riesce quindi ad essere più performante di PostgreSQL anche in lettura mentre quando i tag e/o la loro cardinalità aumentano le prestazioni in lettura di InfluxDB degradano molto più velocemente di quelle di PostgreSQL.

### Occupazione spazio su disco

Per visualizzare in ambiente linux la dimensione dei vari buckets possiamo semplicemente eseguire un comando simile a `du -sh /home/vncnz/.influxdbv2/engine/data/* | sort -hr` ottenendo un output simile al seguente (l'indicazione del bucket è stata aggiunta a posteriori):

```
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
Abbiamo visto come in presenza di un'alta cardinalità le query per la lettura e  manipolazione dei dati abbiano tempi di esecuzione non sostenibili. InfluxDB ha però una funzionalità particolare che può essere utile anche (ma non solo) per questo problema. I task sono uno strumento di "ingestione" dei dati, consentono di effettuare calcoli, analisi e/o aggregazioni sui dati di un bucket scrivendo i risultati in un altro bucket in modo che siano già pronti all'uso, senza la necessità di eseguire query di aggregazione on-the-fly. I task possono inoltre attivare automaticamente notifiche al verificarsi di determinate condizioni o interfacciarsi a strumenti esterni, ad esempio convertendo i risultati in json ed inviandoli automaticamente tramite una chiamata http. Vengono eseguiti in modalità automatica in base a tempistiche configurabili, ad esempio ogni tot tempo. Tornando alla nostra query di prova "Ritardo medio fermata" un task potrebbe essere eseguito ogni settimana e scrivere su un bucket di destinazione la riga contenente i risultati dell'aggregazione dei dati dell'ultima settimana, query che ci possiamo aspettare impiegare pochi secondi (abbiamo visto i tempi su un mese, un periodo lungo quattro volte tanto). Considerato che come abbiamo potuto vedere InfluxDB soffre quando si lavora su intervalli temporali lunghi ma scala bene al crescere della quantità di dati l'esecuzione periodica di un task non soffre del continuo accumulo di dati sul database e può svolgere un'aggregazione dei dati settimanali in maniera efficiente. I task vengono utilizzati dall'engine stesso anche per la pulizia dei dati obsoleti secondo policy di data retention definibili separatamente sui singoli bucket. Queste operazioni di pulizia sono un'altra funzionalità innata di InfluxDB e viene effettuata in maniera efficiente in quanto i dati sono organizzati in "pacchetti" su base temporale. Nella versione cloud del DBMS questi "pacchetti" vengono anche sparsi su macchine diverse bilanciando il più possibile il carico di lavoro della singola macchina, per cui una query che può risultare eccessivamente lenta per la versione installabile in locale può non creare alcun rallentamento nella versione cloud se i dati provengono da più nodi.

## L'alternativa PostgreSQL ai task di InfluxDB: pgAgent
Anche per PostgreSQL esiste la possibilità di eseguire automaticamente alcune operazioni tramite un'estensione chiamata pgAgent, che offre una configurabilità un poco minore: manca ad esempio la possibilità di rimandare un'esecuzione se è ancora in corso la precedente o di eseguirla in ritardo ma considerando il datetime precedente al riinvio. pgAgent inoltre, per il contesto di utilizzo visto, non risolve il problema del rallentamento dovuto alla crescita della tabella su cui deve lavorare e rimanda al sistemista la configurazione di un partizionamento orizzontale e quant'altro possa essere necessario per riuscire a gestire i dati.

## Considerazioni finali

Con questa relazione e questi esperimenti si è voluto evidenziare aspetti positivi e negativi di InfluxDB, un DBMS poco conosciuto e con un orientamento ben preciso, confrontandolo con un DBMS molto conosciuto e più general-purpose. PostgreSQL è un ottimo DBMS che gestisce una vasta gamma di tipi di dato, può addirittura gestire query spaziali con operazioni di intersezione, inclusione ed altro. Nelle ultime versioni è in grado di lavorare con efficienza anche su dati json, andando in competizione (parziale, almeno) anche con sistemi non relazionali come MongoDB. Abbiamo però visto che per determinati contesti ha senso esplorare sistemi alternativi, ad esempio per la gestione di serie temporali che crescono velocemente e per le quali ci può essere necessità di mantenere i dati per un lungo periodo di tempo ma c'è una bassa cardinalità dei dati correlati a ciascun valore della serie.





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