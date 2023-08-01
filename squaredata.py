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
        self.locations = [ location['id'] for location in result.body['locations'] ]

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
        return out

    def update_orders(self):
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
        print('Orders Retreived')

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
                    out[ order['location'] ] = {}
                for item in order['items']:
                    if item not in out[ order['location'] ]:
                        out[ order['location'] ][item] = 0
                    out[ order['location'] ][item] += order['items'][item]
        return out



