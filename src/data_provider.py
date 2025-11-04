"""
Datenlieferant für Marktdaten
"""

import yfinance as yf
from datetime import datetime, timedelta
from typing import List, Optional

class DataProvider:
    """
    Klasse für das Laden von Marktdaten
    """
    
    def __init__(self):
        pass
    
    def get_stock_data(self, symbol: str, days: int) -> List[float]:
        """
        Lädt Aktiendaten von Yahoo Finance
        
        Args:
            symbol: Handelssymbol (z.B. "BTC-USD", "AAPL")
            days: Anzahl der Tage zurück
            
        Returns:
            Liste der Schlusskurse
            
        Raises:
            Exception: Bei Fehlern beim Laden der Daten
        """
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            ticker = yf.Ticker(symbol)
            data = ticker.history(start=start_date, end=end_date)
            
            if data.empty:
                raise ValueError(f"Keine Daten für {symbol} gefunden")
            
            prices = data['Close'].tolist()
            
            if len(prices) < 30:
                raise ValueError(f"Nicht genügend Daten: {len(prices)} Tage")
            
            print(f"✅ {len(prices)} Tage Daten für {symbol} geladen")
            print(f"📊 Preisbereich: ${min(prices):.2f} - ${max(prices):.2f}")
            print(f"📊 Startpreis: ${prices[0]:.2f}, Endpreis: ${prices[-1]:.2f}")
            
            return prices
            
        except Exception as e:
            raise Exception(f"Fehler beim Laden der Daten: {e}")
    
    def get_symbol_info(self, symbol: str) -> dict:
        """
        Holt Informationen über ein Symbol
        
        Args:
            symbol: Handelssymbol
            
        Returns:
            Dict mit Symbol-Informationen
        """
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            return {
                'symbol': symbol,
                'name': info.get('longName', symbol),
                'currency': info.get('currency', 'USD'),
                'market': info.get('market', 'Unknown')
            }
        except Exception:
            return {
                'symbol': symbol,
                'name': symbol,
                'currency': 'USD',
                'market': 'Unknown'
            }
