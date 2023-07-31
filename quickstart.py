from square.client import Client
import json
import os
from datetime import datetime, date
import matplotlib.pyplot as plt
import numpy as np

client = Client(
    access_token=os.environ['SQUARE_ACCESS_TOKEN']
    )


name_map = {
    'locations': {},
    'items': {}
    }

result = client.locations.list_locations()

if result.is_success():
    for location in result.body['locations']:
        print(f"{location['id']}: {location['name']}")
        name_map['locations'][ location['id'] ] = location['name']
elif result.is_error():
    for error in result.errors:
        print(error['category'])
        print(error['code'])
        print(error['detail'])
locations = [ location['id'] for location in result.body['locations'] ]
print(locations)

   
result = client.catalog.list_catalog()
item_names = {}
for catalog_object in result.body['objects']:
    if catalog_object['type'] == "ITEM":
        # print( catalog_object['id'],catalog_object['item_data']['name'] )
        # print(json.dumps(catalog_object,indent=2))
        item_names[ catalog_object['item_data']['variations'][0]['id'] ] = catalog_object['item_data']['name']
print(item_names)

name_map['items'] = item_names


"""
result = client.catalog.upsert_catalog_object(
    body = {
        "idempotency_key": "d191c61a-447f-4d1e-9bf6-874dd6b0ca82",
        "object": {
            "type": "ITEM",
            "id": "#dfs",
            "item_data": {
                "name": "triangle",
                "variations": [
                    {
                        "type": "ITEM_VARIATION",
                        "id": "#aa",
                        "item_variation_data": {
                            "name": "Regular",
                            "pricing_type": "FIXED_PRICING",
                            "price_money": {
                                "amount": 0,
                                "currency": "USD"
                            }
                        }
                    }
                ]
            }
        }
    }
)
"""
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
    return orders
        
orders_raw = get_all_orders()
# print(json.dumps(orders[-1],indent=2))

def reformat_order(order):
    out = {}
    out['time'] = datetime.strptime(order['closed_at'],'%Y-%m-%dT%H:%M:%S.%fZ')
    out['location'] = order['location_id']
    out['id'] = order['id']
    out['items'] = {}
    for item in order['line_items']:
        if item['catalog_object_id'] not in out['items']:
            out['items'][ item['catalog_object_id'] ] = float(item['quantity'])
        else:
            out['items'][ item['catalog_object_id'] ] += float(item['quantity'])
    return out

orders = [reformat_order(order) for order in orders_raw]
# print(json.dumps(orders,indent=2,default=str))

def qty_sold(orders,dates=None,items=None,locations=None):
    def conditions_match(order):
        return (
            (locations is None or order['location'] in locations) and
            (dates is None or order['time'].date() in dates)
            )
    def qty(order):
        if not conditions_match(order):
            return 0
        out = 0
        # print(order)
        for item in order['items']:
            if (items is None or item in items):
                out += order['items'][item]
        return out
    return sum( [qty(order) for order in orders] )

def date_report(date):
    out = {}
    for order in orders:
        if order['time'].date() == date:
            if order['location'] not in out:
                out[ order['location'] ] = {}
            for item in order['items']:
                if item not in out[ order['location'] ]:
                    out[ order['location'] ][item] = 0
                out[ order['location'] ][item] += order['items'][item]
    return out


print(len(orders))
print(qty_sold(orders))

# items_in_orders = set()
# bellpepper_total = 0
# for order in orders:
#     for item in order['items']:
#         items_in_orders.add(item)
#         if item == 'FCGUYJHM2NV4JG2LYYZSI642':
#             bellpepper_total += order['items'][item]
#             print(order['id'])
# print(bellpepper_total)
# print(items_in_orders,len(items_in_orders))

print(qty_sold(orders, dates=[ date(2023,7,5) ], items=[ 'FCGUYJHM2NV4JG2LYYZSI642' ]))

# catalog_ids = set()
# milk_ids = set()
# for order in orders:
#     for item in order['line_items']:
#         catalog_ids.add(item['catalog_version'])
#         if item['name'] == 'Bell Pepper':
#             milk_ids.add(item['catalog_object_id'])
# print(catalog_ids)
# print(milk_ids)
    
plt.style.use('_mpl-gallery')
x = [ date(2023,7,x) for x in range(1,31) ]
y = [ qty_sold(orders, dates=[date]) for date in x ]
fig,ax = plt.subplots()
ax.step(x,y,linewidth=2.5)

# plt.savefig('plot.png')
