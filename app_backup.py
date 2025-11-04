#!/usr/bin/env python3
"""
Trading Bot Flask Web Application
=================================

Web-Interface für den Trading Bot mit REST API und Dashboard.
Läuft in Docker Container für einfaches Deployment.

Autor: Silvan
Datum: September 2025
Version: 3.0.0
"""

from flask import Flask, render_template, jsonify, request
import json
import sys
import os
from datetime import datetime, timedelta

# Pfad für lokale Module hinzufügen
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.config import TradingConfig
from src.data_provider import DataProvider
from src.backtest_engine import BacktestEngine, BacktestResult
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

app = Flask(__name__)

class TradingBotAPI:
    """
    Trading Bot API Klasse für Flask Integration
    """
    
    def __init__(self):
        self.data_provider = DataProvider()
        self.cached_results = {}
        self.cached_config = None
        self.cached_prices = None
        self.cached_start_date = None
        
    def create_strategies(self, config: TradingConfig):
        """Erstellt alle Trading Strategien mit Konfiguration"""
        return [
            RSIStrategy(
                rsi_period=config.rsi_period,
                oversold=config.rsi_oversold,
                overbought=config.rsi_overbought
            ),
            SMAStrategy(
                short_period=config.sma_short_period,
                long_period=config.sma_long_period
            ),
            EMAStrategy(
                short_period=config.ema_short_period,
                long_period=config.ema_long_period
            ),
            MACDStrategy(
                fast=config.macd_fast,
                slow=config.macd_slow
            ),
            BollingerStrategy(
                period=config.bollinger_period,
                std_dev=config.bollinger_std_dev
            ),
            StochasticStrategy(
                period=config.stochastic_period,
                oversold=config.stochastic_oversold,
                overbought=config.stochastic_overbought
            ),
            MomentumStrategy(
                period=config.momentum_period,
                threshold=config.momentum_threshold
            ),
            MeanReversionStrategy(
                period=config.mean_reversion_period,
                threshold=config.mean_reversion_threshold
            ),
            BuyAndHoldStrategy()
        ]
    
    def run_backtest(self, config_dict=None):
        """Führt Backtest durch und gibt Ergebnisse zurück"""
        try:
            # Konfiguration erstellen
            if config_dict:
                config = TradingConfig(**config_dict)
            else:
                config = TradingConfig()
            
            # Startdatum berechnen
            end_date = datetime.now()
            start_date = end_date - timedelta(days=config.backtest_days)
            
            # Daten laden
            prices = self.data_provider.get_stock_data(
                config.symbol, 
                config.backtest_days
            )
            
            # Cache für Details speichern
            self.cached_prices = prices
            self.cached_start_date = start_date
            
            # Backtest Engine
            backtest_engine = BacktestEngine(config.initial_capital)
            
            # Strategien erstellen
            strategies = self.create_strategies(config)
            
            # Backtesting durchführen
            results = backtest_engine.compare_strategies(strategies, prices, start_date)
            
            # Cache results mit ID
            self.cached_results = {}
            for i, result in enumerate(results):
                self.cached_results[i] = result
            
            self.cached_config = config
            
            # Für JSON serialisierbar machen
            results_data = []
            for i, result in enumerate(results):
                results_data.append({
                    'id': i,
                    'strategy_name': result.strategy_name,
                    'initial_capital': result.initial_capital,
                    'final_value': result.final_value,
                    'return_percentage': result.return_percentage,
                    'total_trades': result.total_trades,
                    'profit_loss': result.profit_loss,
                    'max_drawdown': result.max_drawdown,
                    'sharpe_ratio': result.sharpe_ratio,
                    'win_rate': result.win_rate
                })
            
            return {
                'success': True,
                'data': {
                    'config': config.to_dict(),
                    'results': results_data,
                    'market_data': {
                        'symbol': config.symbol,
                        'start_price': prices[0],
                        'end_price': prices[-1],
                        'price_range': {
                            'min': min(prices),
                            'max': max(prices)
                        },
                        'total_days': len(prices)
                    },
                    'timestamp': datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_strategy_details(self, strategy_id):
        """Holt detaillierte Informationen zu einer Strategie"""
        try:
            if strategy_id not in self.cached_results:
                return {
                    'success': False,
                    'error': 'Strategie nicht gefunden. Bitte führe zuerst einen Backtest durch.'
                }
            
            result = self.cached_results[strategy_id]
            
            # Trade History für JSON serialisierbar machen
            trade_history = []
            for trade in result.trade_history:
                trade_dict = {
                    'date': trade.date,
                    'day_index': trade.day_index,
                    'signal': trade.signal,
                    'price': trade.price,
                    'shares_before': trade.shares_before,
                    'shares_after': trade.shares_after,
                    'capital_before': trade.capital_before,
                    'capital_after': trade.capital_after,
                    'portfolio_value': trade.portfolio_value,
                    'indicator_values': trade.indicator_values or {}
                }
                trade_history.append(trade_dict)
            
            return {
                'success': True,
                'data': {
                    'strategy_name': result.strategy_name,
                    'initial_capital': result.initial_capital,
                    'final_value': result.final_value,
                    'return_percentage': result.return_percentage,
                    'total_trades': result.total_trades,
                    'profit_loss': result.profit_loss,
                    'max_drawdown': result.max_drawdown,
                    'sharpe_ratio': result.sharpe_ratio,
                    'win_rate': result.win_rate,
                    'portfolio_values': result.portfolio_values,
                    'trade_history': trade_history,
                    'market_data': {
                        'symbol': self.cached_config.symbol if self.cached_config else 'Unknown',
                        'prices': self.cached_prices[-100:] if self.cached_prices else []  # Nur letzte 100 für Performance
                    }
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

# Trading Bot API Instance
bot_api = TradingBotAPI()

@app.route('/')
def dashboard():
    """Haupt-Dashboard"""
    return render_template('dashboard.html')

@app.route('/strategy/<int:strategy_id>')
def strategy_details(strategy_id):
    """Strategy details page"""
    return render_template('strategy_details.html', strategy_id=strategy_id)

@app.route('/')
def dashboard():
    """Haupt-Dashboard"""
    return render_template('dashboard.html')

@app.route('/compare')
def strategy_comparison():
    """Strategy comparison page"""
    return render_template('strategy_comparison.html')

@app.route('/api/config', methods=['GET'])
def api_config():
    """Get current configuration"""
    return jsonify({
        'success': True,
        'config': {
            'symbol': bot_api.symbol,
            'period': bot_api.period,
            'initial_capital': bot_api.initial_capital
        }
    })

@app.route('/api/backtest', methods=['POST'])

@app.route('/')
def dashboard():
    """Haupt-Dashboard"""
    return render_template('dashboard.html')

@app.route('/strategy/<int:strategy_id>')
def strategy_details(strategy_id):
    """Strategie Details Seite"""
    return render_template('strategy_details.html', strategy_id=strategy_id)

@app.route('/compare')
def strategy_comparison():
    """Strategien Vergleichsseite"""
    return render_template('strategy_comparison.html')

@app.route('/api/backtest', methods=['POST'])
def api_backtest():
    """API Endpoint für Backtest"""
    try:
        config_data = request.get_json() if request.is_json else {}
        result = bot_api.run_backtest(config_data)
        return jsonify(result)
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/strategy/<int:strategy_id>', methods=['GET'])
def api_strategy_details(strategy_id):
    """API Endpoint für Strategie Details"""
    try:
        result = bot_api.get_strategy_details(strategy_id)
        return jsonify(result)
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/compare', methods=['POST'])
def api_strategy_comparison():
    """API Endpoint für Strategien-Vergleich"""
    try:
        data = request.get_json()
        strategy_ids = data.get('strategy_ids', [])
        
        if not strategy_ids:
            return jsonify({
                'success': False,
                'error': 'Keine Strategien zum Vergleich ausgewählt'
            }), 400
        
        comparison_data = []
        for strategy_id in strategy_ids:
            if strategy_id in bot_api.cached_results:
                result = bot_api.cached_results[strategy_id]
                comparison_data.append({
                    'id': strategy_id,
                    'strategy_name': result.strategy_name,
                    'portfolio_values': result.portfolio_values,
                    'return_percentage': result.return_percentage,
                    'final_value': result.final_value
                })
        
        return jsonify({
            'success': True,
            'data': {
                'strategies': comparison_data,
                'market_data': {
                    'prices': bot_api.cached_prices[-100:] if bot_api.cached_prices else []
                }
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/strategy/<int:strategy_id>', methods=['GET'])
def api_get_strategy_details(strategy_id):
    """API Endpoint für Strategie-Details"""
    try:
        if not bot_api.cached_results or strategy_id >= len(bot_api.cached_results):
            return jsonify({
                'success': False,
                'error': 'Strategie nicht gefunden oder kein Backtest durchgeführt'
            }), 404
        
        # Hole die entsprechende Strategie aus den gecachten Ergebnissen
        strategy_result = None
        for result_data in bot_api.cached_results:
            # Hier verwenden wir die ursprünglichen BacktestResult Objekte
            if hasattr(result_data, 'strategy_name'):
                if strategy_id == 0:  # Erste Strategie (beste)
                    strategy_result = result_data
                    break
                strategy_id -= 1
        
        if not strategy_result:
            return jsonify({
                'success': False,
                'error': 'Strategie nicht gefunden'
            }), 404
        
        # Trade History für JSON konvertieren
        trade_history_json = []
        for trade in strategy_result.trade_history:
            trade_history_json.append({
                'date': trade.date,
                'day_index': trade.day_index,
                'signal': trade.signal,
                'price': trade.price,
                'shares_before': trade.shares_before,
                'shares_after': trade.shares_after,
                'capital_before': trade.capital_before,
                'capital_after': trade.capital_after,
                'portfolio_value': trade.portfolio_value
            })
        
        return jsonify({
            'success': True,
            'data': {
                'strategy_name': strategy_result.strategy_name,
                'initial_capital': strategy_result.initial_capital,
                'final_value': strategy_result.final_value,
                'return_percentage': strategy_result.return_percentage,
                'total_trades': strategy_result.total_trades,
                'profit_loss': strategy_result.profit_loss,
                'trade_history': trade_history_json,
                'portfolio_values': strategy_result.portfolio_values
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/config', methods=['GET'])
def api_get_config():
    """API Endpoint für Standard-Konfiguration"""
    config = TradingConfig()
    return jsonify({
        'success': True,
        'data': config.to_dict()
    })

@app.route('/strategy/<int:strategy_id>')
def strategy_details(strategy_id):
    """Strategy details page"""
    return render_template('strategy_details.html', strategy_id=strategy_id)

@app.route('/compare')
def strategy_comparison():
    """Strategy comparison page"""
    return render_template('strategy_comparison.html')

@app.route('/api/config', methods=['GET'])
def api_config():
    """Get current configuration"""
    return jsonify({
        'success': True,
        'config': {
            'symbol': bot_api.symbol,
            'period': bot_api.period,
            'initial_capital': bot_api.initial_capital
        }
    })

@app.route('/api/symbols', methods=['GET'])
def api_get_symbols():
    """API Endpoint für verfügbare Symbole"""
    symbols = [
        {'symbol': 'BTC-USD', 'name': 'Bitcoin USD', 'type': 'Cryptocurrency'},
        {'symbol': 'ETH-USD', 'name': 'Ethereum USD', 'type': 'Cryptocurrency'},
        {'symbol': 'AAPL', 'name': 'Apple Inc.', 'type': 'Stock'},
        {'symbol': 'GOOGL', 'name': 'Alphabet Inc.', 'type': 'Stock'},
        {'symbol': 'MSFT', 'name': 'Microsoft Corporation', 'type': 'Stock'},
        {'symbol': 'TSLA', 'name': 'Tesla Inc.', 'type': 'Stock'},
        {'symbol': 'NVDA', 'name': 'NVIDIA Corporation', 'type': 'Stock'},
        {'symbol': 'SPY', 'name': 'SPDR S&P 500 ETF', 'type': 'ETF'}
    ]
    return jsonify({
        'success': True,
        'data': symbols
    })

@app.route('/api/health', methods=['GET'])
def api_health():
    """Health Check Endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '3.0.0'
    })

@app.errorhandler(404)
def not_found_error(error):
    return jsonify({
        'success': False,
        'error': 'Endpoint not found'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500

if __name__ == '__main__':
    # Development Server
    app.run(host='0.0.0.0', port=8080, debug=True)
