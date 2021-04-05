import logging
import time

import sqlite3 as sql
from datetime import datetime
import time
import pandas as pd

LOGGER = logging.getLogger(__name__)

con = sql.connect('./data/covid.db')
c = con.cursor()

with con:
    c.execute("""CREATE TABLE IF NOT EXISTS covid_germany(
        hash INTEGER UNIQUE,
        date REAL NOT NULL,
        region TEXT NOT NULL,
        cases INTEGER NOT NULL,
        cases_new INTEGER NOT NULL,
        deaths INTEGER,
        deaths_new INTEGER,
        recovered INTEGER,
        recovered_new INTEGER,
        active INTEGER,
        active_new INTEGER,
        incidence REAL
    )""")


def insert_data(data):
    with con:
        c.execute("""INSERT OR IGNORE INTO covid_germany VALUES (:hash, :date, :region, :cases, :cases_new, :deaths, :deaths_new, :recovered, :recovered_new, :active, :active_new, :incidence)
        """, {
            'hash': data['hash'],
            'date': data['date'],
            'region': data['region'],
            'cases': data['cases'],
            'cases_new': data['cases_new'],
            'deaths': data['deaths_new'],
            'deaths_new': data['deaths_new'],
            'recovered': data['recovered'],
            'recovered_new': data['deaths_new'],
            'active': data['active'],
            'active_new': data['active_new'],
            'incidence': data['incidence']
        })