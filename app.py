from flask import (
    Flask,
    render_template,
    redirect,
    url_for,
    request,
    session,
    flash,
    abort,
    g,
    get_flashed_messages,
)
from pathlib import Path
import secrets
from functools import wraps

from db.connection import get_db, close_db
from db.users import add_user, get_user, get_user_by_id, verify_password
from db.workouts import add_workout, list_workouts, get_workout
from db.messages import (
    add_message,
    list_messages,
    get_message_for_edit,
    update_message_content,
)
from db.categories import (
    list_categories,
    assign_categories_to_workout,
    list_workout_categories,
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
    workouts = [
        dict(w) | {"categories": list_workout_categories(w["id"])} for w in workouts
    ]
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
        selected_ids = [
            int(x) for x in request.form.getlist("categories") if x.isdigit()
        ]

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
            wid = add_workout(
                session["user_id"], date, wtype, duration_val, description or None
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
def workouts_all():
    if not require_login():
        return redirect(url_for("login"))
    db = get_db()
    rows = db.execute(
        """SELECT w.id, w.date, w.type, w.duration, w.description, u.username
           FROM workouts w
           JOIN users u ON u.id = w.user_id
           ORDER BY w.date DESC, w.id DESC"""
    ).fetchall()
    items = [
        {
            "id": r[0],
            "date": r[1],
            "type": r[2],
            "duration": r[3],
            "description": r[4],
            "username": r[5],
        }
        for r in rows
    ]
    return render_template("workouts_all.html", workouts=items)


@app.route("/messages", methods=["GET", "POST"], endpoint="messages_route")
def messages_route():
    if not require_login():
        return redirect(url_for("login"))

    db = get_db()

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
            wrows = db.execute(
                """SELECT w.id, w.date, w.type, u.username
                   FROM workouts w
                   JOIN users u ON u.id = w.user_id
                   ORDER BY w.date DESC, w.id DESC"""
            ).fetchall()
            workouts = [
                {"id": r[0], "date": r[1], "type": r[2], "username": r[3]}
                for r in wrows
            ]

            mrows = db.execute(
                """SELECT m.id, m.content, m.created_at,
                          s.username, r.username, w.id, w.type, w.date
                   FROM messages m
                   JOIN users s ON s.id = m.sender_id
                   JOIN users r ON r.id = m.receiver_id
                   JOIN workouts w ON w.id = m.workout_id
                   ORDER BY m.created_at DESC, m.id DESC"""
            ).fetchall()
            messages = [
                {
                    "id": x[0],
                    "content": x[1],
                    "created_at": x[2],
                    "sender": x[3],
                    "receiver": x[4],
                    "workout_id": x[5],
                    "workout_type": x[6],
                    "workout_date": x[7],
                }
                for x in mrows
            ]

            return render_template(
                "messages.html", messages=messages, workouts=workouts
            )

        workout_id = int(workout_id_raw)
        w = db.execute(
            "SELECT id, user_id FROM workouts WHERE id = ?", (workout_id,)
        ).fetchone()
        if not w:
            abort(404)

        receiver_id = w["user_id"]

        try:
            add_message(session["user_id"], receiver_id, workout_id, content)
        except sqlite3.IntegrityError:
            abort(403)

        flash("Viesti lähetetty.", "success")
        return redirect(url_for("messages_route"))

    wrows = db.execute(
        """SELECT w.id, w.date, w.type, u.username
           FROM workouts w
           JOIN users u ON u.id = w.user_id
           ORDER BY w.date DESC, w.id DESC"""
    ).fetchall()
    workouts = [
        {"id": r[0], "date": r[1], "type": r[2], "username": r[3]} for r in wrows
    ]

    mrows = db.execute(
        """SELECT m.id, m.content, m.created_at,
                  s.username, r.username, w.id, w.type, w.date
           FROM messages m
           JOIN users s ON s.id = m.sender_id
           JOIN users r ON r.id = m.receiver_id
           JOIN workouts w ON w.id = m.workout_id
           ORDER BY m.created_at DESC, m.id DESC"""
    ).fetchall()
    messages = [
        {
            "id": x[0],
            "content": x[1],
            "created_at": x[2],
            "sender": x[3],
            "receiver": x[4],
            "workout_id": x[5],
            "workout_type": x[6],
            "workout_date": x[7],
        }
        for x in mrows
    ]

    return render_template("messages.html", messages=messages, workouts=workouts)


@app.route("/edit_message/<int:message_id>", methods=["GET", "POST"])
def edit_message(message_id):
    if not require_login():
        return redirect(url_for("login"))

    db = get_db()
    msg = db.execute(
        "SELECT id, sender_id, content FROM messages WHERE id = ?", (message_id,)
    ).fetchone()
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

        db.execute(
            "UPDATE messages SET content = ? WHERE id = ?", (content, message_id)
        )
        db.commit()
        flash("Viesti päivitetty.", "success")
        return redirect(url_for("messages_route"))

    return render_template("edit_message.html", message=msg)


@app.route("/delete_message/<int:message_id>", methods=["POST"])
def delete_message(message_id):
    if not require_login():
        return redirect(url_for("login"))
    if request.form.get("csrf_token") != session.get("csrf_token"):
        abort(400)

    db = get_db()
    msg = db.execute(
        "SELECT id, sender_id FROM messages WHERE id = ?", (message_id,)
    ).fetchone()
    if not msg:
        abort(404)
    if msg["sender_id"] != session["user_id"]:
        abort(403)

    db.execute("DELETE FROM messages WHERE id = ?", (message_id,))
    db.commit()
    flash("Viesti poistettu.", "success")
    return redirect(url_for("messages_route"))


@app.route("/search")
def search():
    if not require_login():
        return redirect(url_for("login"))
    q = (request.args.get("query") or "").strip()
    results = []
    if q:
        db = get_db()
        results = db.execute(
            """
            SELECT id, date, type, duration, description
            FROM workouts
            WHERE user_id = ?
              AND (type LIKE ? OR description LIKE ? OR date LIKE ?)
            ORDER BY date DESC, id DESC
            """,
            (session["user_id"], f"%{q}%", f"%{q}%", f"%{q}%"),
        ).fetchall()
    return render_template("search.html", query=q, results=results)


@app.route("/user/<int:user_id>")
def show_user(user_id):
    if not require_login():
        return redirect(url_for("login"))

    db = get_db()

    user = db.execute(
        "SELECT id, username FROM users WHERE id = ?", (user_id,)
    ).fetchone()
    if not user:
        abort(404)

    stats_row = db.execute(
        "SELECT COUNT(*), COALESCE(SUM(duration), 0) FROM workouts WHERE user_id = ?",
        (user_id,),
    ).fetchone()
    if not stats_row:
        stats_row = (0, 0)
    stats = {"total_count": stats_row[0] or 0, "total_minutes": stats_row[1] or 0}

    rows = db.execute(
        """SELECT type, COUNT(*), COALESCE(SUM(duration), 0)
           FROM workouts
           WHERE user_id = ?
           GROUP BY type
           ORDER BY COUNT(*) DESC, type ASC""",
        (user_id,),
    ).fetchall()
    by_type = [{"type": r[0], "count": r[1], "minutes": r[2]} for r in rows]

    workouts = db.execute(
        """SELECT id, date, type, duration, description
           FROM workouts
           WHERE user_id = ?
           ORDER BY date DESC, id DESC""",
        (user_id,),
    ).fetchall()

    return render_template(
        "user.html", user=user, workouts=workouts, stats=stats, by_type=by_type
    )


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


if __name__ == "__main__":
    with app.app_context():
        Path("instance").mkdir(exist_ok=True)
        init_db("schema.sql")
    app.run(debug=True)
