"""
SMA Crossover Trading Strategie
"""

from typing import List, Literal
from .base_strategy import BaseStrategy
from ..utils.technical_indicators import TechnicalIndicators

class SMAStrategy(BaseStrategy):
    """
    SMA (Simple Moving Average) Crossover Strategie
    - Kaufen wenn kurzer SMA > langer SMA
    - Verkaufen wenn kurzer SMA < langer SMA
    """
    
    def __init__(self, short_period: int = 10, long_period: int = 30):
        super().__init__(
            "SMA",
            description="SMA (Simple Moving Average) vergleicht zwei Durchschnittspreise. "
                       "Wenn der kurzfristige (10 Tage) über den langfristigen (30 Tage) steigt, ist das ein Kaufsignal. "
                       "Wenn er darunter fällt, wird verkauft. Folgt dem Trend."
        )
        self.short_period = short_period
        self.long_period = long_period
    
    def calculate_signal(self, prices: List[float]) -> Literal['buy', 'sell', 'hold']:
        if len(prices) < self.long_period:
            return 'hold'
        
        sma_short = TechnicalIndicators.sma(prices, self.short_period)
        sma_long = TechnicalIndicators.sma(prices, self.long_period)
        
        if sma_short > sma_long:  # Golden Cross
            return 'buy'
        elif sma_short < sma_long:  # Death Cross
            return 'sell'
        else:
            return 'hold'
