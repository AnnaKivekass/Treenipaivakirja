import secrets
import sqlite3
from functools import wraps
from pathlib import Path

from flask import (
    Flask, abort, flash, g,
    redirect, render_template,
    request, session, url_for
)

from db.categories import (
    assign_categories_to_workout,
    list_categories,
    list_workout_categories,
)

from db.connection import close_db, init_db

from db.messages import (
    add_message,
    get_message,
    update_message,
    delete_message_by_id,
    list_workouts_for_messages,
    list_messages_full,
    get_workout_owner,
)

from db.users import add_user, get_user, verify_password, get_user_by_id

from db.workouts import (
    add_workout,
    get_workout,
    list_workouts,
    list_all_workouts,
    search_workouts,
    update_workout,
    delete_workout_by_id,
    get_user_stats,
    get_user_stats_by_type,
)

app = Flask(__name__)
app.config["SECRET_KEY"] = "dev-secret"
app.config["DATABASE"] = "instance/app.sqlite3"

Path("instance").mkdir(exist_ok=True)

@app.before_request
def ensure_csrf():
    if "csrf_token" not in session:
        session["csrf_token"] = secrets.token_hex(16)
    g.csrf_token = session["csrf_token"]


@app.context_processor
def inject_csrf():
    return {"csrf_token": g.get("csrf_token")}


@app.teardown_appcontext
def _close_db(exc):
    close_db()


@app.cli.command("init-db")
def init_db_command():
    init_db("schema.sql")
    print("Initialized the database.")


def validate_csrf():
    if request.form.get("csrf_token") != session.get("csrf_token"):
        abort(400)


def login_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            flash("Kirjaudu sisään ensin.", "error")
            return redirect(url_for("login"))
        return fn(*args, **kwargs)
    return wrapper


def validate_workout_form(form):
    date = (form.get("date") or "").strip()
    wtype = (form.get("type") or "").strip()
    duration_raw = (form.get("duration") or "").strip()
    description = (form.get("description") or "").strip()

    errors = []

    if not date:
        errors.append("Päivämäärä vaaditaan.")
    if not wtype:
        errors.append("Tyyppi vaaditaan.")
    if len(wtype) > 50:
        errors.append("Tyyppi on liian pitkä (max 50).")
    if len(description) > 1000:
        errors.append("Kuvaus on liian pitkä (max 1000).")

    try:
        duration_val = int(duration_raw)
        if duration_val < 0 or duration_val > 100000:
            errors.append("Kesto ei kelpaa.")
    except ValueError:
        errors.append("Keston tulee olla kokonaisluku.")
        duration_val = None

    return {
        "date": date,
        "type": wtype,
        "duration": duration_raw,
        "description": description,
        "duration_val": duration_val,
    }, errors


@app.route("/")
@login_required
def index():
    workouts = list_workouts(session["user_id"])
    workouts = [
        dict(w) | {"categories": list_workout_categories(w["id"])}
        for w in workouts
    ]
    return render_template("index.html", workouts=workouts)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        validate_csrf()

        username = (request.form.get("username") or "").strip()
        password = (request.form.get("password") or "").strip()
        password2 = (request.form.get("password2") or "").strip()

        if not (3 <= len(username) <= 30):
            flash("Käyttäjätunnuksen pituus 3–30 merkkiä.", "error")
            return render_template("register.html")

        if not (8 <= len(password) <= 128):
            flash("Salasanan pituus 8–128 merkkiä.", "error")
            return render_template("register.html")

        if password != password2:
            flash("Salasanat eivät täsmää.", "error")
            return render_template("register.html")

        if get_user(username):
            flash("Käyttäjätunnus on jo käytössä.", "error")
            return render_template("register.html")

        add_user(username, password)
        flash("Tunnus luotu. Voit nyt kirjautua sisään.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        validate_csrf()

        username = (request.form.get("username") or "").strip()
        password = (request.form.get("password") or "").strip()
        user = get_user(username)

        if user and verify_password(user, password):
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            flash(f"Tervetuloa, {user['username']}!", "success")
            return redirect(url_for("index"))

        flash("Virheellinen käyttäjätunnus tai salasana.", "error")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("Uloskirjautuminen onnistui.", "success")
    return redirect(url_for("login"))


@app.route("/workout/add", methods=["GET", "POST"], endpoint="add_workout")
@login_required
def add_workout_route():
    if request.method == "POST":
        validate_csrf()

        selected_ids = [
            int(x) for x in request.form.getlist("categories")
            if x.isdigit()
        ]

        data, errors = validate_workout_form(request.form)

        if errors:
            for e in errors:
                flash(e, "error")
            return render_template(
                "workout_form.html",
                form=data,
                categories=list_categories(),
                selected=set(selected_ids),
            )

        try:
            wid = add_workout(
                session["user_id"],
                data["date"],
                data["type"],
                data["duration_val"],
                data["description"] or None,
            )
            assign_categories_to_workout(wid, selected_ids)
        except sqlite3.IntegrityError:
            abort(403)

        flash("Treeni lisätty.", "success")
        return redirect(url_for("index"))

    return render_template(
        "workout_form.html",
        form={"date": "", "type": "", "duration": "", "description": ""},
        categories=list_categories(),
        selected=set(),
    )


@app.route("/workouts")
@login_required
def workouts_all():
    rows = list_all_workouts()

    items = [
        {
            "id": r["id"],
            "date": r["date"],
            "type": r["type"],
            "duration": r["duration"],
            "description": r["description"],
            "username": r["username"],
        }
        for r in rows
    ]

    return render_template("workouts_all.html", workouts=items)

@app.errorhandler(400)
@app.errorhandler(403)
@app.errorhandler(404)
def handle_error(e):
    return render_template(f"{e.code}.html"), e.code


if __name__ == "__main__":
    app.run(debug=True)
