# Quantitative Value Strategy Project

This project is an implementation of a quantitative value investing strategy that selects the 50 best value stocks from a universe of stocks. It utilizes financial metrics such as Price-to-Earnings ratio, Price-to-Book ratio, Price-to-Sales ratio, EV/EBITDA, and EV/GP to identify stocks with attractive value characteristics.

## Project Overview

The project is built using Python and relies on the IEX Cloud API to fetch financial data for stocks. It performs the following steps:

1. Imports necessary libraries and retrieves the list of stocks from 'sp_500_stocks.csv'.
2. Makes API calls to fetch stock data, calculate value metrics, and create the initial dataframe.
3. Filters out glamour stocks based on price-to-earnings ratio.
4. Calculates the number of shares to buy for an equal-weight portfolio.
5. Implements a composite valuation metric (RV Score) to identify the best value stocks.
6. Selects the top 50 value stocks based on the RV Score.
7. Calculates the number of shares to buy for the final portfolio.
8. Creates visualizations to understand the distribution of price-to-earnings ratio and price vs. RV Score.
9. Saves the final portfolio data to an Excel file ('value_strategy.xlsx').

## Prerequisites

- Python 3.x
- Libraries: numpy, pandas, requests, xlsxwriter, math, scipy, yfinance (for time series analysis), matplotlib, seaborn

## Getting Started

1. Clone this repository: `git clone https://github.com/your-username/quantitative-value-strategy.git`
2. Navigate to the project directory: `cd quantitative-value-strategy`
3. Install the required libraries: `pip install -r requirements.txt`
4. Run the project: `python value_strategy_project.py`

## Usage

1. The script 'value_strategy_project.py' contains the complete project implementation.
2. Follow the instructions in the terminal to input your portfolio size.
3. The script will generate the final portfolio data and save it to 'value_strategy.xlsx'.
4. Visualizations will be displayed to help you understand the distribution of value metrics and portfolio performance.

## Notes

- The project uses the IEX Cloud API for fetching stock data. Make sure you have a valid API token from IEX Cloud.
- The calculations and metrics used in the project are for educational purposes and may not represent professional investment advice.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
 I thank FreeCodeCamp for helping me with the inspiration of this project, 
