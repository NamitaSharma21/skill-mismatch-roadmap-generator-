# ---------------------------
# Imports
# ---------------------------
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import mysql.connector
from dotenv import load_dotenv
import os
from openai import OpenAI
from pathlib import Path

# ---------------------------
# Load Environment Variables
# ---------------------------
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)

OPENAI_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_KEY:
    raise Exception("OpenAI API key not found! Check your .env file.")

client = OpenAI(api_key=OPENAI_KEY)

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "skillmismatch_db")

# ---------------------------
# Flask Setup
# ---------------------------
app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "my_secret_key_2129")

# ---------------------------
# Database Connection Function
# ---------------------------
def get_db():
    return mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        auth_plugin="mysql_native_password"
    )

# ---------------------------
# Routes
# ---------------------------

# Home
@app.route("/")
def home():
    return render_template("index.html", title="Home")

# Signup
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        conn = get_db()
        cur = conn.cursor()
        cur.execute(
            "SELECT * FROM users WHERE email=%s", (email,)
        )
        if cur.fetchone():
            cur.close()
            conn.close()
            return "Email already registered!", 400

        cur.execute(
            "INSERT INTO users(name, email, password) VALUES (%s, %s, %s)",
            (name, email, password)
        )
        conn.commit()
        cur.close()
        conn.close()

        return redirect(url_for("login"))

    return render_template("signup.html", title="Signup")

# Login
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        conn = get_db()
        cur = conn.cursor(dictionary=True)
        cur.execute(
            "SELECT * FROM users WHERE email=%s AND password=%s",
            (email, password)
        )
        user = cur.fetchone()
        cur.close()
        conn.close()

        if user:
            session["user"] = user
            return redirect(url_for("dashboard"))
        else:
            return "Invalid Credentials", 401

    return render_template("login.html", title="Login")

# Dashboard
@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect(url_for("login"))
    return render_template("dashboard.html", user=session["user"], title="Dashboard")

# Profile
@app.route("/profile")
def profile():
    if "user" not in session:
        return redirect(url_for("login"))
    return render_template("profile.html", user=session["user"], title="Profile")

# Logout
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))

# ---------------------------
# Roadmap Generator (OpenAI)
# ---------------------------
@app.post("/roadmap")
def roadmap():
    data = request.json
    goal = data.get("goal")
    industry = data.get("industry")

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a career mentor."},
            {"role": "user",
             "content": f"Create a detailed roadmap for achieving {goal} in {industry}. Provide steps, skills, timeline, and tools."}
        ]
    )

    roadmap_text = response.choices[0].message.content
    return jsonify({"roadmap": roadmap_text})

# ---------------------------
# AI Chatbot
# ---------------------------
@app.post("/chat")
def chat():
    data = request.json
    msg = data.get("message")

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": msg}]
    )

    reply = response.choices[0].message.content
    return jsonify({"reply": reply})

# ---------------------------
# Run App
# ---------------------------
if __name__ == "__main__":
    app.run(debug=True)
