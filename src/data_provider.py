"""
Data Provider for Trading Bot
Handles fetching stock/crypto data from various sources with robust fallbacks
"""

import yfinance as yf
from datetime import datetime, timedelta
from typing import List, Dict, Any
import logging
import time
import random
import requests

logger = logging.getLogger(__name__)

class DataProvider:
    """
    Provides market data with robust error handling and mock data fallback
    """
    
    def __init__(self):
        """Initialize the data provider"""
        # Configure session with headers to avoid blocking
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def _generate_mock_data(self, symbol: str, days: int) -> List[float]:
        """
        Generate realistic mock data as fallback when real data is unavailable
        """
        logger.warning(f"Generating mock data for {symbol} ({days} days)")
        
        # Base prices for different asset types
        base_prices = {
            'BTC': 45000,
            'ETH': 3000,
            'AAPL': 150,
            'MSFT': 300,
            'TSLA': 200,
            'SPY': 400,
            'NVDA': 400
        }
        
        # Determine base price
        base_price = 100  # default
        for key, price in base_prices.items():
            if key in symbol.upper():
                base_price = price
                break
        
        prices = []
        current_price = base_price
        
        # Generate realistic price movements with trends
        for i in range(days):
            # Add some trend over time (slight upward bias)
            trend = 0.0001 * i  # Slight upward trend
            
            # Random walk with volatility
            daily_change = random.normalvariate(0.02 + trend, 2.0)  # mean 0.02%, std 2%
            change = current_price * (daily_change / 100)
            current_price = max(current_price + change, base_price * 0.1)  # Don't go below 10% of base
            prices.append(round(current_price, 2))
        
        logger.info(f"Generated {len(prices)} mock prices for {symbol}")
        logger.info(f"Price range: ${min(prices):.2f} - ${max(prices):.2f}")
        logger.info(f"Start: ${prices[0]:.2f}, End: ${prices[-1]:.2f}")
        
        return prices
    
    def _try_fetch_symbol(self, symbol: str, days: int) -> List[float]:
        """
        Try to fetch data for a specific symbol with multiple approaches
        """
        try:
            logger.info(f"Attempting to fetch data for {symbol}")
            
            # Calculate date range
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            # Create ticker
            ticker = yf.Ticker(symbol)
            
            # Try different approaches
            data = None
            
            # Method 1: Date range
            try:
                data = ticker.history(start=start_date, end=end_date)
                if not data.empty:
                    logger.info(f"Date range fetch successful for {symbol}")
            except Exception as e:
                logger.debug(f"Date range fetch failed: {e}")
            
            # Method 2: Period-based if date range failed
            if data is None or data.empty:
                try:
                    if days >= 365 * 4:
                        period = "5y"
                    elif days >= 365 * 1.5:
                        period = "2y"
                    elif days >= 365:
                        period = "1y"
                    elif days >= 180:
                        period = "6mo"
                    elif days >= 90:
                        period = "3mo"
                    elif days >= 30:
                        period = "1mo"
                    else:
                        period = "1mo"
                    
                    data = ticker.history(period=period)
                    if not data.empty:
                        logger.info(f"Period fetch ({period}) successful for {symbol}")
                except Exception as e:
                    logger.debug(f"Period fetch failed: {e}")
            
            # Method 3: Try with shorter period
            if data is None or data.empty:
                try:
                    data = ticker.history(period="1y")
                    if not data.empty:
                        logger.info(f"1y fallback fetch successful for {symbol}")
                except Exception as e:
                    logger.debug(f"1y fallback failed: {e}")
            
            # Extract prices if we have data
            if data is not None and not data.empty and 'Close' in data.columns:
                prices = data['Close'].tolist()
                
                # Filter out any NaN values
                prices = [p for p in prices if not (p != p)]  # Remove NaN
                
                if len(prices) >= 30:  # Minimum viable dataset
                    # Trim to requested length if we have more data
                    if len(prices) > days:
                        prices = prices[-days:]
                    
                    logger.info(f"Successfully fetched {len(prices)} prices for {symbol}")
                    logger.info(f"Price range: ${min(prices):.2f} - ${max(prices):.2f}")
                    return prices
                else:
                    logger.warning(f"Insufficient data for {symbol}: {len(prices)} prices")
            else:
                logger.warning(f"No valid data returned for {symbol}")
                
        except Exception as e:
            logger.warning(f"Error fetching {symbol}: {e}")
        
        return None
    
    def get_stock_data(self, symbol: str, days: int) -> List[float]:
        """
        Fetch stock/crypto data with robust fallback mechanisms
        
        Args:
            symbol: Trading symbol (e.g., 'BTC-USD', 'AAPL')
            days: Number of days of historical data
            
        Returns:
            List of closing prices
        """
        logger.info(f"Fetching {days} days of data for {symbol}")
        
        # Define alternative symbols for crypto
        symbols_to_try = [symbol]
        
        if 'BTC' in symbol.upper():
            symbols_to_try.extend(['BTC-USD', 'BTCUSD=X', '^BCOM'])  # Bitcoin alternatives
        elif 'ETH' in symbol.upper():
            symbols_to_try.extend(['ETH-USD', 'ETHUSD=X'])  # Ethereum alternatives
        
        # Try each symbol
        for test_symbol in symbols_to_try:
            prices = self._try_fetch_symbol(test_symbol, days)
            if prices:
                return prices
        
        # If crypto failed and this was a crypto request, try reliable stocks
        if any(crypto in symbol.upper() for crypto in ['BTC', 'ETH', 'CRYPTO']):
            logger.warning("Crypto data unavailable, trying stock market alternatives")
            for fallback in ['AAPL', 'MSFT', 'SPY']:
                prices = self._try_fetch_symbol(fallback, days)
                if prices:
                    logger.info(f"Using {fallback} data as fallback for {symbol}")
                    return prices
        
        # If everything fails, generate mock data
        logger.warning(f"All data sources failed for {symbol}, generating realistic mock data")
        return self._generate_mock_data(symbol, days)
    
    def get_symbol_info(self, symbol: str) -> Dict[str, Any]:
        """
        Get basic information about a trading symbol
        
        Args:
            symbol: Trading symbol
            
        Returns:
            Dictionary with symbol information
        """
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            return {
                'symbol': symbol,
                'name': info.get('longName', symbol),
                'sector': info.get('sector', 'Unknown'),
                'industry': info.get('industry', 'Unknown'),
                'currency': info.get('currency', 'USD'),
                'market_cap': info.get('marketCap', 0),
                'previous_close': info.get('previousClose', 0)
            }
            
        except Exception as e:
            logger.warning(f"Could not fetch info for {symbol}: {e}")
            return {
                'symbol': symbol,
                'name': symbol,
                'sector': 'Unknown',
                'industry': 'Unknown',
                'currency': 'USD',
                'market_cap': 0,
                'previous_close': 0
            }
    
    def validate_symbol(self, symbol: str) -> bool:
        """
        Check if a trading symbol is valid
        
        Args:
            symbol: Trading symbol to validate
            
        Returns:
            True if symbol is valid, False otherwise
        """
        try:
            ticker = yf.Ticker(symbol)
            # Try to get a small amount of recent data
            data = ticker.history(period="5d")
            return not data.empty
        except Exception:
            return False

