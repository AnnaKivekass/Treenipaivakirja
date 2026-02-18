import secrets
import sqlite3
from functools import wraps
from pathlib import Path

from flask import Flask, abort, flash, g, redirect, render_template, request, session, url_for
from db.categories import assign_categories_to_workout, list_categories, list_workout_categories
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
    delete_workout_by_id
)

app = Flask(__name__)
app.config["SECRET_KEY"] = "dev-secret"
app.config["DATABASE"] = "instance/app.sqlite3"
Path("instance").mkdir(exist_ok=True)

app.teardown_appcontext(close_db)

@app.before_request
def ensure_csrf():
    if "csrf_token" not in session:
        session["csrf_token"] = secrets.token_hex(16)
    g.csrf_token = session["csrf_token"]


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


def require_login():
    if "user_id" not in session:
        flash("Kirjaudu sisään ensin.", "error")
        return False
    return True


@app.route("/")
def index():
    if not require_login():
        return redirect(url_for("login"))
    workouts = list_workouts(session["user_id"])
    workouts = [dict(w) | {"categories": list_workout_categories(w["id"])} for w in workouts]
    return render_template("index.html", workouts=workouts)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        if request.form.get("csrf_token") != session.get("csrf_token"):
            abort(400)

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
        if request.form.get("csrf_token") != session.get("csrf_token"):
            abort(400)

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
def add_workout_route():
    if not require_login():
        return redirect(url_for("login"))

    if request.method == "POST":
        if request.form.get("csrf_token") != session.get("csrf_token"):
            abort(400)

        date = (request.form.get("date") or "").strip()
        wtype = (request.form.get("type") or "").strip()
        duration_raw = (request.form.get("duration") or "").strip()
        description = (request.form.get("description") or "").strip()
        selected_ids = [int(x) for x in request.form.getlist("categories") if x.isdigit()]

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

        if errors:
            for e in errors:
                flash(e, "error")
            form = {
                "date": date,
                "type": wtype,
                "duration": duration_raw,
                "description": description,
            }
            return render_template(
                "workout_form.html",
                form=form,
                categories=list_categories(),
                selected=set(selected_ids),
            )

        try:
            wid = add_workout(session["user_id"], date, wtype, duration_val, description or None)
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
def workouts_all():
    if not require_login():
        return redirect(url_for("login"))

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


@app.route("/messages", methods=["GET", "POST"], endpoint="messages_route")
def messages_route():
    if not require_login():
        return redirect(url_for("login"))

    if request.method == "POST":
        if request.form.get("csrf_token") != session.get("csrf_token"):
            abort(400)

        content = (request.form.get("content") or "").strip()
        workout_id_raw = (request.form.get("workout_id") or "").strip()

        errors = []
        if not content:
            errors.append("Viestin sisältö vaaditaan.")
        if not workout_id_raw.isdigit():
            errors.append("Valitse treeni.")

        if errors:
            for e in errors:
                flash(e, "error")

            workouts = list_workouts_for_messages()
            messages = list_messages_full()

            return render_template(
                "messages.html",
                messages=messages,
                workouts=workouts,
            )

        workout_id = int(workout_id_raw)
        w = get_workout_owner(workout_id)
        if not w:
            abort(404)

        receiver_id = w["user_id"]

        try:
            add_message(session["user_id"], receiver_id, workout_id, content)
        except sqlite3.IntegrityError:
            abort(403)

        flash("Viesti lähetetty.", "success")
        return redirect(url_for("messages_route"))

    workouts = list_workouts_for_messages()
    messages = list_messages_full()

    return render_template(
        "messages.html",
        messages=messages,
        workouts=workouts,
    )

@app.route("/edit_message/<int:message_id>", methods=["GET", "POST"])
def edit_message(message_id):
    if not require_login():
        return redirect(url_for("login"))

    msg = get_message(message_id)
    if not msg:
        abort(404)
    if msg["sender_id"] != session["user_id"]:
        abort(403)

    if request.method == "POST":
        if request.form.get("csrf_token") != session.get("csrf_token"):
            abort(400)

        content = (request.form.get("content") or "").strip()

        if not content or len(content) > 1000:
            flash("Sisältö vaaditaan (max 1000 merkkiä).", "error")
            return render_template("edit_message.html", message=msg)

        update_message(message_id, content)

        flash("Viesti päivitetty.", "success")
        return redirect(url_for("messages_route"))

    return render_template("edit_message.html", message=msg)

