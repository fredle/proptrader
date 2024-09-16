import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Load the data from the CSV file
data = pd.read_csv('MSFT_intraday_last_week.csv', index_col='Datetime', parse_dates=True)

# Calculate moving averages
data['SMA_9'] = data['Close'].rolling(window=9).mean()  # Short-term moving average
data['SMA_21'] = data['Close'].rolling(window=21).mean()  # Long-term moving average

# Generate Buy/Sell signals based on moving average crossovers
data['Signal'] = np.where(data['SMA_9'] > data['SMA_21'], 1, 0)  # Buy signal when SMA_9 > SMA_21
data['Position'] = data['Signal'].diff()  # Find the points where the signal changes

# Plot the data with the buy/sell signals
plt.figure(figsize=(12, 6))
plt.plot(data['Close'], label='MSFT Price', alpha=0.5)
plt.plot(data['SMA_9'], label='9-period SMA', alpha=0.75)
plt.plot(data['SMA_21'], label='21-period SMA', alpha=0.75)
plt.plot(data[data['Position'] == 1].index, data['SMA_9'][data['Position'] == 1], '^', markersize=10, color='g', lw=0, label='Buy Signal')
plt.plot(data[data['Position'] == -1].index, data['SMA_9'][data['Position'] == -1], 'v', markersize=10, color='r', lw=0, label='Sell Signal')
plt.title('MSFT Price with Buy and Sell Signals')
plt.legend(loc='best')
plt.show()

# Backtesting to calculate potential profit/loss
initial_balance = 10000  # Starting balance in USD
position = 0  # No initial position (0 means no position, 1 means holding shares)
balance = initial_balance
trades = 0

# Simulate trading by going through the generated signals
for i in range(len(data)):
    if data['Position'][i] == 1 and position == 0:  # Buy signal
        position = balance / data['Close'][i]  # Buy as many shares as possible
        balance = 0
        trades += 1
        print(f"Buy at {data['Close'][i]:.2f}")
    elif data['Position'][i] == -1 and position > 0:  # Sell signal
        balance = position * data['Close'][i]  # Sell all shares
        position = 0
        trades += 1
        print(f"Sell at {data['Close'][i]:.2f}")

# If still holding a position, sell it at the last available price
if position > 0:
    balance = position * data['Close'].iloc[-1]  # Final sell at the last close price
    position = 0

# Print the results of the backtest
print(f"Initial balance: ${initial_balance}")
print(f"Final balance: ${balance:.2f}")
print(f"Total trades executed: {trades}")
