####################################################################################
# Cafe Sales Data Cleaning and Visualization
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Importing the dirty cafe sales data
cafesales_df = pd.read_csv(r"C:\Users\Admin\OneDrive - University Of Houston\python courses\dirty_cafe_sales.csv")
print(cafesales_df)

# Copying the original dataframe 
df_original = cafesales_df.copy()


####################################################################################

# Creating function to convert data to their actual types
# This will allow to perform functions later
def convert_data_types(df):
    # Replace all error and unknown to nan
    df = df.replace("ERROR", np.nan, inplace=True)    
    df = df.replace("UNKNOWN", np.nan, inplace=True)
    df = df.replace(" ", np.nan, inplace=True)

    # Convert Price per Unit into float and Quantity into integer to floats
    df["Total Spent"] = df["Total Spent"].astype(float) #str to float
    df["Price Per Unit"] = df["Price Per Unit"].astype(float) #str to float
    df["Quantity"] = df["Quantity"].astype(pd.Int64Dtype()) #str to int
    
    # Print the info of the dataframe to check the data types
    print(df.info())
    return df

cafesales_df = convert_data_types(cafesales_df)
####################################################################################
# Create a seperate dataframe with Missing Values
missing_df = cafesales_df[cafesales_df.isna().any(axis=1)]

# Rearange Index
missing_df = missing_df.reset_index(drop=True)

print(missing_df)

# # For further data analysis later on..

####################################################################################

# Creating a function to clean the date column
def clean_date(df):
    # Remove duplicates
    df = df.drop_duplicates()
    
    # Convert date column to datetime format
    df["Transaction Date"] = pd.to_datetime(df["Transaction Date"], errors="coerce")

    # Replace NaN rows with mode dates
    # This was the initial idea, but replacing missing date values with mode did lead to biased results.
    # mode_date = df['Transaction Date'].mode()[0]
    # df['Transaction Date'] = df['Transaction Date'].fillna(mode_date) #mode_date = '02/06/2023
    
    # Rearrange date in ascending order
    df = df.sort_values(by='Transaction Date', ascending=True)
    
    # Separate month, day and year into separate columns
    df['Month'] = df['Transaction Date'].dt.month   
    df['Day'] = df['Transaction Date'].dt.day
    df['Year'] = df['Transaction Date'].dt.year

    # Drop remaining rows with missing values in the Transaction Date column
    # This function will slightly unbias the data analysis
    df = df.dropna(subset=['Transaction Date'])
    
    return df

cafesales_df = clean_date(cafesales_df)
print(cafesales_df)

####################################################################################

# Fill Nan in numerical values
def fill_missing_prices(df):
    # Fill Price Per Unit with the known price for each item
    df['Price Per Unit'] = df.groupby('Item')['Price Per Unit'].transform(
        lambda x: x.fillna(x.dropna().iloc[0] if not x.dropna().empty else x)
    )

    # Fill only missing Quantity values
    df['Quantity'] = df.apply(
        lambda row: row['Total Spent'] / row['Price Per Unit']
        if pd.isna(row['Quantity']) and
           not pd.isna(row['Total Spent']) and
           not pd.isna(row['Price Per Unit']) and
           row['Price Per Unit'] != 0
        else row['Quantity'],
        axis=1
    )

    # Fill only missing Total Spent values
    df['Total Spent'] = df.apply(
        lambda row: row['Quantity'] * row['Price Per Unit']
        if pd.isna(row['Total Spent']) and
           not pd.isna(row['Quantity']) and
           not pd.isna(row['Price Per Unit'])
        else row['Total Spent'],
        axis=1
    )

    # Drop remaining rows with missing values in any of the three columns
    df = df.dropna(subset=['Price Per Unit', 'Quantity', 'Total Spent'])

    # Rearrange the dataframe in ascending order based on Total Spent
    df = df.sort_values(by = "Total Spent", ascending = True)

    # Round all items in the Quantity columns to the nearest integer
    df['Quantity'] = df['Quantity'].round().astype(int)
  
    # Round all items in the Price Per Unit and Total Spent columns to 2 decimal places
    df['Price Per Unit'] = df['Price Per Unit'].round(2)
    df['Total Spent'] = df['Total Spent'].round(2)

    return df

cafesales_df = fill_missing_prices(cafesales_df)
print(cafesales_df)

# Checking how many nan values are left in the dataframe
print(cafesales_df['Quantity'].isna().sum()) #0
print(cafesales_df['Price Per Unit'].isna().sum()) #0
print(cafesales_df['Total Spent'].isna().sum()) #0

