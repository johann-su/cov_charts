import re
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
plt.switch_backend('Agg')
plt.style.use('seaborn-whitegrid')
from mpl_toolkits.axes_grid1 import make_axes_locatable
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
                content = content + ' ' + d
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
            tf = tf.loc[lambda tf: tf['county'] == self.county]

            tf = tf.groupby(tf['date']).aggregate(aggregation_functions)
            return tf

    def prepare_data(self, df, data):
        # drop unwanted data
        df_prep = df.drop(['age_group', 'gender'], axis=1)
        tf = self.filter_time(df_prep)
        zone = self.filter_location(tf)
        return (zone.index, zone[self.data])

    def plot(self):
        df = pd.read_csv('./data/covid_de.csv')
        df['date'] = pd.to_datetime(df['date'])
        
        # creating plots for every data-instance
        fig, ax = plt.subplots()
        for data_type in self.data:
            x, y = self.prepare_data(df, data_type)
            
            # choosing the type of chart
            if self.c_type == 'line':
                ax.plot(x, y[data_type], label=data_type)
            elif self.c_type == 'bar':
                ax.bar(x, y[data_type], label=data_type)
            elif self.c_type == 'geo':
                tf = df[df['date'] >= df['date'].max()]

                # drop unwanted data
                df_prep = tf.drop(['age_group', 'gender'], axis=1)

                # load required shape files
                if self.state == None:
                    geodf = gpd.read_file('./data/shapefiles_germany/shapefile_state')

                    df_prep = df_prep.drop('county', axis=1)

                    aggregation_functions = {'state': 'first', 'cases': 'sum', 'deaths': 'sum', 'recovered': 'sum'}
                    tf = df_prep.groupby(df_prep['state']).aggregate(aggregation_functions)

                    geodf['cases'] = list(tf['cases'])
                    geodf['deaths'] = list(tf['deaths'])
                elif self.county == None:
                    geodf = gpd.read_file('./data/shapefiles_germany/shapefile_county')

                    # filter for state
                    counties = df.loc[lambda df: df['state'] == self.state]
                    geodf = geodf.loc[geodf['GEN'].isin(counties['county'].unique())].reset_index(drop=True)

                    aggregation_functions = {'county': 'first', 'cases': 'sum', 'deaths': 'sum', 'recovered': 'sum'}
                    tf = counties.groupby(counties['county']).aggregate(aggregation_functions)

                    geodf['cases'] = list(tf['cases'])
                    geodf['deaths'] = list(tf['deaths'])

                fig, ax = plt.subplots(1, 1)

                # plot the shapefile
                geodf.plot(cmap='OrRd', column=data_type, ax=ax, legend=True)

                break

        if self.c_type != 'geo':
            plt.title(f'{self.content} over the last {self.timeframe} in {self.place}')
        else:
            plt.title(f'{self.content} in {self.place}')
        plt.tight_layout()
        if self.c_type != 'geo':
            plt.legend(loc=0, frameon=False)
        plt.savefig(self.image)
        # return the path to the image
        return self.image
