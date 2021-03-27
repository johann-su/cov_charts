import logging
import os
import time

import requests
import json
import pandas as pd
from datetime import datetime

from hashlib import sha1

from data.sql_lite import insert_data

LOGGER = logging.getLogger(__name__)

def convert_id_to_text(df):
    rki_lookup = pd.read_csv('./data/rki_lookup.csv')

    for i, row in df.iterrows():
        county = rki_lookup.loc[rki_lookup['AdmUnitId'] == row['AdmUnitId']]['Name'].values[0]
        state = rki_lookup.loc[rki_lookup['AdmUnitId'] == row['BundeslandId']]['Name'].values[0]
        df.loc[i, 'AdmUnitId'] = county
        df.loc[i, 'BundeslandId'] = state

    return df

def fetch_data(historical=False):
    # getting historical data from the rki
    current_data = requests.get('https://services7.arcgis.com/mOBPykOjAyBO2ZKk/arcgis/rest/services/rki_key_data_hubv/FeatureServer/0/query?where=1%3D1&outFields=AdmUnitId,BundeslandId,AnzFall,AnzTodesfall,AnzFallNeu,AnzTodesfallNeu,AnzGenesen,AnzGenesenNeu,AnzAktiv,AnzAktivNeu,Inz7T&outSR=4326&f=json').text

    data_status = requests.get('https://services7.arcgis.com/mOBPykOjAyBO2ZKk/arcgis/rest/services/rki_data_status_v/FeatureServer/0/query?where=1%3D1&outFields=Datum,Timestamp_txt,Status&outSR=4326&f=json').text

    current_data = json.loads(current_data)
    data_status = json.loads(data_status)

    if historical == True:
        historical_data = requests.get('https://services7.arcgis.com/mOBPykOjAyBO2ZKk/arcgis/rest/services/rki_history_hubv/FeatureServer/0/query?where=1%3D1&outFields=AdmUnitId,BundeslandId,Datum,AnzFallNeu,AnzFallVortag,AnzFallErkrankung,AnzFallMeldung,KumFall&outSR=4326&f=json').text

        historical_data = json.loads(historical_data)

        return (data_status, current_data, historical_data)
    else:
        return (data_status, current_data)

def prepare_data(data):
    df = pd.DataFrame()

    for i in data['features']:
        df = df.append(i['attributes'], ignore_index=True)

    df = convert_id_to_text(df)

    return df

def collect():
    data = fetch_data(historical=True)

    status = data[0]['features'][0]['attributes']

    if status['Status'] != 'OK':
        raise Exception(f"The data from the RKI has some kind of fault. Api-Message: {status['Status']}")

    for item in data[1:]:
        df = prepare_data(item)

        # TODO: Check if dataframe is not empty
        for i, row in df.iterrows():
            data = {
                'date': row.get('Datum') / 1000 if row.get('Datum') != None else status['Datum'] / 1000,
                'region': row.get('AdmUnitId'),
                'cases': row.get('AnzFall') if row.get('AnzFall') != None else row.get('KumFall'),
                'cases_new': row.get('AnzFallNeu'),
                'deaths': row.get('AnzTodesfall'),
                'deaths_new': row.get('AnzTodesfallNeu'),
                'recovered': row.get('AnzGenesen'),
                'recovered_new': row.get('AnzGenesenNeu'),
                'incidence': row.get('Inz7T')
            }

            unique_key = sha1(str(data.values()).encode('utf-8')).hexdigest() 
            data.update({'hash': unique_key})
            
            insert_data(data)