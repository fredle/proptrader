import requests
import pandas as pd
import time
import datetime

# Your Alpha Vantage API key
#api_key = '0132ATU9ZE2UC4QT'
api_key = 'OUDNF4LALFRLZI78'
# Symbol you want to get data for (e.g., MSFT)
symbol = 'BTC'
interval = "15min"
month = "2024-09"
# URL for Alpha Vantage Intraday API
url = f'https://www.alphavantage.co/query?function=DIGITAL_CURRENCY_INTRADAY&month={month}&symbol={symbol}&interval={interval}&outputsize=full&apikey={api_key}'
#url = f"https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&from_currency={symbol}&to_currency=USD&interval={interval}&outputsize=full&apikey={api_key}"

print(url)
# Make a request to the API
response = requests.get(url)
data = response.json()
print(data)

# Parse the intraday time series data

time_series = data.get(f"Time Series ({interval})", {})

# Convert the data to a pandas DataFrame
df = pd.DataFrame.from_dict(time_series, orient='index')

# Rename columns to something more understandable
df.columns = ['Open', 'High', 'Low', 'Close', 'Volume']

# Convert the index to datetime and sort it in ascending order
df.index = pd.to_datetime(df.index)

# Create a 'Datetime' column from the index
df['Datetime'] = df.index

df = df.sort_index()


# Display the first few rows of data
print(df.head())

# Optionally save to a CSV file
# Get today's date in yyyy-MM-dd format
today = datetime.date.today().strftime('%Y-%m-%d')

# Save DataFrame to a CSV file with today's date in the filename
df.to_csv(f'sampledata/{symbol}_{interval}_intraday_data_{month}.csv')

