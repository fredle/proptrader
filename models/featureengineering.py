

def calculate_rsi(data, window=14):
    delta = data['Close'].diff(1)
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def calculate_macd(data, short_window=12, long_window=26, signal_window=9):
    # Short-term EMA (12-period)
    short_ema = data['Close'].ewm(span=short_window, adjust=False).mean()
    
    # Long-term EMA (26-period)
    long_ema = data['Close'].ewm(span=long_window, adjust=False).mean()
    
    # MACD Line
    macd_line = short_ema - long_ema
    
    # Signal Line (9-period EMA of MACD Line)
    signal_line = macd_line.ewm(span=signal_window, adjust=False).mean()
    
    # MACD Histogram (difference between MACD Line and Signal Line)
    macd_histogram = macd_line - signal_line
    
    return macd_line, signal_line, macd_histogram

def feature_engineering(data):
    # Feature: 10-period moving average
    data['MA10'] = data['Close'].rolling(window=10).mean()

    # Feature: 50-period moving average
    data['MA50'] = data['Close'].rolling(window=50).mean()

    # Feature: Close-to-Close percentage change
    data['Pct_Change'] = data['Close'].pct_change()

    # Feature: High-Low spread
    data['HL_Spread'] = data['High'] - data['Low']

    # Add RSI as a feature
    data['RSI'] = calculate_rsi(data)

    # Add MACD Line, Signal Line, and MACD Histogram as features
    data['MACD_Line'], data['Signal_Line'], data['MACD_Histogram'] = calculate_macd(data)

    # Calculate the percentage above/below current price for moving averages
    data['MA10_pct'] = (data['MA10'] - data['Close']) / data['Close'] * 100
    data['MA50_pct'] = (data['MA50'] - data['Close']) / data['Close'] * 100

    # Drop any rows with missing values due to moving averages
    data = data.dropna()

    return data

features = ['MA10_pct', 'MA50_pct', 'Pct_Change', 'HL_Spread', 'RSI', 'MACD_Line', 'Signal_Line', 'Volume']