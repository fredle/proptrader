# combined_strategy.py

import pandas as pd
from strategies.base_strategy import BaseStrategy

class RSIMACDStrategy(BaseStrategy):
    def __init__(self, data, rsi_period=14, overbought=70, oversold=30, macd_fast=12, macd_slow=26, macd_signal=9):
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
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        avg_gain = gain.rolling(self.rsi_period).mean()
        avg_loss = loss.rolling(self.rsi_period).mean()
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        df['RSI'] = rsi

        # Calculate MACD
        exp1 = df['Last Price'].ewm(span=self.macd_fast, adjust=False).mean()
        exp2 = df['Last Price'].ewm(span=self.macd_slow, adjust=False).mean()
        macd = exp1 - exp2
        signal_line = macd.ewm(span=self.macd_signal, adjust=False).mean()
        df['MACD'] = macd
        df['Signal Line'] = signal_line

        # Generate combined signal
        if df['RSI'].iloc[-1] < self.oversold and df['MACD'].iloc[-1] > df['Signal Line'].iloc[-1]:
            return 'BUY'
        elif df['RSI'].iloc[-1] > self.overbought and df['MACD'].iloc[-1] < df['Signal Line'].iloc[-1]:
            return 'SELL'
        else:
            return 'HOLD'
