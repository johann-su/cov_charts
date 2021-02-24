import re
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import style 
# import geoplot as gplt - installation not working properly
import argparse
from datetime import datetime, date
from collections.abc import Iterable
from vars import choices_state, choices_county

# Parser for arguments - only for easy testing
parser = argparse.ArgumentParser()
parser.add_argument('-c', '--chart', type=str,
                    choices=['line', 'bar', 'geo'],
                    help='The chart type to plot')
parser.add_argument('-r', '--range', type=str,
                    help='The date range for the Chart')
parser.add_argument('-s', '--state', type=str,
                    choices=choices_state,
                    help='The State to look at')
parser.add_argument('-cn', '--county', type=str,
                    choices=choices_county,
                    help='The county to look at')
parser.add_argument('--comparison', type=str, nargs=2,
                    help='What States or Counties to compare between')
parser.add_argument('-d', '--data', type=str, nargs=2,
                    choices=['cases', 'deaths', 'recovered', 'incidence'],
                    help='Show Infections or Incidence')

args = parser.parse_args()

# Read data
df = pd.read_csv('./data/covid_de.csv')
df['date'] = pd.to_datetime(df['date'])

demographics = pd.read_csv('./data/demographics_de.csv')

def filter_time(df, timeframe):
    # filter dataset for entries in timeframe
    td = pd.Timedelta(timeframe)
    return df[df['date'] >= datetime.now() - td]
    
def filter_country(df, state=None, county=None):
    # for Germany
    if state == None:
        tf = df.drop(['state', 'county'], axis=1)

        aggregation_functions = {'cases': 'sum', 'deaths': 'sum', 'recovered': 'sum'}

        tf = tf.groupby(tf['date']).aggregate(aggregation_functions)
        return tf

    # for a state
    elif county == None:
        tf = df.drop(['county'], axis=1)

        aggregation_functions = {'state': 'first', 'cases': 'sum', 'deaths': 'sum', 'recovered': 'sum'}

        tf = tf.loc[lambda df: df['state'] == state]

        tf = tf.groupby(tf['date']).aggregate(aggregation_functions)
        return tf

    # for a county
    else:
        aggregation_functions = {'state': 'first', 'county': 'first', 'cases': 'sum', 'deaths': 'sum', 'recovered': 'sum'}

        tf = df.loc[lambda df: df['state'] == state]
        tf = tf.loc[lambda df: df['county'] == county]

        tf = tf.groupby(tf['date']).aggregate(aggregation_functions)
        return tf

def filter_data(df, data):
    # return data where x is time (index) and y the data
    return (df.index, df[data])

# Function to plot different types of charts
def plot(data, chart, timeframe, state=None, county=None, comparison=None):
    # drop unwanted data
    df_prep = df.drop(['age_group', 'gender'], axis=1)

    # check if chart contains more than one plot
    if comparison != None:
        for string in comparison:
            # split string State.Country
            comps = re.split(r'\.(?!\d)', string)
            
            # set state and county according to input
            if len(comps) == 2:
                state = comps[0]
                county = comps[1]
            elif len(comps) == 1:
                state = comps[0]

            # TODO: Not DRY
            tf = filter_time(df_prep, timeframe=timeframe)
            zone = filter_country(tf, state, county)
            filter_data(zone, data)

            # String with the data in the chart for description
            content = ''

            # creating plots for every data-instance
            for data_type in data:
                x, y = filter_data(zone, data_type)

                # choosing the type of chart
                if chart == 'line':
                    plt.plot(x, y, label=data_type)
                elif chart == 'bar':
                    plt.bar(x, y, label=data_type)
                elif chart == 'geo':
                    raise Exception("Not Implemented")

                # add data type to content
                content = content + ' ' + data_type

    else:
        # TODO: Not DRY (l. 96) - create extra function
        tf = filter_time(df_prep, timeframe=timeframe)
        zone = filter_country(df, state, county)

        content = ''

        for data_type in data:
            x, y = filter_data(zone, data_type)

            plt.plot(x, y, label=data_type)

            content = content + ' ' + data_type

    # variable for the zone the chart looks at - for title
    if state == None:
        place = 'Germany'
    elif county == None:
        place = state
    else:
        place = county

    plt.title(f'{content} over the last {timeframe} in {place}')

    plt.style.use('seaborn-whitegrid')
    plt.legend()
    plt.savefig(f'./charts/{chart}_{place}_{datetime.now()}.png')
    plt.show()

if __name__ == '__main__':
    plot(data=args.data, chart=args.chart, timeframe=args.range, state=args.state, county=args.county, comparison=args.comparison)