# Koraci u razvoju

### Priprema:

- Poželjno bi bilo da se radi na operativnom sustavu *Ubuntu*   (ili nekoj
  drugoj*Linux* distribuciji).  Moguće je i raditi na *Windows* operacijskom
  sustavu  [s podešenim  WSL-om (Windows Subsystem for Linux)](https://www.windowscentral.com/install-windows-subsystem-linux-windows-10).

- Klonirati ova dva *git* repozitorija:
  * [Zadatak.](https://github.com/ket-praksa/hat-quickstart)
  * [Upute i simulator.](https://github.com/ket-praksa/assignment)  

- Instalirati *pip* (ako nije instaliran, *python* također). Naredba:

  ```shell
  sudo apt install python3-pip
  ```

- Preporučljivo bi bilo raditi u virtualnim okruženjima [*(venv)*](https://uoa-eresearch.github.io/eresearch-cookbook/recipe/2014/11/26/python-virtual-env/).

- Instalirati potrebne *python* pakete za **oba repozitorija**. Popis *python*
  paketa za *hat-quickstart* se nalazi u datoteci  requirements.pip.txt* (u oba
  direktorija).  Pozicionirati se u direktorij s navedenom datotekom i
  pokrenuti:

  ```shell
  pip install -r requirements.pip.txt
  ```

- Simulator pokrenuti (i ostaviti da radi) u zasebnom terminalu pozicioniranjem
  u direktorij sa simulatorom (*assignment/simulator*) i pokretanjem naredbe:

  ```shell
  python main.py
  ```

  Simulator će nastaviti raditi u pozadini i slati podatke koje je potrebno
  čitati pomoću *iec104* protokola.
  
- Dodatne upute za podešavanje *quick-start* projekta se nalaze
  [ovdje](https://github.com/ket-praksa/hat-quickstart/blob/master/README.rst)

### Preporučeni koraci rješavanja zadatka:

- Napraviti neovisnu skriptu koja bi se uspješno spojila na simulator. Za
  spajanje na simulator se koristi *iec104 library* implementiran u *
  hat-coreu*:

  [*IEC 60870-5-104 Hat-core* implementacija.](https://core.hat-open.com/docs/libraries/drivers/iec104.html)

  [*IEC 60870-5-104 Hat-core* dokumentacija.](https://core.hat-open.com/docs/pyhat/hat/drivers/iec104/index.html)  

- Kada je uspješno uspostavljena komunikacija sa simulatorom i vidljivi su
  podaci koji dolaze sa simulatora,  može se nastaviti razvijati sustav. Prvi
  korak bi bio proučiti [arhitekturu](architecture.md) sustava.

- Za oba smjera komunikacije potrebna je:
    - Implementacija *devicea*, modula i adaptera.
        - Proučiti dokumentaciju *corea* za tu komponentu.
        - Razviti.
    - Primjeri komponenata se nalaze unutar *quick-start* zadatka.

- Nakon implementacije dodatno je potrebno napraviti sljedeće:
    - automatizacija *builda* (proširenje postojećih *doit taskova*)
    - testovi
    - dokumentacija
    - automatizacija izrade distribucije programa
    - opcionalna proširenja
