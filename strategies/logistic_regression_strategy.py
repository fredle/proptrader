import pandas as pd
import joblib
from strategies.base_strategy import BaseStrategy
from sklearn.preprocessing import StandardScaler
from time import sleep

class LogisticRegressionStrategy(BaseStrategy):
    def __init__(self, data):
        super().__init__(data)

        self.model = joblib.load('models/logistic_regression_model.pkl')
        self.scaler = joblib.load('models/logistic_regression_scaler.pkl')
        self.holding_period = 0  # Counter to track holding periods
        self.position = None  # Track current position ('BUY', 'SELL', or 'HOLD')

    def generate_features(self, df):
        # Feature generation code remains the same
        if len(df) < 50:  # For example, we need at least 50 periods for the MA50 and RSI
            return None  # Not enough data, return None

        # Create the necessary features (SMA, RSI, MACD, etc.)
        df['MA10'] = df['Last Price'].rolling(window=10).mean()
        df['MA50'] = df['Last Price'].rolling(window=50).mean()
        df['Pct_Change'] = df['Last Price'].pct_change()
        df['HL_Spread'] = df['High'] - df['Low']
        
        # Convert MA10 and MA50 to percentage above/below the current price
        df['MA10_pct'] = (df['MA10'] - df['Last Price']) / df['Last Price'] * 100
        df['MA50_pct'] = (df['MA50'] - df['Last Price']) / df['Last Price'] * 100

        # RSI calculation
        delta = df['Last Price'].diff(1)
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))

        # MACD calculation
        short_ema = df['Last Price'].ewm(span=12, adjust=False).mean()
        long_ema = df['Last Price'].ewm(span=26, adjust=False).mean()
        df['MACD_Line'] = short_ema - long_ema
        df['Signal_Line'] = df['MACD_Line'].ewm(span=9, adjust=False).mean()
        df['MACD_Histogram'] = df['MACD_Line'] - df['Signal_Line']

        # Convert MACD and Signal Line to percentages of the current price
        df['MACD_pct'] = df['MACD_Line'] / df['Last Price'] * 100
        df['Signal_pct'] = df['Signal_Line'] / df['Last Price'] * 100

        # Convert MACD Histogram to a percentage of the current price
        df['MACD_Histogram_pct'] = df['MACD_Histogram'] / df['Last Price'] * 100

        # Drop NaNs caused by rolling calculations
        df = df.dropna()

        # Define the features that need to be scaled
        features_to_scale = ['MA10_pct', 'MA50_pct', 'Pct_Change', 'HL_Spread', 'RSI', 'MACD_pct', 'Signal_pct', 'MACD_Histogram']

        data_scaled = df.copy()
        # Scale the selected features

        if df[features_to_scale].empty:
            return None
        
        data_scaled[features_to_scale] = self.scaler.transform(df[features_to_scale])

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
        features = ['MA10_pct', 'MA50_pct', 'Pct_Change', 'HL_Spread', 'RSI', 'MACD_pct', 'Signal_pct', 'MACD_Histogram']
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
