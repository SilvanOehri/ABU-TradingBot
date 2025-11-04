#!/usr/bin/env python3
"""
Trading Bot - Einfache funktionierende Version
============================================

Ein einfacher Trading Bot mit 9 verschiedenen Strategien für Backtesting.
Entwickelt für Schulprojekt mit Yahoo Finance Daten.

Autor: Silvan
Datum: September 2025
"""

import sys
import os
import yfinance as yf
from datetime import datetime, timedelta

# Pfad für andere Module hinzufügen (falls verwendet)
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Konfiguration
SYMBOL = "BTC-USD"
INITIAL_CAPITAL = 100000.0  # Erhöht auf $100,000 für Bitcoin
BACKTEST_DAYS = 365 * 5  # 5 Jahre

def calculate_sma(prices, period):
    """Berechnet Simple Moving Average"""
    if len(prices) < period:
        return prices[-1]
    return sum(prices[-period:]) / period

def calculate_ema(prices, period):
    """Berechnet Exponential Moving Average"""
    if len(prices) < period:
        return prices[-1]
    
    multiplier = 2 / (period + 1)
    ema = prices[0]
    
    for price in prices[1:]:
        ema = (price * multiplier) + (ema * (1 - multiplier))
    
    return ema

def calculate_rsi(prices, period=14):
    """Berechnet Relative Strength Index"""
    if len(prices) < period + 1:
        return 50  # Neutral
    
    gains = []
    losses = []
    
    for i in range(1, len(prices)):
        change = prices[i] - prices[i-1]
        if change > 0:
            gains.append(change)
            losses.append(0)
        else:
            gains.append(0)
            losses.append(-change)
    
    avg_gain = sum(gains[-period:]) / period
    avg_loss = sum(losses[-period:]) / period
    
    if avg_loss == 0:
        return 100
    
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    
    return rsi

def calculate_macd(prices, fast=12, slow=26):
    """Berechnet MACD (Moving Average Convergence Divergence)"""
    if len(prices) < slow:
        return 0
    
    ema_fast = calculate_ema(prices, fast)
    ema_slow = calculate_ema(prices, slow)
    
    return ema_fast - ema_slow

def calculate_bollinger_bands(prices, period=20, std_dev=2):
    """Berechnet Bollinger Bands"""
    if len(prices) < period:
        return prices[-1], prices[-1], prices[-1]
    
    sma = calculate_sma(prices, period)
    recent_prices = prices[-period:]
    
    # Standardabweichung berechnen
    variance = sum((price - sma) ** 2 for price in recent_prices) / period
    std = variance ** 0.5
    
    upper_band = sma + (std_dev * std)
    lower_band = sma - (std_dev * std)
    
    return upper_band, sma, lower_band

def calculate_stochastic(prices, period=14):
    """Berechnet Stochastic Oscillator"""
    if len(prices) < period:
        return 50
    
    recent_prices = prices[-period:]
    lowest_low = min(recent_prices)
    highest_high = max(recent_prices)
    
    if highest_high == lowest_low:
        return 50
    
    k_percent = ((prices[-1] - lowest_low) / (highest_high - lowest_low)) * 100
    return k_percent

def rsi_strategy(prices):
    """RSI Strategie"""
    if len(prices) < 15:
        return 'hold'
    
    rsi = calculate_rsi(prices)
    
    if rsi < 30:  # Überverkauft
        return 'buy'
    elif rsi > 70:  # Überkauft
        return 'sell'
    else:
        return 'hold'

def sma_strategy(prices):
    """Simple Moving Average Crossover Strategie"""
    if len(prices) < 50:
        return 'hold'
    
    sma_10 = calculate_sma(prices, 10)
    sma_30 = calculate_sma(prices, 30)
    
    if sma_10 > sma_30:  # Kurzer MA über langem MA
        return 'buy'
    elif sma_10 < sma_30:  # Kurzer MA unter langem MA
        return 'sell'
    else:
        return 'hold'

def ema_strategy(prices):
    """Exponential Moving Average Strategie"""
    if len(prices) < 50:
        return 'hold'
    
    ema_12 = calculate_ema(prices, 12)
    ema_26 = calculate_ema(prices, 26)
    
    if ema_12 > ema_26:
        return 'buy'
    elif ema_12 < ema_26:
        return 'sell'
    else:
        return 'hold'

