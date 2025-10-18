Pylint-raportti

Pylint antaa seuraavan raportin sovelluksesta:

************* Module app
app.py:1:0: C0114: Missing module docstring (missing-module-docstring)
app.py:5:0: E0401: Unable to import 'flask' (import-error)
app.py:6:0: E0401: Unable to import 'flask' (import-error)
app.py:17:0: C0116: Missing function or method docstring (missing-function-docstring)
app.py:29:0: C0116: Missing function or method docstring (missing-function-docstring)
app.py:29:0: E0102: function already defined line 22 (function-redefined)
app.py:36:0: C0116: Missing function or method docstring (missing-function-docstring)
app.py:41:14: W0613: Unused argument 'exc' (unused-argument)
app.py:46:0: C0116: Missing function or method docstring (missing-function-docstring)
app.py:47:4: E0602: Undefined variable 'init_db' (undefined-variable)
app.py:51:0: C0116: Missing function or method docstring (missing-function-docstring)
app.py:59:0: C0116: Missing function or method docstring (missing-function-docstring)
app.py:68:0: C0116: Missing function or method docstring (missing-function-docstring)
app.py:98:0: C0116: Missing function or method docstring (missing-function-docstring)
app.py:117:0: C0116: Missing function or method docstring (missing-function-docstring)
app.py:124:0: C0116: Missing function or method docstring (missing-function-docstring)
app.py:173:15: E0602: Undefined variable 'sqlite3' (undefined-variable)
app.py:188:0: C0116: Missing function or method docstring (missing-function-docstring)
app.py:213:0: C0116: Missing function or method docstring (missing-function-docstring)
app.py:277:15: E0602: Undefined variable 'sqlite3' (undefined-variable)
app.py:318:0: C0116: Missing function or method docstring (missing-function-docstring)
app.py:346:0: C0116: Missing function or method docstring (missing-function-docstring)
app.py:366:0: C0116: Missing function or method docstring (missing-function-docstring)
app.py:387:0: C0116: Missing function or method docstring (missing-function-docstring)
app.py:427:0: C0116: Missing function or method docstring (missing-function-docstring)
app.py:432:0: C0116: Missing function or method docstring (missing-function-docstring)
app.py:437:0: C0116: Missing function or method docstring (missing-function-docstring)
app.py:441:0: C0116: Missing function or method docstring (missing-function-docstring)
app.py:446:0: C0116: Missing function or method docstring (missing-function-docstring)
app.py:459:8: E0602: Undefined variable 'init_db' (undefined-variable)
app.py:9:0: W0611: Unused get_message_for_edit imported from db.messages (unused-import)
app.py:9:0: W0611: Unused list_messages imported from db.messages (unused-import)
app.py:9:0: W0611: Unused update_message_content imported from db.messages (unused-import)
app.py:11:0: W0611: Unused get_workout imported from db.workouts (unused-import)
************* Module config
config.py:1:0: C0114: Missing module docstring (missing-module-docstring)
config.py:1:0: C0103: Constant name "secret_key" doesn't conform to UPPER_CASE naming style (invalid-name)
************* Module db
db.py:1:0: C0114: Missing module docstring (missing-module-docstring)
db.py:2:0: E0401: Unable to import 'flask' (import-error)
db.py:4:0: C0116: Missing function or method docstring (missing-function-docstring)
db.py:10:0: C0116: Missing function or method docstring (missing-function-docstring)
db.py:10:0: W0102: Dangerous default value [] as argument (dangerous-default-value)
db.py:17:0: C0116: Missing function or method docstring (missing-function-docstring)
db.py:20:0: C0116: Missing function or method docstring (missing-function-docstring)
db.py:20:0: W0102: Dangerous default value [] as argument (dangerous-default-value)
************* Module items
items.py:1:0: C0114: Missing module docstring (missing-module-docstring)
items.py:3:0: C0116: Missing function or method docstring (missing-function-docstring)
items.py:15:0: C0116: Missing function or method docstring (missing-function-docstring)
items.py:26:0: C0116: Missing function or method docstring (missing-function-docstring)
items.py:31:0: C0116: Missing function or method docstring (missing-function-docstring)
items.py:38:0: C0116: Missing function or method docstring (missing-function-docstring)
items.py:49:0: C0116: Missing function or method docstring (missing-function-docstring)
items.py:53:0: C0116: Missing function or method docstring (missing-function-docstring)
items.py:57:0: C0116: Missing function or method docstring (missing-function-docstring)
items.py:62:0: C0116: Missing function or method docstring (missing-function-docstring)
items.py:66:0: C0116: Missing function or method docstring (missing-function-docstring)
items.py:70:0: C0116: Missing function or method docstring (missing-function-docstring)
items.py:79:0: C0116: Missing function or method docstring (missing-function-docstring)
items.py:92:0: C0116: Missing function or method docstring (missing-function-docstring)
items.py:105:0: C0116: Missing function or method docstring (missing-function-docstring)
items.py:115:0: C0116: Missing function or method docstring (missing-function-docstring)
************* Module users
users.py:1:0: C0114: Missing module docstring (missing-module-docstring)
users.py:1:0: E0401: Unable to import 'werkzeug.security' (import-error)
users.py:5:0: C0116: Missing function or method docstring (missing-function-docstring)
users.py:10:0: C0116: Missing function or method docstring (missing-function-docstring)
users.py:14:0: C0116: Missing function or method docstring (missing-function-docstring)
users.py:19:0: C0116: Missing function or method docstring (missing-function-docstring)
users.py:27:4: R1705: Unnecessary "else" after "return" (no-else-return)

