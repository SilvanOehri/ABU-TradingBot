"""
Konfiguration für den Trading Bot
"""

from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class TradingConfig:
    """
    Konfiguration für Trading Bot Parameter
    """
    # Allgemeine Einstellungen
    symbol: str = "BTC-USD"
    initial_capital: float = 100000.0
    backtest_days: int = 365 * 5  # 5 Jahre
    
    # RSI Einstellungen
    rsi_period: int = 14
    rsi_oversold: float = 30
    rsi_overbought: float = 70
    
    # SMA Einstellungen
    sma_short_period: int = 10
    sma_long_period: int = 30
    
    # EMA Einstellungen
    ema_short_period: int = 12
    ema_long_period: int = 26
    
    # MACD Einstellungen
    macd_fast: int = 12
    macd_slow: int = 26
    
    # Bollinger Bands Einstellungen
    bollinger_period: int = 20
    bollinger_std_dev: float = 2.0
    
    # Stochastic Einstellungen
    stochastic_period: int = 14
    stochastic_oversold: float = 20
    stochastic_overbought: float = 80
    
    # Momentum Einstellungen
    momentum_period: int = 10
    momentum_threshold: float = 5.0
    
    # Mean Reversion Einstellungen
    mean_reversion_period: int = 20
    mean_reversion_threshold: float = 10.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Konvertiert Config zu Dictionary"""
        return {
            'symbol': self.symbol,
            'initial_capital': self.initial_capital,
            'backtest_days': self.backtest_days,
            'rsi': {
                'period': self.rsi_period,
                'oversold': self.rsi_oversold,
                'overbought': self.rsi_overbought
            },
            'sma': {
                'short_period': self.sma_short_period,
                'long_period': self.sma_long_period
            },
            'ema': {
                'short_period': self.ema_short_period,
                'long_period': self.ema_long_period
            },
            'macd': {
                'fast': self.macd_fast,
                'slow': self.macd_slow
            },
            'bollinger': {
                'period': self.bollinger_period,
                'std_dev': self.bollinger_std_dev
            },
            'stochastic': {
                'period': self.stochastic_period,
                'oversold': self.stochastic_oversold,
                'overbought': self.stochastic_overbought
            },
            'momentum': {
                'period': self.momentum_period,
                'threshold': self.momentum_threshold
            },
            'mean_reversion': {
                'period': self.mean_reversion_period,
                'threshold': self.mean_reversion_threshold
            }
        }
