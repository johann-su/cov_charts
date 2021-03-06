import re
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from matplotlib import style 
import argparse
from datetime import datetime, date
from collections.abc import Iterable
from vars import choices_state, choices_county
import types

class Chart:
    # The timeframe for the chart ('1W', '1D')
    timeframe=''
    # The chart type to plot ('line', 'bar')
    c_type=''
    # The State to look at ('Sachsen')
    state=''
    # The county to look at ('SK Dresden')
    county=''
    # What States or Counties to compare between (['Sachsen.SK Dresden', 'Bayern'])
    comparison=''
    # Show cases, deaths or Incidence ('cases', ['deaths', incidence'])
    data=''
    # returns the path to the image with the chart
    image=''

    # returns the place that the chart shows
    @property
    def place(self):
        if self.state == None:
            return 'Germany'
        elif self.county == None:
            return self.state
        else:
            return self.county

    @property
    def content(self):
        if isinstance(self.data, list):
            content=''
            for d in self.data:
                content = content + ', ' + data_type
            return content
        else:
            return self.data

    def __init__(self, data, timeframe, c_type, state=None, county=None, comparison=None):
        self.timeframe = timeframe
        self.c_type = c_type
        self.state = state
        self.county = county
        self.comparison = comparison
        self.data = data
        self.image = f"./charts/{c_type}_{self.place}_{datetime.now()}.png"

    def __repr__(self):
        return f"{self.chart} of {self.place} in {timeframe}"

    # filter data for values in timeframe
    def filter_time(self, df):
        td = pd.Timedelta(self.timeframe)
        tf = df[df['date'] >= datetime.now() - td]
        return tf

    # filter data for values in location
    def filter_location(self, df):
        # for Germany
        if self.state == None:
            tf = df.drop(['state', 'county'], axis=1)

            aggregation_functions = {'cases': 'sum', 'deaths': 'sum', 'recovered': 'sum'}

            tf = tf.groupby(tf['date']).aggregate(aggregation_functions)
            return tf

        # for a state
        elif self.county == None:
            tf = df.drop(['county'], axis=1)

            aggregation_functions = {'state': 'first', 'cases': 'sum', 'deaths': 'sum', 'recovered': 'sum'}

            tf = tf.loc[lambda df: df['state'] == self.state]

            tf = tf.groupby(tf['date']).aggregate(aggregation_functions)
            return tf

        # for a county
        else:
            aggregation_functions = {'state': 'first', 'county': 'first', 'cases': 'sum', 'deaths': 'sum', 'recovered': 'sum'}

            tf = df.loc[lambda df: df['state'] == self.state]
            tf = tf.loc[lambda df: df['county'] == self.county]

            tf = tf.groupby(tf['date']).aggregate(aggregation_functions)
            return tf

    def prepare_data(self, df, data):
        # drop unwanted data
        df_prep = df.drop(['age_group', 'gender'], axis=1)
        tf = self.filter_time(df_prep)
        zone = self.filter_location(tf)
        # TODO: test for multiple data
        return (zone.index, zone[self.data])

    def plot(self):
        df = pd.read_csv('./data/covid_de.csv')
        df['date'] = pd.to_datetime(df['date'])
        # creating plots for every data-instance
        for data_type in self.data:
            x, y = self.prepare_data(df, data_type)

            # choosing the type of chart
            if self.c_type == 'line':
                plt.plot(x, y, label=data_type)
            elif self.c_type == 'bar':
                plt.bar(x, y, label=data_type)
            elif self.c_type == 'geo':
                # load required shape files
                if self.state == None:
                    geodf = gpd.read_file('./data/shapefiles_germany/vg2500_bld.shp')
                elif self.county == None:
                    geodf = gpd.read_file('./data/shapefiles_germany/vg2500_krs.shp')

                # plot the shapefile
                # TODO: Add color for states, counties
                geodf.plot()

            plt.title(f'{self.content} over the last {self.timeframe} in {self.place}')

        plt.style.use('seaborn-whitegrid')
        plt.savefig(self.image)
        # return the path to the image
        return self.image
