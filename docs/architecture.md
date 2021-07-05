# Arhitektura

## 'Event driven' programiranje.

Kako se da zaključiti iz imena, *'event driven'* programiranje je pristup
programiranju s fokusom na *evente* (događaje). Eventi mogu biti stvoreni od
strane korisnika ili programa.

Klasično, odnosno, linearno programiranje se temelji na jedinstvenom tijeku
događaja. Događaji se izvršavaju slijedno i tako prolaze kroz predodređene
točke grananja.

S druge strane, *event-driven* paradigma se temelji na čekanju na događaj
(*event*), te po primitku događaja - odrađivanju željene akcije.

Dakle, razlika *event driven* programiranja u odnosu na linearno programiranje
je da se u linearnom programiranju instrukcije izvode u predodređenom,
nepromjenjivom slijedu. Međutim, u *event driven* programiranju sljedeći
događaj koji će se desiti  ovisi o *eventu* koji se registrira u sustavu u tom
trenu.  Dakle, *event driven* programiranje se može smatrati više dinamičnim
i stoga fleksibilnijim od linearnog programiranja.

### Osnovni pojmovi:

**Event (događaj)**:

Događaj koji se stvara tijekom rada programa i zahtijeva određenu akciju od
strane sustava. Događaji mogu zahtijevati dohvaćanje i/ili prikazivanje
informacija u sustavu, dodatnu obradu podataka ili promjenu stanja sustava.

**Poruka**:

Poruka je struktura podataka koja predstavlja *event*. Poruke se razmjenjuju
kroz sustav i sadrže informacije poput vrste *eventa i podataka koji se
predaju sustavu na obradu.

**Event handler**:

Dio sustava odgovaran za obradu događaja. Aktivira se primitkom događaja
propisanoga tipa.

**Event loop**:

Beskonačna petlja koja čeka događaje, te, po primitku događaja šalje iste na
pripadne *event handlere*.

# Hat-Core