def macd_strategy(prices):
    """MACD Strategie"""
    if len(prices) < 26:
        return 'hold'
    
    macd = calculate_macd(prices)
    
    # Einfache MACD Strategie: Positiv = Buy, Negativ = Sell
    if macd > 0:
        return 'buy'
    elif macd < 0:
        return 'sell'
    else:
        return 'hold'

def bollinger_strategy(prices):
    """Bollinger Bands Strategie"""
    if len(prices) < 20:
        return 'hold'
    
    upper, middle, lower = calculate_bollinger_bands(prices)
    current_price = prices[-1]
    
    # Kaufen wenn Preis nahe der unteren Band
    if current_price <= lower:
        return 'buy'
    # Verkaufen wenn Preis nahe der oberen Band
    elif current_price >= upper:
        return 'sell'
    else:
        return 'hold'

def stochastic_strategy(prices):
    """Stochastic Oscillator Strategie"""
    if len(prices) < 14:
        return 'hold'
    
    stoch = calculate_stochastic(prices)
    
    if stoch < 20:  # Überverkauft
        return 'buy'
    elif stoch > 80:  # Überkauft
        return 'sell'
    else:
        return 'hold'

def momentum_strategy(prices):
    """Momentum Strategie"""
    if len(prices) < 10:
        return 'hold'
    
    # Berechne Momentum über 10 Tage
    momentum = (prices[-1] - prices[-10]) / prices[-10] * 100
    
    # Kaufen bei starkem positiven Momentum
    if momentum > 5:  # 5% Anstieg in 10 Tagen
        return 'buy'
    # Verkaufen bei starkem negativen Momentum
    elif momentum < -5:  # 5% Rückgang in 10 Tagen
        return 'sell'
    else:
        return 'hold'

def mean_reversion_strategy(prices):
    """Mean Reversion Strategie"""
    if len(prices) < 20:
        return 'hold'
    
    # Berechne 20-Tage Durchschnitt
    avg_20 = calculate_sma(prices, 20)
    current_price = prices[-1]
    
    # Prozentuale Abweichung vom Durchschnitt
    deviation = ((current_price - avg_20) / avg_20) * 100
    
    # Kaufen wenn Preis weit unter Durchschnitt (erwartet Rückkehr)
    if deviation < -10:  # 10% unter Durchschnitt
        return 'buy'
    # Verkaufen wenn Preis weit über Durchschnitt
    elif deviation > 10:  # 10% über Durchschnitt
        return 'sell'
    else:
        return 'hold'

def buy_and_hold_strategy(prices):
    """Buy & Hold Strategie - Kaufen und halten"""
    # Diese Strategie kauft nur am ersten Tag und hält dann
    # Im Backtesting System wird dies durch einen Kauf am Anfang
    # und dann nur 'hold' Signale erreicht
    return 'buy'

def simple_backtest(prices, strategy_func, initial_capital):
    """Einfaches Backtesting"""
    capital = initial_capital
    shares = 0
    portfolio_values = []
    trades = 0
    
    for i, price in enumerate(prices):
        current_prices = prices[:i+1]
        
        # Strategie anwenden
        if strategy_func == buy_and_hold_strategy:
            # Spezielle Behandlung für Buy & Hold
            if i == 0:  # Nur am ersten Tag kaufen
                signal = 'buy'
            else:
                signal = 'hold'
        else:
            signal = strategy_func(current_prices)
        
        # Trading Logik
        if signal == 'buy' and capital > price:
            # Kaufen (alles verfügbare Kapital einsetzen)
            shares_to_buy = capital / price  # Erlaube Bruchteile
            shares += shares_to_buy
            capital = 0  # Alles investiert
            trades += 1
        elif signal == 'sell' and shares > 0:
            # Verkaufen (alle Aktien verkaufen)
            capital += shares * price
            shares = 0
            trades += 1
        
        # Portfolio Wert berechnen
        portfolio_value = capital + (shares * price)
        portfolio_values.append(portfolio_value)
    
    return portfolio_values, trades

