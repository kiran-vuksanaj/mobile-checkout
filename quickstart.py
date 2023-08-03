from square.client import Client
import json
import os
from datetime import datetime, date
import matplotlib.pyplot as plt
import numpy as np

client = Client(
    access_token=os.environ['SQUARE_ACCESS_TOKEN']
    )


def build_locations():
    result = client.locations.list_locations()    
    return [ location['id'] for location in result.body['locations'] ]

locations = build_locations()

def get_all_orders():
    search_body = {
        'location_ids': locations,
        'limit':500
        }
    orders = []
    result = client.orders.search_orders(body=search_body)
    while 'cursor' in result.body:
        orders += result.body['orders']
        search_body['cursor'] = result.body['cursor']
        print('searching again')
        result = client.orders.search_orders(body=search_body)
    orders += result.body['orders']
    print(json.dumps(orders[0],indent=2))
    return orders
        
orders_raw = get_all_orders()
# print(json.dumps(orders[-1],indent=2))

def reformat_order(order):
    out = {}
    out['time'] = datetime.strptime(order['closed_at'],'%Y-%m-%dT%H:%M:%S.%fZ')
    out['location'] = order['location_id']
    out['id'] = order['id']
    out['catalog_version'] = max( [ li['catalog_version'] for li in order['line_items'] ])
    out['items'] = {}
    for item in order['line_items']:
        if item['catalog_object_id'] not in out['items']:
            out['items'][ item['catalog_object_id'] ] = float(item['quantity'])
        else:
            out['items'][ item['catalog_object_id'] ] += float(item['quantity'])
    return out

orders = [reformat_order(order) for order in orders_raw]
print(json.dumps(orders,indent=2,default=str))

