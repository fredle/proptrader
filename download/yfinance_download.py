import yfinance as yf
import pandas as pd
from datetime import datetime

# Define the ticker symbol
ticker = "BTC-USD"
period = "1mo"
interval = "15m"
month = "2024-07"
# Calculate start and end dates based on the month
start = f"{month}-01"
end_date = datetime.strptime(start, "%Y-%m-%d").replace(day=28) + pd.DateOffset(days=4)
end = (end_date - pd.DateOffset(days=end_date.day)).strftime("%Y-%m-%d")

#start = "2024-07-23"

# Download intraday data for the last 5 business days (market days)
#data = yf.download(ticker, period=period, interval=interval)
data = yf.download(ticker, start=start, end=end, interval=interval)

# Check if the data is not empty
if not data.empty:
    print(f'Intraday data for {ticker} (High/Low)')
    print(data[['High', 'Low']].tail())  # Display the High and Low columns
    
    # Optionally save the data to CSV
    data.to_csv(f'sampledata/{ticker}_{period}_{interval}_{month}_intraday.csv')
else:
    print("No data available. Check your parameters or internet connection.")