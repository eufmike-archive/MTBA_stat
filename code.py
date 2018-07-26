# %%
# Dependencies
import os, sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt 
import regex
from datetime import datetime as dt

# %%
# load files
path = '/Users/michaelshih/Documents/code/personal_project/MTBA_stat'
subfolder = 'resources'
filename = 'Facebook Insights Data Export - Midwest Taiwanese Biotechnology Association - MTBA - 2018-07-25.csv'
filepath = os.path.join(path, subfolder, filename)

data = pd.read_csv(filepath, header=0, skiprows=[1])
data = pd.DataFrame(data)
data.head(5)

# %%
columnname = list(data.columns.values)
print(columnname)

# %%
# function
def citydatareshaper(data, keyword):
    targetcol = list(filter(lambda x: regex.match(keyword, x), columnname))
    targetcol = ['Date'] + targetcol
    data_likect = data[targetcol]
    data_likect_stacked = data_likect.melt(id_vars = ['Date'])
    data_likect_stacked.rename(columns = {'variable': 'location', 'value': 'count'}, inplace = True)
    
    # extrac city and state
    data_likect_stacked['city'] = list(map(lambda x: regex.sub('(,\ )(.*)', '', x), data_likect_stacked['location']))
    data_likect_stacked['city'] = list(map(lambda x: regex.sub('(.*)(\ -\ )', '', x), data_likect_stacked['city']))
    data_likect_stacked['state'] = list(map(lambda x: regex.sub('(.*)(,\ )', '', x), data_likect_stacked['location']))
    data_likect_stacked2 = data_likect_stacked[['city', 'state', 'Date', 'count']]
    
    # fill na and change type
    data_likect_stacked2 = data_likect_stacked2.fillna(0)
    data_likect_stacked2['count'] = data_likect_stacked2['count'].astype('int64')
    return data_likect_stacked2


# %%
# get "Lifetime Likes by City"
target = 'Weekly Reach by City'
data_reshaped = citydatareshaper(data, target)
data_reshaped.head(5)

#%%
states = ["AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DC", "DE", "FL", "GA", 
          "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD", 
          "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ", 
          "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC", 
          "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"]
stateEastNorthCentral = ['OH', 'IN', 'IL', 'WI', 'MI']
stateWestNorthCentral = ['MN', 'IA', 'MO', 'ND', 'SD', 'NE', 'KS']
stateMidWest = stateEastNorthCentral + stateWestNorthCentral
outsideMidwest = []
for state in states:
    if state not in stateMidWest:
        outsideMidwest.append(state)

target_state = stateEastNorthCentral + ['MO', 'KS', 'IA', 'MN','TN', 'KY']


#%%
# cell conditioning (by location)
# in US (in_US, outside_US)
conditions = [list(data_reshaped['state'].isin(states)), list(~data_reshaped['state'].isin(states))]
option_1 = ['in_US', 'outside_US']
data_reshaped['location_US'] = np.select(conditions, option_1)

# in midwest (EastNorthCentral, WestNorthCentral, outsidemidwest)
conditions = [list(data_reshaped['state'].isin(stateEastNorthCentral)), 
                list(data_reshaped['state'].isin(stateWestNorthCentral)),
                list(data_reshaped['state'].isin(outsideMidwest))
                ]
option_1 = ['EastNorthCentral', 'WestNorthCentral', 'outsidemidwest']
data_reshaped['location_Midwest'] = np.select(conditions, option_1)

# in target_state (in_target_state, outside_target_state)
conditions = [list(data_reshaped['state'].isin(target_state)), list(~data_reshaped['state'].isin(target_state))]
option_1 = ['in_target_state', 'outside_target_state']
data_reshaped['target_state'] = np.select(conditions, option_1)

#%%
# change datetime
data_reshaped['Date'] = pd.to_datetime(data_reshaped['Date'])
maxdate = pd.to_datetime('2018-07-23')
data_reshaped_rmdate = data_reshaped.loc[data_reshaped['Date'] <= maxdate]
data_reshaped_rmdate.tail(5)

#%%
outputpath = path
outputsubfolder = 'output'
outputfilename = regex.sub('\ ', '_', target) + '.csv'
print(outputfilename)
outputfilepath = os.path.join(outputpath, outputsubfolder, outputfilename)
data_reshaped_rmdate.to_csv(outputfilepath, index = False)



