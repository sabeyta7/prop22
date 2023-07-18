# Attempting to gather data from BLS API
import requests
import json
import prettytable
import pandas as pd
from retrying import retry
import os
import numpy as np

# Employment and  unemployment number by state and month
df_1 = pd.read_csv('employ_unemploy_st_mnth.csv')

# Snap data
df_2 = pd.read_csv('snap_data.csv')

# Federal Reserve Economic Data (FRED) data by state and month
df_3 = pd.read_pickle('fred_data.pkl')

# Medicaid and Children's Health Insurance Program (CHIP) enrollment and change by state and month csv
df_4 = pd.read_csv('medicaid_data.csv')




# In df_1, the column 'state' is the state abbreviation. In df_2, the column 'state' is the state name, so we need to
# create a dictionary to map the state abbreviations to the state names.
state_names = {
    "AL": "Alabama",
    "AK": "Alaska",
    "AZ": "Arizona",
    "AR": "Arkansas",
    "CA": "California",
    "CO": "Colorado",
    "CT": "Connecticut",
    "DE": "Delaware",
    "FL": "Florida",
    "GA": "Georgia",
    "HI": "Hawaii",
    "ID": "Idaho",
    "IL": "Illinois",
    "IN": "Indiana",
    "IA": "Iowa",
    "KS": "Kansas",
    "KY": "Kentucky",
    "LA": "Louisiana",
    "ME": "Maine",
    "MD": "Maryland",
    "MA": "Massachusetts",
    "MI": "Michigan",
    "MN": "Minnesota",
    "MS": "Mississippi",
    "MO": "Missouri",
    "MT": "Montana",
    "NE": "Nebraska",
    "NV": "Nevada",
    "NH": "New Hampshire",
    "NJ": "New Jersey",
    "NM": "New Mexico",
    "NY": "New York",
    "NC": "North Carolina",
    "ND": "North Dakota",
    "OH": "Ohio",
    "OK": "Oklahoma",
    "OR": "Oregon",
    "PA": "Pennsylvania",
    "RI": "Rhode Island",
    "SC": "South Carolina",
    "SD": "South Dakota",
    "TN": "Tennessee",
    "TX": "Texas",
    "UT": "Utah",
    "VT": "Vermont",
    "VA": "Virginia",
    "WA": "Washington",
    "WV": "West Virginia",
    "WI": "Wisconsin",
    "WY": "Wyoming"
}


# Create a new column in df_1 that is state month year which will then be merged with df_2.
df_1['state_name_month_year'] = df_1['state_area'] + ' ' + df_1['month'].astype(str) + ' ' + df_1['year'].astype(str)

# Merge the two dataframes on the state_name_month_year column, and keep only data after 2011
df_merged = pd.merge(df_1, df_2, on='state_name_month_year', how='left', indicator=True)
df_merged = df_merged[df_merged['year_x'] >= 2011]
df_merged['_merge1'] = df_merged['_merge']

# Drop row in which _merge is not both, drop the merge column, and merge df_3 with df_merged
df_merged = df_merged.drop(['_merge'], axis=1)
df_merged = pd.merge(df_merged, df_3, on=['state_name_month_year'], how='left', indicator=True)
df_merged['_merge2'] = df_merged['_merge']
df_merged = df_merged.drop(['_merge'], axis=1)

# Mergin in df_4
df_merged = pd.merge(df_merged, df_4, on=['state_name_month_year'], how='left', indicator=True)

# Dropping repeat information
df_merged = df_merged.drop(['Date_y', 'State_y', 'month_y', 'year_y'], axis=1)
df_merged = df_merged.rename(columns={'Date_x': 'date', 'State_x': 'state', 'month_x': 'month', 'year_x': 'year'})

# Reorder columns so that State is first, followed by date, month, year, and then the rest of the columns
new_column_order = ['state', 'date', 'month', 'year'] + [col for col in df_merged.columns if col not in ['State', 'date', 'month', 'year']]
df_merged = df_merged.reindex(columns=new_column_order)

# Identify duplicated column names and select only unique columns
duplicated_columns = df_merged.columns[df_merged.columns.duplicated()]
final_df = df_merged.loc[:, ~df_merged.columns.duplicated()]

# Columns to replace
columns_to_replace = ['hh_participant', 'ind_participant', 'tot_snap_cost', 'hh_snap_cost', 'ind_snap_cost', 'Average_Weekly_Hours', 'Average_Hourly_Earnings']

# Add category '0' to _merge1 and _merge2 columns
final_df['_merge1'] = final_df['_merge1'].cat.add_categories(0)
final_df['_merge2'] = final_df['_merge2'].cat.add_categories(0)

# Replace _merge1 and _merge2 with NaN where applicable
final_df.loc[final_df['_merge1'] == 'left_only', '_merge1'] = np.nan
final_df.loc[final_df['_merge2'] == 'left_only', '_merge2'] = np.nan

# Replace specific columns with 0 where _merge1 or _merge2 is 'left_only'
final_df.loc[final_df['_merge1'] == 'left_only', columns_to_replace] = 0
final_df.loc[final_df['_merge2'] == 'left_only', columns_to_replace] = 0

# Drop if state is NaN
final_df = final_df.dropna(subset=['state'])

# Drop _merge1, _merge2, and _merge columns
final_df = final_df.drop(['_merge1', '_merge2', '_merge'], axis=1)

# Ensuring all states are represented the correct number of times (i.e. 149 months in total)

# Save final_df as a pickle file
final_df.to_csv('state_month.csv')


