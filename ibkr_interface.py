# brokers/ibkr_interface.py

from ib_insync import IB, MarketOrder
import math

class IBKRInterface:
    def __init__(self, contract, order_size=10000):
        self.ib = IB()
        self.ib.connect('127.0.0.1', 7497, clientId=1)
        self.contract = contract
        self.order_size = order_size

    def get_live_data(self):
        # Request live market data
        ticker = self.ib.reqMktData(self.contract)
        self.ib.sleep(1)  # Wait for data to populate
        
        if math.isnan(ticker.last):
            return (ticker.bid + ticker.ask) / 2
        else:
            return ticker.last

    def place_order(self, action):
        order = MarketOrder(action, self.order_size)
        trade = self.ib.placeOrder(self.contract, order)
        # Wait for the order to fill
        while trade.orderStatus.status != 'Filled':
            self.ib.waitOnUpdate()
        
        # Return the executed price once the order is filled
        return trade.orderStatus.avgFillPrice

    def disconnect(self):
        self.ib.disconnect()
