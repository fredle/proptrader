import csv
import os
import math
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from ibkr_interface import IBKRInterface
from historicaldata_interface import HistoricalDataInterface
from strategies.sma_strategy import SMAStrategy
from strategies.sma_strategy_reverse import SMAStrategyReverse
from strategies.rsi_strategy import RSIStrategy
from ib_insync import Forex
from ib_insync import Stock
from chart_utils import update_chart
from tradedistribution import plot_pnl_distribution
from strategies.rsimacd_strategy import RSIMACDStrategy
from strategies.rsimacd_strategy_fast import RSIMACDStrategyFast
from strategies.logistic_regression_strategy import LogisticRegressionStrategy

# Function to calculate P&L
def calculate_pnl(buy_price, sell_price, size, commission):
    return (sell_price - buy_price) * size - (2 * commission)

# Main trading loop
def run_trading(strategy, ibkr, session_file, balance=100000, display_chart=True, logging_prices=True, logging_trades=True, stop_loss_percent=0.025, profit_taker_percent=0.05):
    prices, buys, sells, live_data = [], [], [], []
    current_position = None
    stop_loss_price = None
    profit_taker_price = None
    commission_per_trade = 2.0
    total_trades = 0
    total_commission = 0.0
    order_size = ibkr.order_size
    trade_log = []
    last_trade_index = None  # To store the index of the last trade

    if display_chart:
        from chart_utils import initialize_chart, update_chart
        fig, ax, prices_line, buys_scatter, sells_scatter, N = initialize_chart(400)

    try:
        while True:
            try:
                new_quote = ibkr.get_live_data()
                last_price = new_quote['Last Price']
            except IndexError:
                # End of data
                break

            if not math.isnan(last_price):
                live_data.append(new_quote)
                if len(live_data) > 50:
                    live_data.pop(0)

                signal = strategy.generate_signal(live_data)
                if logging_prices:
                    print(f"New Price: {last_price}, Signal: {signal}")

                trade_periods = 0  # To track the periods between trades

                if current_position is not None:
                    # Stop loss condition
                    if (current_position > 0 and last_price <= stop_loss_price) or (current_position < 0 and last_price >= stop_loss_price):
                        
                        print(f'Stop Loss triggered {current_position} {last_price} {stop_loss_price}')
                        execution_price = ibkr.place_order('SELL' if current_position > 0 else 'BUY')
                        sells.append(len(prices) if current_position > 0 else None)
                        pnl = calculate_pnl(current_position, execution_price, order_size, commission_per_trade)
                        balance += pnl - commission_per_trade
                        total_trades += 1
                        total_commission += commission_per_trade

                        if last_trade_index is not None:
                            trade_periods = len(prices) - last_trade_index  # Calculate periods since the last trade

                        trade_log.append({
                            'type': 'STOP LOSS',
                            'price': last_price,
                            'executionprice': execution_price,
                            'pnl': pnl,
                            'balance': balance,
                            'periods_between_trades': trade_periods
                        })

                        last_trade_index = len(prices)  # Update the last trade index

                        if logging_trades:
                            print(f"Stop Loss triggered. Profit/Loss: {pnl}, New Balance: {balance}")

                        current_position = None
                        stop_loss_price = None
                        profit_taker_price = None
                        continue  # Skip to next price, trade is closed

                    # Profit taker condition
                    if (current_position > 0 and last_price >= profit_taker_price) or (current_position < 0 and last_price <= profit_taker_price):
                        execution_price = ibkr.place_order('SELL' if current_position > 0 else 'BUY')
                        sells.append(len(prices) if current_position > 0 else None)
                        pnl = calculate_pnl(current_position, execution_price, order_size, commission_per_trade)
                        balance += pnl - commission_per_trade
                        total_trades += 1
                        total_commission += commission_per_trade

                        if last_trade_index is not None:
                            trade_periods = len(prices) - last_trade_index  # Calculate periods since the last trade

                        trade_log.append({
                            'type': 'PROFIT TAKER',
                            'price': last_price,
                            'executionprice': execution_price,
                            'pnl': pnl,
                            'balance': balance,
                            'periods_between_trades': trade_periods
                        })

                        last_trade_index = len(prices)  # Update the last trade index

                        if logging_trades:
                            print(f"Profit Taker triggered. Profit/Loss: {pnl}, New Balance: {balance}")

                        current_position = None
                        stop_loss_price = None
                        profit_taker_price = None
                        continue  # Skip to next price, trade is closed

                # Handle buy signal
                if signal == 'BUY' and current_position is None:
                    execution_price = ibkr.place_order('BUY')
                    buys.append(len(prices))
                    current_position = execution_price
                    stop_loss_price = execution_price * (1 - stop_loss_percent)  # Set stop loss below buy price
                    profit_taker_price = execution_price * (1 + profit_taker_percent)  # Set profit taker above buy price
                    balance -= commission_per_trade
                    total_trades += 1
                    total_commission += commission_per_trade

                    if last_trade_index is not None:
                        trade_periods = len(prices) - last_trade_index  # Calculate periods since the last trade

                    trade_log.append({
                        'type': 'BUY',
                        'price': last_price,
                        'executionprice': execution_price,
                        'pnl': '',
                        'balance': balance,
                        'stop_loss': stop_loss_price,
                        'profit_taker': profit_taker_price,
                        'periods_between_trades': trade_periods
                    })

                    last_trade_index = len(prices)  # Update the last trade index
                    if logging_trades:
                        print(f"BUY. last_price: {last_price}, execution_price : {execution_price}, New Balance: {balance}")

                # Handle sell signal
                elif signal == 'SELL' and current_position is not None:
                    execution_price = ibkr.place_order('SELL')
                    sells.append(len(prices))
                    pnl = calculate_pnl(current_position, execution_price, order_size, commission_per_trade)
                    balance += pnl - commission_per_trade
                    total_trades += 1
                    total_commission += commission_per_trade

                    if last_trade_index is not None:
                        trade_periods = len(prices) - last_trade_index  # Calculate periods since the last trade

                    trade_log.append({
                        'type': 'SELL',
                        'price': last_price,
                        'executionprice': execution_price,
                        'pnl': pnl,
                        'balance': balance,
                        'periods_between_trades': trade_periods
                    })

                    last_trade_index = len(prices)  # Update the last trade index

                    if logging_trades:
                        print(f"SELL: last_price: {last_price}, execution_price : {execution_price}, New Balance: {balance}, Profit/Loss: {pnl}, New Balance: {balance}")

                    current_position = None
                    stop_loss_price = None
                    profit_taker_price = None

                prices.append(last_price)

            
            # Update chart if needed
            if display_chart:
                update_chart(ax, prices_line, buys_scatter, sells_scatter, prices, buys, sells, balance, N)
    except KeyboardInterrupt:
        print("Trading interrupted by user")

    
    # Write trade logs to CSV after the loop completes
    with open(session_file, mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=['type', 'price', 'executionprice', 'pnl', 'balance', 'stop_loss', 'profit_taker', 'periods_between_trades'])
        writer.writeheader()
        for trade in trade_log:
            writer.writerow(trade)

    # Print final trade statistics
    print(f"Final Balance: {balance}")
    print(f"Total Trades: {total_trades}")
    print(f"Total Commission Cost: {total_commission:.2f}")


