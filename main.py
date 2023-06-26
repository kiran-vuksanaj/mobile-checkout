from flask import Flask, render_template,request
import sqlite3

app = Flask(__name__)

# DB OPERATIONS

def add_item(name):
    con = sqlite3.connect('inventory.db')
    cur = con.cursor()
    cur.execute('INSERT INTO items(name) VALUES(?)',(name,))
    con.commit()
    con.close()

def add_visit(name,date,items):
    con = sqlite3.connect("inventory.db")
    cur = con.cursor()
    cur.execute("INSERT INTO visits(name,date) VALUES(?, ?)",(name,date))
    v_id = cur.execute('SELECT last_insert_rowid()').fetchone()[0]
    
    for item in items:
        cur.execute("INSERT INTO visit_items(v_id,i_id) VALUES(?, ?)",(v_id,item))
    con.commit()
    con.close()

def list_inventory(visit_id=None):
    con = sqlite3.connect("inventory.db")
    cur = con.cursor()
    cmd = "SELECT i_id,name FROM items";
    if not visit_id is None:
        cmd += " WHERE i_id IN (SELECT i_id FROM visit_items WHERE v_id = {})".format(visit_id)
    print(cmd)
    res = cur.execute(cmd)
    return res.fetchall()

# FLASK ROUTES

@app.route("/")
def home():
    con = sqlite3.connect("inventory.db")
    cur = con.cursor()
    res = cur.execute("SELECT n FROM counter")
    n = res.fetchone()
    print(n)
    con.close()
    items = list_inventory()
    return render_template("home.html",n=n,items=items)

@app.route("/api/add_item")
def api_add_item():
    name = request.args.get('name')
    try:
        add_item(name)
        return "success"
    except:
        return "uh oh"
    
