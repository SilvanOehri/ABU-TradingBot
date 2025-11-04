"""
Weitere Trading Strategien
"""

from typing import List, Literal
from .base_strategy import BaseStrategy
from ..utils.technical_indicators import TechnicalIndicators

class EMAStrategy(BaseStrategy):
    """EMA Crossover Strategie"""
    
    def __init__(self, short_period: int = 12, long_period: int = 26):
        super().__init__("EMA", "⚡")
        self.short_period = short_period
        self.long_period = long_period
    
    def calculate_signal(self, prices: List[float]) -> Literal['buy', 'sell', 'hold']:
        if len(prices) < self.long_period:
            return 'hold'
        
        ema_short = TechnicalIndicators.ema(prices, self.short_period)
        ema_long = TechnicalIndicators.ema(prices, self.long_period)
        
        if ema_short > ema_long:
            return 'buy'
        elif ema_short < ema_long:
            return 'sell'
        else:
            return 'hold'

class MACDStrategy(BaseStrategy):
    """MACD Strategie"""
    
    def __init__(self, fast: int = 12, slow: int = 26):
        super().__init__("MACD", "🎯")
        self.fast = fast
        self.slow = slow
    
    def calculate_signal(self, prices: List[float]) -> Literal['buy', 'sell', 'hold']:
        if len(prices) < self.slow:
            return 'hold'
        
        macd = TechnicalIndicators.macd(prices, self.fast, self.slow)
        
        if macd > 0:
            return 'buy'
        elif macd < 0:
            return 'sell'
        else:
            return 'hold'

class BollingerStrategy(BaseStrategy):
    """Bollinger Bands Strategie"""
    
    def __init__(self, period: int = 20, std_dev: float = 2):
        super().__init__("Bollinger", "🔔")
        self.period = period
        self.std_dev = std_dev
    
    def calculate_signal(self, prices: List[float]) -> Literal['buy', 'sell', 'hold']:
        if len(prices) < self.period:
            return 'hold'
        
        upper, middle, lower = TechnicalIndicators.bollinger_bands(prices, self.period, self.std_dev)
        current_price = prices[-1]
        
        if current_price <= lower:
            return 'buy'
        elif current_price >= upper:
            return 'sell'
        else:
            return 'hold'

class StochasticStrategy(BaseStrategy):
    """Stochastic Oscillator Strategie"""
    
    def __init__(self, period: int = 14, oversold: float = 20, overbought: float = 80):
        super().__init__("Stochastic", "📡")
        self.period = period
        self.oversold = oversold
        self.overbought = overbought
    
    def calculate_signal(self, prices: List[float]) -> Literal['buy', 'sell', 'hold']:
        if len(prices) < self.period:
            return 'hold'
        
        stoch = TechnicalIndicators.stochastic(prices, self.period)
        
        if stoch < self.oversold:
            return 'buy'
        elif stoch > self.overbought:
            return 'sell'
        else:
            return 'hold'

class MomentumStrategy(BaseStrategy):
    """Momentum Strategie"""
    
    def __init__(self, period: int = 10, threshold: float = 5):
        super().__init__("Momentum", "🚀")
        self.period = period
        self.threshold = threshold
    
    def calculate_signal(self, prices: List[float]) -> Literal['buy', 'sell', 'hold']:
        if len(prices) < self.period:
            return 'hold'
        
        momentum = TechnicalIndicators.momentum(prices, self.period)
        
        if momentum > self.threshold:
            return 'buy'
        elif momentum < -self.threshold:
            return 'sell'
        else:
            return 'hold'

class MeanReversionStrategy(BaseStrategy):
    """Mean Reversion Strategie"""
    
    def __init__(self, period: int = 20, threshold: float = 10):
        super().__init__("Mean Reversion", "🔄")
        self.period = period
        self.threshold = threshold
    
    def calculate_signal(self, prices: List[float]) -> Literal['buy', 'sell', 'hold']:
        if len(prices) < self.period:
            return 'hold'
        
        avg = TechnicalIndicators.sma(prices, self.period)
        current_price = prices[-1]
        
        deviation = ((current_price - avg) / avg) * 100
        
        if deviation < -self.threshold:  # Weit unter Durchschnitt
            return 'buy'
        elif deviation > self.threshold:  # Weit über Durchschnitt
            return 'sell'
        else:
            return 'hold'