if __name__ == "__main__":
    #contract = Forex('GBPUSD')
    contract = Stock('AAPL', 'SMART', 'USD')
    order_size = 100
    ibkr = IBKRInterface(contract, order_size)  # Initialize broker connection
    #ibkr = HistoricalDataInterface("sampledata/MSFT_5d_1m_intraday_last_week.csv", order_size)  # Initialize broker connection
    #ibkr = HistoricalDataInterface("sampledata/msft_intraday_data.csv", order_size)  # Initialize broker connection

    #strategy = RSIMACDStrategy(data=[], rsi_period=14, overbought=70, oversold=30, macd_fast=12, macd_slow=26, macd_signal=9)
    #strategy = RSIMACDStrategyFast(data=[])
    strategy = LogisticRegressionStrategy(data=[])
    #strategy = RSIStrategy(data=[], period=14, overbought=70, oversold=30)
    # strategy = SMAStrategy(data=[], short_window=9, long_window=26)
    # strategy = SMAStrategyReverse(data=[], short_window=9, long_window=21)

    # Generate a unique file name using the timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    session_file = f"sessions/trades_{timestamp}.csv"
    os.makedirs('sessions', exist_ok=True)

    run_trading(strategy, ibkr, session_file, display_chart=True, logging_prices=True, logging_trades=True, stop_loss_percent=0.02, profit_taker_percent=0.08)

    # Plot P&L distribution
    plot_pnl_distribution(session_file)
