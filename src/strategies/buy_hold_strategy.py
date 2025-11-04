"""
Buy & Hold Trading Strategie
"""

from typing import List, Literal
from .base_strategy import BaseStrategy

class BuyAndHoldStrategy(BaseStrategy):
    """
    Buy & Hold Strategie
    - Kauft einmal am Anfang und hält die Position
    """
    
    def __init__(self):
        super().__init__("Buy & Hold", "💎")
        self.has_bought = False
    
    def calculate_signal(self, prices: List[float]) -> Literal['buy', 'sell', 'hold']:
        if not self.has_bought and len(prices) > 0:
            self.has_bought = True
            return 'buy'
        return 'hold'
    
    def reset(self):
        super().reset()
        self.has_bought = False
