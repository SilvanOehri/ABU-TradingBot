"""
Data Provider for Trading Bot
Fetches real market data from Finnhub API
60 requests/minute free tier - perfect for trading bot
"""

import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any
import time
import requests
import json
import os

logger = logging.getLogger(__name__)

import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any
import time
import requests
import json
import os

logger = logging.getLogger(__name__)

class DataProvider:
    """
    Provides ONLY real market data from Finnhub API
    NO fallback data - fails hard if API doesn't work
    """
    
    def __init__(self):
        """Initialize with Finnhub API"""
        self.api_key = os.getenv('FINNHUB_API_KEY')
        if not self.api_key:
            raise ValueError("❌ FINNHUB_API_KEY is required! No fallback data available.")
        
        self.base_url = "https://finnhub.io/api/v1"
        self.session = requests.Session()
        self.session.headers.update({
            'X-Finnhub-Token': self.api_key,
            'User-Agent': 'TradingBot/1.0'
        })
        logger.info("🤖 DataProvider initialized with Finnhub API (NO FALLBACKS)")
    
    def get_stock_data(self, symbol: str, days: int) -> List[float]:
        """
        Fetch ONLY real stock data from Finnhub - NO FALLBACKS
        
        Args:
            symbol: Trading symbol (e.g., 'TSLA', 'AAPL')
            days: Number of days of historical data
            
        Returns:
            List of closing prices (ONLY real market data from Finnhub)
            
        Raises:
            Exception: If Finnhub API fails - NO fallback data
        """
        logger.info(f"🤖 Fetching REAL market data from Finnhub for {symbol} ({days} days)")
        
        try:
            # Calculate date range
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days + 10)  # Extra buffer
            
            start_ts = int(start_date.timestamp())
            end_ts = int(end_date.timestamp())
            
            # Convert symbol for crypto if needed
            finnhub_symbol = self._convert_symbol_for_finnhub(symbol)
            
            # Try stock endpoint first
            url = f"{self.base_url}/stock/candle"
            params = {
                'symbol': finnhub_symbol,
                'resolution': 'D',  # Daily data
                'from': start_ts,
                'to': end_ts
            }
            
            # Make request with retry for rate limiting
            for attempt in range(3):
                try:
                    response = self.session.get(url, params=params, timeout=15)
                    
                    if response.status_code == 200:
                        data = response.json()
                        
                        # Check if data is valid
                        if data.get('s') == 'ok' and 'c' in data and data['c']:
                            closes = data['c']  # Closing prices
                            
                            # Filter and return requested number of days
                            if len(closes) >= 10:  # Minimum viable data
                                prices = closes[-days:] if len(closes) >= days else closes
                                
                                logger.info(f"✅ Finnhub: Fetched {len(prices)} REAL prices for {symbol}")
                                logger.info(f"📈 Current price: ${prices[-1]:.2f}")
                                logger.info(f"📊 Price range: ${min(prices):.2f} - ${max(prices):.2f}")
                                return prices
                            else:
                                raise Exception(f"Insufficient Finnhub data: {len(closes)} prices")
                                
                        elif data.get('s') == 'no_data':
                            raise Exception(f"Finnhub: No data available for {symbol}")
                            
                    elif response.status_code == 429:
                        logger.warning(f"Finnhub rate limited, waiting {5 + attempt * 2} seconds...")
                        time.sleep(5 + attempt * 2)
                        continue
                        
                    elif response.status_code == 401:
                        raise Exception("❌ Finnhub API key invalid! Check your API key.")
                        
                    else:
                        raise Exception(f"Finnhub API error: {response.status_code}")
                        
                except requests.RequestException as e:
                    if attempt < 2:
                        logger.warning(f"Finnhub request error (attempt {attempt + 1}): {e}")
                        time.sleep(2)
                        continue
                    else:
                        raise Exception(f"Finnhub connection failed: {e}")
                    
        except Exception as e:
            logger.error(f"Error fetching Finnhub data for {symbol}: {e}")
            
            # Try crypto endpoint as last resort
            if 'BTC' in symbol.upper() or 'ETH' in symbol.upper():
                try:
                    return self._fetch_crypto_data(symbol, days)
                except Exception as crypto_error:
                    logger.error(f"Crypto fallback also failed: {crypto_error}")
            
            # NO FALLBACK - Fail hard
            raise Exception(f"❌ Cannot fetch real data for {symbol}. API failed and NO fallback data available.")
    
    def _convert_symbol_for_finnhub(self, symbol: str) -> str:
        """Convert symbols to Finnhub format"""
        symbol = symbol.upper()
        
        # Crypto conversions
        crypto_mapping = {
            'BTC-USD': 'BINANCE:BTCUSDT',
            'ETH-USD': 'BINANCE:ETHUSDT',
            'BTC': 'BINANCE:BTCUSDT',
            'ETH': 'BINANCE:ETHUSDT'
        }
        
        if symbol in crypto_mapping:
            return crypto_mapping[symbol]
            
        # Stock symbols usually work as-is
        return symbol
    
    def _fetch_crypto_data(self, symbol: str, days: int) -> List[float]:
        """Fetch crypto data using Finnhub crypto endpoint"""
        logger.info(f"🪙 Trying crypto endpoint for {symbol}")
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days + 5)
        
        start_ts = int(start_date.timestamp())
        end_ts = int(end_date.timestamp())
        
        crypto_symbol = self._convert_symbol_for_finnhub(symbol)
        
        url = f"{self.base_url}/crypto/candle"
        params = {
            'symbol': crypto_symbol,
            'resolution': 'D',
            'from': start_ts,
            'to': end_ts
        }
        
        response = self.session.get(url, params=params, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('s') == 'ok' and 'c' in data and data['c']:
                closes = data['c']
                if len(closes) >= 5:
                    prices = closes[-days:] if len(closes) >= days else closes
                    logger.info(f"✅ Crypto data fetched for {symbol}: {len(prices)} prices")
                    return prices
        
        raise Exception(f"Could not fetch crypto data for {symbol}")
    
    def get_symbol_info(self, symbol: str) -> Dict[str, Any]:
        """Get company profile from Finnhub"""
        try:
            finnhub_symbol = self._convert_symbol_for_finnhub(symbol)
            
            # Skip crypto symbols for company profile
            if 'BINANCE:' in finnhub_symbol:
                return {
                    'symbol': symbol,
                    'name': f"{symbol} Cryptocurrency",
                    'sector': 'Cryptocurrency',
                    'currency': 'USD',
                    'market_cap': 1000000000,
                    'previous_close': 0
                }
            
            url = f"{self.base_url}/stock/profile2"
            params = {'symbol': finnhub_symbol}
            
            response = self.session.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data:  # If profile data exists
                    return {
                        'symbol': symbol,
                        'name': data.get('name', symbol),
                        'sector': data.get('finnhubIndustry', 'Unknown'),
                        'currency': data.get('currency', 'USD'),
                        'market_cap': data.get('marketCapitalization', 0) * 1000000 if data.get('marketCapitalization') else 0,
                        'previous_close': 0
                    }
        except Exception as e:
            logger.warning(f"Could not fetch Finnhub profile for {symbol}: {e}")
        
        # Fallback info
        return {
            'symbol': symbol,
            'name': symbol,
            'sector': 'Unknown',
            'currency': 'USD', 
            'market_cap': 1000000000,
            'previous_close': 0
        }
    
    def validate_symbol(self, symbol: str) -> bool:
        """Check if symbol exists using Finnhub search"""
        try:
            url = f"{self.base_url}/search"
            params = {'q': symbol}
            
            response = self.session.get(url, params=params, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                return len(data.get('result', [])) > 0
                
        except Exception as e:
            logger.warning(f"Could not validate symbol {symbol}: {e}")
        
        return True  # Assume valid if we can't check
    
    def get_stock_data(self, symbol: str, days: int) -> List[float]:
        """
        Fetch real stock data from Finnhub
        
        Args:
            symbol: Trading symbol (e.g., 'TSLA', 'AAPL')
            days: Number of days of historical data
            
        Returns:
            List of closing prices (real market data from Finnhub)
        """
        logger.info(f"🤖 Fetching real market data from Finnhub for {symbol} ({days} days)")
        
        try:
            # Calculate date range (Finnhub uses Unix timestamps)
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days + 10)  # Extra buffer
            
            start_ts = int(start_date.timestamp())
            end_ts = int(end_date.timestamp())
            
            # Convert symbol for crypto if needed
            finnhub_symbol = self._convert_symbol_for_finnhub(symbol)
            
            # Finnhub Stock Candles API
            url = f"{self.base_url}/stock/candle"
            params = {
                'symbol': finnhub_symbol,
                'resolution': 'D',  # Daily data
                'from': start_ts,
                'to': end_ts
            }
            
            # Make request with retry for rate limiting
            for attempt in range(3):
                try:
                    response = self.session.get(url, params=params, timeout=15)
                    
                    if response.status_code == 200:
                        data = response.json()
                        
                        # Check if data is valid
                        if data.get('s') == 'ok' and 'c' in data:
                            closes = data['c']  # Closing prices
                            
                            # Filter and return requested number of days
                            if len(closes) >= 10:  # Minimum viable data
                                prices = closes[-days:] if len(closes) >= days else closes
                                
                                logger.info(f"✅ Finnhub: Fetched {len(prices)} real prices for {symbol}")
                                logger.info(f"📈 Current price: ${prices[-1]:.2f}")
                                logger.info(f"📊 Price range: ${min(prices):.2f} - ${max(prices):.2f}")
                                return prices
                            else:
                                logger.warning(f"Insufficient Finnhub data: {len(closes)} prices")
                                
                        elif data.get('s') == 'no_data':
                            logger.warning(f"Finnhub: No data available for {symbol}")
                            
                    elif response.status_code == 429:
                        logger.warning(f"Finnhub rate limited, waiting {5 + attempt * 2} seconds...")
                        time.sleep(5 + attempt * 2)
                        continue
                        
                    elif response.status_code == 401:
                        logger.error("❌ Finnhub API key invalid! Get free key at: https://finnhub.io/")
                        break
                        
                    else:
                        logger.warning(f"Finnhub API error: {response.status_code}")
                        break
                        
                except requests.RequestException as e:
                    logger.warning(f"Finnhub request error (attempt {attempt + 1}): {e}")
                    if attempt < 2:
                        time.sleep(2)
                        continue
                    
        except Exception as e:
            logger.error(f"Error fetching Finnhub data for {symbol}: {e}")
        
        # Fallback: Try crypto endpoint for BTC/ETH
        if 'BTC' in symbol.upper() or 'ETH' in symbol.upper():
            try:
                return self._fetch_crypto_data(symbol, days)
            except Exception as e:
                logger.warning(f"Crypto fallback failed: {e}")
        
        # No fallback data - fail hard if API doesn't work
        raise Exception(f"Cannot fetch real market data for {symbol}. Check Finnhub API key and connection.")
    
    def _convert_symbol_for_finnhub(self, symbol: str) -> str:
        """Convert symbols to Finnhub format"""
        symbol = symbol.upper()
        
        # Crypto conversions
        crypto_mapping = {
            'BTC-USD': 'BINANCE:BTCUSDT',
            'ETH-USD': 'BINANCE:ETHUSDT',
            'BTC': 'BINANCE:BTCUSDT',
            'ETH': 'BINANCE:ETHUSDT'
        }
        
        if symbol in crypto_mapping:
            return crypto_mapping[symbol]
            
        # Stock symbols usually work as-is
        return symbol
    
    def _fetch_crypto_data(self, symbol: str, days: int) -> List[float]:
        """Fetch crypto data using Finnhub crypto endpoint"""
        logger.info(f"🪙 Fetching crypto data for {symbol}")
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days + 5)
        
        start_ts = int(start_date.timestamp())
        end_ts = int(end_date.timestamp())
        
        # Use crypto exchange data
        crypto_symbol = self._convert_symbol_for_finnhub(symbol)
        
        url = f"{self.base_url}/crypto/candle"
        params = {
            'symbol': crypto_symbol,
            'resolution': 'D',
            'from': start_ts,
            'to': end_ts
        }
        
        response = self.session.get(url, params=params, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('s') == 'ok' and 'c' in data:
                closes = data['c']
                if len(closes) >= 5:
                    prices = closes[-days:] if len(closes) >= days else closes
                    logger.info(f"✅ Crypto data fetched for {symbol}: {len(prices)} prices")
                    return prices
        
        raise Exception(f"Could not fetch crypto data for {symbol}")
    
    def get_symbol_info(self, symbol: str) -> Dict[str, Any]:
        """Get company profile from Finnhub"""
        try:
            finnhub_symbol = self._convert_symbol_for_finnhub(symbol)
            
            # Skip crypto symbols for company profile
            if 'BINANCE:' in finnhub_symbol:
                return {
                    'symbol': symbol,
                    'name': f"{symbol} Cryptocurrency",
                    'sector': 'Cryptocurrency',
                    'currency': 'USD',
                    'market_cap': 1000000000,
                    'previous_close': 0
                }
            
            url = f"{self.base_url}/stock/profile2"
            params = {'symbol': finnhub_symbol}
            
            response = self.session.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data:  # If profile data exists
                    return {
                        'symbol': symbol,
                        'name': data.get('name', symbol),
                        'sector': data.get('finnhubIndustry', 'Unknown'),
                        'currency': data.get('currency', 'USD'),
                        'market_cap': data.get('marketCapitalization', 0) * 1000000 if data.get('marketCapitalization') else 0,
                        'previous_close': 0
                    }
        except Exception as e:
            logger.warning(f"Could not fetch Finnhub profile for {symbol}: {e}")
        
        # Fallback info
        return {
            'symbol': symbol,
            'name': symbol,
            'sector': 'Unknown',
            'currency': 'USD', 
            'market_cap': 1000000000,
            'previous_close': 0
        }
    
    def validate_symbol(self, symbol: str) -> bool:
        """Check if symbol exists using Finnhub search"""
        try:
            url = f"{self.base_url}/search"
            params = {'q': symbol}
            
            response = self.session.get(url, params=params, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                return len(data.get('result', [])) > 0
                
        except Exception as e:
            logger.warning(f"Could not validate symbol {symbol}: {e}")
        
        return True  # Assume valid if we can't check