import logging
import os

import requests
import json
import pandas as pd
from datetime import datetime

LOGGER = logging.getLogger(__name__)

# load current dataframe
df = pd.read_csv('./data/covid_de.csv')

# load new data from rki
rki_data = requests.get('https://services7.arcgis.com/mOBPykOjAyBO2ZKk/arcgis/rest/services/rki_altersgruppen_hubv/FeatureServer/0/query?where=1%3D1&outFields=AdmUnitId,BundeslandId,Altersgruppe,AnzFallM,AnzFallW,AnzTodesfallM,AnzTodesfallW,ObjectId&outSR=4326&f=json').text

rki_data = json.loads(rki_data)
date = datetime.now().date()

rki_data_df = pd.DataFrame(columns=['AdmUnitId', 'BundeslandId', 'Altersgruppe', 'AnzFallM', 'AnzFallW', 'AnzTodesfallM', 'AnzTodesfallW', 'ObjectId'])

for i in rki_data['features']:
    rki_data_df = rki_data_df.append(i['attributes'], ignore_index=True)

# loading lookup table for RKI AdmUnitIds
if not os.path.isfile('./data/rki_lookup.csv'):
    rki_lookup = requests.get('https://services7.arcgis.com/mOBPykOjAyBO2ZKk/ArcGIS/rest/services/rki_admunit_v/FeatureServer/0/query?where=1%3D1&outFields=AdmUnitId,Name&f=json').text

    rki_lookup = json.loads(rki_lookup)

    rki_lookup_df = pd.DataFrame(columns=['AdmUnitId', 'Name'])

    for i in rki_lookup['features']:
        rki_lookup_df = rki_lookup_df.append(i['attributes'], ignore_index=True)

    rki_lookup_df.to_csv('./data/rki_lookup.csv', index=False)
else:
    rki_lookup_df = pd.read_csv('./data/rki_lookup.csv')

for i, row in rki_data_df.iterrows():
    # print(rki_lookup_df.loc[rki_lookup_df['AdmUnitId'] == rki_data_df['AdmUnitId'][i]]['Name'].values[0])

    F = {
        'state': rki_lookup_df.loc[rki_lookup_df['AdmUnitId'] == rki_data_df['BundeslandId'][i]]['Name'].values[0],
        'county': rki_lookup_df.loc[rki_lookup_df['AdmUnitId'] == rki_data_df['AdmUnitId'][i]]['Name'].values[0],
        'age_group': rki_data_df['Altersgruppe'][i].replace('A', ''),
        'gender': 'F',
        'date': date,
        'cases': rki_data_df['AnzFallW'][i],
        'deaths': rki_data_df['AnzTodesfallW'][i],
        'recovered': 0,
        # 'incidence': incidence()
    }
    M = {
        'state': rki_lookup_df.loc[rki_lookup_df['AdmUnitId'] == rki_data_df['BundeslandId'][i]]['Name'].values[0],
        'county': rki_lookup_df.loc[rki_lookup_df['AdmUnitId'] == rki_data_df['AdmUnitId'][i]]['Name'].values[0],
        'age_group': rki_data_df['Altersgruppe'][i].replace('A', ''),
        'gender': 'M',
        'date': date,
        'cases': rki_data_df['AnzFallM'][i],
        'deaths': rki_data_df['AnzTodesfallM'][i],
        'recovered': 0,
        # 'incidence': incidence()
    }

    df = df.append([F,M], ignore_index=True)

df.to_csv('./data/covid_de.csv')