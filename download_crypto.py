#!/usr/bin/env python3
"""
Download BTC and ETH historical data from CryptoCompare (no API key needed for basic use)
"""

import requests
import json
from datetime import datetime, timedelta

BASE_URL = "https://min-api.cryptocompare.com/data/v2/histoday"

CRYPTO_SYMBOLS = {
    'BTC_USD': 'BTC',
    'ETH_USD': 'ETH'
}

print("🤖 CryptoCompare Data Downloader")
print("=" * 50)

for filename, symbol in CRYPTO_SYMBOLS.items():
    try:
        print(f"📥 Downloading {symbol}...")
        
        # CryptoCompare allows 2000 days max per request
        params = {
            'fsym': symbol,
            'tsym': 'USD',
            'limit': 1825  # 5 years
        }
        
        response = requests.get(BASE_URL, params=params, timeout=30)
        
        if response.status_code != 200:
            print(f"  ❌ HTTP {response.status_code}")
            continue
        
        data_json = response.json()
        
        if data_json.get('Response') != 'Success':
            print(f"  ❌ API Error: {data_json.get('Message', 'Unknown error')}")
            continue
        
        # Extract data
        raw_data = data_json['Data']['Data']
        
        # Convert to our format
        data = []
        for item in raw_data:
            date = datetime.fromtimestamp(item['time']).strftime('%Y-%m-%d')
            data.append({
                'date': date,
                'open': float(item['open']),
                'high': float(item['high']),
                'low': float(item['low']),
                'close': float(item['close']),
                'volume': float(item['volumeto'])  # Volume in USD
            })
        
        # Save to JSON
        filepath = f"market_data/{filename}.json"
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        
        latest = data[-1]
        print(f"  ✅ Saved {len(data)} days")
        print(f"     Latest: {latest['date']} - ${latest['close']:,.2f}")
        
    except Exception as e:
        print(f"  ❌ Error: {str(e)}")

print("=" * 50)
print("✅ Crypto data downloaded!")
