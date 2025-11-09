#!/usr/bin/env python3
"""
Test script for the improved DataProvider class
"""

import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from src.data_provider import DataProvider
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')

def test_data_provider():
    """Test the DataProvider with various symbols"""
    
    dp = DataProvider()
    
    test_symbols = [
        'BTC-USD',
        'AAPL', 
        'MSFT',
        'INVALID-SYMBOL',
        'SPY'
    ]
    
    print("Testing DataProvider with improved error handling...")
    print("="*60)
    
    for symbol in test_symbols:
        print(f"\nTesting symbol: {symbol}")
        print("-" * 30)
        
        # Test symbol validation
        is_valid = dp.validate_symbol(symbol)
        print(f"Symbol validation: {'VALID' if is_valid else 'INVALID'}")
        
        if is_valid:
            try:
                # Test data fetching
                prices = dp.get_stock_data(symbol, 100)
                print(f"✓ Successfully loaded {len(prices)} prices")
                print(f"  Price range: ${min(prices):.2f} - ${max(prices):.2f}")
                print(f"  Latest price: ${prices[-1]:.2f}")
                
            except Exception as e:
                print(f"✗ Failed to load data: {e}")
        else:
            print("⚠ Skipping data fetch for invalid symbol")

if __name__ == "__main__":
    test_data_provider()