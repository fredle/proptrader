import pandas as pd

class HistoricalDataInterface:
    def __init__(self, csv_file, order_size, spread=0.0001):
        # Load historical data from CSV
        self.data = pd.read_csv(csv_file)
        self.current_index = 0
        self.order_size = order_size
        self.last_row = None
        self.spread = spread  # Spread in price terms (e.g., 0.0001 for 1 pip)
    
    def get_live_data(self):
        # Simulate getting historical data by advancing through the CSV
        if self.current_index >= len(self.data):
            raise IndexError("End of historical data.")
        
        row = self.data.iloc[self.current_index]
        self.current_index += 1
        self.last_row = row

        # Return Close, High, and Low as a dictionary
        return {'Last Price': row['Close'], 'High': row['High'], 'Low': row['Low']}
    
    def place_order(self, action):
        # Simulate placing an order with spread included
        execution_price = None
        mid_price = self.last_row['Close']  # Use the closing price as the mid-price

        if action.lower() == 'buy':
            # Buy at the ask price (mid_price + half the spread)
            execution_price = mid_price + (self.spread / 2)
        elif action.lower() == 'sell':
            # Sell at the bid price (mid_price - half the spread)
            execution_price = mid_price - (self.spread / 2)
        else:
            raise ValueError("Action must be 'buy' or 'sell'")

        return execution_price

    def reset(self):
        # Reset to the start of historical data
        self.current_index = 0
