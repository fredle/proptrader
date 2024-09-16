import yfinance as yf
import pandas as pd

# Define the ticker symbol
ticker = "GBPUSD=X"
period = "5d"
interval = "1m"

# Download intraday data for the last 5 business days (market days)
data = yf.download(ticker, period=period, interval=interval)

# Check if the data is not empty
if not data.empty:
    print(f'Intraday data for {ticker} (High/Low)')
    print(data[['High', 'Low']].tail())  # Display the High and Low columns
    
    # Optionally save the data to CSV
    data.to_csv(f'sampledata/{ticker}_{period}_{interval}_intraday_last_week.csv')
else:
    print("No data available. Check your parameters or internet connection.")