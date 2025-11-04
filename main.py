#!/usr/bin/env python3
"""
Trading Bot - Modulare Version
==============================

Ein professioneller Trading Bot mit modularer Architektur.
Entwickelt für Schulprojekt mit Yahoo Finance Daten.

Autor: Silvan
Datum: September 2025
Version: 2.0.0
"""

import sys
import os
from datetime import datetime, timedelta

# Pfad für lokale Module hinzufügen
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.config import TradingConfig
from src.data_provider import DataProvider
from src.backtest_engine import BacktestEngine
from src.strategies import (
    RSIStrategy,
    SMAStrategy,
    BuyAndHoldStrategy,
    EMAStrategy,
    MACDStrategy,
    BollingerStrategy,
    StochasticStrategy,
    MomentumStrategy,
    MeanReversionStrategy
)

class TradingBot:
    """
    Hauptklasse für den Trading Bot
    """
    
    def __init__(self, config: TradingConfig = None):
        self.config = config or TradingConfig()
        self.data_provider = DataProvider()
        self.backtest_engine = BacktestEngine(self.config.initial_capital)
        
    def create_strategies(self):
        """Erstellt alle Trading Strategien mit Konfiguration"""
        return [
            RSIStrategy(
                rsi_period=self.config.rsi_period,
                oversold=self.config.rsi_oversold,
                overbought=self.config.rsi_overbought
            ),
            SMAStrategy(
                short_period=self.config.sma_short_period,
                long_period=self.config.sma_long_period
            ),
            EMAStrategy(
                short_period=self.config.ema_short_period,
                long_period=self.config.ema_long_period
            ),
            MACDStrategy(
                fast=self.config.macd_fast,
                slow=self.config.macd_slow
            ),
            BollingerStrategy(
                period=self.config.bollinger_period,
                std_dev=self.config.bollinger_std_dev
            ),
            StochasticStrategy(
                period=self.config.stochastic_period,
                oversold=self.config.stochastic_oversold,
                overbought=self.config.stochastic_overbought
            ),
            MomentumStrategy(
                period=self.config.momentum_period,
                threshold=self.config.momentum_threshold
            ),
            MeanReversionStrategy(
                period=self.config.mean_reversion_period,
                threshold=self.config.mean_reversion_threshold
            ),
            BuyAndHoldStrategy()
        ]
    
    def run_analysis(self):
        """Führt die komplette Analyse durch"""
        try:
            print("🤖 TRADING BOT GESTARTET (Modulare Version)")
            print("="*60)
            print(f"Symbol: {self.config.symbol}")
            print(f"Zeitraum: {self.config.backtest_days} Tage")
            print(f"Startkapital: ${self.config.initial_capital:,.2f}")
            print("="*60)
            
            # Daten laden
            print("\n📊 Lade Marktdaten...")
            prices = self.data_provider.get_stock_data(
                self.config.symbol, 
                self.config.backtest_days
            )
            
            # Strategien erstellen
            strategies = self.create_strategies()
            
            # Backtesting durchführen
            print(f"\n🔍 Teste {len(strategies)} Strategien...")
            results = self.backtest_engine.compare_strategies(strategies, prices)
            
            # Ergebnisse anzeigen
            self.display_results(results, prices)
            
        except Exception as e:
            print(f"\n❌ Fehler: {e}")
            print("Mögliche Lösungen:")
            print("1. Internetverbindung prüfen")
            print("2. Anderes Symbol versuchen (z.B. AAPL)")
            print("3. Zeitraum reduzieren")
    
    def display_results(self, results, prices):
        """Zeigt die Backtest-Ergebnisse an"""
        # Zeitraum berechnen
        end_date = datetime.now()
        start_date = end_date - timedelta(days=self.config.backtest_days)
        
        print("\n" + "="*80)
        print("🤖 TRADING BOT BACKTESTING ERGEBNISSE - ALLE STRATEGIEN")
        print("="*80)
        
        print(f"\nSymbol: {self.config.symbol}")
        print(f"Zeitraum: {start_date.date()} bis {end_date.date()}")
        print(f"Anfangskapital: ${self.config.initial_capital:,.2f}")
        
        print(f"\n{'Strategie':<20} {'Endkapital':<15} {'Rendite':<12} {'Trades':<8}")
        print("-" * 65)
        
        for i, result in enumerate(results):
            emoji = "🏆" if i == 0 else "📈" if result.return_percentage > 0 else "📉"
            print(f"{emoji} {result.strategy_name:<18} ${result.final_value:>12,.2f} "
                  f"{result.return_percentage:>8.2f}% {result.total_trades:>6}")
        
        # Beste Strategie
        best_result = results[0]
        print(f"\n🏆 BESTE STRATEGIE: {best_result.strategy_name} "
              f"mit {best_result.return_percentage:.2f}% Rendite!")
        
        # Performance-Statistiken
        positive_strategies = [r for r in results if r.return_percentage > 0]
        print(f"📊 {len(positive_strategies)}/{len(results)} Strategien "
              f"waren profitabel")
        
        print("="*80)
        print("\n✅ Backtesting erfolgreich abgeschlossen!")

def main():
    """Hauptfunktion"""
    # Standardkonfiguration oder benutzerdefiniert
    config = TradingConfig()
    
    # Trading Bot erstellen und ausführen
    bot = TradingBot(config)
    bot.run_analysis()

if __name__ == "__main__":
    main()
