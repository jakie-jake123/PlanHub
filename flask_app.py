from flask import Flask, redirect, render_template, request, url_for
from mysql.connector import pooling
from dotenv import load_dotenv
import os
import git
import hmac
import hashlib

load_dotenv()

# Load .env variables
DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_DATABASE")
}
W_SECRET = os.getenv("W_SECRET")

# Init flask app
app = Flask(__name__)
app.config["DEBUG"] = True

# Init db
pool = pooling.MySQLConnectionPool(pool_name="pool", pool_size=5, **DB_CONFIG)
def get_conn():
    return pool.get_connection()

# DB-Helper
def db_execute(sql, params=None, write=False):
    conn = get_conn()
    try:
        cur = conn.cursor(dictionary=not write)
        cur.execute(sql, params or ())
        if write:
            conn.commit()
            return None
        return cur.fetchall()
    finally:
        try:
            cur.close()
        except:
            pass
        conn.close()

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

@app.route("/", methods=["GET", "POST"])
def index():
    # GET
    if request.method == "GET":
        todos = db_execute("SELECT id, content, due FROM todos ORDER BY due")
        return render_template("main_page.html", todos=todos)

    # POST
    content = request.form["contents"]
    due = request.form["due_at"]
    db_execute("INSERT INTO todos (content, due) VALUES (%s, %s)", (content, due, ), True)
    return redirect(url_for("index"))

@app.post("/complete")
def complete():
    todo_id = request.form.get("id")
    db_execute("DELETE FROM todos WHERE id=%s", (todo_id,), True)
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run()
