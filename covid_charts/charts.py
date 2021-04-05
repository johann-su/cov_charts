import logging

import pandas as pd
import geopandas as gpd

import matplotlib.pyplot as plt
plt.switch_backend('Agg')
plt.style.use('seaborn-whitegrid')

from datetime import datetime

import sqlite3 as sql
from data import sql_lite
import time

from covid_charts.exceptions import DataException

from covid_charts.vars import ARS, choices_state, choices_county

LOGGER = logging.getLogger(__name__)

class Chart:
    # The timeframe for the chart ('1W', '1D')
    timeframe=''
    # The chart type to plot ('line', 'bar')
    c_type=''
    # The Region to look at ('Sachsen')
    region=''
    # What States or Counties to compare between (['Sachsen.SK Dresden', 'Bayern'])
    comparison=''
    # Show cases, deaths or Incidence ('cases', ['deaths', incidence'])
    data=''
    # returns the path to the image with the chart
    image=''

    @property
    def content(self):
        if isinstance(self.data, list):
            content=''
            for d in self.data:
                content = content + ' ' + d
            return content
        else:
            return self.data

    def __init__(self, data, timeframe, c_type, region='Sachsen', comparison=None):
        self.timeframe = timeframe
        self.c_type = c_type
        self.region = region
        self.comparison = comparison
        self.data = data
        self.image = f"./charts/{c_type}_{self.region}_{datetime.now()}.png"

    def __repr__(self):
        return f"{self.chart} of {self.region} in {timeframe}"

    def get_data(self, data_type):
        if self.c_type != 'geo':
            with sql.connect('./data/covid.db') as con:
                c = con.cursor()
                c.execute("SELECT cases, deaths, incidence, date FROM covid_germany WHERE date >= :timeframe AND region=:region ORDER BY date DESC", {
                    'region': self.region if self.region == None else self.region,
                    'timeframe': time.mktime((datetime.now() - pd.Timedelta(self.timeframe)).timetuple())
                })
                query_data = c.fetchall()

            x = [datetime.fromtimestamp(i[3]) for i in query_data]

            index = {
                'cases': 0,
                'deaths': 1,
                'incidence': 2
            }

            y = [i[index[self.data[0]]] for i in query_data]
            
            if None in y:
                raise DataException("There are not enough values for timeframe")

            return (x, y)
        else:
            regions = ()
            if self.region in choices_county:
                regions = f"('{self.region}')"
            elif self.region != 'Bundesrepublik Deutschland':
                regions = tuple(ARS[self.region])
            elif self.region in choices_state:
                regions = tuple(choices_state)

            with sql.connect('./data/covid.db') as con:
                c = con.cursor()
                # BAD PRACTICE: SUSEPTABLE TO SQL INJECTION (string formating)
                c.execute(f"""SELECT cases, deaths, incidence, region 
                FROM covid_germany 
                WHERE region IN {regions} 
                AND date=(SELECT MAX(date) from covid_germany WHERE region IN {regions})""")
                query_data = c.fetchall()

            # load required shape files
            if self.region == 'Bundesrepublik Deutschland':
                geodf = gpd.read_file('./data/shapefiles_germany/shapefile_state')

                for i in query_data:
                    row = geodf.loc[geodf['GEN'] == i[3]]
                    geodf.loc[row.index, 'cases'] = i[0]
                    geodf.loc[row.index, 'deaths'] = i[1]
                    geodf.loc[row.index, 'incidence'] = i[2]

            elif self.region in choices_state:
                geodf = gpd.read_file('./data/shapefiles_germany/shapefile_county')

                geodf = geodf.loc[geodf['state'] == self.region].reset_index(drop=True)

                for i in query_data:
                    row = geodf.loc[geodf['GEN'] == i[3]]
                    geodf.loc[row.index, 'cases'] = i[0]
                    geodf.loc[row.index, 'deaths'] = i[1]
                    geodf.loc[row.index, 'incidence'] = i[2]
    
            else:
                geodf = gpd.read_file(
                     './data/shapefiles_germany/shapefile_county')

                geodf = geodf.loc[geodf['GEN'] == self.region].reset_index(drop=True)

                geodf.loc[0, 'cases'] = query_data[0][0]
                geodf.loc[0, 'deaths'] = query_data[0][1]
                geodf.loc[0, 'incidence'] = query_data[0][2]

            print(geodf)
            return geodf

    def plot(self):
        # TODO: Fix subplots for geo chart
        # creating plots for every data-instance
        fig, ax = plt.subplots()
        for i, data_type in enumerate(self.data):
            # choosing the type of chart
            if self.c_type == 'line':
                x, y = self.get_data(data_type=i)
                ax.plot(x, y, label=data_type)
            elif self.c_type == 'bar':
                x, y = self.get_data(data_type=i)
                ax.bar(x, y, label=data_type)
            elif self.c_type == 'geo':
                fig, ax = plt.subplots()

                geodf = self.get_data(data_type=i)
                # plot the shapefile
                geodf.plot(edgecolor='black', cmap='OrRd', column=data_type, ax=ax, legend=True, missing_kwds={"color": "lightgrey", "edgecolor": "black", "hatch": "///", "label": "Missing values"})

        if self.c_type != 'geo':
            plt.title(f'{self.content} over the last {self.timeframe} in {self.region}')
            plt.legend(loc=0, frameon=False)
        else:
            plt.axis('off')
            plt.title(f'{self.content} in {self.region}')
        plt.tight_layout()
        plt.savefig(self.image)
        # return the path to the image
        return self.image
