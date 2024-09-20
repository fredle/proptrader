import pandas as pd
import joblib
from strategies.base_strategy import BaseStrategy
from sklearn.preprocessing import StandardScaler
from time import sleep

from models.featureengineering import feature_engineering
from models.featureengineering import features

class LogisticRegressionStrategy(BaseStrategy):
    def __init__(self, data):
        super().__init__(data)

        self.model = joblib.load('models/logistic_regression_model.pkl')
        self.scaler = joblib.load('models/logistic_regression_scaler.pkl')
        self.holding_period = 0  # Counter to track holding periods
        self.position = None  # Track current position ('BUY', 'SELL', or 'HOLD')

    def generate_features(self, df):

        if len(df) < 50:  # For example, we need at least 50 periods for the MA50 and RSI
            return None  # Not enough data, return None

        expandeddata = feature_engineering(df)
        data_scaled = expandeddata.copy()
        data_scaled[features] = self.scaler.transform(expandeddata[features])
        return data_scaled


    def generate_signal(self, data):
        self.data = data
        df = pd.DataFrame(self.data)

        if df.empty:
            return 'HOLD'

        # Generate features
        df = self.generate_features(df)

        # If df is None, there's not enough data, so return 'HOLD'
        if df is None or df.empty:
            return 'HOLD'

        # Select the features the model was trained on
        features = ['MA10_pct', 'MA50_pct', 'Pct_Change', 'HL_Spread', 'RSI', 'MACD_Line', 'Signal_Line','Volume']
        X = df[features]

        # Ensure we have enough rows to make a prediction (at least one row of features)
        if X.empty or len(X) < 1:
            return 'HOLD'

        # Predict using the model
        prediction = self.model.predict(X)[-1]  # Predict on the latest row of data

        # Implement 3-period hold logic
        if self.holding_period > 0:
            self.holding_period -= 1
            return 'HOLD'  # Continue holding if in holding period

        if prediction == 1:  # Buy signal (price expected to go up)
            if self.position != 'BUY':
                self.position = 'BUY'
                self.holding_period = 4  # Start hold counter after a BUY
                return 'BUY'
        elif prediction == 0:  # Sell signal (price expected to go down)
            if self.position == 'BUY':  # Automatically sell after holding
                self.position = 'SELL'
                return 'SELL'
        
        return 'HOLD'
