from ib_insync import *

# Connect to Interactive Brokers (TWS or IB Gateway)
ib = IB()
ib.connect('127.0.0.1', 7497, clientId=1)  # Use port 7497 for paper trading, 7496 for live trading

contract = Crypto('BTC', 'PAXOS', 'USD')

# Request market data
ticker = ib.reqMktData(contract)

# Callback function to handle live updates
def onPendingTickers(tickers):
    for ticker in tickers:
        print(f"Symbol: {ticker.contract.symbol}")
        print(f"Last Price: {ticker.last}")
        print(f"Bid: {ticker.bid}")
        print(f"Ask: {ticker.ask}")
        print("-" * 30)

# Register the callback
ib.pendingTickersEvent += onPendingTickers

# Keep the connection alive to receive streaming data
ib.run()