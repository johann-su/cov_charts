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

from covid_charts import vars

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

    def get_data(self):
        with sql.connect('./data/covid.db') as con:
            c = con.cursor()
            c.execute("SELECT cases, date FROM covid_germany WHERE date >= :timeframe AND region=:region ORDER BY date DESC", {
                'region': self.region if self.region == None else self.region,
                'timeframe': time.mktime((datetime.now() - pd.Timedelta(self.timeframe)).timetuple()),
                'data': self.data[0]
            })
            data = c.fetchall()

        x = [datetime.fromtimestamp(i[1]) for i in data]
        y = [i[0] for i in data]
       
        return (x, y)

    def plot(self):
        # creating plots for every data-instance
        fig, ax = plt.subplots()
        for data_type in self.data:
            x, y = self.get_data()

            # choosing the type of chart
            if self.c_type == 'line':
                ax.plot(x, y, label=data_type)
            elif self.c_type == 'bar':
                ax.bar(x, y, label=data_type)
            elif self.c_type == 'geo':
                with sql.connect('./data/covid.db') as con:
                    c = con.cursor()
                    c.execute("SELECT sum(cases), sum(deaths), avg(incidence) FROM covid_germany WHERE date >= :timeframe AND region=:region", {
                        'region': self.region if self.region == None else self.region,
                        'timeframe': time.mktime((datetime.now() - pd.Timedelta(self.timeframe)).timetuple()),
                        # 'data': self.data[0]
                    })
                    data = c.fetchall()[0]

                cases = data[0]
                deaths = data[1]
                incidence = data[2]

                # load required shape files
                if self.region == 'Bundesrepublik Deutschland':
                    geodf = gpd.read_file('./data/shapefiles_germany/shapefile_state')

                    geodf['cases'] = cases
                    geodf['deaths'] = deaths
                    geodf['incidence'] = incidence

                elif self.region in vars.choices_state:
                    geodf = gpd.read_file('./data/shapefiles_germany/shapefile_county')

                    # TODO: add state to counties
                    geodf = geodf.loc[geodf['state'] == region].reset_index(drop=True)

                    cases = data[0]
                    deaths = data[1]
                    incidence = data[2]

                else:
                    raise Exception("Plotting a Chart for a single state is not possible.")

                fig, ax = plt.subplots(1, 1)

                # plot the shapefile
                geodf.plot(cmap='OrRd', column=data_type, ax=ax, legend=True)

                break

        if self.c_type != 'geo':
            plt.title(f'{self.content} over the last {self.timeframe} in {self.region}')
        else:
            plt.title(f'{self.content} in {self.region}')
        plt.tight_layout()
        if self.c_type != 'geo':
            plt.legend(loc=0, frameon=False)
        plt.savefig(self.image)
        # return the path to the image
        return self.image
