"""
Datenlieferant für Marktdaten
"""

import yfinance as yf
from datetime import datetime, timedelta
from typing import List, Optional
import requests
import time

class DataProvider:
    """
    Klasse für das Laden von Marktdaten
    """
    
    def __init__(self):
        # Set comprehensive headers to avoid being blocked
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
    
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
        max_retries = 3
        retry_delay = 2
        
        for attempt in range(max_retries):
            try:
                print(f"🔄 Versuch {attempt + 1}/{max_retries}: Lade Daten für {symbol}...")
                print(f"📅 Zeitraum: {days} Tage zurück")
                
                end_date = datetime.now()
                start_date = end_date - timedelta(days=days + 10)  # Extra Puffer
                
                print(f"📅 Von {start_date.strftime('%Y-%m-%d')} bis {end_date.strftime('%Y-%m-%d')}")
                
                # Methode 1: Direkter Download (oft zuverlässiger)
                print(f"� Methode 1: Direkter Download...")
                data = yf.download(
                    symbol,
                    start=start_date,
                    end=end_date,
                    progress=False,
                    auto_adjust=True,
                    threads=False,  # Wichtig für Railway
                    timeout=30
                )
                
                if not data.empty:
                    print(f"✅ Methode 1 erfolgreich: {len(data)} Zeilen")
                else:
                    print(f"⚠️ Methode 1 fehlgeschlagen, versuche Methode 2...")
                    
                    # Methode 2: Ticker mit Session
                    ticker = yf.Ticker(symbol, session=self.session)
                    data = ticker.history(
                        start=start_date,
                        end=end_date,
                        auto_adjust=True,
                        actions=False,
                        timeout=30
                    )
                    
                    if not data.empty:
                        print(f"✅ Methode 2 erfolgreich: {len(data)} Zeilen")
                
                if data.empty:
                    if attempt < max_retries - 1:
                        print(f"⏳ Keine Daten erhalten, warte {retry_delay} Sekunden...")
                        time.sleep(retry_delay)
                        continue
                    else:
                        raise ValueError(
                            f"Keine Daten für {symbol} verfügbar nach {max_retries} Versuchen. "
                            f"Mögliche Gründe:\n"
                            f"1. Symbol ist falsch oder nicht mehr verfügbar\n"
                            f"2. Yahoo Finance blockiert Server-Zugriffe (Cloudflare)\n"
                            f"3. Netzwerkprobleme auf Railway\n\n"
                            f"💡 Tipp: Versuche BTC-USD, AAPL, MSFT oder ETH-USD"
                        )
                
                # Daten verarbeiten
                prices = data['Close'].tolist()
                
                # Nur die gewünschte Anzahl an Tagen verwenden
                if len(prices) > days:
                    prices = prices[-days:]
                
                print(f"💰 {len(prices)} Preise extrahiert")
                
                if len(prices) < 30:
                    if attempt < max_retries - 1:
                        print(f"⏳ Zu wenig Daten ({len(prices)}), warte {retry_delay} Sekunden...")
                        time.sleep(retry_delay)
                        continue
                    else:
                        raise ValueError(f"Nicht genügend Daten: {len(prices)} Tage (minimum 30 erforderlich)")
                
                print(f"✅ {len(prices)} Tage Daten für {symbol} geladen")
                print(f"📊 Preisbereich: ${min(prices):.2f} - ${max(prices):.2f}")
                print(f"📊 Startpreis: ${prices[0]:.2f}, Endpreis: ${prices[-1]:.2f}")
                
                return prices
                
            except ValueError as ve:
                # ValueError sofort durchreichen (keine Retries)
                print(f"❌ ValueError: {str(ve)}")
                raise
            except Exception as e:
                print(f"❌ Fehler in Versuch {attempt + 1}: {type(e).__name__}: {str(e)}")
                
                if attempt < max_retries - 1:
                    print(f"⏳ Warte {retry_delay} Sekunden vor erneutem Versuch...")
                    time.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
                else:
                    error_msg = (
                        f"Fehler beim Laden der Daten für {symbol} nach {max_retries} Versuchen.\n"
                        f"Letzter Fehler: {str(e)}\n\n"
                        f"💡 Mögliche Lösungen:\n"
                        f"1. Versuche ein anderes Symbol (BTC-USD, AAPL, MSFT)\n"
                        f"2. Warte 1-2 Minuten und versuche es erneut\n"
                        f"3. Railway könnte Yahoo Finance blockieren"
                    )
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
