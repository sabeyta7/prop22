# Attempting to gather data from BLS API
import requests
import json
import prettytable
import pandas as pd
from retrying import retry
import os

# Loading in the medicaid data
df_1 = pd.read_csv('medicaid_chip.csv')
df_2 = pd.read_csv('medicaid_change.csv')

# Add dfs to list
dfs = [df_1, df_2]

# Define a dictionary to map month abbreviations to numbers (as strings)
month_map = {
    'Jan': '1', 'Feb': '2', 'Mar': '3', 'Apr': '4', 'May': '5', 'Jun': '6',
    'Jul': '7', 'Aug': '8', 'Sep': '9', 'Oct': '10', 'Nov': '11', 'Dec': '12'
}

merged_df = None  # Initialize the merged DataFrame

for i, df in enumerate(dfs):
    # Dropping the ["Footnotes"] column
    df = df.drop(columns=['Footnotes'])

    # Set value_name based on DataFrame being processed
    value_name = 'medicaid_chip_enrollment' if i == 0 else 'medicaid_chip_change'

    # Reshape the DataFrame to long format
    long_df = df.melt(id_vars='Location', var_name='month_year', value_name=value_name)

    # Extract month and year from 'month_year' column using a regex pattern
    pattern = r'(\w{3}) (\d{4})__'
    long_df[['Month', 'Year']] = long_df['month_year'].str.extract(pattern)

    # Drop the 'month_year' column
    long_df = long_df.drop(columns='month_year')

    # Map month abbreviations to numbers in the 'Month' column
    long_df['Month'] = long_df['Month'].map(month_map)

    # Create a new column for state month year
    long_df['state_name_month_year'] = long_df['Location'] + ' ' + long_df['Month'] + ' ' + long_df['Year']

    # Drop unnecessary columns
    long_df = long_df.drop(columns=['Location', 'Year', 'Month'])

    if merged_df is None:
        merged_df = long_df  # Assign the first DataFrame to merged_df
    else:
        # Merge the current DataFrame with merged_df based on 'state_name_month_year'
        merged_df = pd.merge(merged_df, long_df, on='state_name_month_year')

# Move the 'state_name_month_year' column to the beginning of the DataFrame
cols = list(merged_df.columns)
cols = ['state_name_month_year'] + [col for col in cols if col != 'state_name_month_year']
merged_df = merged_df[cols]

# Print the merged DataFrame
merged_df.head()

# Save the merged DataFrame to a CSV file
merged_df.to_csv('medicaid_data.csv', index=False)
