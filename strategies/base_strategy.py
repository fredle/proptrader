# strategies/base_strategy.py

class BaseStrategy:
    def __init__(self, data):
        self.data = data  # Data for running the strategy
    
    def generate_signal(self):
        """
        Implement this method in every strategy.
        Returns 'BUY', 'SELL', or 'HOLD'.
        """
        raise NotImplementedError("Must implement generate_signal() in subclass")