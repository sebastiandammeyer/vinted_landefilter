"""
Henter ÉN side søgeresultater (det kald der allerede virker fint) og
viser pris/fragt- OG land/valuta-relaterede felter for varerne, så vi
kan se om der findes et brugbart spor for hvilket land varen er fra.

Brug:
    python debug_search_fields.py "<din-vinted-søge-url>"
"""

import sys

from vinted_client import parse_search_url, make_session, fetch_search_page

KEYWORDS = [
    "price", "fee", "shipping", "delivery", "cost", "total",
    "countr", "locale", "market", "iso", "domain", "region", "currency",
]


def find_fields(obj, path=""):
    found = []
    if isinstance(obj, dict):
        for key, value in obj.items():
            new_path = f"{path}.{key}" if path else key
            if any(kw in key.lower() for kw in KEYWORDS):
                found.append((new_path, value))
            if isinstance(value, (dict, list)):
                found.extend(find_fields(value, new_path))
    elif isinstance(obj, list):
        for i, value in enumerate(obj[:1]):
            found.extend(find_fields(value, f"{path}[{i}]"))
    return found


def main():
    if len(sys.argv) < 2:
        raise SystemExit('Brug: python debug_search_fields.py "<søge-url>"')

    search_url = sys.argv[1]
    domain, params = parse_search_url(search_url)
    session = make_session(domain)

    data = fetch_search_page(session, domain, params, page=1, per_page=10)
    items = data.get("items", [])

    print(f"Fandt {len(items)} varer på testsiden.\n")
    print("Alle nøgler i det rå vare-objekt (øverste niveau), til reference:")
    if items:
        print(list(items[0].keys()))
    print()

    for item in items:
        print("=" * 60)
        print(f"Vare: {item.get('title')}")
        fields = find_fields(item)
        if not fields:
            print("  (ingen relevante felter fundet)")
        for path, value in fields:
            value_str = str(value)
            if len(value_str) > 200:
                value_str = value_str[:200] + "..."
            print(f"  {path}: {value_str}")
        print()


if __name__ == "__main__":
    main()

