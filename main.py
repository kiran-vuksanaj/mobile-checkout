from flask import Flask, render_template,request
import sqlite3
from datetime import datetime, date
from quickstart import qty_sold, orders, date_report, name_map


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

def del_item(i_id):
    con = sqlite3.connect("inventory.db")
    cur = con.cursor()
    cur.execute("DELETE FROM items WHERE i_id=?",(i_id,))
    cur.execute("DELETE FROM visit_items WHERE i_id=?",(i_id,))
    con.commit()
    con.close()

    
# FLASK ROUTES

@app.route("/")
def home():
    items = list_inventory()
    return render_template("home.html",items=items)

@app.route("/daily")
def daily_report():
    today = datetime.now().date()
    return render_template("daily.html",
                           data=date_report(today),
                           names=name_map)

@app.route("/api/date")
def api_date_report():
    date = datetime.strptime( request.args['date'], '%Y-%m-%d' ).date()
    return {
        'data': date_report(date),
        'names': name_map
        }

@app.route("/api/qty")
def api_qty_data():
    x = [ date(2023,7,x) for x in range(12,31) ]
    y = [ qty_sold(orders, dates=[date]) for date in x ]
    x_str = [ d.strftime("%Y-%m-%d") for d in x ]
    data = [ [x_str[i],y[i]] for i in range(len(x)) ]
    return {
        'success':True,
        'data': data
        }

@app.route("/api/items")
def api_list_items():
    return {'items': list_inventory()}

@app.route("/api/add_item")
def api_add_item():
    name = request.args.get('name')
    try:
        add_item(name)
        return "success"
    except:
        return "uh oh"
    
@app.route("/api/del_item")
def api_del_item():
    i_id = request.args.get('i_id')
    del_item(int(i_id))
    return "success"