@app.route("/delete_message/<int:message_id>", methods=["POST"])
def delete_message(message_id):
    if not require_login():
        return redirect(url_for("login"))

    if request.form.get("csrf_token") != session.get("csrf_token"):
        abort(400)

    msg = get_message(message_id)
    if not msg:
        abort(404)
    if msg["sender_id"] != session["user_id"]:
        abort(403)

    delete_message_by_id(message_id)

    flash("Viesti poistettu.", "success")
    return redirect(url_for("messages_route"))


@app.route("/search")
def search():
    if not require_login():
        return redirect(url_for("login"))

    q = (request.args.get("query") or "").strip()
    results = search_workouts(session["user_id"], q) if q else []

    return render_template("search.html", query=q, results=results)

@app.errorhandler(400)
def bad_request(_e):
    return render_template("400.html"), 400


@app.errorhandler(403)
def forbidden(_e):
    return render_template("403.html"), 403


@app.errorhandler(404)
def not_found(_e):
    return render_template("404.html"), 404


def require_login_or_403():
    if "user_id" not in session:
        abort(403)


def login_required_view(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        return fn(*args, **kwargs)

    return wrapper

@app.route("/profile")
def profile():
    """Ohjaa kirjautuneen käyttäjän omalle sivulle."""
    if "user_id" not in session:
        return redirect(url_for("login"))
    return redirect(url_for("user_page", user_id=session["user_id"]))

@app.route("/user/<int:user_id>")
def user_page(user_id):
    """Näytä käyttäjän treenit."""
    if not require_login():
        return redirect(url_for("login"))

    user = get_user_by_id(user_id)
    if user is None:
        abort(404)

    workouts = list_workouts(user_id)

    return render_template("user.html", user=user, workouts=workouts)

@app.route("/workout/<int:workout_id>/edit", methods=["GET", "POST"])
def edit_workout(workout_id):
    """Muokkaa olemassa olevaa treeniä."""
    if "user_id" not in session:
        return redirect(url_for("login"))

    workout = get_workout(workout_id)
    if workout is None:
        abort(404)
    if workout["user_id"] != session["user_id"]:
        abort(403)

    if request.method == "POST":
        if request.form.get("csrf_token") != session.get("csrf_token"):
            abort(400)

        date = (request.form.get("date") or "").strip()
        wtype = (request.form.get("type") or "").strip()
        duration_raw = (request.form.get("duration") or "").strip()
        description = (request.form.get("description") or "").strip()
        selected_ids = [int(x) for x in request.form.getlist("categories") if x.isdigit()]

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

        if errors:
            for e in errors:
                flash(e, "error")

            form = {
                "date": date,
                "type": wtype,
                "duration": duration_raw,
                "description": description,
            }

            return render_template(
                "workout_form.html",
                form=form,
                categories=list_categories(),
                selected=set(selected_ids),
            )

        update_workout(
            workout_id,
            session["user_id"],
            date,
            wtype,
            duration_val,
            description or None,
        )

        assign_categories_to_workout(workout_id, selected_ids)

        flash("Treeni päivitetty.", "success")
        return redirect(url_for("user_page", user_id=session["user_id"]))

    form = {
        "date": workout["date"],
        "type": workout["type"],
        "duration": workout["duration"],
        "description": workout["description"] or "",
    }
    current_cats = list_workout_categories(workout_id)
    selected_ids = {c["id"] for c in current_cats}

    return render_template(
        "workout_form.html",
        form=form,
        categories=list_categories(),
        selected=selected_ids,
    )

@app.route("/workout/<int:workout_id>/delete", methods=["POST"])
def delete_workout(workout_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    if request.form.get("csrf_token") != session.get("csrf_token"):
        abort(400)

    success = delete_workout_by_id(workout_id, session["user_id"])

    if not success:
        abort(403)

    flash("Treeni poistettu.", "success")
    return redirect(url_for("user_page", user_id=session["user_id"]))


if __name__ == "__main__":
    app.run(debug=True)
