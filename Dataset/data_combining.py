# Attempting to gather data from BLS API
import requests
import json
import prettytable
import pandas as pd
from retrying import retry
import os

# Employment and  unemployment number by state and month
df_1 = pd.read_csv('employ_unemploy_st_mnth.csv')

# Osha inspections and wage violations by state and month
df_2 = pd.read_pickle('labor_month_state_year')

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

# Create a new column in df_2 that contains the state names instead of the state abbreviations.
df_2['state_name'] = df_2['state'].map(state_names)

# Combine into state_name_month_year
df_2['state_name_month_year'] = df_2['state_name'] + ' ' + df_2['month'].astype(str) + ' ' + df_2['year'].astype(str)

# Create a new column in df_1 that is state month year which will then be merged with df_2.
df_1['state_name_month_year'] = df_1['state_area'] + ' ' + df_1['month'].astype(str) + ' ' + df_1['year'].astype(str)

# Merge the two dataframes on the state_name_month_year column, and keep only data after 2012
df_merged = pd.merge(df_1, df_2, on='state_name_month_year', how='left', indicator=True)
df_merged = df_merged[df_merged['year_x'] >= 2012]

# Drop row in which _merge is not both, drop the merge column, and merge df_3 with df_merged
df_merged = df_merged[df_merged['_merge'] == 'both']
df_merged = df_merged.drop(['_merge'], axis=1)
df_merged = pd.merge(df_merged, df_3, on=['state_name_month_year'], how='left', indicator=True)

# Drop row in which _merge is not both, drop columns that are not needed, and rename columns
df_merged = df_merged[df_merged['_merge'] == 'both']
df_merged= df_merged.drop(['_merge', 'state_area', 'month_y', 'year_y', 'state-month-year', 'state', 'Year', 'Month', 'state_name', 'year-month'], axis=1)
df_merged = df_merged.rename(columns={'month_x': 'month', 'year_x': 'year', 'State': 'state', 'Date': 'date'})

# Mergin in df_4
df_merged = pd.merge(df_merged, df_4, on=['state_name_month_year'], how='left', indicator=True)

# Drop row in which _merge is not both and dropping merged column
df_merged = df_merged[df_merged['_merge'] == 'both']
df_merged = df_merged.drop(['_merge'], axis=1)

# Reorder columns so that State is first, followed by date, month, year, and then the rest of the columns
new_column_order = ['state', 'date', 'month', 'year'] + [col for col in df_merged.columns if col not in ['State', 'date', 'month', 'year']]
df_merged = df_merged.reindex(columns=new_column_order)

# Identify duplicated column names and select only unique columns
duplicated_columns = df_merged.columns[df_merged.columns.duplicated()]
final_df = df_merged.loc[:, ~df_merged.columns.duplicated()]