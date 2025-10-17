Sovelluksessa on seuraavat ominaisuudet
- Käyttäjätilit:
  - Käyttäjä voi rekisteröityä ja kirjautua sisään.
  - Jokaisella käyttäjällä on oma näkymä, jossa näkyvät hänen lisäämänsä treenit.

- Treenien hallinta:
  - Käyttäjä voi lisätä uuden treenin, joka sisältää päivämäärän, tyypin, keston ja kuvauksen.
  - Kaikki käyttäjän treenit näkyvät etusivulla.
  - Treenejä voi myös hakea hakutoiminnolla.

- Luokittelu:
  - Treenille voi valita yhden tai useamman luokan (esim. voima, cardio, venyttely).
  - Luokat tallennetaan tietokantaan ja niitä voidaan hyödyntää tilastoissa ja hauissa.

- Viestit:
  - Käyttäjät voivat lähettää viestejä toisten käyttäjien treeneihin liittyen.
  - Viestit tallennetaan tietokantaan ja näkyvät viestisivulla.

- Tilastot ja käyttäjäsivu:
  - Käyttäjäsivulla näkyy yhteenveto käyttäjän lisäämistä treeneistä ja mahdolliset tilastot.

Sovelluksen asennus ja käyttöohjeet

Jos Flask ei ole vielä asennettu, suorita terminaalissa komentorivillä:

```bash
pip install flask

Sovellus käyttää SQLite-tietokantaa.
Tiedostossa schema.sql on taulujen määritykset. Luo tietokanta näin:

sqlite3 instance/app.sqlite3 < schema.sql

Käynnistä sovellus

Suorita seuraava komento:

flask --app app.py run
