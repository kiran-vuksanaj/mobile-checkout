from flask import Flask, render_template
import sqlite3

app = Flask(__name__)

@app.route("/")
def home():
    con = sqlite3.connect("inventory.db")
    cur = con.cursor()
    res = cur.execute("SELECT n FROM counter")
    n = res.fetchone()
    print(n)
    con.close()
    return render_template("home.html",n=n)

@app.route("/create")
def create():
    con = sqlite3.connect("inventory.db")
    cur = con.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS counter(n)")
    cur.execute("INSERT INTO counter VALUES(?)",(0,))
    con.commit()
    con.close()
    return "hi"

@app.route("/add")
def add():
    con = sqlite3.connect("inventory.db")
    cur = con.cursor()
    cur.execute("UPDATE counter SET n = n + 1")
    con.commit()
    con.close()
    return "hiho"

    
    
