from square.client import Client
import json
import os
from datetime import datetime, date
import matplotlib.pyplot as plt
import numpy as np

class SquareData:
    name_map = {
        'locations': {},
        'items': {}
    }
    locations = []
    orders = []

    client = Client(
        access_token=os.environ['SQUARE_ACCESS_TOKEN']
    )


    def __init__(self):
        self.build_locations()
        self.build_item_names()
        self.update_orders()
        print('Square connection initialized')

    def build_locations(self):
        result = self.client.locations.list_locations()

        if result.is_success():
            for location in result.body['locations']:
                # print(f"{location['id']}: {location['name']}")
                self.name_map['locations'][ location['id'] ] = location['name']
        elif result.is_error():
            for error in result.errors:
                print(error['category'])
                print(error['code'])
                print(error['detail'])
        self.locations = [ location['id'] for location in result.body['locations']]

    def build_item_names(self):
        result = self.client.catalog.list_catalog()
        item_names = {}
        for catalog_object in result.body['objects']:
            if catalog_object['type'] == "ITEM":
                # print( catalog_object['id'],catalog_object['item_data']['name'] )
                # print(json.dumps(catalog_object,indent=2))
                item_names[ catalog_object['item_data']['variations'][0]['id'] ] = catalog_object['item_data']['name']        
        self.name_map['items'] = item_names

    def reformat_order(self,order):
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

            # add name to name_map if its not alr there
            # eg deleted items
            if item['catalog_object_id'] not in self.name_map['items']:
                self.name_map['items'][item['catalog_object_id']] = item['name']
        return out

    def update_orders(self):

        # get the IDs of recent updates
        search_body = {
            'location_ids': self.locations,
            'limit': 100,
            'return_entries': True,
            'query': {
                'filter': {
                    'state_filter': {
                        'states': ['COMPLETED']
                        }
                    }, 
                'sort': {
                    'sort_field': 'CLOSED_AT',
                    'sort_order': 'DESC'
                }
            }
        }
        keep_going = True
        existing_ids = [ order['id'] for order in self.orders ]
        batch_ids = []
        while keep_going:
            result = self.client.orders.search_orders(body=search_body)
        
            new_ids = [ entry['order_id'] for entry in result.body['order_entries'] if entry['order_id'] not in existing_ids ]
            batch_ids += new_ids
            keep_going = ( 'cursor' in result.body ) and ( len(new_ids) == len(result.body['order_entries']))
            if 'cursor' in result.body:
                search_body['cursor'] = result.body['cursor']
                
        for i in range(0,len(batch_ids),100):
            retrieve_body = {
                'order_ids': batch_ids[i: min(i+100,len(batch_ids))]
            }
            result = self.client.orders.batch_retrieve_orders(body=retrieve_body)
            self.orders += [ self.reformat_order(order) for order in result.body['orders'] ]
        print('Order list updated')
        return
    
    def update_orders_all(self):
        # deprecated--not in use
        search_body = {
            'location_ids': self.locations,
            'limit':500
        }
        orders_raw = []
        result = self.client.orders.search_orders(body=search_body)
        while 'cursor' in result.body:
            orders_raw += result.body['orders']
            search_body['cursor'] = result.body['cursor']
            print('searching again')
            result = self.client.orders.search_orders(body=search_body)
        orders_raw += result.body['orders']
        self.orders = [ self.reformat_order(order) for order in orders_raw ]
        print(self.orders[-1])
        print('Orders Retreived')

    def field_value(self,order,field):
        if field == "visits":
            return 1
        elif field == "allitems":
            return sum(order['items'].values())
        elif field in order['items']:
            return order['items'][field]
        else:
            return 0
        
    def totals(self,date_match,fields,location_match):
        
        def conditions_match(order):
            return date_match(order['time'].date()) and location_match(order['location'])
        out = {}
        for field in fields:
            out[field] = sum( [self.field_value(order,field) for order in self.orders if conditions_match(order)] )
        return out
        
    def qty_sold(self,dates=None,items=None,locations=None):
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
        return sum( [qty(order) for order in self.orders] )

    def date_report(self,date):
        out = {}
        for order in self.orders:
            if order['time'].date() == date:
                if order['location'] not in out:
                    out[ order['location'] ] = {'items':{},'visits':0}
                out[ order['location'] ]['visits'] += 1
                for item in order['items']:
                    if item not in out[ order['location'] ]['items']:
                        out[ order['location'] ]['items'][item] = 0
                    out[ order['location'] ]['items'][item] += order['items'][item]
        return out

    def average_bag(self,location):
        item_qty = {}
        visit_total = 0
        for order in self.orders:
            if order['location'] == location:
                visit_total += 1
                for item in order['items']:
                    if item not in item_qty:
                        item_qty[item] = 0
                    item_qty[item] += order['items'][item]
        averages = []
        for item in item_qty:
            averages.append( (item, item_qty[item] / visit_total) )
        averages.sort(key = lambda x: x[1])
        averages.reverse()
        return averages



