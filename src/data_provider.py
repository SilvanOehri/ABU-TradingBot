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
            print(f"🔄 Lade Daten für {symbol}...")
            print(f"📅 Zeitraum: {days} Tage zurück")
            
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            print(f"📅 Von {start_date.strftime('%Y-%m-%d')} bis {end_date.strftime('%Y-%m-%d')}")
            
            # Versuche Daten mit Timeout zu laden
            ticker = yf.Ticker(symbol)
            print(f"🔍 Ticker erstellt: {symbol}")
            
            data = ticker.history(start=start_date, end=end_date, timeout=30)
            print(f"📊 Historie geladen: {len(data)} Zeilen")
            
            if data.empty:
                print(f"❌ Keine Daten für {symbol} gefunden - leere Antwort von Yahoo Finance")
                raise ValueError(f"Keine Daten für {symbol} gefunden. Prüfe, ob das Symbol korrekt ist.")
            
            prices = data['Close'].tolist()
            print(f"💰 {len(prices)} Preise extrahiert")
            
            if len(prices) < 30:
                print(f"⚠️ Zu wenig Daten: {len(prices)} Tage (minimum 30 erforderlich)")
                raise ValueError(f"Nicht genügend Daten: {len(prices)} Tage (minimum 30 erforderlich)")
            
            print(f"✅ {len(prices)} Tage Daten für {symbol} geladen")
            print(f"📊 Preisbereich: ${min(prices):.2f} - ${max(prices):.2f}")
            print(f"📊 Startpreis: ${prices[0]:.2f}, Endpreis: ${prices[-1]:.2f}")
            
            return prices
            
        except ValueError as ve:
            # Re-raise ValueError with original message
            print(f"❌ ValueError: {str(ve)}")
            raise
        except Exception as e:
            print(f"❌ Unerwarteter Fehler: {type(e).__name__}: {str(e)}")
            error_msg = f"Fehler beim Laden der Daten für {symbol}: {str(e)}"
            print(f"❌ {error_msg}")
            raise Exception(error_msg)
    
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