[Dokumentacija](https://core.hat-open.com/)  

[Implementacija](https://core.hat-open.com/docs/)  

[Github](https://github.com/hat-open/hat-core)

## (hat-core) Event komponenta

[Detaljno o event komponenti (dokumentacija)](https://core.hat-open.com/docs/components/event/index.html)

[Implementacija event modula](https://core.hat-open.com/docs/pyhat/hat/event/index.html)

## (hat-core) Event Server

*Event server* kao paket definiran unutar *har-core* biblioteke je centralna
komponenta za obradu evenata. Služi za registriranje, procesiranje,
pohranjivanje i pružanje pristupa događajima (*eventovima*).

### (hat-core) Event

Definiran kao struktura podataka s propisanim formatom. Event je nepromjenjiv
i jednoznačno određen pomoću '*event_id*'.

Struktura eventa sadrži:

- "*id*": Jedinstveni identifikator *eventa*. Uvijek postavljeno od strane
  *event servera*.

- "*type*": Lista *stringova* definirana od strane korisnika. Semantika i
  redoslijed liste je potpuno definirana od strane korisnika i nije
  predefinirana *event serverom*. Svaki *event* bi trebao imati svoju
  nomenklaturu koja se ne podudara s imenovanjem drugih *evenata*. Zabranjeno
  je da neki od elemenata liste bude `'?'` ili `'*'`.

  Kod pretplate na *event* i upita o *eventovima* vrijede sljedeća pravila:

    - Svaki *string* u listi se može zamijeniti znakom `'?'`. *String* `'?'`
      odgovara bilo kojem (jednom) proizvoljnom *stringu*.

    - Zadnji *string* u listi se može zamijeniti znakom `'*'`. *String* `'*'`
      odgovara bilo kojem broju (0 ili više) *stringova*.

  Odnosno, upit ovoga formata: `['a', '?', 'c', *]`
  odgovara ovakvim tipovima *evenata*:  
  `['a', 'b', 'c', 'd', 'e']`,  
  `['a', 'xyz', 'c', 'd']`  
  Ali ne odgovara ovakvim tipovima *evenata*:  
  `['a', 'c', 'd', 'e']`,  
  `['a', 'b1', 'b2, 'c', 'd']`

- "*timestamp*": Vrijeme registracije *eventa* na poslužitelju. Uvijek
  postavljeno od strane poslužitelja.

- "*payload*": Opcionalno. Postavljeno od strane klijenta koji registrira *
  event*. Sadržaj određen tipom eventa i može se dekodirati s klijentom koji
  razumije evente toga istoga tipa. *Payload* može biti enkodiran kao binarni
  podatak, JSON ili SBS podatak. *Event server* ne dekodira *payload*.

#### Primjer generičnog eventa:

```
   Event(
      event_type=('a', 'b', 'c'),
      source_timestamp=Timestamp(s=123, us=456),
      payload=EventPayload(
        type=<EventPayloadType.JSON: 2>,
        data={'attr1': True, 'attr2': [1,2,3]'}))

```

## (hat-core) Gateway

[Detaljno o gateway komponenti (dokumentacija)](https://core.hat-open.com/docs/components/gateway/index.html)

[Implementacija gateway modula](https://core.hat-open.com/docs/pyhat/hat/gateway/index.html)

[Primjer implementacije devicea (iz quickstart repozitorija)](https://github.com/ket-praksa/hat-quickstart/blob/master/src_py/project/devices/example.py)

Služi povezivanju uređaja koji koriste razne vrste komunikacijskih protokola s
*event serverom*. Specifično ponašanje za svaki vanjski uređaj. Kada vanjski
uređaj pošalje poruku na *Gateway*, stvara se *event* (*event registration*) s
potrebnim značenjem i potrebnim podacima te se šalje na *Event server*. Jednako
ponašanje vrijedi i za suprotnu stranu komunikacije. Na temelju dobivenog
*eventa* od strane *event servera* šalje se poruka specifičnim komunikacijskim
protokolom na odgovarajući uređaj. Drugim riječima, *gateway* omogućuje
dvosmjernu komunikaciju između vanjskih uređaja i *event servera*.

Komunikacija se odvija pomoću specifičnih vrsta evenata sljedeće strukture:

`'gateway', <gateway_name>, <device_type>, <device_name>, <source>, ...`

, gdje:

- <gateway_name> - identifikator instance *gatewaya*
- <device_type> - identifikator tipa uređaja
- <device_name> - identifikator instance uređaja
- <source> - *gateway* ili *system* (ovisno o smjeru komunikacije)

## (hat-core) GUI Server

GUI server je komponenta koja služi tome da poslužuje grafička sučelja. Ona su
izvedena u web tehnologijama, uglavnom kao single page aplikacije.
Implementacija frontenda se nalazi u jedinicama koje nazivamo viewovima. View
je buildani javascript modul koji ispunjava određeno sučelje.


Za više informacija o frontend razvoju u hat-rendereru, imamo kratki
[tutorial](frontend).

Server u sebi sadrži adaptere, neovisne potkomponente koje se pretplaćuju na
evente i poslužuju svoj dio stanja web klijentima. Adapter je objekt koji se
instancira pri startu GUI servera i obavlja dohvat evenata. Kad se novi klijent
spoji, stvara se sesija. Svaki adapter ima funkciju za stvaranje sesije, i ona
dobiva referencu na konekciju - istu konekciju koju frontend koristi u
`hat.conn` varijabli. Adapterova sesija koristi tu referencu na konekciju da
notificira stanje adaptera svom klijentu.

Sama konekcija koja se koristi za komunikaciju frontenda i backenda koristi
[juggler](https://core.hat-open.com/docs/libraries/juggler/index.html)
protokol. Juggler je wrapper oko websocket protokola koji pretpostavlja da se
sve poruke šalju u obliku JSON-a. Sadrži podršku za sinkronizaciju stanja, gdje
svaka instanca konekcije ima svoje lokalno i remote stanje. Lokalno stanje je
stanje strane na kojoj se je instanca konekcije, a remote stanje je stanje koje
određuje strana na koju je instanca spojena. Tako je npr. u javascriptu lokalno
stanje stanje aplikacije koja se izvodi u browseru, a remote je stanje koje
dojavljuje sesija adaptera. Kod konekcije u sesiji adaptera, priča je obrnuta.
Juggler također nudi podršku za slanje JSON poruka. Detalji oko toga kako
raditi s jugglerom su opisani u [frontend tutorialu](frontend).

Kod implementacije viewova, remote stanje se uvijek nalazi na lokaciji `remote`
(poziv `r.get(remote)`). Juggler također nudi podršku za slanje JSON poruka - u
viewu je moguće pozvati `hat.conn.send('<ime adaptera>', {poruka: 'sadržaj'})`.
Na konekciji sesije adaptera `<ime adaptera>` je moguće dohvatiti 

[Detaljno o GUI server (dokumentacija)](https://core.hat-open.com/docs/components/gui/index.html)  

[Implementacija GUI modula](https://core.hat-open.com/docs/pyhat/hat/gui/index.html)  

[Primjer implementacije adaptera (iz quickstart repozitorija)](https://github.com/ket-praksa/hat-quickstart/blob/master/src_py/project/adapters/example.py)

# Tok podataka

Vanjski uređaj šalje podatak (npr. mjerenje snage) nekim komunikacijskim
protokolom (npr. *IEC 60870-5-104*). *Gateway device* čita tu informaciju te na
temelju te informacije registrira pripadan *event* koji se propagira na *event
server*. *Event server* prosljeđuje evente pripadnom modulu *event servera*.
Modul *event servera* prosljeđuje *eventove* na adapter *GUI servera*. Adapter
ažurira interno stanje. Na grafičkom sučelju se prikazuju podaci internog
stanja.

Ako na grafičkom sučelju postoji način promjene prikazanih podataka (npr.
opcija za gašenje/paljenje sklopke), mijenja se vrijednost pripadnog atributa u
stanju. Juggler protokolom se adapteru javlja promjena stanja. Iz adaptera se
tada *event* propagira kroz modul do pripadnoga *gateway devicea* koji pretvara
sadržaj *eventa* u poruku u zadanom komunikacijskom protokolu te istu šalje na
vanjski uređaj.
