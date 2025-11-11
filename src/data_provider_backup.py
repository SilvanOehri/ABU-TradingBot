"""
Data Provider for Trading Bot
Hybrid System: Try Finnhub API first, fallback to pre-downloaded JSON files
Perfect for Vercel deployment with backup strategy!
"""

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
    Hybrid data provider:
    1. Try Finnhub API for real-time data
    2. Fallback to JSON files if API fails
    """
    
    def __init__(self):
        """Initialize with Finnhub API and JSON fallback"""
        self.api_key = os.getenv('FINNHUB_API_KEY', 'demo')
        self.base_url = "https://finnhub.io/api/v1"
        self.session = requests.Session()
        self.session.headers.update({
            'X-Finnhub-Token': self.api_key,
            'User-Agent': 'TradingBot/1.0'
        })
        self.data_dir = os.path.join(os.path.dirname(__file__), '..', 'market_data')
        logger.info("DataProvider initialized (Finnhub API + JSON Fallback)")
        
        if self.api_key == 'demo':
            logger.warning("Using demo API key. JSON fallback will be used.")

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
            raise ValueError("FINNHUB_API_KEY is required! No fallback data available.")
        
        self.base_url = "https://finnhub.io/api/v1"
        self.session = requests.Session()
        self.session.headers.update({
            'X-Finnhub-Token': self.api_key,
            'User-Agent': 'TradingBot/1.0'
        })
        logger.info("DataProvider initialized with Finnhub API (NO FALLBACKS)")
    
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
        logger.info(f"Fetching REAL market data from Finnhub for {symbol} ({days} days)")
        
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
                                
                                logger.info(f"Finnhub: Fetched {len(prices)} REAL prices for {symbol}")
                                logger.info(f"Current price: ${prices[-1]:.2f}")
                                logger.info(f"Price range: ${min(prices):.2f} - ${max(prices):.2f}")
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
                        raise Exception("Finnhub API key invalid! Check your API key.")
                        
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
            raise Exception(f"Cannot fetch real data for {symbol}. API failed and NO fallback data available.")
    
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
                    logger.info(f"Crypto data fetched for {symbol}: {len(prices)} prices")
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
        Get stock data with hybrid approach:
        1. Try Finnhub API first
        2. Fallback to JSON file if API fails
        
        Args:
            symbol: Trading symbol (e.g., 'TSLA', 'BTC-USD')
            days: Number of days of historical data
            
        Returns:
            List of closing prices
        """
        logger.info(f"Fetching data for {symbol} ({days} days)")
        
        # Strategy 1: Try Finnhub API
        try:
            prices = self._fetch_from_finnhub(symbol, days)
            if prices and len(prices) >= 10:
                logger.info(f"Finnhub API success: {len(prices)} prices for {symbol}")
                return prices
        except Exception as e:
            logger.warning(f"Finnhub API failed for {symbol}: {e}")
        
        # Strategy 2: Fallback to JSON file
        try:
            prices = self._load_from_json(symbol, days)
            if prices and len(prices) >= 10:
                logger.info(f"JSON fallback success: {len(prices)} prices for {symbol}")
                return prices
        except Exception as e:
            logger.warning(f"JSON fallback failed for {symbol}: {e}")
        
        # Both strategies failed
        raise Exception(f"Cannot fetch data for {symbol}. API failed and no JSON backup available.")
    
    def _fetch_from_finnhub(self, symbol: str, days: int) -> List[float]:
        """Try to fetch data from Finnhub API"""
        logger.info(f"Trying Finnhub API for {symbol}...")
        
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days + 10)
        
        start_ts = int(start_date.timestamp())
        end_ts = int(end_date.timestamp())
        
        # Convert symbol for Finnhub
        finnhub_symbol = self._convert_symbol_for_finnhub(symbol)
        
        # Finnhub Stock Candles API
        url = f"{self.base_url}/stock/candle"
        params = {
            'symbol': finnhub_symbol,
            'resolution': 'D',
            'from': start_ts,
            'to': end_ts
        }
        
        response = self.session.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get('s') == 'ok' and 'c' in data:
                closes = data['c']
                if len(closes) >= 10:
                    prices = closes[-days:] if len(closes) >= days else closes
                    return prices
        
        raise Exception(f"Finnhub API returned status {response.status_code}")
    
    def _load_from_json(self, symbol: str, days: int) -> List[float]:
        """Load data from pre-downloaded JSON file"""
        logger.info(f"Loading from JSON for {symbol}...")
        
        # Construct filename
        filename = f"{symbol.replace('-', '_')}.json"
        filepath = os.path.join(self.data_dir, filename)
        
        if not os.path.exists(filepath):
            raise Exception(f"JSON file not found: {filepath}")
        
        # Load JSON
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        prices = data.get('prices', [])
        
        if not prices:
            raise Exception(f"No prices in JSON file for {symbol}")
        
        # Return last N days
        return prices[-days:] if len(prices) >= days else prices
    
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
        """Fetch crypto data - tries Finnhub crypto endpoint, then JSON"""
        logger.info(f"Trying Finnhub crypto endpoint for {symbol}")
        
        try:
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
                if data.get('s') == 'ok' and 'c' in data:
                    closes = data['c']
                    if len(closes) >= 5:
                        prices = closes[-days:] if len(closes) >= days else closes
                        logger.info(f"Finnhub crypto: {len(prices)} prices")
                        return prices
        except Exception as e:
            logger.warning(f"Finnhub crypto failed: {e}")
        
        # Fallback to JSON
        return self._load_from_json(symbol, days)
    
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