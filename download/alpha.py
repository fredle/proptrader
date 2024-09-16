import requests
import pandas as pd
import time

# Your Alpha Vantage API key
api_key = '0132ATU9ZE2UC4QT'

# Symbol you want to get data for (e.g., MSFT)
symbol = 'AAPL'

# URL for Alpha Vantage Intraday API
url = f'https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={symbol}&interval=1min&outputsize=full&apikey={api_key}'

# Make a request to the API
response = requests.get(url)
data = response.json()

# Parse the intraday time series data
time_series = data.get("Time Series (1min)", {})

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
df.to_csv(f'sampledata/{symbol}_intraday_data.csv')

