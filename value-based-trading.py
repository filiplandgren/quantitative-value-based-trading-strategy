# -*- coding: utf-8 -*-
"""
Created on Sat Aug 26 18:43:43 2023

@author: fl5g21
"""

# Importing necessary libraries
import numpy as np
import pandas as pd
import requests
import xlsxwriter
import math
from scipy import stats
from statistics import mean
import matplotlib.pyplot as plt
import seaborn as sns

# Importing stock list and API token
stocks = pd.read_csv('sp_500_stocks.csv')
from secrets import IEX_CLOUD_API_TOKEN

# Making an API call to get stock data
symbol = 'AAPL'
api_url = f'https://sandbox.iexapis.com/stable/stock/{symbol}/quote?token={IEX_CLOUD_API_TOKEN}'
data = requests.get(api_url).json()

# Parsing data from the API response
pe_ratio = data['peRatio']

# Function to divide list into chunks
def chunks(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

# Creating symbol groups for batch API calls
symbol_groups = list(chunks(stocks['Ticker'], 100))
symbol_strings = [','.join(symbol_group) for symbol_group in symbol_groups]

# Columns for the final DataFrame
my_columns = ['Ticker', 'Price', 'Price-to-Earnings Ratio', 'Number of Shares to Buy']

# Creating a DataFrame to store data
final_dataframe = pd.DataFrame(columns=my_columns)

# Filling the DataFrame with API data
for symbol_string in symbol_strings:
    batch_api_call_url = f'https://sandbox.iexapis.com/stable/stock/market/batch/?types=quote&symbols={symbol_string}&token={IEX_CLOUD_API_TOKEN}'
    data = requests.get(batch_api_call_url).json()
    for symbol in symbol_string.split(','):
        final_dataframe = final_dataframe.append(
            pd.Series([symbol, 
                       data[symbol]['quote']['latestPrice'],
                       data[symbol]['quote']['peRatio'],
                       'N/A'],
                      index=my_columns),
            ignore_index=True
        )

# Removing glamour stocks and calculating shares to buy
final_dataframe.sort_values('Price-to-Earnings Ratio', inplace=True)
final_dataframe = final_dataframe[final_dataframe['Price-to-Earnings Ratio'] > 0]
final_dataframe = final_dataframe[:50]
final_dataframe.reset_index(drop=True, inplace=True)

# Function to get user input for portfolio size
def portfolio_input():
    global portfolio_size
    portfolio_size = input("Enter the value of your portfolio:")
    try:
        val = float(portfolio_size)
    except ValueError:
        print("That's not a number! \n Try again:")
        portfolio_input()

# Accepting portfolio size from user
portfolio_input()

# Calculating shares to buy for each stock
position_size = float(portfolio_size) / len(final_dataframe.index)
for i in range(len(final_dataframe)):
    final_dataframe.loc[i, 'Number of Shares to Buy'] = math.floor(position_size / final_dataframe['Price'][i])

# Creating a DataFrame for robust value strategy (rv)
rv_columns = [
    'Ticker', 'Price', 'Number of Shares to Buy', 'Price-to-Earnings Ratio', 'PE Percentile', 
    'Price-to-Book Ratio', 'PB Percentile', 'Price-to-Sales Ratio', 'PS Percentile', 'EV/EBITDA', 
    'EV/EBITDA Percentile', 'EV/GP', 'EV/GP Percentile', 'RV Score'
]
rv_dataframe = pd.DataFrame(columns=rv_columns)

# Calculating various valuation metrics
for symbol_string in symbol_strings:
    batch_api_call_url = f'https://sandbox.iexapis.com/stable/stock/market/batch?symbols={symbol_string}&types=quote,advanced-stats&token={IEX_CLOUD_API_TOKEN}'
    data = requests.get(batch_api_call_url).json()
    for symbol in symbol_string.split(','):
        advanced_stats = data[symbol]['advanced-stats']
        enterprise_value = advanced_stats['enterpriseValue']
        ebitda = advanced_stats['EBITDA']
        gross_profit = advanced_stats['grossProfit']
        
        ev_to_ebitda = enterprise_value / ebitda if ebitda else np.NaN
        ev_to_gross_profit = enterprise_value / gross_profit if gross_profit else np.NaN
        
        rv_dataframe = rv_dataframe.append(
            pd.Series([
                symbol,
                data[symbol]['quote']['latestPrice'],
                'N/A',
                data[symbol]['quote']['peRatio'],
                'N/A',
                advanced_stats['priceToBook'],
                'N/A',
                advanced_stats['priceToSales'],
                'N/A',
                ev_to_ebitda,
                'N/A',
                ev_to_gross_profit,
                'N/A',
                'N/A'
            ],
            index=rv_columns),
            ignore_index=True
        )

# Filling missing data with average non-NaN values
for column in ['Price-to-Earnings Ratio', 'Price-to-Book Ratio', 'Price-to-Sales Ratio', 'EV/EBITDA', 'EV/GP']:
    rv_dataframe[column].fillna(rv_dataframe[column].mean(), inplace=True)

# Calculating value percentiles
metrics = {
    'Price-to-Earnings Ratio': 'PE Percentile',
    'Price-to-Book Ratio': 'PB Percentile',
    'Price-to-Sales Ratio': 'PS Percentile',
    'EV/EBITDA': 'EV/EBITDA Percentile',
    'EV/GP': 'EV/GP Percentile'
}

for row in rv_dataframe.index:
    for metric in metrics.keys():
        rv_dataframe.loc[row, metrics[metric]] = stats.percentileofscore(rv_dataframe[metric], rv_dataframe.loc[row, metric]) / 100

# Calculating RV Score
for row in rv_dataframe.index:
    value_percentiles = [rv_dataframe.loc[row, metrics[metric]] for metric in metrics.keys()]
    rv_dataframe.loc[row, 'RV Score'] = mean(value_percentiles)

# Selecting the 50 best value stocks
rv_dataframe.sort_values(by='RV Score', inplace=True)
rv_dataframe = rv_dataframe[:50]
rv_dataframe.reset_index(drop=True, inplace=True)

# Calculating shares to buy for each stock in the refined strategy
position_size = float(portfolio_size) / len(rv_dataframe.index)
for i in range(len(rv_dataframe)):
    rv_dataframe.loc[i, 'Number of Shares to Buy'] = math.floor(position_size / rv_dataframe['Price'][i])
    
    
    
    
    
    
# Visualizations


# Visualizing Price-to-Earnings Ratio Distribution
plt.figure(figsize=(10, 6))
sns.histplot(rv_dataframe['Price-to-Earnings Ratio'], bins=20, kde=True)
plt.title('Price-to-Earnings Ratio Distribution')
plt.xlabel('Price-to-Earnings Ratio')
plt.ylabel('Frequency')
plt.show()

# Scatter Plot: Price vs. RV Score
plt.figure(figsize=(10, 6))
sns.scatterplot(x='Price', y='RV Score', data=rv_dataframe)
plt.title('Price vs. RV Score')
plt.xlabel('Price')
plt.ylabel('RV Score')
plt.show()

# Creating Excel output using XlsxWriter

writer = pd.ExcelWriter('value_strategy.xlsx', engine='xlsxwriter')
rv_dataframe.to_excel(writer, sheet_name='Value Strategy', index=False)

# Creating cell formats for formatting Excel output
background_color = '#0a0a23'
font_color = '#ffffff'

string_template = writer.book.add_format({'font_color': font_color, 'bg_color': background_color, 'border': 1})
dollar_template = writer.book.add_format({'num_format': '$0.00', 'font_color': font_color, 'bg_color': background_color, 'border': 1})
integer_template = writer.book.add_format({'num_format': '0', 'font_color': font_color, 'bg_color': background_color, 'border': 1})
float_template = writer.book.add_format({'num_format': '0', 'font_color': font_color, 'bg_color': background_color, 'border': 1})
percent_template = writer.book.add_format({'num_format': '0.0%', 'font_color': font_color, 'bg_color': background_color, 'border': 1})

column_formats = {
    'A': ['Ticker', string_template],
    'B': ['Price', dollar_template],
    'C': ['Number of Shares to Buy', integer_template],
    'D': ['Price-to-Earnings Ratio', float_template],
    'E': ['PE Percentile', percent_template],
    'F': ['Price-to-Book Ratio', float_template],
    'G': ['PB Percentile', percent_template],
    'H': ['Price-to-Sales Ratio', float_template],
    'I': ['PS Percentile', percent_template],
    'J': ['EV/EBITDA', float_template],
    'K': ['EV/EBITDA Percentile', percent_template],
    'L': ['EV/GP', float_template],
    'M': ['EV/GP Percentile', percent_template],
    'N': ['RV Score', percent_template]
}

# Applying formats to Excel output
for column in column_formats.keys():
    writer.sheets['Value Strategy'].set_column(f'{column}:{column}', 25, column_formats[column][1])
    writer.sheets['Value Strategy'].write(f'{column}1', column_formats[column][0], column_formats[column][1])

# Saving Excel output
writer.save()