####################################################################################

# Replacing the nan values in Payment Method and location with 'Unknown'
# Not dropping the values completely in order to use the most amount of observations possible
# Adequate analysis can still be achieved with Unknown values in these columns
def fill_missing_payment_location(df):
    df['Payment Method'] = df['Payment Method'].fillna('Unknown')
    df['Location'] = df['Location'].fillna('Unknown')
    return df
cafesales_df = fill_missing_payment_location(cafesales_df)
print(cafesales_df)

# Checking the nan values in the Payment Method and Location columns
print(cafesales_df['Payment Method'].isna().sum()) #0
print(cafesales_df['Location'].isna().sum()) #0
print(cafesales_df['Item'].isna().sum()) #0

# Rearrage to date being in acending order
cafesales_df = cafesales_df.sort_values(by = "Transaction Date", ascending = True)

# Rearrange index in dataframe
cafesales_df = cafesales_df.reset_index(drop=True)
                                        
print(cafesales_df)
####################################################################################

# Summary statistics of the cleaned dataframe
sumstat_totalspent = cafesales_df['Total Spent'].describe().round(2)
sumstat_priceperunit = cafesales_df['Price Per Unit'].describe().round(2)
sumstat_quantity = cafesales_df['Quantity'].describe().round(2)
sumstat_location = cafesales_df['Location'].describe() # top is Unknown
sumstat_paymntmthd = cafesales_df['Payment Method'].describe() #top is Unknown
sumstat_item = cafesales_df['Item'].describe() # top is Juice

# Print Summary Statistics Tables (DataFrames)
print("Summary Statistics for Total Spent:\n", sumstat_totalspent)
print("Summary Statistics for Price Per Unit:\n", sumstat_priceperunit)
print("Summary Statistics for Quantity:\n", sumstat_quantity)
print("Summary Statistics for Location:\n", sumstat_location)
print("Summary Statistics for Payment Method:\n", sumstat_paymntmthd)
print("Summary Statistics for Item:\n", sumstat_item)

print("Summary for Location:\n", cafesales_df.groupby("Location", group_keys=True)[["Transaction ID"]].count())
print("Summary for Payment Method:\n", cafesales_df.groupby("Payment Method", group_keys=True)[["Transaction ID"]].count())

####################################################################################

# Creating a function to visualize the cleaned data
def visualize_data(df):
    # Visualizing the distribution of Total Spent
    # Histogram of Total Spent
    plt.figure(figsize=(10, 6))
    plt.hist(df['Total Spent'], bins=30, color='skyblue', edgecolor='black')
    plt.title('Distribution of Total Spent')
    plt.xlabel('Total Spent')
    plt.ylabel('Frequency')
    plt.grid(axis='y', alpha=0.75)
    plt.show()

    # Visualizing the distribution of Price Per Unit
    # Histogram of Price Per Unit
    plt.figure(figsize=(10, 6))
    plt.hist(df['Price Per Unit'], bins=30, color='lightgreen', edgecolor='black')
    plt.title('Distribution of Price Per Unit')
    plt.xlabel('Price Per Unit')
    plt.ylabel('Frequency')
    plt.grid(axis='y', alpha=0.75)
    plt.show()

    # Visualizing the distribution of Quantity
    # Histogram of Quantity
    plt.figure(figsize=(10, 6))     
    plt.hist(df['Quantity'], bins=30, color='salmon', edgecolor='black')
    plt.title('Distribution of Quantity')
    plt.xlabel('Quantity')
    plt.ylabel('Frequency')
    plt.grid(axis='y', alpha=0.75)
    plt.show()
    
    # Visualizing Total Spent over months
    # Linear plot of Total Spent over months
    plt.figure(figsize=(12, 6))
    # Grouping by month and summing Total Spent 
    monthly_totalspent = cafesales_df.groupby(cafesales_df['Month'])['Total Spent'].sum()   
    plt.plot(monthly_totalspent.index, monthly_totalspent.values, marker='o', linestyle='-', color='blue')
    plt.title('Total Spent Over Months')
    plt.xlabel('Month')
    plt.ylabel('Total Spent')
    plt.xticks(monthly_totalspent.index)  # Set x-ticks to be the months
    plt.grid()
    plt.show()

visualize_data(cafesales_df)

####################################################################################
# Export dataframe to csv
cafesales_df.to_csv(r"C:/Users/Admin/Downloads/cleaned_cafe_sales.csv", index=False)

####################################################################################

