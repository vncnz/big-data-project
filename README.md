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
La quantità di record da inserire cambia in base al database:
- 1490706 record in postgres
- 2067523 record in influxdb
Questo è dovuto al fatto che per ogni passaggio a fermata effettuato possono esistere da uno a tre dati raccolti:
- ritardo/anticipo
- passeggeri saliti
- passeggeri scesi
In PostgreSQL questi (eventualmente) tre dati vengono inseriti in un unico record mentre in InfluxDB vengono inseriti come tre diversi datapoints. Già in questo vediamo una differenza sostanziale in uno scenario di utilizzo in real time di uno e dell'altro database: con InfluxDB ogni dato che arriva dal campo si trasforma in un punto da inserire, con PostgreSQL ogni dato si trasforma invece in una _insert or update_. L'alternativa, per quanto riguarda PostgreSQL, è scegliere un momento in cui il sistema è scarico e preparare preventivamente tutti i record che dovranno ospitare i dati in arrivo durante la giornata, così da evitare le _insert or update_ ed effettuare solo degli _update_. Naturalmente è possibile strutturare la tabella in PostgreSQL in modo che ospiti una colonna _field_ ed una _value_ assumendo un aspetto più simile al bucket in InfluxDB ma questo sembra meno naturale per un database relazionale.


The written time for 2067523 records in influxdb is: 0:02:08.089249 (16141.27 records per second) <-- fake
The written time for 1490706 records in postgresql is: 0:01:10.859296 (21037.55 records per second) <-- fake

The written time for 2067523 records in influxdb is: 0:08:16.944981 (4160.47 records per second) <-- real
The written time for 1490706 records in postgresql is: 0:31:51.030815 (780.05 records per second) <-- real



```
[TODO: rimuovere, esempio inserimento per copia-incolla della tilda]
```

## Estrazione dei dati e prestazioni di select

### Ritardo medio fermata (InfluxDB)
La prima query per testare e confrontare le prestazioni tra i due database in esame riguarda il calcolo del ritardo medio per ciascuna corsa in ciascuna fermata in un certo periodo di tempo.

Questa query è stata creata in due versioni diverse e lanciata in entrambe le versioni su periodi di uno, tre e sei mesi. Le due versioni differiscono tra loro per l'assenza o la presenza di un raggruppamento su base mensile.

I tempi perché il processo in Python ottenesse la lista completa di risultati sono i seguenti, espressi nel formato h:mm:ss.sss :

|Raggruppamento|Un mese       |Tre mesi      |Sei mesi      |
|--------------|--------------|--------------|--------------|
|Senza         |0:00:07.370876|0:00:12.338076|0:01:09.479471|
|Con           |0:00:18.962651|0:00:41.957013|0:02:21.480946|

Si può notare come il raggruppamento aumenti il tempo in maniera nient'affatto trascurabile, anche nel caso i risultati rientrino tutti in un'unica finestra.


```
Query executed in : 0:00:07.370876 seconds --> 1 mese senza raggruppamento
Query executed in : 0:00:18.962651 seconds --> 1 mese e raggruppato per mese

Query executed in : 0:00:12.338076 seconds --> 3 mesi senza raggruppamento
Query executed in : 0:00:41.957013 seconds --> 3 mesi e raggruppato per mese

Query executed in : 0:01:09.479471 seconds --> 6 mesi senza raggruppamento
Query executed in : 0:02:21.480946 seconds --> 6 mesi e raggruppato per mese
```