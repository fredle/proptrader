
from ib_insync import *

# Connect to IBKR's TWS or IB Gateway
ib = IB()
ib.connect('127.0.0.1', 7497, clientId=1)  # Port 7497 for paper trading, 7496 for live

# Define the stock contract (for MSFT in this case)
contract = Stock('MSFT', 'SMART', 'USD')

# Request market data for MSFT
ib.qualifyContracts(contract)  # Ensures the contract is fully specified
ticker = ib.reqMktData(contract)

# Wait for data to populate
ib.sleep(2)

# Print live market data
print(f"Symbol: {ticker.contract.symbol}")
print(f"Last price: {ticker.last}")
print(f"Bid: {ticker.bid}")
print(f"Ask: {ticker.ask}")

# Disconnect
ib.disconnect()