def get_stock_data(symbol, days):
    """Lädt Aktiendaten von Yahoo Finance"""
    try:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        ticker = yf.Ticker(symbol)
        data = ticker.history(start=start_date, end=end_date)
        
        if data.empty:
            raise ValueError(f"Keine Daten für {symbol} gefunden")
        
        prices = data['Close'].tolist()
        
        if len(prices) < 30:
            raise ValueError(f"Nicht genügend Daten: {len(prices)} Tage")
        
        print(f"✅ {len(prices)} Tage Daten für {symbol} geladen")
        print(f"📊 Preisbereich: ${min(prices):.2f} - ${max(prices):.2f}")
        print(f"📊 Startpreis: ${prices[0]:.2f}, Endpreis: ${prices[-1]:.2f}")
        return prices
        
    except Exception as e:
        raise Exception(f"Fehler beim Laden der Daten: {e}")

def main():
    """Hauptfunktion"""
    try:
        print("🤖 TRADING BOT GESTARTET")
        print("="*50)
        print(f"Symbol: {SYMBOL}")
        print(f"Zeitraum: {BACKTEST_DAYS} Tage")
        print(f"Startkapital: ${INITIAL_CAPITAL:,.2f}")
        print("="*50)
        
        # Daten laden
        print("\n📊 Lade Marktdaten...")
        prices = get_stock_data(SYMBOL, BACKTEST_DAYS)
        
        # Zeitraum für Ausgabe
        end_date = datetime.now()
        start_date = end_date - timedelta(days=BACKTEST_DAYS)
        
        # Alle Strategien definieren
        strategies = [
            ("📊 RSI", rsi_strategy),
            ("📈 SMA", sma_strategy),
            ("⚡ EMA", ema_strategy),
            ("🎯 MACD", macd_strategy),
            ("🔔 Bollinger", bollinger_strategy),
            ("📡 Stochastic", stochastic_strategy),
            ("🚀 Momentum", momentum_strategy),
            ("🔄 Mean Reversion", mean_reversion_strategy),
            ("💎 Buy & Hold", buy_and_hold_strategy)
        ]
        
        results = []
        
        # Alle Strategien testen
        for name, strategy_func in strategies:
            print(f"\n{name} Strategie...")
            portfolio, trades = simple_backtest(prices, strategy_func, INITIAL_CAPITAL)
            final_value = portfolio[-1]
            return_pct = ((final_value - INITIAL_CAPITAL) / INITIAL_CAPITAL) * 100
            
            results.append({
                'name': name,
                'final': final_value,
                'return': return_pct,
                'trades': trades
            })
        
        # Ausgabe
        print("\n" + "="*80)
        print("🤖 TRADING BOT BACKTESTING ERGEBNISSE - ALLE STRATEGIEN")
        print("="*80)
        
        print(f"\nSymbol: {SYMBOL}")
        print(f"Zeitraum: {start_date.date()} bis {end_date.date()}")
        print(f"Anfangskapital: ${INITIAL_CAPITAL:,.2f}")
        
        print(f"\n{'Strategie':<20} {'Endkapital':<15} {'Rendite':<12} {'Trades':<8}")
        print("-" * 65)
        
        # Sortiere Strategien nach Rendite (beste zuerst)
        results.sort(key=lambda x: x['return'], reverse=True)
        
        for i, result in enumerate(results):
            emoji = "🏆" if i == 0 else "📈" if result['return'] > 0 else "📉"
            print(f"{emoji} {result['name']:<18} ${result['final']:>12,.2f} {result['return']:>8.2f}% {result['trades']:>6}")
        
        # Beste Strategie
        best_strategy = results[0]
        print(f"\n🏆 BESTE STRATEGIE: {best_strategy['name']} mit {best_strategy['return']:.2f}% Rendite!")
        
        print("="*80)
        
        print("\n✅ Backtesting erfolgreich abgeschlossen!")
        
    except Exception as e:
        print(f"\n❌ Fehler: {e}")
        print("Mögliche Lösungen:")
        print("1. Internetverbindung prüfen")
        print("2. Anderes Symbol versuchen (z.B. AAPL)")
        print("3. Zeitraum reduzieren")

if __name__ == "__main__":
    main()
