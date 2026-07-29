# Vinted Landefilter

Lille lokalt program: du indsætter en Vinted søge-URL, vælger et land, og
det finder kun de varer, der med stor sandsynlighed er fra en sælger i
det land. Kører som en rigtig lille webside i din browser (localhost),
men al logik kører lokalt på din egen maskine - intet sendes til andre
servere end Vinted selv.

## Sådan henter du koden

1. Gå til GitHub-siden for projektet.
2. Klik den grønne knap **"Code"** → **"Download ZIP"** (nemmest hvis du
   ikke bruger git selv), og pak ZIP-filen ud et sted på din computer.
   (Alternativt: `git clone <repo-url>`, hvis du er vant til git.)
3. Fortsæt til "Hurtig start" nedenfor - det er den udpakkede mappe, du
   skal arbejde i.

## Hurtig start (uden terminal)

**Mac:**
1. Dobbeltklik `start-mac.command`.
2. Første gang skal du højreklikke på filen → "Åbn" (macOS blokerer normalt
   ukendte scripts ved almindeligt dobbeltklik første gang) → bekræft "Åbn".
3. Herefter kan filen dobbeltklikkes normalt. Den sætter automatisk alt op
   første gang (kan tage et minut), og åbner derefter browseren for dig.
4. For at lukke appen igen: luk bare det terminalvindue, der åbnede.

Hvis dobbeltklik ikke starter noget (kan ske ved download fra GitHub), skal
filen først gøres "eksekverbar" én gang i Terminal:
```bash
chmod +x start-mac.command
```

**Windows:**
1. Dobbeltklik `start-windows.bat`.
2. Den sætter automatisk alt op første gang, og åbner derefter browseren.
3. For at lukke appen igen: luk bare det vindue, der åbnede.

## Sådan kører du det (med terminal)

Kræver Python 3.9+.

```bash
cd vinted_landefilter        # eller navnet på den mappe, du hentede/pakkede ud
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Åbn derefter **http://localhost:5050** i din browser.

Indsæt en søge-URL fra vinted.dk (fx efter du har søgt på "cykel" og
evt. sat filtre for pris/størrelse - kopiér linket fra adressefeltet),
og tryk "Søg".

## Hvordan det virker

1. Vinted har ikke en officiel API, men deres hjemmeside bruger internt
   `https://www.vinted.dk/api/v2/catalog/items` til at hente søgeresultater.
   Scriptet genskaber dette kald og bladrer automatisk alle sider igennem
   (i stedet for at du selv skal klikke "næste side").
2. Vinted viser ikke sælgerens land direkte. Til gengæld indeholder hver
   vare et `conversion`-felt, når prisen er regnet om fra sælgerens egen
   valuta til din visningsvaluta. Er `conversion` IKKE til stede, er varen
   allerede prissat i den valuta, du vælger, af sælgeren selv - fx er DKK
   et stærkt (om end ikke 100% garanteret) tegn på en dansk sælger, fordi
   DKK reelt kun bruges af Vinteds danske marked.
3. Scriptet filtrerer på præcis dét, ud fra det land/den valuta du vælger
   i dropdown'en, og viser kun de varer, der matcher, i et billedgitter
   med link direkte til varen på Vinted.

Denne metode er markant hurtigere og mere robust end at slå hver vares
land op enkeltvis, fordi den udelukkende bruger data, der allerede
kommer med i det almindelige søgekald - ingen ekstra kald pr. vare,
og ingen risiko for at blive blokeret af bot-beskyttelse.

## Vigtigt at vide

- **Dette er en proxy, ikke en garanti.** Metoden antager, at "ingen
  valutaomregning nødvendig" betyder "sælger er dansk". Det holder i
  langt de fleste tilfælde (DKK bruges stort set kun i Danmark), men
  kan i sjældne tilfælde ramme forkert.
- For lande der deler valuta (fx eurolandene) kan metoden ikke skelne
  mellem dem indbyrdes - kun mellem "eurozonen" og "ikke eurozonen".
  Til dansk filtrering (unik valuta, DKK) er den til gengæld meget
  pålidelig.
- **Dette er ikke en officiel Vinted-funktion.** Scriptet genskaber et
  internt API-kald ved at efterligne det, en almindelig browser laver.
  Vinted kan ændre strukturen uden varsel.
- Brug det roligt til personligt brug, men undgå at sætte `max sider`
  meget højt eller køre det i loop hele dagen - det belaster Vinteds
  servere og øger risikoen for at blive rate-limited (midlertidigt
  blokeret).
- Ligesom enhver uofficiel Vinted-integration ligger dette i en gråzone
  ift. Vinteds vilkår om automatiseret dataudtræk. Overvej det, hvis du
  deler projektet offentligt (fx på GitHub) - det er ikke en officiel,
  understøttet integration, og Vinted kan til enhver tid ændre eller
  blokere adgangen.

## Kan den lægges op med et rigtigt link, så andre bare kan besøge den?

Kort svar: nej, ikke i praksis. Appen er testet med gratis hosting
(Render.com), og Vinted blokerer kald derfra (statuskode 403) - deres
bot-beskyttelse er mere mistroisk over for datacenter-IP-adresser end
almindelige hjemme-IP'er. Det samme vil sandsynligvis ske med andre
tilsvarende gratis hosting-tjenester.

Appen er derfor tænkt som et **lokalt program**: hver person, der vil
bruge det, henter koden (se "Sådan henter du koden" ovenfor) og kører
den selv med sin egen internetforbindelse via "Hurtig start". Det er
sådan set den normale model for den slags uofficielle, personlige
værktøjer.

## Fejlsøgning

Vinteds interne API er udokumenteret, så feltnavnene i JSON-svaret kan
ændre sig over tid. Mappen indeholder et par hjælpescripts, hvis noget
holder op med at virke:

- `debug_search_fields.py "<søge-url>"` - viser alle felter på et par
  varer fra en søgning, og fremhæver dem der ligner pris/valuta/land.
  Brug den til at tjekke, om `conversion`-feltet stadig hedder det
  samme, hvis filtreringen pludselig holder op med at give resultater.

Hvis feltnavnet er ændret, ret det i `seller_currency_of()` i
`vinted_client.py`.

## Filer

- `start-mac.command` / `start-windows.bat` - dobbeltklik for at starte
  appen uden terminal (se "Hurtig start" ovenfor)
- `app.py` - lille Flask-server (webinterfacet + API-endpoints)
- `vinted_client.py` - selve søge- og filtreringslogikken
- `templates/index.html` - brugerfladen
- `debug_search_fields.py` - fejlsøgningsværktøj til at undersøge
  feltnavne i søgeresultater
- `requirements.txt` - Python-pakker der skal bruges (flask, requests)
