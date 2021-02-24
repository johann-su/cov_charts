import pandas as pd
import matplotlib.pyplot as plt
# import geoplot as gplt
import argparse
from datetime import datetime
from collections.abc import Iterable

# Parser for arguments
parser = argparse.ArgumentParser()
parser.add_argument('-d', '--data', type=str,
                    help='What data to show in the Chart')
parser.add_argument('-c', '--chart', type=str,
                    help='The chart type to plot')
parser.add_argument('-r', '--range', type=str,
                    help='The date range for the Chart')
parser.add_argument('--state', type=str, default="Sachsen",
                    help='The State to look at')
parser.add_argument('--county', type=str, required=False,
                    help='The county to look at')

args = parser.parse_args()

# Read data
df = pd.read_csv('./data/covid_de.csv')
df['date'] = pd.to_datetime(df['date'])
df = df.sort_values(by='date', ascending=False)

demographics = pd.read_csv('./data/demographics_de.csv')

# Function to plot different types of charts
def plot(data, chart, range, state):

    # days in specified timeframe
    timedelta = pd.Timedelta(range).days

    aggregation_functions = {'state': 'first', 'cases': 'sum', 'deaths': 'sum', 'recovered': 'sum'}
    
    # drop useless columns and filter for state
    tf = df.drop(['county', 'age_group', 'gender'], axis=1).loc[lambda df: df['state'] == args.state]
    # combine values for dates
    tf = tf.groupby(tf['date']).aggregate(aggregation_functions)

    # make index numerical
    tf['date'] = tf.index
    tf = tf.reset_index(drop=True)

    if data == 'infections':
        # filter for the time specified in timeframe
        tf = tf.loc[:timedelta]
    elif data == 'incidence':
        # calculate 7 day incidence
        tf = tf.loc[:6]

        dm = demographics.drop(['gender', 'age_group'], axis=1).loc[lambda df: demographics['state'] == args.state]
        dm = dm.groupby(dm['state']).aggregate({'state': 'first', 'population': 'sum'})

        dm['date'] = dm.index
        dm = dm.reset_index(drop=True)

        incidence = float(tf.aggregate({'cases': 'sum'})['cases'] / dm['population'] * 100000)

    # plot the Graph
    if chart == 'line':
        if data == 'infections':
            x = tf['date']
            y_inf = tf['cases']
            y_death = tf['deaths']

            plt.plot(x, y_inf, label="Infections", color="b")
            plt.plot(x, y_death, label="Deaths", color="r")

            plt.title(f'Infections / Deaths over the last {range}')

        elif data == 'incidence':
            # TODO: Better way to visulize incidence
           print(f"The seven day incidence for {state} is {incidence}")

    elif chart == 'bar':
        if data == 'infections':
            x = tf['date']
            y_inf = tf['cases']
            y_death = tf['deaths']

            plt.bar(x, y_inf, label="Infections", color="b")
            plt.bar(x, y_death, label="Deaths", color="r")

            plt.title(f'Infections / Deaths over the last {range}')

        elif data == 'incidence':
            # TODO: Better way to visulize incidence
           print(f"The seven day incidence for {state} is {incidence}")

    elif chart == 'map':
        if data == 'infections':

    plt.legend()
    plt.savefig(f'./charts/{chart}_{state}_{range}_{datetime.now()}.png')
    # plt.show()

plot(args.data, args.chart, args.range, args.state)
