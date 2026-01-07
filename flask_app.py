
@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    # GET
    if request.method == "GET":
        todos = db_read(
            "SELECT id, content, due FROM todos WHERE user_id=%s ORDER BY due",
            (current_user.id,)
        )
        return render_template("main_page.html", todos=todos)

    # POST
    content = request.form["contents"]
    due = request.form["due_at"]
    db_write(
        "INSERT INTO todos (user_id, content, due) VALUES (%s, %s, %s)",
        (current_user.id, content, due)
    )
    return redirect(url_for("index"))


    # ──────────────
    # Termine aus DB holen
    # ──────────────
    todos = db_read(
        """SELECT id, title, description, due, is_exam, silent_mode
           FROM todos
           WHERE user_id=%s
           ORDER BY due""",
        (current_user.id,)
    )

    # ──────────────
    # HTML für Termine bauen
    # ──────────────
    termine_html = ""

    for t in todos:
        termine_html += f"""
        <div>
            <strong>{t.title}</strong><br>
            {t.description or ""}<br>
            Datum: {t.due.strftime('%d.%m.%Y %H:%M')}<br>
        """

        if t.is_exam:
            termine_html += "<p>Dieser Termin ist als Prüfung markiert.</p>"

        if t.silent_mode:
            termine_html += "<p>Stummschalt-Modus ist aktiv.</p>"

        termine_html += f"""
            <a href="/silent/{t.id}">Stumm umschalten</a>

            <form action="/exam/{t.id}" method="POST">
                <input type="number" name="countdown_start"
                       placeholder="Countdown (Minuten vorher)">
                <button type="submit">Als Prüfung markieren</button>
            </form>

            <form action="/complete" method="POST">
                <input type="hidden" name="id" value="{t.id}">
                <button type="submit">Termin löschen</button>
            </form>
            <hr>
        </div>
        """

    # HTML-Datei laden und Platzhalter ersetzen
    with open("templates/main_page.html", "r", encoding="utf-8") as f:
        html = f.read()

    html = html.replace(
        "<!-- TERMINE_WERDEN_HIER_EINGEFUEGT -->",
        termine_html
    )

    return html
