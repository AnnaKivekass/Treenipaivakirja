Pylint antaa seuraavan raportin sovelluksesta:

************* Module app
app.py:1:0: C0114: Missing module docstring (missing-module-docstring)
app.py:5:0: E0401: Unable to import 'flask' (import-error)
app.py:6:0: E0401: Unable to import 'flask' (import-error)
...
users.py:27:4: R1705: Unnecessary "else" after "return"

Your code has been rated at 7.82/10 (previous run: 7.82/10, +0.00)


Suuri osa raportin ilmoituksista on seuraavan tyyppisiä ilmoituksia:

app.py:1:0: C0114: Missing module docstring (missing-module-docstring)
app.py:17:0: C0116: Missing function or method docstring (missing-function-docstring)


Nämä ilmoitukset tarkoittavat, että moduuleissa ja funktioissa ei ole docstring-kommentteja.  
Sovelluksen kehityksessä tehty tietoinen päätös olla käyttämättä docstring-kommentteja.


Raportissa on seuraavat ilmoitukset liittyen import-komentoihin:

app.py:5:0: E0401: Unable to import 'flask' (import-error)
users.py:1:0: E0401: Unable to import 'werkzeug.security' (import-error)

Nämä johtuvat Pylintin ajosta eri ympäristössä kuin missä riippuvuudet on asennettu.  
Raportissa on ilmoituksia:
app.py:264:8: R1705: Unnecessary "else" after "return"

Koodi:
```python
if "remove" in request.form:
    items.remove_item(item_id)
    return redirect("/")
else:
    return redirect("/item/" + str(item_id))

Tämä on säilytetty sellaisenaan, koska else tekee koodin luettavuudesta selkeämmän.

Puuttuva palautusarvo (R1710)

Pylint varoittaa tilanteista, joissa kaikki return-komennot eivät palauta arvoa.
Koska Flaskin @app.route rajoittaa metodit (esim. GET ja POST), tällainen tilanne ei voi tapahtua käytännössä.


Vakion nimi (C0103)

Ilmoitus:

Vaarallinen oletusarvo (W0102)

Pylint antaa varoituksen:

Yhteenveto

Kaikki toiminnallisuuteen vaikuttavat virheet on korjattu.

Jäljelle jääneet ilmoitukset ovat tyylillisiä tai kehitysympäristöön liittyviä.

Lopullinen arvosana: 7.82 / 10.

Koodi on muotoiltu black- ja isort-työkaluilla.

Dokumentointi on selitetty tässä raportissa.
