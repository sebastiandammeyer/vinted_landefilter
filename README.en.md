# Vinted Landefilter

*[Læs på dansk / Read in Danish](README.md)*

A small local tool: paste in a Vinted search URL, pick a country, and it
filters the results down to items that are very likely from a seller in
that country. It runs as a small website in your own browser
(localhost), but all the logic runs locally on your own machine -
nothing is sent to any server other than Vinted itself.

**Note:** this was originally built for Denmark specifically (hence the
name) - filtering Vinted searches down to Danish sellers only, since
Vinted doesn't offer that natively. It has since been generalized to
support other countries too, but Denmark (DKK) is where the underlying
method is most reliable - see "How it works" below for why.

## Getting the code

1. Go to the project's GitHub page.
2. Click the green **"Code"** button → **"Download ZIP"** (easiest if
   you don't use git yourself), then unzip it somewhere on your computer.
   (Alternatively: `git clone <repo-url>` if you're used to git.)
3. Continue to "Quick start" below - that's the unzipped folder you'll
   be working in.

## Quick start (no terminal needed)

**Mac:**
1. Double-click `start-mac.command`.
2. The first time, macOS blocks the file with a warning along the lines of
   *"Apple could not verify that start-mac.command is free of malware"* -
   this is completely normal for any unknown file downloaded from the
   internet, and nothing wrong with the file itself. Here's how to get
   past it:
   - **Easiest:** Go to **System Settings → Privacy & Security**, scroll
     down - there should be a message saying "start-mac.command" was
     blocked, with an **"Open Anyway"** button. Click it, try opening the
     file again, and confirm in the dialog that appears.
   - **Alternative (via Terminal, only needed once):**
     ```bash
     xattr -d com.apple.quarantine start-mac.command
     ```
     After that, a normal double-click will work without any warning.
3. After that, you can just double-click it normally. It automatically
   sets everything up the first time (can take a minute), then opens
   your browser for you.
4. To close the app again: just close the terminal window that opened.

If double-clicking does nothing at all (can happen after downloading
from GitHub), the file needs to be made "executable" once in Terminal:
```bash
chmod +x start-mac.command
```

**Windows:**
1. Double-click `start-windows.bat`.
2. It automatically sets everything up the first time, then opens your
   browser.
3. To close the app again: just close the window that opened.

## Running it (with a terminal)

Requires Python 3.9+.

```bash
cd vinted_landefilter        # or whatever you named/unzipped the folder to
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Then open **http://localhost:5050** in your browser.

Paste in a search URL from vinted.dk (e.g. after searching "bike" and
optionally setting price/size filters - copy the link from the address
bar), and click "Søg" (Search).

## How it works

1. Vinted doesn't have an official API, but their website internally
   uses `https://www.vinted.dk/api/v2/catalog/items` to fetch search
   results. The script recreates that call and automatically pages
   through every result page (instead of you clicking "next page").
2. Vinted doesn't show the seller's country directly. However, every
   item includes a `conversion` field whenever the price has been
   converted from the seller's own currency into your display currency.
   If `conversion` is NOT present, the item is already priced in the
   currency you selected by the seller themselves - e.g. DKK is a
   strong (though not 100% guaranteed) signal of a Danish seller,
   because DKK is realistically only used on Vinted's Danish
   marketplace.
3. The script filters on exactly that, based on the country/currency
   you choose in the dropdown, and shows only the matching items in an
   image grid with a link straight to the item on Vinted.

This method is significantly faster and more robust than looking up
each item's country individually, because it relies entirely on data
that's already included in the regular search call - no extra call per
item, and no risk of being blocked by bot protection.

## Good to know

- **This is a proxy, not a guarantee.** The method assumes "no currency
  conversion needed" means "seller is Danish" (or whichever country you
  picked). That holds true in the vast majority of cases (DKK is used
  almost exclusively in Denmark), but it can occasionally be wrong.
- For countries that share a currency (e.g. the eurozone), the method
  can't distinguish between them individually - only between "eurozone"
  and "not eurozone". For Danish filtering specifically (a unique
  currency, DKK), it's very reliable.
- **This is not an official Vinted feature.** The script recreates an
  internal API call by mimicking what a regular browser does. Vinted
  can change the structure without notice.
- Feel free to use it for personal use, but avoid setting "max pages"
  very high or running it in a loop all day - it puts load on Vinted's
  servers and increases the risk of being rate-limited (temporarily
  blocked).
- Like any unofficial Vinted integration, this sits in a gray area with
  respect to Vinted's terms on automated data extraction. Keep that in
  mind if you share the project publicly (e.g. on GitHub) - it's not an
  official, supported integration, and Vinted can change or block
  access at any time.

## Can it be hosted with a real link, so others can just visit it?

Short answer: no, not in practice. The app was tested with free hosting
(Render.com), and Vinted blocks requests from there (status 403) -
their bot protection is more suspicious of datacenter IP addresses than
regular home IPs. The same will likely happen with other similar free
hosting services.

The app is therefore meant to be a **local program**: each person who
wants to use it downloads the code (see "Getting the code" above) and
runs it themselves, using their own internet connection, via "Quick
start". This is more or less the standard model for this kind of
unofficial, personal tool.

## Troubleshooting

Vinted's internal API is undocumented, so the field names in the JSON
response can change over time. The folder includes a couple of helper
scripts if something stops working:

- `debug_search_fields.py "<search-url>"` - shows all fields on a few
  items from a search, and highlights the ones that look like
  price/currency/country. Use it to check whether the `conversion`
  field is still called that, if filtering suddenly stops returning
  results.

If the field name has changed, update it in `seller_currency_of()` in
`vinted_client.py`.

## Setting an icon on the start file

There's a logo ready to go in the `icon/` folder - a PNG for Mac, and an
`.ico` file for Windows (Windows requires that specific format for icons,
regular images won't work).

**Mac:**
1. Open `icon/6-pin-og-vinted-tekst.png`, and copy the image (select it
   in Finder and press `Cmd+C`, or open it in Preview and press `Cmd+A`
   → `Cmd+C`).
2. Click once on `start-mac.command` in Finder, then press `Cmd+I` (Get Info).
3. Click the small icon in the top-left of the info window so it's
   selected (turns blue).
4. Press `Cmd+V` to paste the image in as the icon.
5. Close the info window - the file now has the new icon.

**Note:** this is only saved locally on your own computer and doesn't
travel with the file if it's shared further (e.g. via GitHub) - each
person needs to do this themselves if they want the icon.

**Windows:**
Windows doesn't let you set an icon directly on a `.bat` file - it has
to be done via a shortcut instead:
1. Right-click `start-windows.bat` → **Send to → Desktop (create
   shortcut)**. A new file will appear on your desktop, e.g.
   "start-windows.bat - Shortcut".
2. Right-click the **shortcut** → **Properties**.
3. Click **Change Icon...** under the "Shortcut" tab.
4. Click **Browse...**, and find `icon/vinted-landefilter.ico` inside
   the unzipped project folder.
5. Select the file → **OK** → **Apply** → **OK**.

The shortcut on your desktop now has the new icon, and starts the app
when double-clicked (it points to the original `.bat` file).

## Files

- `icon/` - logo to set as the icon on the start files (see above)
- `start-mac.command` / `start-windows.bat` - double-click to start the
  app without a terminal (see "Quick start" above)
- `app.py` - small Flask server (the web interface + API endpoints)
- `vinted_client.py` - the actual search and filtering logic
- `templates/index.html` - the user interface
- `debug_search_fields.py` - troubleshooting tool for inspecting field
  names in search results
- `requirements.txt` - the Python packages needed (flask, requests)
