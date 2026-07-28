# Vinted Landefilter

Lille lokalt program: du indsætter en Vinted søge-URL, og det finder
kun de varer, der med stor sandsynlighed er fra en dansk sælger. Kører
som en rigtig lille webside i din browser (localhost), men al logik
kører lokalt på din egen maskine - intet sendes til andre servere end
Vinted selv.

## Sådan kører du det

Kræver Python 3.9+.

```bash
cd vinted-dk-filter
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
   valuta til din visningsvaluta (DKK). Er `conversion` IKKE til stede,
   er varen allerede prissat i DKK af sælgeren selv - og da DKK reelt
   kun bruges af Vinteds danske marked, er det et stærkt (om end ikke
   100% garanteret) tegn på, at sælgeren er dansk.
3. Scriptet filtrerer på præcis dét, og viser kun de varer, der matcher,
   i et billedgitter med link direkte til varen på Vinted.

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

## Lægge den op med et rigtigt link (Render)

Denne app har en Python/Flask-baggrund (den henter og filtrerer Vinted-data
server-side), så den kan IKKE ligge som almindelig GitHub Pages - det kan
kun vise rene HTML/CSS/JS-sider. I stedet bruger vi Render.com, som kan
køre selve Python-koden og give dig et rigtigt link.

1. **Push koden til GitHub** som et almindeligt repo (`git init`,
   `git add .`, `git commit -m "Første version"`, opret repo på GitHub,
   `git push`). `venv/` og `__pycache__/` bliver automatisk sprunget
   over pga. `.gitignore`.

2. **Opret en gratis konto på** [render.com](https://render.com) og log
   ind med din GitHub-konto.

3. Klik **New +** → **Web Service**, og vælg dit repo.

4. Udfyld:
   - **Name**: et navn efter eget valg (bliver en del af URL'en)
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app` (Render finder den ofte selv
     via `Procfile`)
   - **Instance Type**: Free

5. Klik **Create Web Service**. Efter et par minutters bygning får du et
   link i stil med `https://dit-navn.onrender.com` - det er det, du kan
   sende videre.

**Værd at vide om den gratis Render-plan:**
- Appen "sover", når der ikke har været besøgende et stykke tid - det
  første besøg efter en pause kan derfor tage 30-60 sekunder at loade,
  mens den vågner.
- Fordi det nu er et offentligt, delt link, kan ALLE med linket bruge
  det til at forespørge Vinted - det øger risikoen for, at Vinted
  rate-limiter eller blokerer selve Render-serverens IP (ikke kun din
  egen). Det er stadig fint til at dele med nogle få personer, men
  ikke tænkt som noget, der skal bruges i stor skala.



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

- `app.py` - lille Flask-server (webinterfacet + API-endpoints)
- `vinted_client.py` - selve søge- og filtreringslogikken
- `templates/index.html` - brugerfladen
- `debug_search_fields.py` - fejlsøgningsværktøj til at undersøge
  feltnavne i søgeresultater
- `requirements.txt` - Python-pakker der skal bruges (flask, requests)
