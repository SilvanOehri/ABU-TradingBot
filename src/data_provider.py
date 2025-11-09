"""
Data Provider for Trading Bot
Handles fetching stock/crypto data from various sources
"""

import yfinance as yf
from datetime import datetime, timedelta
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class DataProvider:
    """
    Provides market data from Yahoo Finance
    """
    
    def __init__(self):
        """Initialize the data provider"""
        pass
    
    def get_stock_data(self, symbol: str, days: int) -> List[float]:
        """
        Fetch stock/crypto data from Yahoo Finance
        
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
            
            # Fetch data using yfinance
            ticker = yf.Ticker(symbol)
            data = ticker.history(start=start_date, end=end_date)
            
            if data.empty:
                raise ValueError(f"No data found for symbol {symbol}")
            
            # Extract closing prices
            prices = data['Close'].tolist()
            
            # Validate minimum data requirement
            if len(prices) < 30:
                raise ValueError(f"Insufficient data: {len(prices)} days (minimum 30 required)")
            
            logger.info(f"Successfully loaded {len(prices)} days of data for {symbol}")
            logger.info(f"Price range: ${min(prices):.2f} - ${max(prices):.2f}")
            logger.info(f"Start price: ${prices[0]:.2f}, End price: ${prices[-1]:.2f}")
            
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
            ticker = yf.Ticker(symbol)
            # Try to get a small amount of recent data
            data = ticker.history(period="5d")
            return not data.empty
        except Exception:
            return False