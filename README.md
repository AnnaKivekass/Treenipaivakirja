# Treenipäiväkirja

Flask-pohjainen web-sovellus treenien kirjaamiseen ja tarkasteluun.  
Sovelluksessa käyttäjät voivat lisätä treenejä, luokitella niitä, tarkastella tilastoja sekä lähettää viestejä toisten käyttäjien treeneihin liittyen.

---

## Ominaisuudet

- **Käyttäjätilit**
  - Rekisteröityminen ja kirjautuminen
  - Jokaisella käyttäjällä oma näkymä omiin treeneihin

- **Treenien hallinta**
  - Uuden treenin lisääminen (päivämäärä, tyyppi, kesto, kuvaus)
  - Käyttäjän treenit näkyvät etusivulla
  - Treenien haku

- **Luokittelu**
  - Treenille voi valita yhden tai useamman luokan (esim. voima, cardio, venyttely)
  - Luokat tallennetaan tietokantaan ja niitä hyödynnetään hauissa

- **Viestit**
  - Käyttäjät voivat lähettää viestejä toisten käyttäjien treeneihin liittyen
  - Viestit tallennetaan tietokantaan ja näkyvät viestisivulla

- **Tilastot ja käyttäjäsivu**
  - Käyttäjäsivulla näkyy yhteenveto käyttäjän lisäämistä treeneistä

---

## Teknologiat

- Python 3
- Flask
- SQLite
- HTML / CSS

---

## Asennus ja käyttöohjeet

### 1. Kloonaa repositorio

```bash
git clone https://github.com/AnnaKivekass/Treenipaivakirja.git
cd treenipaivakirja

## Luo ja aktivoi virtuaaliympäristö
python3 -m venv venv
source venv/bin/activate

## Asenna flask
pip install flask

## Alusta tietokanta
mkdir -p instance
sqlite3 instance/app.sqlite3 < schema.sql
sqlite3 instance/app.sqlite3 < seed.sql

## Käynnistä sovellus
flask --app app.py run

