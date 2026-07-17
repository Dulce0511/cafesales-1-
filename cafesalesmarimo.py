import marimo

__generated_with = "0.23.14"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import pandas as pd
    import numpy as np
    import matplotlib.pyplot as plt

    # Importing the dirty cafe sales data
    cafesales_df = pd.read_csv(r"C:\Users\Admin\OneDrive - University Of Houston\python courses\dirty_cafe_sales.csv")
    print(cafesales_df.head())

    # Copying the original dataframe 
    df_original = cafesales_df.copy()
    return cafesales_df, mo, np, pd


@app.cell
def _(np, pd):
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

    return (convert_data_types,)


@app.cell
def _(pd):
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

    return (clean_date,)


@app.cell
def _(pd):
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

    return (fill_missing_prices,)


@app.function
# Replacing the nan values in Payment Method and location with 'Unknown'
# Not dropping the values completely in order to use the most amount of observations possible
# Adequate analysis can still be achieved with Unknown values in these columns

def fill_missing_payment_location(df):
    df['Payment Method'] = df['Payment Method'].fillna('Unknown')
    df['Location'] = df['Location'].fillna('Unknown')
    return df


@app.function
# Rearranging values in dataframe
def arrange(df):
    # Rearrage to date being in acending order
    df = df .sort_values(by = 'Transaction Date', ascending = True)

    # Rearrange index in dataframe
    df = df.reset_index(drop= True)

    return df


@app.cell
def _(cafesales_df, clean_date, convert_data_types, fill_missing_prices):
    cafe_df = convert_data_types(cafesales_df)
    cafec_df = clean_date(cafe_df)
    cafecl_df = fill_missing_prices(cafec_df)
    cafecle_df = fill_missing_payment_location(cafecl_df)
    cafeclean_df = arrange(cafecle_df)
    cafeclean_df
    return (cafeclean_df,)


@app.cell
def _(cafeclean_df):
    print(cafeclean_df['Quantity'].isna().sum()) #0
    print(cafeclean_df['Price Per Unit'].isna().sum()) #0
    print(cafeclean_df['Total Spent'].isna().sum()) #0
    print(cafeclean_df['Payment Method'].isna().sum()) #0
    print(cafeclean_df['Location'].isna().sum()) #0
    print(cafeclean_df['Item'].isna().sum())
    return


@app.cell
def _(cafeclean_df, mo):
    mo.ui.dataframe(cafeclean_df)
    return


@app.cell
def _(cafeclean_df, mo):
    mo.ui.data_explorer(cafeclean_df)
    return


@app.cell
def _(cafesales_df):
    # Creating a missing values dataframe
    missing_df = cafesales_df[cafesales_df.isna().any(axis=1)]

    # Rearange Index
    missing_df = missing_df.reset_index(drop=True)

    print(missing_df)
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
