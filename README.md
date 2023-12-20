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

I due database confrontati non differiscono solo nella struttura (relazionale vs buckets) e nell'obiettivo (dati generici vs serie temporali) ma anche nell'architettura di base. Mentre PostgreSQL viene eseguito solitamente come mono-istanza in locale, sulla macchina che ospita anche gli altri servizi o al massimo su una macchina dedicata, InfluxDB nasce come sistema di memorizzazione in cloud ed è fortemente orientato a tale scenario di utilizzo. Per questo progetto, tuttavia, è stata utilizzata una versione installabile in locale per poter confrontare le prestazioni a parità di risorse hardware.

# Parte teorica

## Database model
InfluxDB è un "timeseries database", cioè un database orientato al salvataggio di dati temporali
## Architetura
## Licenza
## Use cases
## Scalability
# Parte pratica
## [Tecnologie usate]

Il progetto è realizzato in Python, utilizza Flask per la creazione di un servizio web ed apposite librerie per l'esecuzione dei salvataggi e delle interrogazioni.

## Descrizione dell'organizzazione dei dati
Siccome InfluxDB nasce per gestire serie temporali e non altro, la maggior parte dei dati richiedono il salvataggio in un database di appoggio che può essere proprio PostgreSQL. Mentre PostgreSQL può essere l'unico database utilizzato per raggiungere l'obiettivo nel caso di InfluxDB si avrà invece la coesistenza dei due database, uno utilizzato per la memorizzazione di tutti i dati non temporali ed uno utilizzato per questi ultimi.
In questo progetto si immagina l'anagrafica di fermate e linee residenti in una tabella di PostgreSQL dedicata che non viene però implementata perché non interferisca con le query in esame. La struttura del database PostgreSQL da cui sono stati estratti i dati ha le seguenti colonne:

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
- [x] vehicle_id: id del veicolo che ha effettuato la fermata
- [x] delay: ritardo rispetto al passaggio previsto
- [ ] reported: fermata recistrata
- [x] route_id: id della linea
- [ ] quality: qualità del servizio in base al ritardo
- [ ] served: non usato
- [ ] fake: boolean che indica se la registrazione della fermata è reale o calcolata a posteriori

I dati indicati con un check sono stati implementati in questo progetto, gli altri dati sono stati esclusi perché considerati non utili ai fini del confronto tra i database.

### [Descrizione della base dati postgres]
Per l'implementazione in PostgreSQL è stata creata una tabella con i dati sopra indicati. Per ciascuna stop call sono presenti in un unico record delay, psg_up e psg_down (se esistenti). #TODO: segnare quali colonne sono state indicizzate e quant'altro

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
- (_field) "psg_up/psg_down/delay"
- (_value) numero di passeggeri saliti e scesi, ritardo

E' importante ricordare che in InfluxDB solo i tag vengono indicizzati, i valori (_field e _value) non sono indicizzati. Si è scelto quindi di utilizzare il numero di passeggeri saliti/scesi ed il mezzo che ha effettuato la fermata come valori memorizzati ed i vari identificatori della fermata (la fermata fisica, la linea, la corsa, eccetera) come tag. Sono anche quei campi tendenzialmente ripetitivi (una corsa ha molte fermate, da una fermata passano molte corse, eccetera) e questo assicura di non far esplodere la cardinalità della serie anche se essa sarà comunque relativamente alta, in particolare per colpa dello stop_id.


## Riempimento dei dati e prestazioni di inserimento
[TODO, inserire anche tempistica di creazione query/point]

## Estrazione dei dati e prestazioni di select
[TODO]

