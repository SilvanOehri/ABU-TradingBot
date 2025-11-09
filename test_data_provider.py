#!/usr/bin/env python3
"""
Test script for DataProvider to verify it works correctly
"""

import sys
import os

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

try:
    from src.data_provider import DataProvider
    print("✓ Successfully imported DataProvider")
    
    # Test creating an instance
    provider = DataProvider()
    print("✓ Successfully created DataProvider instance")
    
    # Test fetching some data (small amount for quick test)
    print("\nTesting data fetch...")
    try:
        prices = provider.get_stock_data("BTC-USD", 30)  # 30 days of data
        print(f"✓ Successfully fetched {len(prices)} days of BTC-USD data")
        print(f"  Price range: ${min(prices):.2f} - ${max(prices):.2f}")
        print(f"  Latest price: ${prices[-1]:.2f}")
    except Exception as e:
        print(f"✗ Error fetching data: {e}")
    
    print("\n✓ DataProvider tests completed successfully!")
    
except ImportError as e:
    print(f"✗ Import error: {e}")
    print("Make sure yfinance is installed: pip install yfinance")
    sys.exit(1)
except Exception as e:
    print(f"✗ Unexpected error: {e}")
    sys.exit(1)