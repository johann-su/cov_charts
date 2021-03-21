import logging

import sqlite3 as sql
from datetime import datetime
import time
import pandas as pd

LOGGER = logging.getLogger(__name__)

con = sql.connect('./database/covid.db')
c = con.cursor()

try:
    with con:
        c.execute("""CREATE TABLE covid_germany(
            date REAL,
            state TEXT,
            county TEXT,
            infections_new INTEGER,
            infections_acu INTEGER,
            deaths_new INTEGER,
            deaths_acu INTEGER,
            active_new INTEGER,
            active_acu INTEGER,
            incidence REAL
        )""")
except:
    pass

def insert_data(data):
    with con:
        c.execute("INSERT INTO covid_germany VALUES (:date, :state, :county, :infections_new, :infections_acu, :deaths_new, :deaths_acu, :active_new, :active_acu, :incidence)", {
            'date': data['date'],
            'state': data['state'],
            'county': data['county'],
            'infections_new': data['infections_new'],
            'infections_acu': data['infections_acu'],
            'deaths_new': data['deaths_new'],
            'deaths_acu': data['deaths_acu'],
            'active_new': data['active_new'],
            'active_acu': data['active_acu'],
            'incidence': data['incidence']
        })

def get_data(region, timeframe, data):
    c.execute("SELECT sum(:data) FROM covid_germany WHERE date >= :timeframe AND state=:region OR county=:region", {
        'region': region,
        'timeframe': time.mktime((datetime.now() - pd.Timedelta(timeframe)).timetuple()),
        'data': data
    })
    return c.fetchall()