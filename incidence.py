import pandas as pd
import numpy as np
from tqdm import tqdm

df = pd.read_csv('./data/covid_de.csv')
df['date'] = pd.to_datetime(df['date'])
demographics = pd.read_csv('./data/demographics_de.csv')

df['incidence'] = np.full([len(df)], np.nan)

for i, row in tqdm(df.iterrows()):
    if i<7:
        continue
    
    aggregation_functions = {'state': 'first', 'county': 'first', 'cases': 'sum', 'deaths': 'sum', 'recovered': 'sum'}

    state = df.loc[lambda df: df['state'] == row['state']]
    county = state.loc[lambda df: state['county'] == row['county']]
    
    county = county.groupby(county['date']).aggregate(aggregation_functions)
    county['date'] = county.index
    county = county.reset_index(drop=True)

    county = county.sort_values(by=['date'])

    seven_days = county.loc[i-6:i]
    added_cases = seven_days['cases'].sum()

    demographics = demographics.loc[lambda df: demographics['state'] == row['state']]

    aggregation_functions_dem = {'state': 'first', 'population': 'sum'}
    demographics = demographics.groupby(demographics['state']).aggregate(aggregation_functions_dem)

    population = demographics['population'].values[0]

    seven_day_incidence = added_cases / population * 100000
    
    df['incidence'][i] = seven_day_incidence

df.to_csv('./data/covid_de.csv')