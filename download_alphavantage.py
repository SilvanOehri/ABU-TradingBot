#!/usr/bin/env python3
"""
Download historical market data using Alpha Vantage API.
Free tier: 25 requests per day, 5 per minute.
Get your free API key at: https://www.alphavantage.co/support/#api-key
"""

import requests
import json
import os
from datetime import datetime, timedelta
import time

os.makedirs('market_data', exist_ok=True)

# Get API key from user
API_KEY = input("Enter your Alpha Vantage API key (or press Enter to use demo): ").strip()
if not API_KEY:
    API_KEY = "7A00TLHC59KX1BEO"
    print("⚠️  Using demo key - only works for IBM")

# Symbols to download (Alpha Vantage doesn't support crypto directly)
SYMBOLS = {
    'TSLA': 'TSLA',
    'AAPL': 'AAPL', 
    'MSFT': 'MSFT',
    'GOOGL': 'GOOGL',
    'AMZN': 'AMZN',
    'NVDA': 'NVDA',
    'META': 'META',
    'SPY': 'SPY',
    # For crypto, we'll use Coinbase data via different endpoint
    'BTC_USD': 'BTC',
    'ETH_USD': 'ETH'
}

BASE_URL = "https://www.alphavantage.co/query"

print("🤖 Alpha Vantage Market Data Downloader")
print("=" * 50)
print(f"API Key: {API_KEY[:8]}...")
print("=" * 50)

successful = 0
failed = 0

for symbol, api_symbol in SYMBOLS.items():
    try:
        print(f"📥 Downloading {symbol}...")
        
        # Different endpoint for crypto
        if symbol in ['BTC_USD', 'ETH_USD']:
            params = {
                'function': 'DIGITAL_CURRENCY_DAILY',
                'symbol': api_symbol,
                'market': 'USD',
                'apikey': API_KEY,
                'outputsize': 'full'
            }
        else:
            params = {
                'function': 'TIME_SERIES_DAILY',
                'symbol': api_symbol,
                'apikey': API_KEY,
                'outputsize': 'full'
            }
        
        response = requests.get(BASE_URL, params=params, timeout=30)
        
        if response.status_code != 200:
            print(f"  ❌ HTTP {response.status_code}")
            failed += 1
            time.sleep(12)  # Rate limit: 5 per minute
            continue
        
        data_json = response.json()
        
        # Check for API errors
        if 'Error Message' in data_json:
            print(f"  ❌ API Error: {data_json['Error Message']}")
            failed += 1
            time.sleep(12)
            continue
            
        if 'Note' in data_json:
            print(f"  ❌ Rate limit hit: {data_json['Note']}")
            failed += 1
            break  # Stop if we hit the rate limit
        
        # Extract time series data
        if symbol in ['BTC_USD', 'ETH_USD']:
            time_series_key = 'Time Series (Digital Currency Daily)'
        else:
            time_series_key = 'Time Series (Daily)'
            
        if time_series_key not in data_json:
            print(f"  ❌ No data found. Keys: {list(data_json.keys())}")
            failed += 1
            time.sleep(12)
            continue
        
        time_series = data_json[time_series_key]
        
        # Convert to our format
        data = []
        for date_str, values in sorted(time_series.items()):
            if symbol in ['BTC_USD', 'ETH_USD']:
                # Crypto has different field names
                data.append({
                    'date': date_str,
                    'open': float(values['1a. open (USD)']),
                    'high': float(values['2a. high (USD)']),
                    'low': float(values['3a. low (USD)']),
                    'close': float(values['4a. close (USD)']),
                    'volume': float(values['5. volume'])
                })
            else:
                data.append({
                    'date': date_str,
                    'open': float(values['1. open']),
                    'high': float(values['2. high']),
                    'low': float(values['3. low']),
                    'close': float(values['4. close']),
                    'volume': int(values['5. volume'])
                })
        
        # Save to JSON file
        filename = f"market_data/{symbol}.json"
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"  ✅ Saved {len(data)} days to {filename}")
        successful += 1
        
        # Rate limiting: 5 requests per minute
        print("  ⏳ Waiting 12 seconds (rate limit)...")
        time.sleep(12)
        
    except Exception as e:
        print(f"  ❌ Error: {str(e)}")
        failed += 1
        time.sleep(12)

print("=" * 50)
print(f"✅ Successfully downloaded: {successful}")
print(f"❌ Failed: {failed}")
print("=" * 50)
print("\n💡 Free tier limit: 25 requests/day, 5/minute")
print("   Get your free key at: https://www.alphavantage.co/support/#api-key")
