#!/bin/bash
# Dobbeltklik denne fil for at starte Vinted Landefilter.
# Første gang opsætter den automatisk alt (venv + pakker).
# For at lukke appen igen: luk bare dette terminalvindue (Cmd+W), eller tryk Ctrl+C.

cd "$(dirname "$0")"

if [ ! -d "venv" ]; then
    echo "Første gang - opretter virtuelt miljø og installerer pakker (tager et øjeblik)..."
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
else
    source venv/bin/activate
fi

echo ""
echo "Starter Vinted Landefilter på http://localhost:5050 ..."
echo "(Luk dette vindue for at lukke appen igen)"
echo ""

# Åbn browseren automatisk, lidt forsinket så serveren når at starte
( sleep 2 && open "http://localhost:5050" ) &

python app.py
