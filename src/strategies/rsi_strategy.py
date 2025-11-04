"""
RSI Trading Strategie
"""

from typing import List, Literal
from .base_strategy import BaseStrategy
from ..utils.technical_indicators import TechnicalIndicators

class RSIStrategy(BaseStrategy):
    """
    RSI (Relative Strength Index) Strategie
    - Kaufen wenn RSI < 30 (überverkauft)
    - Verkaufen wenn RSI > 70 (überkauft)
    """
    
    def __init__(self, rsi_period: int = 14, oversold: float = 30, overbought: float = 70):
        super().__init__("RSI", "📊")
        self.rsi_period = rsi_period
        self.oversold = oversold
        self.overbought = overbought
    
    def calculate_signal(self, prices: List[float]) -> Literal['buy', 'sell', 'hold']:
        if len(prices) < self.rsi_period + 1:
            return 'hold'
        
        rsi = TechnicalIndicators.rsi(prices, self.rsi_period)
        
        if rsi < self.oversold:  # Überverkauft
            return 'buy'
        elif rsi > self.overbought:  # Überkauft
            return 'sell'
        else:
            return 'hold'
