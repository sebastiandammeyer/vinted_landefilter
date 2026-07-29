@echo off
REM Dobbeltklik denne fil for at starte Vinted Landefilter.
REM Foerste gang opsaetter den automatisk alt (venv + pakker).
REM For at lukke appen igen: luk bare dette vindue, eller tryk Ctrl+C.

cd /d "%~dp0"

if not exist venv (
    echo Foerste gang - opretter virtuelt miljoe og installerer pakker...
    python -m venv venv
    call venv\Scripts\activate
    pip install -r requirements.txt
) else (
    call venv\Scripts\activate
)

echo.
echo Starter Vinted Landefilter paa http://localhost:5050 ...
echo (Luk dette vindue for at lukke appen igen)
echo.

start "" "http://localhost:5050"

python app.py
