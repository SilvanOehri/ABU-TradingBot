"""
Technische Indikatoren für Trading Strategien
"""

from typing import List, Tuple

class TechnicalIndicators:
    """
    Klasse mit statischen Methoden für technische Indikatoren
    """
    
    @staticmethod
    def sma(prices: List[float], period: int) -> float:
        """Berechnet Simple Moving Average"""
        if len(prices) < period:
            return prices[-1] if prices else 0
        return sum(prices[-period:]) / period
    
    @staticmethod
    def ema(prices: List[float], period: int) -> float:
        """Berechnet Exponential Moving Average"""
        if len(prices) < period:
            return prices[-1] if prices else 0
        
        multiplier = 2 / (period + 1)
        ema = prices[0]
        
        for price in prices[1:]:
            ema = (price * multiplier) + (ema * (1 - multiplier))
        
        return ema
    
    @staticmethod
    def rsi(prices: List[float], period: int = 14) -> float:
        """Berechnet Relative Strength Index"""
        if len(prices) < period + 1:
            return 50  # Neutral
        
        gains = []
        losses = []
        
        for i in range(1, len(prices)):
            change = prices[i] - prices[i-1]
            if change > 0:
                gains.append(change)
                losses.append(0)
            else:
                gains.append(0)
                losses.append(-change)
        
        avg_gain = sum(gains[-period:]) / period
        avg_loss = sum(losses[-period:]) / period
        
        if avg_loss == 0:
            return 100
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    @staticmethod
    def macd(prices: List[float], fast: int = 12, slow: int = 26) -> float:
        """Berechnet MACD (Moving Average Convergence Divergence)"""
        if len(prices) < slow:
            return 0
        
        ema_fast = TechnicalIndicators.ema(prices, fast)
        ema_slow = TechnicalIndicators.ema(prices, slow)
        
        return ema_fast - ema_slow
    
    @staticmethod
    def bollinger_bands(prices: List[float], period: int = 20, std_dev: float = 2) -> Tuple[float, float, float]:
        """Berechnet Bollinger Bands (upper, middle, lower)"""
        if len(prices) < period:
            current_price = prices[-1] if prices else 0
            return current_price, current_price, current_price
        
        sma = TechnicalIndicators.sma(prices, period)
        recent_prices = prices[-period:]
        
        # Standardabweichung berechnen
        variance = sum((price - sma) ** 2 for price in recent_prices) / period
        std = variance ** 0.5
        
        upper_band = sma + (std_dev * std)
        lower_band = sma - (std_dev * std)
        
        return upper_band, sma, lower_band
    
    @staticmethod
    def stochastic(prices: List[float], period: int = 14) -> float:
        """Berechnet Stochastic Oscillator"""
        if len(prices) < period:
            return 50
        
        recent_prices = prices[-period:]
        lowest_low = min(recent_prices)
        highest_high = max(recent_prices)
        
        if highest_high == lowest_low:
            return 50
        
        k_percent = ((prices[-1] - lowest_low) / (highest_high - lowest_low)) * 100
        return k_percent
    
    @staticmethod
    def momentum(prices: List[float], period: int = 10) -> float:
        """Berechnet Momentum (prozentuale Veränderung)"""
        if len(prices) < period:
            return 0
        
        return ((prices[-1] - prices[-period]) / prices[-period]) * 100
