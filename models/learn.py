import pandas as pd

# Load the CSV file, assuming it's saved as 'data.csv'
data = pd.read_csv('data.csv', parse_dates=['Datetime'], index_col='Datetime')

# Display the data to ensure it's loaded correctly
print(data.head())



# Feature: 10-period moving average
data['MA10'] = data['Close'].rolling(window=10).mean()

# Feature: 50-period moving average
data['MA50'] = data['Close'].rolling(window=50).mean()

# Feature: Close-to-Close percentage change
data['Pct_Change'] = data['Close'].pct_change()

# Feature: High-Low spread
data['HL_Spread'] = data['High'] - data['Low']

# Drop any rows with missing values due to moving averages
data = data.dropna()


# Target: If the next period's close price is higher than the current period's close, it's a buy signal (1), otherwise sell (0)
data['Target'] = (data['Close'].shift(-1) > data['Close']).astype(int)

# Drop the last row since it doesn't have a target value
data = data.dropna()

#4. Train-Test Split
#Before training the model, split your data into training and testing sets:

from sklearn.model_selection import train_test_split
# Define feature columns and target
features = ['MA10', 'MA50', 'Pct_Change', 'HL_Spread']
X = data[features]
y = data['Target']

# Split the data (80% train, 20% test)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)



#5. Train a Logistic Regression Model
#Logistic regression is a simple model you can use as a starting point:
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score