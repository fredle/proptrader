# rsi_strategy.py

import pandas as pd
from strategies.base_strategy import BaseStrategy

class RSIStrategy(BaseStrategy):
    def __init__(self, data, period=14, overbought=70, oversold=30):
        super().__init__(data)
        self.period = period
        self.overbought = overbought
        self.oversold = oversold

    def generate_signal(self, data):
        self.data = data
        df = pd.DataFrame(self.data)
        delta = df['Last Price'].diff()
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)

        avg_gain = gain.rolling(self.period).mean()
        avg_loss = loss.rolling(self.period).mean()

        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))

        df['RSI'] = rsi

        if df['RSI'].iloc[-1] > self.overbought:
            return 'SELL'
        elif df['RSI'].iloc[-1] < self.oversold:
            return 'BUY'
        return 'HOLD'
