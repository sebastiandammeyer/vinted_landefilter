"""
Kernelogik: henter en Vinted-søgning via deres interne API, og filtrerer
varerne til dem, der (med stor sandsynlighed) er fra en given sælger-valuta
- som proxy for land, fx DKK for Danmark.

Baggrund: Vinted viser IKKE sælgerens land direkte i søgeresultaterne, og
selve vare-detalje-kaldet (hvor land ellers ville kunne læses) er beskyttet
af bot-beskyttelse. TIL GENGÆLD indeholder søgeresultatet et 'conversion'-felt,
når varens pris er omregnet fra sælgerens egen valuta til din visningsvaluta.
Er 'conversion' IKKE til stede, er varen allerede prissat i din visningsvaluta
fra sælgerens side - det betyder sælgeren bruger den valuta som sin hjemme-
valuta på Vinted. For DKK er det en meget stærk proxy for "sælger i Danmark",
fordi DKK reelt kun bruges af Vinteds danske marked.

OBS: Dette er en proxy, ikke en garanti. Det er (indirekte) baseret på
hvilken Vinted-landeversion sælgeren bruger, ikke en 100% verificeret
adresse. For lande der deler valuta (fx EUR-lande) kan denne metode ikke
skelne mellem dem.
"""

import time
from urllib.parse import urlparse, parse_qs, urlencode

import requests

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
)

# Landekode -> valuta, til at afgøre "sælgerens hjemme-valuta" ud fra
# fraværet/tilstedeværelsen af et 'conversion'-felt.
COUNTRY_CURRENCY = {
    "DK": "DKK",
    "SE": "SEK",
    "NO": "NOK",
    "PL": "PLN",
    "CZ": "CZK",
    "HU": "HUF",
    "RO": "RON",
    "GB": "GBP",
    "UK": "GBP",
    "US": "USD",
    # Eurolande - kan ikke skelnes indbyrdes med denne metode (alle EUR)
    "DE": "EUR", "FR": "EUR", "ES": "EUR", "IT": "EUR", "NL": "EUR",
    "BE": "EUR", "AT": "EUR", "FI": "EUR", "PT": "EUR", "IE": "EUR",
    "LT": "EUR", "LV": "EUR", "EE": "EUR", "SK": "EUR", "SI": "EUR",
    "LU": "EUR",
}


class VintedError(Exception):
    """Fejl vi vil vise pænt i UI'et, i stedet for et rå stacktrace."""


def parse_search_url(search_url: str):
    """Splitter en Vinted søge-URL i (domæne, query-parametre)."""
    parsed = urlparse(search_url)
    if not parsed.netloc or "vinted" not in parsed.netloc:
        raise VintedError(
            "Det ligner ikke en Vinted-URL. Kopiér linket direkte fra "
            "adressefeltet, når du har lavet din søgning på vinted.dk."
        )
    domain = parsed.netloc
    params = {k: v[0] for k, v in parse_qs(parsed.query).items()}
    return domain, params


def make_session(domain: str) -> requests.Session:
    """Henter forsiden først for at få de cookies (session/csrf), som API'et kræver."""
    session = requests.Session()
    session.headers.update(
        {
            "User-Agent": USER_AGENT,
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "da-DK,da;q=0.9,en;q=0.8",
        }
    )
    resp = session.get(f"https://{domain}/", timeout=15)
    resp.raise_for_status()
    return session


VALID_ORDERS = {"relevance", "newest_first", "price_low_to_high", "price_high_to_low"}


def fetch_search_page(session, domain, params, page, per_page=96, order="relevance"):
    q = dict(params)
    q["page"] = page
    q["per_page"] = per_page
    if order in VALID_ORDERS:
        q["order"] = order
    url = f"https://{domain}/api/v2/catalog/items?{urlencode(q)}"
    resp = session.get(url, timeout=15)
    if resp.status_code == 400:
        # Vinted sætter en øvre grænse for hvor langt man kan bladre
        # (typisk omkring ~1000 varer i alt). Det er ikke en fejl -
        # vi er bare nået til bunden af, hvad Vinted vil udlevere.
        return None
    if resp.status_code in (401, 403):
        raise VintedError(
            f"Vinted afviste kaldet (status {resp.status_code}). Vent lidt og "
            "prøv igen - sker typisk hvis der sendes for mange kald for hurtigt."
        )
    resp.raise_for_status()
    return resp.json()


def collect_search_results(session, domain, params, max_pages, per_page, order="relevance", progress_cb=None):
    items = []
    for page in range(1, max_pages + 1):
        data = fetch_search_page(session, domain, params, page, per_page, order)
        if data is None:
            if progress_cb:
                progress_cb(
                    f"Nåede Vinteds grænse for hvor langt man kan bladre "
                    f"(stoppede ved side {page}, {len(items)} varer hentet i alt)."
                )
            break
        page_items = data.get("items", [])
        if not page_items:
            break
        items.extend(page_items)
        if progress_cb:
            progress_cb(f"Hentet {len(items)} varer fra søgningen (side {page})...")
        time.sleep(0.25)  # høflig pause mellem sider
    return items


def seller_currency_of(item):
    """
    Sælgerens formodede hjemme-valuta:
    - Hvis 'conversion' findes, er prisen omregnet FRA denne valuta.
    - Hvis 'conversion' IKKE findes, er varen allerede vist i sælgerens
      egen valuta (dvs. ingen omregning var nødvendig).
    """
    conversion = item.get("conversion")
    if conversion and conversion.get("seller_currency"):
        return conversion["seller_currency"]
    price = item.get("price") or {}
    return price.get("currency_code")


def search_and_filter(
    search_url,
    country_code="DK",
    max_pages=10,
    per_page=96,
    order="relevance",
    workers=12,  # ikke længere brugt, beholdt for kompatibilitet med app.py
    progress_cb=None,
):
    target_currency = COUNTRY_CURRENCY.get(country_code.upper())
    if not target_currency:
        raise VintedError(
            f"Landekoden '{country_code}' understøttes ikke af denne metode endnu."
        )

    domain, params = parse_search_url(search_url)
    session = make_session(domain)

    if progress_cb:
        progress_cb("Henter søgeresultater fra Vinted...")
    raw_items = collect_search_results(session, domain, params, max_pages, per_page, order, progress_cb)

    if not raw_items:
        return []

    matched = []
    for item in raw_items:
        if seller_currency_of(item) != target_currency:
            continue
        price = item.get("price") or {}
        total_price = item.get("total_item_price") or {}
        matched.append(
            {
                "id": item.get("id"),
                "title": item.get("title"),
                "price": price.get("amount"),
                "currency": price.get("currency_code"),
                "total_price": total_price.get("amount"),
                "favourite_count": item.get("favourite_count"),
                "status": item.get("status"),
                "photo": ((item.get("photo") or {}).get("url")),
                "url": item.get("url") or f"https://{domain}/items/{item.get('id')}",
                "city": None,
            }
        )

    if progress_cb:
        progress_cb(
            f"Færdig! {len(matched)} af {len(raw_items)} varer ser ud til at være "
            f"fra en sælger med {target_currency} som hjemme-valuta."
        )

    return matched
