import pandas as pd
import matplotlib.pyplot as plt
# import geoplot as gplt
import argparse
from datetime import datetime, date
from collections.abc import Iterable

# Parser for arguments
parser = argparse.ArgumentParser()
parser.add_argument('-d', '--data', type=str,
                    help='What data to show in the Chart')
parser.add_argument('-c', '--chart', type=str,
                    help='The chart type to plot')
parser.add_argument('-r', '--range', type=str,
                    help='The date range for the Chart')
parser.add_argument('--state', type=str, required=False,
                    help='The State to look at')
parser.add_argument('--county', type=str, required=False,
                    help='The county to look at')

args = parser.parse_args()

# Read data
df = pd.read_csv('./data/covid_de.csv')
df['date'] = pd.to_datetime(df['date'])

demographics = pd.read_csv('./data/demographics_de.csv')

# Function to plot different types of charts
def plot(data, chart, range, state):
    # drop unwanted data
    tf = df.drop(['age_group', 'gender'], axis=1)

    # filter dataset for entries in range
    td = pd.Timedelta(range)
    tf = tf[tf['date'] > datetime.now() - td]

    # for Germany
    if state == None:
        tf = tf.drop(['state', 'county'], axis=1)

        aggregation_functions = {'cases': 'sum', 'deaths': 'sum', 'recovered': 'sum'}

        tf = tf.groupby(tf['date']).aggregate(aggregation_functions)

    # for a state
    elif county == None:
        print(tf)
        tf = tf.drop(['county'], axis=1)

        aggregation_functions = {'state': 'first', 'cases': 'sum', 'deaths': 'sum', 'recovered': 'sum'}

        tf = tf.loc[lambda df: df['state'] == state]
        tf = tf.groupby(tf['date']).aggregate(aggregation_functions)

    # for a county
    else:
        aggregation_functions = {'state': 'first', 'county': 'first', 'cases': 'sum', 'deaths': 'sum', 'recovered': 'sum'}
        tf = tf.loc[lambda df: df['state'] == state]
        tf = tf.loc[lambda df: df['county'] == county]
        tf = tf.groupby(tf['date']).aggregate(aggregation_functions)

    # plot the Graph
    x = tf['date']
    y_inf = tf['cases']
    y_death = tf['deaths']

    plt.plot(x, y_inf, label="Infections", color="b")
    plt.plot(x, y_death, label="Deaths", color="r")

    plt.title(f'Infections / Deaths over the last {range}')

    plt.legend()
    plt.savefig(f'./charts/{chart}_{state}_{range}_{datetime.now()}.png')
    plt.show()

plot(args.data, args.chart, args.range, args.state)
