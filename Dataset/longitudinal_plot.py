# Attempting to gather data from BLS API
import requests
import json
import pandas as pd
import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
import statsmodels.api as sm
import statsmodels.formula.api as smf
from statsmodels.stats.outliers_influence import variance_inflation_factor

"""
I am just going to start out making some plots to help with visualizing some of these trends
"""

# Loading in the dataset
df = pd.read_csv('state_month.csv')

# Making a new df that is 2014 and later and dropping Unnamed: 0
df_2014 = df[df['year'] >= 2014]
df_2014 = df_2014.drop(columns=['Unnamed: 0'])
# Convert columns to integers by removing commas and using pd.to_numeric
df_2014['popest'] = pd.to_numeric(df_2014['popest'].str.replace(',', ''), errors='coerce').astype('Int64')
df_2014['labor_force'] = pd.to_numeric(df_2014['labor_force'].str.replace(',', ''), errors='coerce').astype('Int64')
df_2014['total_employed'] = pd.to_numeric(df_2014['total_employed'].str.replace(',', ''), errors='coerce').astype('Int64')
df_2014['ind_participant'] = pd.to_numeric(df_2014['ind_participant'], errors='coerce')

# Convert the 'date' column to pandas datetime type
df_2014['date'] = pd.to_datetime(df_2014['date'])

# Drop null values from the 'ind_snap_cost' column
df_2014_new = df_2014.dropna(subset=['medicaid_chip_enrollment'])
df_2014_new['medicaid_chip_enrollment'] = pd.to_numeric(df_2014_new['medicaid_chip_enrollment'], errors='coerce')

# Separate the data for Texas, California, Washington, and other states
texas = df_2014_new[df_2014_new['state'] == 'Texas']
california = df_2014_new[df_2014_new['state'] == 'California']
washington = df_2014_new[df_2014_new['state'] == 'Washington']
other_states = df_2014_new[~df_2014_new['state'].isin(['Texas', 'California', 'Washington'])]

# Calculate the average for other states
average_other_states = other_states.groupby('date')['medicaid_chip_enrollment'].mean().reset_index()

# Set up the figure and axes
fig, ax = plt.subplots(figsize=(18, 12))

# Define the pleasing CSS colors
colors = ['#007bff', '#ffe53b', '#191970', '#777777']

# Plot the lines with the specified colors and set the labels for the lines
line_texas, = ax.plot(texas['date'], texas['medicaid_chip_enrollment'], color=colors[0], linewidth=3, label='Texas')
line_california, = ax.plot(california['date'], california['medicaid_chip_enrollment'], color=colors[1], linewidth=3, label='California')
line_washington, = ax.plot(washington['date'], washington['medicaid_chip_enrollment'], color=colors[2], linewidth=3, label='Washington')
line_average, = ax.plot(average_other_states['date'], average_other_states['medicaid_chip_enrollment'], color=colors[3], linewidth=3, label='Average (Other States)')

# Set the x-axis label with dark grey text
ax.set_xlabel('Date', fontsize=20, labelpad=15, color='dimgray')  # Increase the fontsize for x-axis label

# Set the y-axis label with dark grey text
ax.set_ylabel('Medicaid and CHIP Enrollment (millions)', fontsize=20, labelpad=15, color='dimgray')  # Increase the fontsize for y-axis label

# Set the plot title with dark grey text
ax.set_title('Medicaid and CHIP Enrollment by Month', fontsize=24, pad=20, color='dimgray')  # Increase the fontsize for the title

# Set larger tick label fonts for both x and y axes
ax.tick_params(axis='both', which='major', labelsize=16, color='dimgray')  # Set tick label color to dark grey

# Set larger font and dark grey color for the axis tick values
for tick in ax.get_xticklabels() + ax.get_yticklabels():
    tick.set_fontsize(14)
    tick.set_color('dimgray')

# Remove the border around the plot
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['bottom'].set_visible(False)
ax.spines['left'].set_visible(False)

# Remove the small axis spines
ax.xaxis.set_tick_params(width=0)
ax.yaxis.set_tick_params(width=0)

# Add vertical dashes for specific dates
ax.axvline(pd.to_datetime('2020-01-01'), color='grey', linestyle='--')
ax.axvline(pd.to_datetime('2020-03-01'), color='red', linestyle='--')
ax.axvline(pd.to_datetime('2021-01-01'), color='grey', linestyle='--')
ax.axvline(pd.to_datetime('2022-12-01'), color='grey', linestyle='--')

# Set the x-axis limits to cut the timeline at 2018
ax.set_xlim(pd.to_datetime('2018-01-01'), pd.to_datetime('2023-03-01'))  # Adjust the upper limit as needed

# Add vertical text labels next to the top of each of the vertical lines
vertical_labels = ['Enactment of AB 5', 'Start of Covid-19 Pandemic', 'Enactment of Prop 22', 'Enactment of Washington Bill']
vertical_positions = [pd.to_datetime('2020-01-01'), pd.to_datetime('2020-03-01'),
                      pd.to_datetime('2021-01-01'), pd.to_datetime('2022-12-01')]

label_offset = 50.0  # Increase this value to move the labels more

for label, pos in zip(vertical_labels, vertical_positions):
    line_color = 'red' if label == 'Start of Covid-19 Pandemic' else 'grey'
    ax.axvline(x=pos, color=line_color, linestyle='--')
    ax.text(pos, ax.get_ylim()[1], label, rotation='vertical', ha='right', va='top', fontsize=16, color='black')

# Show the state names at the end of each line with adjusted vertical position
state_names = ['Texas', 'California', 'Washington', 'Average (Other States)']
y_offsets = [16, -5, 5, -15]  # Adjust the offsets for each state name as needed

for line, name, color, y_offset in zip([line_texas, line_california, line_washington, line_average],
                                       state_names, colors, y_offsets):
    x = line.get_xdata()[-1]
    y = line.get_ydata()[-1]
    ax.annotate(name, xy=(x, y), xytext=(10, y_offset), textcoords='offset points', color=color, fontsize=16)

# Show the plot
plt.show()