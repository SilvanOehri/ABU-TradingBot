from flask import Flask, render_template, request, jsonify
from src.backtest_engine import BacktestEngine
from src.config import Config
from src.data_provider import DataProvider
from src.strategies.rsi_strategy import RSIStrategy
from src.strategies.sma_strategy import SMAStrategy
from src.strategies.ema_strategy import EMAStrategy
from src.strategies.macd_strategy import MACDStrategy
from src.strategies.bollinger_strategy import BollingerStrategy
from src.strategies.stochastic_strategy import StochasticStrategy
from src.strategies.momentum_strategy import MomentumStrategy
from src.strategies.mean_reversion_strategy import MeanReversionStrategy
from src.strategies.buy_hold_strategy import BuyHoldStrategy
from datetime import datetime, timedelta
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

class TradingBotAPI:
    def __init__(self):
        self.symbol = 'BTC-USD'
        self.period = '5y'
        self.initial_capital = 100000
        self.cached_results = None
        self.cached_prices = None
        
        # Initialize strategies
        self.strategies = [
            RSIStrategy(),
            SMAStrategy(),
            EMAStrategy(),
            MACDStrategy(),
            BollingerStrategy(),
            StochasticStrategy(),
            MomentumStrategy(),
            MeanReversionStrategy(),
            BuyHoldStrategy()
        ]
    
    def run_backtest(self, config_data):
        """Run backtest with given configuration"""
        try:
            # Update configuration
            self.symbol = config_data.get('symbol', 'BTC-USD')
            self.period = f"{config_data.get('backtest_days', 1825)}d"
            self.initial_capital = config_data.get('initial_capital', 100000)
            
            # Create config object
            config = Config(
                symbol=self.symbol,
                period=self.period,
                initial_capital=self.initial_capital
            )
            
            # Get market data
            data_provider = DataProvider()
            prices = data_provider.get_stock_data(config.symbol, config.period)
            
            if len(prices) < 100:
                return {
                    'success': False,
                    'error': 'Nicht genügend Marktdaten verfügbar'
                }
            
            # Cache prices for later use
            self.cached_prices = prices
            
            # Run backtest for each strategy
            backtest_engine = BacktestEngine()
            results = []
            
            for strategy in self.strategies:
                logger.info(f"Running backtest for {strategy.__class__.__name__}")
                result = backtest_engine.run_backtest(strategy, config, prices)
                
                # Assign strategy ID
                result.id = len(results)
                results.append(result)
            
            # Sort by performance (return percentage)
            results.sort(key=lambda x: x.return_percentage, reverse=True)
            
            # Cache results
            self.cached_results = results
            
            # Convert results to dict format for JSON response
            results_data = []
            for result in results:
                results_data.append({
                    'id': result.id,
                    'strategy_name': result.strategy_name,
                    'final_value': result.final_value,
                    'return_percentage': result.return_percentage,
                    'portfolio_values': result.portfolio_values,
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
            logger.error(f"Backtest error: {e}")
            return {
                'success': False,
                'error': str(e)
            }

# Trading Bot API Instance
bot_api = TradingBotAPI()

# Routes
@app.route('/')
def dashboard():
    """Main Dashboard"""
    return render_template('dashboard.html')

@app.route('/strategy/<int:strategy_id>')
def strategy_details(strategy_id):
    """Strategy details page"""
    return render_template('strategy_details.html', strategy_id=strategy_id)

@app.route('/compare')
def strategy_comparison():
    """Strategy comparison page"""
    return render_template('strategy_comparison.html')

# API Routes
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
def api_backtest():
    """API Endpoint für Backtest"""
    try:
        config_data = request.json
        result = bot_api.run_backtest(config_data)
        return jsonify(result)
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/compare', methods=['POST'])
def api_compare_strategies():
    """API Endpoint für Strategien-Vergleich"""
    try:
        data = request.json
        strategy_ids = data.get('strategy_ids', [])
        
        if not strategy_ids or len(strategy_ids) < 2:
            return jsonify({
                'success': False,
                'error': 'Keine Strategien zum Vergleich ausgewählt'
            }), 400
        
        if not bot_api.cached_results:
            return jsonify({
                'success': False,
                'error': 'Kein Backtest durchgeführt'
            }), 400
        
        comparison_data = []
        for strategy_id in strategy_ids:
            if strategy_id < len(bot_api.cached_results):
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
        
        strategy_result = bot_api.cached_results[strategy_id]
        
        # Trade History für JSON konvertieren
        trade_history_json = []
        for trade in strategy_result.trade_history:
            trade_history_json.append({
                'date': trade.date.isoformat(),
                'signal': trade.signal,
                'price': trade.price,
                'shares': trade.shares,
                'capital': trade.capital,
                'portfolio_value': trade.portfolio_value,
                'indicator_values': trade.indicator_values
            })
        
        return jsonify({
            'success': True,
            'data': {
                'strategy_name': strategy_result.strategy_name,
                'final_value': strategy_result.final_value,
                'return_percentage': strategy_result.return_percentage,
                'portfolio_values': strategy_result.portfolio_values,
                'total_trades': strategy_result.total_trades,
                'profit_loss': strategy_result.profit_loss,
                'max_drawdown': strategy_result.max_drawdown,
                'sharpe_ratio': strategy_result.sharpe_ratio,
                'win_rate': strategy_result.win_rate,
                'trade_history': trade_history_json,
                'market_prices': bot_api.cached_prices[-len(strategy_result.portfolio_values):] if bot_api.cached_prices else []
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/symbols', methods=['GET'])
def api_get_symbols():
    """Get available trading symbols"""
    symbols = [
        {'symbol': 'BTC-USD', 'name': 'Bitcoin', 'type': 'Crypto'},
        {'symbol': 'ETH-USD', 'name': 'Ethereum', 'type': 'Crypto'},
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
    app.run(debug=True, host='0.0.0.0', port=8080)