import yfinance as yf
from datetime import datetime, timedelta
from typing import List, Dict, Any
import logging
import time
import random
import requests

logger = logging.getLogger(__name__)

class DataProvider:
    """
    Provides market data from Yahoo Finance with robust error handling
    """
    
    def __init__(self):
        """Initialize the data provider"""
        # Configure session with headers to avoid blocking
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # Override yfinance session
        yf.utils.get_json = self._get_json_with_retry

import yfinance as yf
from datetime import datetime, timedelta
from typing import List, Dict, Any
import logging
import time

logger = logging.getLogger(__name__)

class DataProvider:
    """
    Provides market data from Yahoo Finance with improved error handling
    """
    
    # Symbol mappings for common issues
    SYMBOL_ALTERNATIVES = {
        'BTC-USD': ['BTC-USD', 'BTCUSD=X', 'BTC=F'],
        'ETH-USD': ['ETH-USD', 'ETHUSD=X', 'ETH=F'],
        'BTC': ['BTC-USD', 'BTCUSD=X', 'BTC=F'],
        'ETH': ['ETH-USD', 'ETHUSD=X', 'ETH=F']
    }
    
    def __init__(self):
        """Initialize the data provider"""
        # Configure yfinance to be more robust
        yf.set_tz_cache_location("./tmp/cache")
    
    def _try_fetch_with_alternatives(self, symbol: str, start_date: datetime, end_date: datetime) -> tuple:
        """
        Try fetching data with alternative symbol formats
        
        Returns:
            (data, successful_symbol) tuple or (None, None) if all fail
        """
        # Get list of symbols to try
        symbols_to_try = self.SYMBOL_ALTERNATIVES.get(symbol, [symbol])
        
        for attempt_symbol in symbols_to_try:
            try:
                logger.info(f"Trying to fetch data for symbol: {attempt_symbol}")
                ticker = yf.Ticker(attempt_symbol)
                
                # Add a small delay to avoid rate limiting
                time.sleep(0.5)
                
                # Try fetching with different methods
                data = None
                
                # Method 1: Standard history call
                try:
                    data = ticker.history(start=start_date, end=end_date, auto_adjust=True, prepost=True)
                except Exception as e:
                    logger.warning(f"Standard history call failed for {attempt_symbol}: {e}")
                
                # Method 2: If standard fails, try with period instead
                if data is None or data.empty:
                    try:
                        days_diff = (end_date - start_date).days
                        if days_diff > 365 * 2:
                            period = "5y"
                        elif days_diff > 365:
                            period = "2y"
                        elif days_diff > 90:
                            period = "1y"
                        else:
                            period = "3mo"
                        
                        logger.info(f"Trying period-based fetch with period: {period}")
                        data = ticker.history(period=period, auto_adjust=True, prepost=True)
                    except Exception as e:
                        logger.warning(f"Period-based fetch failed for {attempt_symbol}: {e}")
                
                # Check if we got valid data
                if data is not None and not data.empty and 'Close' in data.columns:
                    logger.info(f"Successfully fetched {len(data)} records for {attempt_symbol}")
                    return data, attempt_symbol
                else:
                    logger.warning(f"No valid data returned for {attempt_symbol}")
                    
            except Exception as e:
                logger.warning(f"Failed to fetch {attempt_symbol}: {e}")
                continue
        
        return None, None
    
    def get_stock_data(self, symbol: str, days: int) -> List[float]:
        """
        Fetch stock/crypto data from Yahoo Finance with robust error handling
        
        Args:
            symbol: Trading symbol (e.g., 'BTC-USD', 'AAPL')
            days: Number of days of historical data
            
        Returns:
            List of closing prices
            
        Raises:
            Exception: If data cannot be fetched or insufficient data
        """
        try:
            # Calculate date range
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            logger.info(f"Fetching {days} days of data for {symbol}")
            logger.info(f"Date range: {start_date.date()} to {end_date.date()}")
            
            # Try fetching data with alternative symbols
            data, successful_symbol = self._try_fetch_with_alternatives(symbol, start_date, end_date)
            
            if data is None or data.empty:
                # Last resort: try some popular stock symbols if crypto fails
                if symbol.upper() in ['BTC-USD', 'BTC', 'BITCOIN']:
                    logger.warning(f"Bitcoin data unavailable, trying AAPL as fallback")
                    data, successful_symbol = self._try_fetch_with_alternatives('AAPL', start_date, end_date)
                
                if data is None or data.empty:
                    raise ValueError(f"No data found for symbol {symbol} or any alternatives")
            
            # Extract closing prices
            if 'Close' not in data.columns:
                raise ValueError(f"No closing price data found for {successful_symbol}")
            
            prices = data['Close'].dropna().tolist()
            
            # Validate data quality
            if len(prices) == 0:
                raise ValueError(f"No valid price data for {successful_symbol}")
            
            if len(prices) < 30:
                logger.warning(f"Limited data available: {len(prices)} days")
                if len(prices) < 10:
                    raise ValueError(f"Insufficient data: {len(prices)} days (minimum 10 required)")
            
            # Remove any invalid prices (zeros, negative values for most assets)
            valid_prices = [p for p in prices if p > 0]
            if len(valid_prices) != len(prices):
                logger.warning(f"Removed {len(prices) - len(valid_prices)} invalid price entries")
                prices = valid_prices
            
            if len(prices) == 0:
                raise ValueError(f"No valid price data after cleaning for {successful_symbol}")
            
            # Truncate to requested number of days if we got more data
            if len(prices) > days:
                prices = prices[-days:]
            
            logger.info(f"Successfully loaded {len(prices)} days of data for {successful_symbol}")
            logger.info(f"Price range: ${min(prices):.2f} - ${max(prices):.2f}")
            logger.info(f"Start price: ${prices[0]:.2f}, End price: ${prices[-1]:.2f}")
            
            if successful_symbol != symbol:
                logger.info(f"Note: Used alternative symbol {successful_symbol} instead of {symbol}")
            
            return prices
            
        except Exception as e:
            error_msg = f"Error fetching data for {symbol}: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)
    
    def get_symbol_info(self, symbol: str) -> Dict[str, Any]:
        """
        Get basic information about a trading symbol
        
        Args:
            symbol: Trading symbol
            
        Returns:
            Dictionary with symbol information
        """
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            return {
                'symbol': symbol,
                'name': info.get('longName', symbol),
                'sector': info.get('sector', 'Unknown'),
                'industry': info.get('industry', 'Unknown'),
                'currency': info.get('currency', 'USD'),
                'market_cap': info.get('marketCap', 0),
                'previous_close': info.get('previousClose', 0)
            }
            
        except Exception as e:
            logger.warning(f"Could not fetch info for {symbol}: {e}")
            return {
                'symbol': symbol,
                'name': symbol,
                'sector': 'Unknown',
                'industry': 'Unknown',
                'currency': 'USD',
                'market_cap': 0,
                'previous_close': 0
            }
    
    def validate_symbol(self, symbol: str) -> bool:
        """
        Check if a trading symbol is valid
        
        Args:
            symbol: Trading symbol to validate
            
        Returns:
            True if symbol is valid, False otherwise
        """
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=7)
            
            data, _ = self._try_fetch_with_alternatives(symbol, start_date, end_date)
            return data is not None and not data.empty
        except Exception:
            return False