"""
Data Provider for Trading Bot
Provides mock data for demo purposes since Yahoo Finance is unreliable in deployment
"""

import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any
import random
import math

logger = logging.getLogger(__name__)

class DataProvider:
    """
    Provides market data - using mock data for reliable deployment
    """
    
    def __init__(self):
        """Initialize the data provider"""
        pass
    
    def get_stock_data(self, symbol: str, days: int) -> List[float]:
        """
        Generate realistic mock stock/crypto data for demo purposes
        
        Args:
            symbol: Trading symbol (e.g., 'BTC-USD', 'AAPL')
            days: Number of days of historical data
            
        Returns:
            List of closing prices (mock data)
        """
        logger.info(f"🎭 Generating mock data for {symbol} ({days} days)")
        return self._generate_mock_data(symbol, days)
    
    def _generate_mock_data(self, symbol: str, days: int) -> List[float]:
        """Generate realistic mock price data"""
        
        # Base prices for different symbols
        base_prices = {
            'BTC-USD': 45000,
            'ETH-USD': 2500,
            'AAPL': 180,
            'MSFT': 350,
            'TSLA': 220,
            'NVDA': 450,
            'SPY': 430,
            'GOOGL': 140,
            'AMZN': 150
        }
        
        # Get base price
        base_price = base_prices.get(symbol.upper(), 100)
        
        # Generate seed based on symbol for consistent data
        random.seed(hash(symbol) % 10000)
        
        prices = []
        current_price = base_price
        
        # Market parameters based on asset type
        if 'BTC' in symbol.upper() or 'ETH' in symbol.upper():
            # Crypto: Higher volatility, stronger trends
            volatility = random.uniform(0.03, 0.06)  # 3-6% daily volatility
            trend_factor = random.uniform(-0.0002, 0.0008)  # Slight upward bias
        else:
            # Stocks: Lower volatility, moderate trends
            volatility = random.uniform(0.015, 0.025)  # 1.5-2.5% daily volatility
            trend_factor = random.uniform(0.0001, 0.0003)  # Steady upward bias
        
        # Generate price series
        for day in range(days):
            # Long-term trend
            current_price *= (1 + trend_factor)
            
            # Daily random movement
            daily_change = random.gauss(0, volatility)
            current_price *= (1 + daily_change)
            
            # Add market cycles (bull/bear phases)
            cycle_length = random.randint(150, 300)  # 5-10 month cycles
            cycle_strength = 0.1 if 'BTC' in symbol.upper() else 0.05
            cycle_factor = cycle_strength * math.sin(2 * math.pi * day / cycle_length)
            current_price *= (1 + cycle_factor * volatility)
            
            # Add weekly patterns (slight weekend effect)
            weekly_factor = 0.002 * math.sin(2 * math.pi * day / 7) * volatility
            current_price *= (1 + weekly_factor)
            
            # Prevent negative prices
            current_price = max(current_price, base_price * 0.2)
            
            # Add some occasional "events" (news spikes/crashes)
            if random.random() < 0.02:  # 2% chance per day
                event_magnitude = random.uniform(-0.15, 0.2)  # -15% to +20%
                current_price *= (1 + event_magnitude)
            
            prices.append(round(current_price, 2))
        
        # Ensure we have the right number of data points
        while len(prices) < days:
            # Fill with slight variations of the last price
            last_price = prices[-1] if prices else base_price
            variation = random.gauss(0, volatility * 0.5)
            new_price = max(last_price * (1 + variation), base_price * 0.2)
            prices.append(round(new_price, 2))
        
        # Trim to exact length if needed
        prices = prices[:days]
        
        logger.info(f"✅ Generated {len(prices)} mock prices for {symbol}")
        logger.info(f"📈 Price range: ${min(prices):.2f} - ${max(prices):.2f}")
        logger.info(f"📊 Start: ${prices[0]:.2f}, End: ${prices[-1]:.2f}")
        
        return prices
    
    def get_symbol_info(self, symbol: str) -> Dict[str, Any]:
        """
        Get basic information about a trading symbol (mock data)
        """
        symbol_info = {
            'BTC-USD': {'name': 'Bitcoin', 'type': 'Cryptocurrency', 'market_cap': 800000000000},
            'ETH-USD': {'name': 'Ethereum', 'type': 'Cryptocurrency', 'market_cap': 300000000000},
            'AAPL': {'name': 'Apple Inc.', 'type': 'Technology Stock', 'market_cap': 3000000000000},
            'MSFT': {'name': 'Microsoft Corporation', 'type': 'Technology Stock', 'market_cap': 2800000000000},
            'TSLA': {'name': 'Tesla Inc.', 'type': 'Automotive Stock', 'market_cap': 700000000000},
            'NVDA': {'name': 'NVIDIA Corporation', 'type': 'Technology Stock', 'market_cap': 1500000000000},
            'SPY': {'name': 'SPDR S&P 500 ETF', 'type': 'Index Fund', 'market_cap': 400000000000},
            'GOOGL': {'name': 'Alphabet Inc.', 'type': 'Technology Stock', 'market_cap': 1800000000000}
        }
        
        info = symbol_info.get(symbol.upper(), {
            'name': symbol,
            'type': 'Unknown Asset',
            'market_cap': 1000000000
        })
        
        return {
            'symbol': symbol,
            'name': info['name'],
            'sector': info['type'],
            'currency': 'USD',
            'market_cap': info['market_cap'],
            'previous_close': 0
        }
    
    def validate_symbol(self, symbol: str) -> bool:
        """Check if symbol is supported (all symbols supported in demo mode)"""
        return True