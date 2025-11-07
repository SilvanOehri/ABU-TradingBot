"""
Weitere Trading Strategien
"""

from typing import List, Literal
from .base_strategy import BaseStrategy
from ..utils.technical_indicators import TechnicalIndicators

class EMAStrategy(BaseStrategy):
    """EMA Crossover Strategie"""
    
    def __init__(self, short_period: int = 12, long_period: int = 26):
        super().__init__(
            "EMA",
            description="EMA (Exponential Moving Average) funktioniert wie SMA, reagiert aber schneller auf neue Preise. "
                       "Kauft bei steigendem Trend, verkauft bei fallendem. Besser für volatile Märkte."
        )
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
        super().__init__(
            "MACD",
            description="MACD (Moving Average Convergence Divergence) zeigt Trendwechsel an. "
                       "Wenn die MACD-Linie nach oben kreuzt, ist das ein Kaufsignal. "
                       "Kreuzt sie nach unten, wird verkauft. Gut für Trendfolge."
        )
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
        super().__init__(
            "Bollinger",
            description="Bollinger Bands zeigen einen 'Kanal' um den Durchschnittspreis. "
                       "Wenn der Preis das untere Band berührt, ist es günstig (kaufen). "
                       "Beim oberen Band ist es teuer (verkaufen). Nutzt Volatilität aus."
        )
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
        super().__init__(
            "Stochastic",
            description="Stochastic Oscillator vergleicht den aktuellen Preis mit der Preisspanne. "
                       "Unter 20 = überverkauft, Zeit zum Kaufen. "
                       "Über 80 = überkauft, Zeit zum Verkaufen. Ähnlich wie RSI."
        )
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
    
    def __init__(self, period: int = 20, threshold: float = 2.0):
        super().__init__(
            "Momentum",
            description="Momentum misst, wie schnell sich der Preis verändert. "
                       "Steigt der Preis stark = kaufen (Trend ist dein Freund). "
                       "Fällt der Preis stark = verkaufen. Basiert auf der Idee: Was steigt, steigt weiter."
        )
        self.period = period
        self.threshold = threshold
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
    
    def __init__(self, period: int = 20, threshold: float = 2.5):
        super().__init__(
            "Mean Reversion",
            description="Mean Reversion geht davon aus, dass Preise zum Durchschnitt zurückkehren. "
                       "Ist der Preis weit unter dem Durchschnitt = kaufen (wird wieder steigen). "
                       "Weit darüber = verkaufen (wird wieder fallen). Gegenstrategie zu Momentum."
        )
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