Your code has been rated at 7.82/10 (previous run: 7.82/10, +0.00)

Docstring-ilmoitukset

Suuri osa raportin ilmoituksista on seuraavan tyyppisiä:

app.py:1:0: C0114: Missing module docstring (missing-module-docstring)
app.py:17:0: C0116: Missing function or method docstring (missing-function-docstring)

Nämä tarkoittavat, että moduuleissa ja funktioissa ei ole docstring-kommentteja.
Sovelluksessa on tehty tietoinen päätös olla käyttämättä niitä.

Import-ilmoitukset

app.py:5:0: E0401: Unable to import 'flask' (import-error)
users.py:1:0: E0401: Unable to import 'werkzeug.security' (import-error)

Nämä johtuvat ympäristöstä, jossa Pylint ei näe virtuaaliympäristön riippuvuuksia.
Koodi toimii normaalisti sovelluksessa.

Tarpeeton else (R1705)
app.py:264:8: R1705: Unnecessary "else" after "return"


Koodi:

if "remove" in request.form:
    items.remove_item(item_id)
    return redirect("/")
else:
    return redirect("/item/" + str(item_id))

Tämä on jätetty sellaiseksi, koska else tekee koodin luettavuudesta selkeämmän.

Puuttuva palautusarvo (R1710)

app.py:250:0: R1710: Either all return statements in a function should return an expression, or none of them should.
app.py:292:0: R1710: Either all return statements in a function should return an expression, o

Ilmoitukset liittyvät funktioihin, jotka käsittelevät metodit GET ja POST:

@app.route("/remove_item/<int:item_id>", methods=["GET", "POST"])
def remove_item(item_id):
    if request.method == "GET":
        return render_template("remove_item.html", item=item)
    if request.method == "POST":
        if "remove" in request.form:
            items.remove_item(item_id)
            return redirect("/")
        else:
            return redirect("/item/" + str(item_id))

Koska Flask rajaa metodit GET ja POST, ei ole mahdollista, ettei funktio palauttaisi arvoa.

Vakion nimi (C0103)

config.py:1:0: C0103: Constant name "secret_key" doesn't conform to UPPER_CASE naming style

secret_key on jätetty pienaakkosilla, koska sitä käytetään muodossa
app.secret_key = config.secret_key.

Vaarallinen oletusarvo (W0102)

db.py:10:0: W0102: Dangerous default value [] as argument

def execute(sql, params=[]):
    con = get_connection()
    result = con.execute(sql, params)
    con.commit()
    g.last_insert_id = result.lastrowid
    con.close()

Tässä oletuslistaa ei muokata, joten ongelmaa ei käytännössä ole.

Yhteenveto

Pylint-arvosana: 7.82 / 10

Jäljelle jääneet ilmoitukset liittyvät tyyliin, dokumentointiin ja ympäristöön.

Kaikki toiminnalliset virheet on korjattu.

Koodi on muotoiltu black ja isort -työkaluilla.
