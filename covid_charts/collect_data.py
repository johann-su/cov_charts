import logging
import os
import time

import requests
import json
import pandas as pd
from datetime import datetime

from data.sql_lite import insert_data
from hashlib import sha1

from tqdm import tqdm

LOGGER = logging.getLogger(__name__)

rki_lookup = pd.read_csv('./data/rki_lookup.csv')

def convert_id_to_text(data):
    data['AdmUnitId'] = rki_lookup.loc[rki_lookup['AdmUnitId'] ==
                                       data['AdmUnitId']]['Name'].values[0].replace('LK ', '').replace('SK ', '')
    return data

def fetch_data(historical=False):
    # getting historical data from the rki
    current_data = requests.get('https://services7.arcgis.com/mOBPykOjAyBO2ZKk/arcgis/rest/services/rki_key_data_hubv/FeatureServer/0/query?where=1%3D1&outFields=*&outSR=4326&f=json').text

    data_status = requests.get('https://services7.arcgis.com/mOBPykOjAyBO2ZKk/arcgis/rest/services/rki_data_status_v/FeatureServer/0/query?where=1%3D1&outFields=Datum,Timestamp_txt,Status&outSR=4326&f=json').text

    current_data = json.loads(current_data)
    data_status = json.loads(data_status)

    # TODO: find better way to fetch historical data (API restriction to 1000 items)
    if historical == True:
        i = 0
        max_records = json.loads(requests.get('https://services7.arcgis.com/mOBPykOjAyBO2ZKk/arcgis/rest/services/rki_history_hubv/FeatureServer/0/query?where=1%3D1&f=json&outFields=*&returnCountOnly=true').text)['count']
        historical_data = None

        while i <= max_records:
            historical_data_txt = requests.get(f'https://services7.arcgis.com/mOBPykOjAyBO2ZKk/arcgis/rest/services/rki_history_hubv/FeatureServer/0/query?where=1%3D1&f=json&outFields=*&resultOffset={i}').text

            if i == 0:
                historical_data = json.loads(historical_data_txt)
            else:
                historical_data_list = json.loads(historical_data_txt)['features']
                historical_data['features'] = historical_data['features'] + historical_data_list

            i += 1000

        return (data_status, current_data, historical_data)
    else:
        return (data_status, current_data)

def prepare_data(data, status):
    df = pd.DataFrame([i['attributes'] for i in data['features']])

    df = df.apply(convert_id_to_text, axis=1)
    # hash, date, region, cases, cases_new, deaths, deaths_new, recovered, recovered_new, incidence
    if df.loc[0].get('Datum') == None:
        df = df.drop(columns=['BundeslandId', 'AnzFall7T', 'ObjectId'])

        df.rename(columns={
            'AdmUnitId': 'region', 
            'AnzFall': 'cases', 
            'AnzTodesfall': 'deaths', 
            'AnzFallNeu': 'cases_new', 
            'AnzTodesfallNeu': 'deaths_new',
            'AnzGenesen': 'recovered', 
            'AnzGenesenNeu': 'recovered_new', 
            'AnzAktiv': 'active', 
            'AnzAktivNeu': 'active_new', 
            'Inz7T': 'incidence'
        }, inplace=True)

        df['date'] = status['Datum'] / 1000
    else:
        df.drop(columns=['BundeslandId', 'AnzFallVortag',
                'AnzFallErkrankung', 'AnzFallMeldung', 'ObjectId'])

        df.rename(columns={
            'AdmUnitId': 'region',
            'Datum': 'date',
            'AnzFallNeu': 'cases_new',
            'KumFall': 'cases'
        }, inplace=True)

        df['date'] = df['date'].apply(lambda x: x / 1000)

        df['deaths'], df['deaths_new'], df['recovered'], df['recovered_new'], df['active'], df['active_new'], df['incidence'] = [None for i in range(7)]

    df['hash'] = df.apply(
        lambda x: sha1(f"{x['date']}{x['region']}".encode('utf-8')).hexdigest(), axis=1)

    return df

def collect(historical=False):
    data = fetch_data(historical=historical)

    status = data[0]['features'][0]['attributes']

    if status['Status'] != 'OK':
        raise Exception(f"The Data from the RKI-API returned: {status['Status']}")

    for item in data[1:]:
        df = prepare_data(item, status)

        df.apply(insert_data, axis=1)
