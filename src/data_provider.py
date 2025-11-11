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
            logger.warning("Using demo API key. JSON fallback will be primary source.")

    def get_available_symbols(self) -> List[str]:
        """Get list of all available symbols from JSON files"""
        symbols = []
        
        if os.path.exists(self.data_dir):
            for filename in os.listdir(self.data_dir):
                if filename.endswith('.json') and filename != 'all_symbols.json':
                    # Convert filename back to symbol (e.g., BTC_USD.json -> BTC-USD)
                    symbol = filename.replace('.json', '').replace('_', '-')
                    symbols.append(symbol)
        
        # Sort alphabetically
        symbols.sort()
        logger.info(f"Available symbols: {symbols}")
        return symbols
    
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
        
        # Strategy 1: Try Finnhub API (only if not demo key)
        if self.api_key != 'demo':
            try:
                prices = self._fetch_from_finnhub(symbol, days)
                if prices and len(prices) >= 10:
                    logger.info(f"Finnhub API: {len(prices)} prices, current ${prices[-1]:.2f}")
                    return prices, 'API'
            except Exception as e:
                logger.warning(f"Finnhub API failed for {symbol}: {e}")
        
        # Strategy 2: Fallback to JSON file
        try:
            prices = self._load_from_json(symbol, days)
            if prices and len(prices) >= 10:
                logger.info(f"JSON file: {len(prices)} prices, current ${prices[-1]:.2f}")
                return prices, 'JSON'
        except Exception as e:
            logger.warning(f"JSON fallback failed for {symbol}: {e}")
        
        # Both strategies failed
        raise Exception(f"Cannot fetch data for {symbol}. API and JSON backup both unavailable.")
    
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
        
        # Determine endpoint (stock vs crypto)
        if 'BINANCE:' in finnhub_symbol:
            url = f"{self.base_url}/crypto/candle"
        else:
            url = f"{self.base_url}/stock/candle"
        
        params = {
            'symbol': finnhub_symbol,
            'resolution': 'D',
            'from': start_ts,
            'to': end_ts
        }
        
        # Retry logic for rate limiting
        for attempt in range(2):
            try:
                response = self.session.get(url, params=params, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if data.get('s') == 'ok' and 'c' in data and data['c']:
                        closes = data['c']
                        if len(closes) >= 10:
                            prices = closes[-days:] if len(closes) >= days else closes
                            return prices
                
                elif response.status_code == 429:
                    logger.warning(f"Rate limited, waiting...")
                    time.sleep(5)
                    continue
                    
                raise Exception(f"HTTP {response.status_code}")
                
            except requests.RequestException as e:
                if attempt == 0:
                    time.sleep(2)
                    continue
                raise Exception(f"Connection failed: {e}")
        
        raise Exception("Finnhub API failed after retries")
    
    def _load_from_json(self, symbol: str, days: int) -> List[float]:
        """Load data from pre-downloaded JSON file"""
        logger.info(f"Loading from JSON for {symbol}...")
        
        # Construct filename (BTC-USD -> BTC_USD.json)
        filename = f"{symbol.replace('-', '_')}.json"
        filepath = os.path.join(self.data_dir, filename)
        
        if not os.path.exists(filepath):
            raise Exception(f"JSON file not found: {filename}")
        
        # Load JSON
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        # Extract closing prices
        if isinstance(data, list) and len(data) > 0:
            # Format: [{"date": "2020-01-01", "close": 100, ...}, ...]
            prices = [item['close'] for item in data if 'close' in item]
        else:
            raise Exception(f"Invalid JSON format for {symbol}")
        
        if not prices or len(prices) < 10:
            raise Exception(f"Insufficient data in JSON: {len(prices)} prices")
        
        # Return last N days
        return prices[-days:] if len(prices) >= days else prices
    
    def _convert_symbol_for_finnhub(self, symbol: str) -> str:
        """Convert symbols to Finnhub format"""
        symbol = symbol.upper()
        
        # Crypto conversions
        crypto_mapping = {
            'BTC-USD': 'BINANCE:BTCUSDT',
            'ETH-USD': 'BINANCE:ETHUSDT',
            'BTC_USD': 'BINANCE:BTCUSDT',
            'ETH_USD': 'BINANCE:ETHUSDT',
        }
        
        return crypto_mapping.get(symbol, symbol)
    
    def get_symbol_info(self, symbol: str) -> Dict[str, Any]:
        """Get company profile - simple fallback info"""
        
        # Nice names for known symbols
        names = {
            'TSLA': 'Tesla Inc',
            'AAPL': 'Apple Inc',
            'MSFT': 'Microsoft Corporation',
            'GOOGL': 'Alphabet Inc (Google)',
            'AMZN': 'Amazon.com Inc',
            'NVDA': 'NVIDIA Corporation',
            'META': 'Meta Platforms Inc',
            'SPY': 'S&P 500 ETF',
            'BTC-USD': 'Bitcoin',
            'BTC_USD': 'Bitcoin',
            'ETH-USD': 'Ethereum',
            'ETH_USD': 'Ethereum',
        }
        
        sectors = {
            'TSLA': 'Automotive',
            'AAPL': 'Technology',
            'MSFT': 'Technology',
            'GOOGL': 'Technology',
            'AMZN': 'E-commerce',
            'NVDA': 'Technology',
            'META': 'Technology',
            'SPY': 'ETF',
            'BTC-USD': 'Cryptocurrency',
            'BTC_USD': 'Cryptocurrency',
            'ETH-USD': 'Cryptocurrency',
            'ETH_USD': 'Cryptocurrency',
        }
        
        return {
            'symbol': symbol,
            'name': names.get(symbol, symbol),
            'sector': sectors.get(symbol, 'Unknown'),
            'currency': 'USD',
            'market_cap': 1000000000,
            'previous_close': 0
        }
    
    def validate_symbol(self, symbol: str) -> bool:
        """Check if symbol is available (has JSON file)"""
        filename = f"{symbol.replace('-', '_')}.json"
        filepath = os.path.join(self.data_dir, filename)
        return os.path.exists(filepath)
    