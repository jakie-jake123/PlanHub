from flask import Flask, redirect, render_template, request, url_for
from dotenv import load_dotenv
import os
import git
import hmac
import hashlib
from db import db_read, db_write
from auth import login_manager, authenticate, register_user
from flask_login import login_user, logout_user, login_required, current_user
import logging

from datetime import datetime

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

# Load .env variables
load_dotenv()
W_SECRET = os.getenv("W_SECRET")

# Init flask app
app = Flask(__name__)
app.config["DEBUG"] = True
app.secret_key = "supersecret"

# Init auth
login_manager.init_app(app)
login_manager.login_view = "login"

# DON'T CHANGE
def is_valid_signature(x_hub_signature, data, private_key):
    hash_algorithm, github_signature = x_hub_signature.split('=', 1)
    algorithm = hashlib.__dict__.get(hash_algorithm)
    encoded_key = bytes(private_key, 'latin-1')
    mac = hmac.new(encoded_key, msg=data, digestmod=algorithm)
    return hmac.compare_digest(mac.hexdigest(), github_signature)

# DON'T CHANGE
@app.post('/update_server')
def webhook():
    x_hub_signature = request.headers.get('X-Hub-Signature')
    if is_valid_signature(x_hub_signature, request.data, W_SECRET):
        repo = git.Repo('./mysite')
        origin = repo.remotes.origin
        origin.pull()
        return 'Updated PythonAnywhere successfully', 200
    return 'Unathorized', 401



@app.route("/login", methods=["GET", "POST"])
def login():
    error = None

    if request.method == "POST":
        user = authenticate(
            request.form["username"],
            request.form["password"]
        )

        if user:
            login_user(user)
            return redirect(url_for("index"))

        error = "Benutzername oder Passwort ist falsch."

    return render_template(
        "auth.html",
        title="In dein Konto einloggen",
        action=url_for("login"),
        button_label="Einloggen",
        error=error,
        footer_text="Noch kein Konto?",
        footer_link_url=url_for("register"),
        footer_link_label="Registrieren"
    )


@app.route("/register", methods=["GET", "POST"])
def register():
    error = None

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        ok = register_user(username, password)
        if ok:
            return redirect(url_for("login"))

        error = "Benutzername existiert bereits."

    return render_template(
        "auth.html",
        title="Neues Konto erstellen",
        action=url_for("register"),
        button_label="Registrieren",
        error=error,
        footer_text="Du hast bereits ein Konto?",
        footer_link_url=url_for("login"),
        footer_link_label="Einloggen"
    )

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))





#usecase 1 oder so : Termin kreieren


@app.route("/", methods=["GET", "POST"])
@login_required
def index():

    # POST → Termin erstellen
    if request.method == "POST":
        title = request.form["title"]
        date = request.form["date"]
        time = request.form["time"]

        db_write(
            """
            INSERT INTO termins (user_id, title, date, time)
            VALUES (%s, %s, %s, %s)
            """,
            (current_user.id, title, date, time)
        )
        return redirect(url_for("index"))

    # GET → Termine laden
    termins = db_read(
        """
        SELECT id, title, date, time, is_exam
        FROM termins
        WHERE user_id=%s
        ORDER BY date, time
        """,
        (current_user.id,)
    )

    countdown = None
    now = datetime.now()

    for t in termins:
        # time → string für HTML
        total_seconds = t["time"].total_seconds()
        hours = int(total_seconds // 3600)
        minutes = int((total_seconds % 3600) // 60)
        t["time_str"] = f"{hours:02d}:{minutes:02d}"

        # Countdown nur für Prüfungen
        if t["is_exam"]:
            termin_datetime = datetime.combine(t["date"], datetime.min.time())
            termin_datetime = termin_datetime.replace(
                hour=hours,
                minute=minutes
            )

            diff = termin_datetime - now
            if diff.total_seconds() > 0:
                days = diff.days
                hrs = diff.seconds // 3600
                countdown = f"{t['title']} in {days} Tagen {hrs} Stunden"

    return render_template(
        "main_page.html",
        termins=termins,
        countdown=countdown
    )







"""
# App routes
@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    # GET
    if request.method == "GET":
        todos = db_read("SELECT id, content, due FROM todos WHERE user_id=%s ORDER BY due", (current_user.id,))
        return render_template("main_page.html", todos=todos)

    # POST
    content = request.form["contents"]
    due = request.form["due_at"]
    db_write("INSERT INTO todos (user_id, content, due) VALUES (%s, %s, %s)", (current_user.id, content, due, ))
    return redirect(url_for("index"))
"""

# Usecase 2 Termin löschen

@app.post("/delete_termin")
@login_required
def delete_termin():
    termin_id = request.form.get("id")
    db_write(
        "DELETE FROM termins WHERE user_id=%s AND id=%s",
        (current_user.id, termin_id)
    )
    return redirect(url_for("index"))


"""
@app.post("/complete")
@login_required
def complete():
    todo_id = request.form.get("id")
    db_write("DELETE FROM todos WHERE user_id=%s AND id=%s", (current_user.id, todo_id,))
    return redirect(url_for("index"))
"""

# termin bearbeiten

@app.route("/edit_termin/<int:id>", methods=["GET", "POST"])
@login_required
def edit_termin(id):
    # Termin laden
    termin = db_read(
        "SELECT * FROM termins WHERE id=%s AND user_id=%s",
        (id, current_user.id),
        single=True
    )

    if not termin:
        return "Termin nicht gefunden", 404

    # POST → speichern
    if request.method == "POST":
        title = request.form["title"]
        date = request.form["date"]
        time = request.form["time"]

        if not title or not date or not time:
            return "Alle Felder sind Pflicht", 400

        db_write(
            """
            UPDATE termins
            SET title=%s, date=%s, time=%s
            WHERE id=%s AND user_id=%s
            """,
            (title, date, time, id, current_user.id)
        )

        return redirect(url_for("index"))

    # GET → Formular anzeigen
    return render_template("edit_termin.html", termin=termin)


# countdown oder so

@app.post("/mark_exam")
@login_required
def mark_exam():
    termin_id = request.form.get("id")

    # Toggle is_exam
    db_write(
        """
        UPDATE termins
        SET is_exam = NOT is_exam
        WHERE id=%s AND user_id=%s
        """,
        (termin_id, current_user.id)
    )

    return redirect(url_for("index"))

@app.route("/calendar")
@login_required
def calendar():
    termins = db_read(
        """
        SELECT id, title, date, time, is_exam
        FROM termins
        WHERE user_id = %s
        """,
        (current_user.id,)
    )

    events = []

    for t in termins:
        # time (timedelta) → HH:MM
        total_seconds = t["time"].total_seconds()
        hours = int(total_seconds // 3600)
        minutes = int((total_seconds % 3600) // 60)
        time_str = f"{hours:02d}:{minutes:02d}"

        start = f"{t['date']}T{time_str}"

        events.append({
            "id": t["id"],
            "title": ("📝 " if t["is_exam"] else "") + t["title"],
            "start": start
        })

    return render_template("calendar.html", events=events)









if __name__ == "__main__":
    app.run()
