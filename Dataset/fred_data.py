import pandas as pd
import numpy as np
import fredpy as fp
import matplotlib.pyplot as plt
import time
from dotenv import load_dotenv
import os

# Load the .env file
load_dotenv()
fp.api_key = os.environ.get('API_KEY')

# State FIPS codes dictionary
state_fips_dict = {
    "01": "Alabama",
    "02": "Alaska",
    "04": "Arizona",
    "05": "Arkansas",
    "06": "California",
    "08": "Colorado",
    "09": "Connecticut",
    "10": "Delaware",
    "11": "District of Columbia",
    "12": "Florida",
    "13": "Georgia",
    "15": "Hawaii",
    "16": "Idaho",
    "17": "Illinois",
    "18": "Indiana",
    "19": "Iowa",
    "20": "Kansas",
    "21": "Kentucky",
    "22": "Louisiana",
    "23": "Maine",
    "24": "Maryland",
    "25": "Massachusetts",
    "26": "Michigan",
    "27": "Minnesota",
    "28": "Mississippi",
    "29": "Missouri",
    "30": "Montana",
    "31": "Nebraska",
    "32": "Nevada",
    "33": "New Hampshire",
    "34": "New Jersey",
    "35": "New Mexico",
    "36": "New York",
    "37": "North Carolina",
    "38": "North Dakota",
    "39": "Ohio",
    "40": "Oklahoma",
    "41": "Oregon",
    "42": "Pennsylvania",
    "44": "Rhode Island",
    "45": "South Carolina",
    "46": "South Dakota",
    "47": "Tennessee",
    "48": "Texas",
    "49": "Utah",
    "50": "Vermont",
    "51": "Virginia",
    "53": "Washington",
    "54": "West Virginia",
    "55": "Wisconsin",
    "56": "Wyoming",
    "72": "Puerto Rico"
}


# Define the FIPS codes and dataset codes you want to loop through
fips_codes = list(state_fips_dict.keys())  # FIPS codes from the dictionary
dataset_codes = ["02", "03"]  # Example dataset codes

# Initialize an empty dictionary to store the data
dataset_data = {}

# Loop through the dataset codes
for data_code in dataset_codes:
    dataset_name = f"Dataset_{data_code}"  # Example dataset name
    fips_data = {}

    # Loop through the FIPS codes
    for fips_code in fips_codes:
        state_name = state_fips_dict[fips_code]
        series_code = f'SMU{fips_code}0000005000000{data_code}'
        data = fp.series(series_code)
        fips_data[state_name] = data.data

        # Pause for 5.5 seconds
        time.sleep(5.5)

        # Print a message indicating the progress
        print(f"Fetched data for State: {state_name}, Data Code: {data_code}")

    # Create a DataFrame from the dictionary of data
    df = pd.DataFrame(fips_data)

    # Store the DataFrame in the dataset dictionary
    dataset_data[dataset_name] = df

# Access the DataFrames for each dataset
dataset_02_df = dataset_data["Dataset_02"]
dataset_03_df = dataset_data["Dataset_03"]


# Convert dataset 02 to long format
dataset_02_long = (
    pd.melt(dataset_02_df.reset_index(), id_vars='date', var_name='State', value_name='Average_Weekly_Hours')
    .rename(columns={'date': 'Date'})
    .assign(Year=lambda x: x['Date'].dt.year, Month=lambda x: x['Date'].dt.month)
    .assign(state_name_month_year=lambda x: x['State'] + ' ' + x['Month'].astype(str) + ' ' + x['Year'].astype(str))
)

# Convert dataset 03 to long format
dataset_03_long = (
    pd.melt(dataset_03_df.reset_index(), id_vars='date', var_name='State', value_name='Average_Hourly_Earnings')
    .rename(columns={'date': 'Date'})
    .assign(Year=lambda x: x['Date'].dt.year, Month=lambda x: x['Date'].dt.month)
    .assign(state_name_month_year=lambda x: x['State'] + ' ' + x['Month'].astype(str) + ' ' + x['Year'].astype(str))
)

# Merge datasets
df_merged = (
    dataset_02_long.merge(dataset_03_long, on='state_name_month_year', how='left')
    .drop(['Date_y', 'State_y', 'Year_y', 'Month_y'], axis=1)
    .rename(columns={'Date_x': 'Date', 'State_x': 'State', 'Year_x': 'Year', 'Month_x': 'Month'})
    .query('Year >= 2011')
)


# Pickling the data
df_merged.to_pickle('fred_data.pkl')