from flask import Flask, render_template, redirect, url_for, request, session, flash, abort
from pathlib import Path
from db import (
    get_db, close_db, init_db,
    add_user, get_user, add_workout, list_workouts, add_message, list_messages
)

app = Flask(__name__)
app.config["SECRET_KEY"] = "dev-secret"
app.config["DATABASE"] = "instance/app.sqlite3"
Path("instance").mkdir(exist_ok=True)

@app.teardown_appcontext
def _close_db(exc):
    close_db()

@app.cli.command("init-db")
def init_db_command():
    init_db("schema.sql")
    print("Initialized the database.")

def require_login():
    if "user_id" not in session:
        flash("Please log in first.", "error")
        return False
    return True

@app.route("/")
def index():
    if not require_login():
        return redirect(url_for("login"))
    items = list_workouts(session["user_id"])
    return render_template("index.html", workouts=items)

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = (request.form.get("username") or "").strip()
        password = (request.form.get("password") or "").strip()
        if not username or not password:
            flash("Username and password required.", "error")
            return render_template("register.html")
        if get_user(username):
            flash("Username already exists.", "error")
            return render_template("register.html")
        add_user(username, password)
        flash("Account created. Please log in.", "success")
        return redirect(url_for("login"))
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = (request.form.get("username") or "").strip()
        password = (request.form.get("password") or "").strip()
        user = get_user(username)
        if user and user["password"] == password:
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            flash(f"Welcome, {user['username']}!", "success")
            return redirect(url_for("index"))
        flash("Invalid credentials.", "error")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out.", "success")
    return redirect(url_for("login"))

@app.route("/workout/add", methods=["GET", "POST"], endpoint="add_workout")
def add_workout_route():
    if not require_login():
        return redirect(url_for("login"))

    if request.method == "POST":
        date = (request.form.get("date") or "").strip()
        wtype = (request.form.get("type") or "").strip()
        duration_raw = (request.form.get("duration") or "").strip()
        description = (request.form.get("description") or "").strip()

        errors = []
        if not date:
            errors.append("Date is required.")
        if not wtype:
            errors.append("Type is required.")
        try:
            duration_val = int(duration_raw)
            if duration_val < 0:
                errors.append("Duration must be non-negative.")
        except ValueError:
            errors.append("Duration must be an integer.")

        if errors:
            for e in errors:
                flash(e, "error")
            form = {"date": date, "type": wtype, "duration": duration_raw, "description": description}
            return render_template("workout_form.html", form=form)

        add_workout(session["user_id"], date, wtype, duration_val, description or None)
        flash("Workout added.", "success")
        return redirect(url_for("index"))

    return render_template("workout_form.html", form={"date": "", "type": "", "duration": "", "description": ""})


@app.route("/messages", methods=["GET", "POST"])
def messages_route():
    if not require_login():
        return redirect(url_for("login"))

    if request.method == "POST":
        content = (request.form.get("content") or "").strip()
        workout_id = request.form.get("workout_id")

        if not content or not workout_id:
            flash("Message content and workout are required.", "error")
            msgs = list_messages(session["user_id"])
            workouts = list_workouts(session["user_id"])
            return render_template("messages.html", messages=msgs, workouts=workouts)

        add_message(session["user_id"], session["user_id"], int(workout_id), content)
        flash("Message sent.", "success")
        return redirect(url_for("messages_route"))

    msgs = list_messages(session["user_id"])
    workouts = list_workouts(session["user_id"])
    return render_template("messages.html", messages=msgs, workouts=workouts)


@app.route("/edit_message/<int:message_id>", methods=["GET", "POST"])
def edit_message(message_id):
    if not require_login():
        return redirect(url_for("login"))
    db = get_db()
    msg = db.execute("SELECT * FROM messages WHERE id = ?", (message_id,)).fetchone()
    if not msg:
        abort(404)
    if msg["sender_id"] != session["user_id"]:
        abort(403)
    if request.method == "POST":
        content = (request.form.get("content") or "").strip()
        if not content:
            flash("Content is required.", "error")
            return render_template("edit_message.html", message=msg)
        db.execute("UPDATE messages SET content = ? WHERE id = ?", (content, message_id))
        db.commit()
        flash("Message updated.", "success")
        return redirect(url_for("messages_route"))
    return render_template("edit_message.html", message=msg)

@app.route("/delete_message/<int:message_id>")
def delete_message(message_id):
    if not require_login():
        return redirect(url_for("login"))
    db = get_db()
    msg = db.execute("SELECT * FROM messages WHERE id = ?", (message_id,)).fetchone()
    if not msg:
        abort(404)
    if msg["sender_id"] != session["user_id"]:
        abort(403)
    db.execute("DELETE FROM messages WHERE id = ?", (message_id,))
    db.commit()
    flash("Message deleted.", "success")
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
    user = db.execute("SELECT id, username FROM users WHERE id = ?", (user_id,)).fetchone()
    if not user:
        abort(404)
    workouts = db.execute(
        "SELECT id, date, type, duration, description FROM workouts WHERE user_id = ? ORDER BY date DESC, id DESC",
        (user_id,),
    ).fetchall()
    return render_template("user.html", user=user, workouts=workouts)

if __name__ == "__main__":
    with app.app_context():
        Path("instance").mkdir(exist_ok=True)
        init_db("schema.sql")
    app.run(debug=True)

