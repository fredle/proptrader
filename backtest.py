import pandas as pd
from rsimacd_strategy import RSIMACDStrategy
from historicaldata_interface import HistoricalDataInterface

def backtest_strategy(strategy_class, data_file, parameter_grid, initial_balance=100000, commission_per_trade=2.0, order_size=10000):
    results = []

    for params in parameter_grid:
        # Initialize strategy and data interface
        data_interface = HistoricalDataInterface(data_file, order_size)
        strategy = strategy_class(data=[], **params)

        # Trading variables
        balance = initial_balance
        current_position = None
        total_commission = 0.0
        total_trades = 0
        trade_log = []
        live_data = []

        while True:
            try:
                new_price = data_interface.get_live_data()
            except IndexError:
                # End of data
                break

            if not pd.isna(new_price):
                live_data.append({'Last Price': new_price})
                if len(live_data) > 50:
                    live_data.pop(0)

                signal = strategy.generate_signal(live_data)

                # Handle buy signal
                if signal == 'BUY' and current_position is None:
                    execution_price = data_interface.place_order('BUY')
                    current_position = execution_price
                    balance -= commission_per_trade
                    total_trades += 1
                    total_commission += commission_per_trade

                    trade_log.append({
                        'type': 'BUY',
                        'price': new_price,
                        'execution_price': execution_price,
                        'pnl': '',
                        'balance': balance
                    })

                # Handle sell signal
                elif signal == 'SELL' and current_position is not None:
                    execution_price = data_interface.place_order('SELL')
                    pnl = (execution_price - current_position) * data_interface.order_size - (2 * commission_per_trade)
                    balance += pnl - commission_per_trade
                    total_trades += 1
                    total_commission += commission_per_trade

                    trade_log.append({
                        'type': 'SELL',
                        'price': new_price,
                        'execution_price': execution_price,
                        'pnl': pnl,
                        'balance': balance
                    })

                    current_position = None

        # Calculate performance metrics
        net_profit = balance - initial_balance
        return_percentage = (net_profit / initial_balance) * 100
        results.append({
            'params': params,
            'net_profit': net_profit,
            'return_percentage': return_percentage,
            'total_trades': total_trades,
            'total_commission': total_commission
        })

    return pd.DataFrame(results)

# Define a grid of parameters to test
parameter_grid = [
    {'rsi_period': 14, 'overbought': 70, 'oversold': 30, 'macd_fast': 12, 'macd_slow': 26, 'macd_signal': 9},
    {'rsi_period': 10, 'overbought': 80, 'oversold': 20, 'macd_fast': 10, 'macd_slow': 20, 'macd_signal': 7},
    # Add more parameter combinations as needed
]

# Run backtesting
results_df = backtest_strategy(RSIMACDStrategy, 'sampledata/GBPJPY=X_1y_1h_intraday_last_week.csv', parameter_grid, order_size=500)
print(results_df)