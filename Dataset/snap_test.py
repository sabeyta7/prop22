import pandas as pd
import os

state_indicators = [
    "Alabama", "Alaska", "Arizona", "Arkansas", "California", "Colorado", "Connecticut", "Delaware", "Florida", "Georgia",
    "Hawaii", "Idaho", "Illinois", "Indiana", "Iowa", "Kansas", "Kentucky", "Louisiana", "Maine", "Maryland",
    "Massachusetts", "Michigan", "Minnesota", "Mississippi", "Missouri", "Montana", "Nebraska", "Nevada", "New Hampshire", "New Jersey",
    "New Mexico", "New York", "North Carolina", "North Dakota", "Ohio", "Oklahoma", "Oregon", "Pennsylvania", "Rhode Island", "South Carolina",
    "South Dakota", "Tennessee", "Texas", "Utah", "Vermont", "Virginia", "Washington", "West Virginia", "Wisconsin", "Wyoming"
]


# Specify the directory path
directory = os.getcwd()

# Get a list of all XLS and XLSX files in the directory
excel_files = [file for file in os.listdir(directory) if file.endswith(('.xls', '.xlsx'))]

# Initialize an empty DataFrame to store the results
new_df = pd.DataFrame(columns=["State", "Date", "hh_participant", "ind_participant", "tot_snap_cost", "hh_snap_cost", "ind_snap_cost"])

# Iterate over each Excel file
for file in excel_files:
    # Specify the path to the Excel workbook
    excel_file = os.path.join(directory, file)

    # Read all sheets from the Excel file into a dictionary of DataFrames
    sheets = pd.read_excel(excel_file, sheet_name=None)

    # Concatenate the DataFrames into a single DataFrame
    concatenated_df = pd.concat(sheets.values())

    # Reset the index of the concatenated DataFrame
    df = concatenated_df.reset_index(drop=True)

    # Iterate over the rows of the DataFrame starting from index 7
    for index in range(7, len(df)):
        row = df.iloc[index]

        # Check if the row contains a state name
        if row[0] in state_indicators:
            state = row[0]
            dates = df.iloc[index + 1:index + 13, 0]
            values = df.iloc[index + 1:index + 13, 1:6].values

            # Create a new row for the state with the corresponding dates and values
            new_rows = pd.DataFrame({
                "State": [state] * 12,
                "Date": dates,
                "hh_participant": values[:, 0],
                "ind_participant": values[:, 1],
                "tot_snap_cost": values[:, 2],
                "hh_snap_cost": values[:, 3],
                "ind_snap_cost": values[:, 4]
            })

            # Append the new rows to the new DataFrame
            new_df = new_df.append(new_rows, ignore_index=True)

# Organize the DataFrame by state
new_df = new_df.sort_values(by=["State"])

# Print the final DataFrame
print(new_df)

# Drop the rows with missing values
new_df = new_df.dropna()

# From date separating into month and year
new_df['month'] = pd.DatetimeIndex(new_df['Date']).month
new_df['year'] = pd.DatetimeIndex(new_df['Date']).year

# Construct a state name + month + year column
new_df['state_name_month_year'] = new_df['State'] + " " + new_df['month'].astype(str) + " " + new_df['year'].astype(str)

# Organize by state name + month + year
new_df = new_df.sort_values(by=["state_name_month_year"])

# Save the DataFrame to a CSV file
new_df.to_csv("snap_data.csv", index=False)