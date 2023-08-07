from flask import Flask, render_template,request
from datetime import datetime, date
from squaredata import SquareData
import json

app = Flask(__name__)
sq = SquareData()

    
# FLASK ROUTES

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/daily")
def daily_report():
    sq.update_orders()
    today = datetime.now().date()
    return render_template("daily.html",
                           data=sq.date_report(today),
                           names=sq.name_map)

@app.route("/trends")
def trends_page():
    return render_template("trends.html")

@app.route("/inventory")
def inventory_page():
    return render_template("inventory.html")

@app.route("/bag")
def average_bag_page():
    return render_template("bag.html", names=sq.name_map)


@app.route("/visit")
def plan_visit_page():
    sq.update_catalog()
    return render_template("visit.html",
                           locations=sq.locations,
                           names=sq.name_map,
                           catalog=[item for item in sq.catalog if item['type']=='ITEM']
                           )

@app.route("/api/date")
def api_date_report():
    sq.update_orders()
    date = datetime.strptime( request.args['date'], '%Y-%m-%d' ).date()
    return {
        'data': sq.date_report(date),
        'names': sq.name_map
        }

@app.route("/api/qty")
def api_qty_data():
    sq.update_orders()
    x = [ date(2023,7,x) for x in range(1,31) ] + [ date(2023,8,x) for x in range(1,31) ]
    y = [ sq.qty_sold(dates=[date]) for date in x ]
    x_str = [ d.strftime("%Y-%m-%d") for d in x ]
    data = [ [x_str[i],y[i]] for i in range(len(x)) ]
    return {
        'success':True,
        'data': data
        }

@app.route("/api/totals")
def api_totals():
    start = datetime.strptime( request.args['start'], '%Y-%m-%d').date()
    end = datetime.strptime( request.args['end'], '%Y-%m-%d').date()
    fields = json.loads(request.args['fields'])

    def date_match(date):
        return date >= start and date <= end

    location_match = lambda x: True
    if 'location' in request.args:
        location_match = lambda x: x==request.args['location']
        
    data = sq.totals(date_match,fields,location_match)
    
    return {
        'success':True,
        'names':sq.name_map,
        'fields':data
    }

@app.route("/api/set_availability")
def api_set_availability():
    location = request.args['location']
    items = json.loads(request.args['items'])
    result = sq.set_available_items(location,items)
    return {
        'success': 'errors' not in result.body,
        'count': len(items),
        'names': sq.name_map
    }


@app.route("/api/add_item")
def api_add_item():
    name = request.args['name']
    result = sq.new_item(name)
    return {'success': 'errors' not in result.body}
    

@app.route("/api/bag")
def api_average_bag():
    sq.update_orders()
    location = request.args.get('location')
    return {
        'data': sq.average_bag(location),
        'names': sq.name_map
        }

