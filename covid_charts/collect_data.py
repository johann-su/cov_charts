import logging
import os
import time

import requests
import json
import pandas as pd
from datetime import datetime

from database.sql_lite import insert_data

LOGGER = logging.getLogger(__name__)

# getting historical data from the rki
current_data = requests.get('https://services7.arcgis.com/mOBPykOjAyBO2ZKk/arcgis/rest/services/rki_key_data_hubv/FeatureServer/0/query?where=1%3D1&outFields=AdmUnitId,BundeslandId,AnzFall,AnzTodesfall,AnzFallNeu,AnzTodesfallNeu,AnzGenesen,AnzGenesenNeu,AnzAktiv,AnzAktivNeu,Inz7T&outSR=4326&f=json').text

historical_data = requests.get('https://services7.arcgis.com/mOBPykOjAyBO2ZKk/arcgis/rest/services/rki_history_hubv/FeatureServer/0/query?where=1%3D1&outFields=AdmUnitId,BundeslandId,Datum,AnzFallNeu,AnzFallVortag,AnzFallErkrankung,AnzFallMeldung,KumFall&outSR=4326&f=json').text

data_status = requests.get('https://services7.arcgis.com/mOBPykOjAyBO2ZKk/arcgis/rest/services/rki_data_status_v/FeatureServer/0/query?where=1%3D1&outFields=Datum,Timestamp_txt,Status&outSR=4326&f=json').text

current_data = json.loads(current_data)
historical_data = json.loads(historical_data)
data_status = json.loads(data_status)

data_status_df = pd.DataFrame(columns=['Datum', 'Timestamp_txt', 'Status'])

for i in data_status['features']:
    data_status_df = data_status_df.append(i['attributes'], ignore_index=True)

if data_status_df['Status'].values[0] != 'OK':
    raise Exception(f"Data from RKI is somehow not Ok! - status: {data_status_df['Status']}")

# constructiing a pandas dataframe with historical data
current_df = pd.DataFrame(columns=['AdmUnitId', 'BundeslandId', 'AnzFall', 'AnzTodesfall', 'AnzFallNeu', 'AnzTodesfallNeu', 'AnzFall7T', 'AnzGenesen', 'AnzGenesenNeu', 'AnzAktiv', 'AnzAktivNeu', 'Inz7T'])

for i in current_data['features']:
    current_df = current_df.append(i['attributes'], ignore_index=True)

# replacing 'AdmUnitId' and 'BundeslandId' with names
rki_lookup = pd.read_csv('./data/rki_lookup.csv')

for i, row in current_df.iterrows():
    county = rki_lookup.loc[rki_lookup['AdmUnitId'] == row[0]]['Name'].values[0]
    state = rki_lookup.loc[rki_lookup['AdmUnitId'] == row[1]]['Name'].values[0]
    current_df.loc[i, 'AdmUnitId'] = county
    current_df.loc[i, 'BundeslandId'] = state
    
    data = {
        'date': time.mktime(datetime.strptime(data_status_df['Timestamp_txt'].values[0][:17], "%d.%m.%Y, %H:%M").timetuple()),
        'state': row['BundeslandId'],
        'county': row['AdmUnitId'],
        'infections_new': row['AnzFallNeu'],
        'infections_acu': row['AnzFall'],
        'deaths_new': row['AnzTodesfallNeu'],
        'deaths_acu': row['AnzTodesfall'],
        'active_new': row['AnzAktivNeu'],
        'active_acu': row['AnzAktiv'],
        'incidence': row['Inz7T']
    }
    insert_data(data)

df_historical = pd.DataFrame(columns=['AdmUnitId', 'BundeslandId', 'Datum', 'AnzFallNeu', 'AnzFallVortag', 'AnzFallErkrankung', 'AnzFallMeldung', 'KumFall'])

for i in historical_data['features']:
    df_historical = df_historical.append(i['attributes'], ignore_index=True)

for i, row in df_historical.iterrows():
    county = rki_lookup.loc[rki_lookup['AdmUnitId'] == row[0]]['Name'].values[0]
    state = rki_lookup.loc[rki_lookup['AdmUnitId'] == row[1]]['Name'].values[0]
    df_historical.loc[i, 'AdmUnitId'] = county
    df_historical.loc[i, 'BundeslandId'] = state
    
    data = {
        'date': row['Datum'],
        'state': row['BundeslandId'],
        'county': row['AdmUnitId'],
        'infections_new': row['AnzFallNeu'],
        'infections_acu': row['KumFall'],
        'deaths_new': None,
        'deaths_acu': None,
        'active_new': None,
        'active_acu': None,
        'incidence': None
    }
    insert_data(data)