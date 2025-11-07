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
        super().__init__(
            "RSI",
            description="Der RSI (Relative Strength Index) misst die Stärke von Preisbewegungen. "
                       "Kauft wird, wenn der Wert unter 30 fällt (überverkauft = günstiger Einstieg). "
                       "Verkauft wird bei über 70 (überkauft = Zeit zu verkaufen)."
        )
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
