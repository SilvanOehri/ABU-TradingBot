"""
Basis-Klasse für alle Trading Strategien
"""

from abc import ABC, abstractmethod
from typing import List, Literal

class BaseStrategy(ABC):
    """
    Abstrakte Basisklasse für alle Trading Strategien
    """
    
    def __init__(self, name: str, emoji: str = "📊"):
        self.name = name
        self.emoji = emoji
        self.trades_count = 0
    
    @abstractmethod
    def calculate_signal(self, prices: List[float]) -> Literal['buy', 'sell', 'hold']:
        """
        Berechnet das Trading Signal basierend auf den Preisdaten
        
        Args:
            prices: Liste der historischen Preise
            
        Returns:
            'buy', 'sell' oder 'hold'
        """
        pass
    
    def get_display_name(self) -> str:
        """Gibt den Anzeigenamen mit Emoji zurück"""
        return f"{self.emoji} {self.name}"
    
    def reset(self):
        """Setzt die Strategie zurück"""
        self.trades_count = 0
