import time
from datetime import datetime, timedelta
from ib_insync import IB, MarketOrder
import math
from ib_insync import Stock

import requests
import pandas as pd
import yfinance as yf




class IBKRInterface:
    def __init__(self, contract, order_size=10000, time_frame=60, lookback_minutes=50):

        self.contract = contract
        # Retrieve historical data during initialization
        self.historical_data = self.get_historical_data_yfinance(lookback_minutes)

        self._historical_data_iter = iter(self.historical_data)

        self.ib = IB()
        try:
            self.ib.connect('127.0.0.1', 7497, clientId=1)
        except Exception as e:
            print(f"Connection failed: {e}")

        self.order_size = order_size
        self.time_frame = time_frame  # Time frame in seconds
        self.switched_to_live = False  # Flag to track live data switch



    def get_historical_data(self, lookback_minutes, bar_size='1 min'):
        """
        Retrieves historical data for the specified lookback period.
        """
        # Request historical data for the last N minutes
        lookback_seconds = lookback_minutes*60
        end_time = datetime.now()
        bars = self.ib.reqHistoricalData(
            self.contract,
            endDateTime=end_time,
            durationStr=f'{lookback_seconds} S',
            barSizeSetting=bar_size,
            whatToShow='MIDPOINT',  # Can also use 'BID', 'ASK', 'TRADES', etc.
            useRTH=True,  # Use Regular Trading Hours
            formatDate=1
        )
        
        # Extract and return OHLC data from the bars
        ohlc_data = [{
            'Datetime': bar.date.strftime('%Y-%m-%d %H:%M:%S'),
            'Open': bar.open,
            'High': bar.high,
            'Low': bar.low,
            'Close': bar.close
        } for bar in bars]
        
        print(f"Retrieved {len(ohlc_data)} historical data points.")
        return ohlc_data

    def get_historical_data_yfinance(self, lookback_minutes, interval='1m'):
        """
        Retrieves historical data for the specified lookback period from Yahoo Finance (via yfinance).
        """
        try:

            # Download historical data from Yahoo Finance
            data = yf.download(self.contract.symbol, period="1d", interval=interval)

            if data.empty:
                print("No historical data retrieved from yfinance.")
                return []

            # Reset index to access the 'Datetime' column easily
            data.reset_index(inplace=True)

            # Convert the DataFrame into a list of dictionaries (OHLC format)
            ohlc_data = [{
                'Datetime': row['Datetime'].strftime('%Y-%m-%d %H:%M:%S'),
                'Open': row['Open'],
                'High': row['High'],
                'Low': row['Low'],
                'Last Price': row['Close']
            } for _, row in data.iterrows()]

            print(f"Retrieved {len(ohlc_data)} historical data points from yfinance.")

            return ohlc_data[-lookback_minutes:]

        except Exception as e:
            print(f"Error retrieving historical data from yfinance: {e}")
            return []
        
    def get_live_data(self):

        try:
            # Return the next data point from the historical data
            data_point = next(self._historical_data_iter)
            return data_point
        
        except StopIteration:

            if not self.switched_to_live:
                print("Switching to live data collection...")
                self.switched_to_live = True  # Set flag to True after switching

            self.ib.qualifyContracts(self.contract)  # Ensures the contract is fully specified
            ticker = self.ib.reqMktData(self.contract)

            # Initialize OHLC values for live data
            open_price = None
            high_price = -float('inf')
            low_price = float('inf')
            close_price = None
            
            # Set the end time for the current OHLC period
            end_time = datetime.now() + timedelta(seconds=self.time_frame)
            
            while datetime.now() < end_time:
                # Get the current price
                self.ib.sleep(2)
                price = self._get_price(ticker)

                if price is None:
                    print("Failed to get price data. Retrying...")
                    continue

                # Set the open price if it's the first price in the time frame
                if open_price is None:
                    open_price = price

                # Track high and low prices
                high_price = max(high_price, price)
                low_price = min(low_price, price)

                # The most recent price is the close price
                close_price = price
                
            # Return the OHLC object at the end of the time frame
            ohlc_data = {
                'Datetime': end_time.strftime('%Y-%m-%d %H:%M:%S'),
                'Open': open_price,
                'High': high_price,
                'Low': low_price,
                'Last Price': close_price
            }
            
            return ohlc_data

    def _get_price(self, ticker):
        """
        Helper method to extract the current price from the ticker.
        """
        if ticker is None:
            return None
        
        if math.isnan(ticker.last):
            if ticker.bid and ticker.ask:
                return (ticker.bid + ticker.ask) / 2
            else:
                return None
        else:
            return ticker.last
    
    def place_order(self, action, timeout=30):
        """
        Place a market order with a timeout for filling the order.
        """
        order = MarketOrder(action, self.order_size)
        trade = self.ib.placeOrder(self.contract, order)
        
        start_time = datetime.now()
        while trade.orderStatus.status != 'Filled':
            self.ib.waitOnUpdate()
            if (datetime.now() - start_time).total_seconds() > timeout:
                print(f"Order not filled within {timeout} seconds. Cancelling order.")
                self.ib.cancelOrder(trade)
                return None
        
        # Return the executed price once the order is filled
        return trade.orderStatus.avgFillPrice

    def disconnect(self):
        if self.ib.isConnected():
            self.ib.disconnect()

# Example usage (called from an external class)
if __name__ == "__main__":

    # Define the stock contract (for MSFT in this case)
    contract = Stock('AAPL', 'SMART', 'USD')
    ibkr = IBKRInterface(contract=contract)
    
    # Now proceed with live data collection, after using historical data
    live_data = ibkr.get_historical_data_yfinance(lookback_minutes=50)
    
    print(live_data)

    # Example of placing an order
    # price = ibkr.place_order(action='BUY')
    
    # Disconnect IBKR
    ibkr.disconnect()
