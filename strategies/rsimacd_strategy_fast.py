# combined_strategy.py

import pandas as pd
from strategies.base_strategy import BaseStrategy
class RSIMACDStrategyFast(BaseStrategy):
    #def __init__(self, data, rsi_period=7, overbought=65, oversold=35, macd_fast=5, macd_slow=13, macd_signal=4):
    def __init__(self, data, rsi_period=5, overbought=70, oversold=30, macd_fast=3, macd_slow=8, macd_signal=2):
        super().__init__(data)
        self.rsi_period = rsi_period
        self.overbought = overbought
        self.oversold = oversold
        self.macd_fast = macd_fast
        self.macd_slow = macd_slow
        self.macd_signal = macd_signal

    def generate_signal(self, data):
        self.data = data
        df = pd.DataFrame(self.data)

        # Calculate RSI
        delta = df['Last Price'].diff()
        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)
        avg_gain = gain.ewm(span=self.rsi_period, adjust=False).mean()
        avg_loss = loss.ewm(span=self.rsi_period, adjust=False).mean()
        rs = avg_gain / avg_loss
        df['RSI'] = 100 - (100 / (1 + rs))

        # Calculate MACD
        exp1 = df['Last Price'].ewm(span=self.macd_fast, adjust=False).mean()
        exp2 = df['Last Price'].ewm(span=self.macd_slow, adjust=False).mean()
        macd = exp1 - exp2
        signal_line = macd.ewm(span=self.macd_signal, adjust=False).mean()
        df['MACD'] = macd
        df['Signal Line'] = signal_line

        # Generate combined signal
        last_rsi = df['RSI'].iloc[-1]
        last_macd = df['MACD'].iloc[-1]
        last_signal = df['Signal Line'].iloc[-1]
        
        if last_rsi < self.oversold and last_macd > last_signal:
            return 'BUY'
        elif last_rsi > self.overbought and last_macd < last_signal:
            return 'SELL'
        else:
            return 'HOLD'
