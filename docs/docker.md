# Preporučeni docker workflow

Hat-quickstart projekt može se pokretati i kroz docker i u ovom dokumentu je
predložen workflow za takav način rada. Ovakav način pokretanja je više
workaround za platformno-neovisno pokretanje - nativno pokretanje, WSL i
virtualne mašine su adekvatne, ako ne i bolje opcije. Kako je docker dosta jak
alat i ima jako puno konfiguracijskih opcija, za slučaj da bude previše
overwhelming smo složili ovaj kratki tutorial.

Prvi korak je instalacija dockera, za što preporučujemo [službenu
dokumentaciju](https://docs.docker.com/get-started/). Nakon instalacije,
komandnolinijska naredba `docker` bi trebala postati upotrebljiva.

Nakon instalacije, potrebno je izgraditi docker image - nešto na što možemo
gledati kao klasu za različite konkretne instance virtualnih mašina
(containera). Image se gradi tako da se pozicionira u direktorij s `Dockerfile`
datotekom i pozove:

```shell
docker build -t hat .
```

Gdje je `hat` odabrano ime imagea.

Kad imamo image, možemo stvarati containere - konkretne instance virtualnih
uređaja. Najjednostavniji način da se stvori container je pozivanjem naredbe
`docker run`, no mi preporučujemo tu istu naredbu sa sljedećim opcijama:

```shell
docker run --name project -p 23023:23023 --mount type=bind,source=/putanja/do/hat/direktorija,target=/hat -it hat
```

Dakle, koristi se run naredba, ali uz opcije:

  * `name` je ime containera, koristit ćemo ga kasnije da se spojimo na njega
    iz drugih terminala
  * `-p 23023:23023` radi mapiranje portova - defaultno svi procesi u
    containeru ne exposeaju svoje portove host uređaju, a ovako containeru
    kažemo "posluži servis na portu 23023 na host uređaju na portu 23023"
  * `--mount type=bind...` kaže containeru da sinkroznizira direktorij na hostu
    `source` s direktorijem `target` na containeru, u ovom slučaju je odabran
    `target=/hat` jer je to defaultni radni direktorij naveden u Dockerfileu
  * `-i` otvara instancu containerovog terminala nakon što se on pokrene
  * `-t hat` referencira image iz kojeg se stvara container

Bitno je da se nakon `-it hat` ne dodaju novi argumenti za run naredbu jer ih
naredba interpretira kao komandnolinijski poziv za container.

Nakon što smo pokrenuli container, s prethodnom naredbom, zbog `-i` opcije, će
se već u tom terminalu otvoriti terminal containera, no, kako često imamo
potrebu za više paralelnih terminala, možemo u odvojenom terminalu na host
uređaju pozvati:

```shell
docker exec -it project bash
```

Što će otvoriti novi terminal containera project.

Ako se dogodi da run ne prolazi jer npr. neka prijašnja instance `project`
containera već postoji, poziv:

```shell
docker container rm -f /project
```

bi trebao izbrisati stari container. Ovo nam je prihvatljivo jer docker ovdje
ionako koristimo samo za buildanje i pokretanje implementacije koja se piše na
host uređaju. Ipak, ako iz nekog razloga ne bude prihvatljivo brisati
container, postoje opcije za startanje/stopanje itd.
