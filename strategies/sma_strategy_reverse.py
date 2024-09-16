# sma_strategy.py

import pandas as pd
from strategies.base_strategy import BaseStrategy

class SMAStrategyReverse(BaseStrategy):
    def __init__(self, data, short_window=9, long_window=21):
        super().__init__(data)
        self.short_window = short_window
        self.long_window = long_window

    def generate_signal(self, data):
        self.data = data
        df = pd.DataFrame(self.data)
        if df.empty:
            return 'HOLD'
        
        #print(df['Last Price'])
        df['SMA_9'] = df['Last Price'].rolling(window=self.short_window).mean()
        df['SMA_21'] = df['Last Price'].rolling(window=self.long_window).mean()
        

        if df['SMA_9'].iloc[-1] > df['SMA_21'].iloc[-1] and df['SMA_9'].iloc[-2] <= df['SMA_21'].iloc[-2]:
            return 'SELL'
        elif df['SMA_9'].iloc[-1] < df['SMA_21'].iloc[-1] and df['SMA_9'].iloc[-2] >= df['SMA_21'].iloc[-2]:
            return 'BUY'
        return 'HOLD'


