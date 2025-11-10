import sys
import os
from flask import Flask, render_template, request, jsonify
from datetime import datetime, timedelta
import logging

# Add the project root to Python path to ensure proper module imports
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# For Vercel, we need to handle the src imports differently
try:
    from src.backtest_engine import BacktestEngine
    from src.config import TradingConfig
    from src.data_provider import DataProvider
    from src.strategies.rsi_strategy import RSIStrategy
    from src.strategies.sma_strategy import SMAStrategy
    from src.strategies.buy_hold_strategy import BuyAndHoldStrategy
    from src.strategies.advanced_strategies import (
        EMAStrategy, MACDStrategy, BollingerStrategy, 
        StochasticStrategy, MomentumStrategy, MeanReversionStrategy
    )
except ImportError as e:
    print(f"Import error: {e}")
    # For Vercel deployment, try alternative import paths
    import importlib.util
    
    # Try to import modules directly
    sys.path.append(os.path.join(project_root, 'src'))
    from backtest_engine import BacktestEngine
    from config import TradingConfig
    from data_provider import DataProvider
    from strategies.rsi_strategy import RSIStrategy
    from strategies.sma_strategy import SMAStrategy
    from strategies.buy_hold_strategy import BuyAndHoldStrategy
    from strategies.advanced_strategies import (
        EMAStrategy, MACDStrategy, BollingerStrategy, 
        StochasticStrategy, MomentumStrategy, MeanReversionStrategy
    )

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Disable caching in development mode
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    response.headers["Access-Control-Allow-Origin"] = "*"
    return response

class TradingBotAPI:
    def __init__(self):
        self.symbol = 'AAPL'  # Use AAPL as default since BTC-USD is problematic
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
            BuyAndHoldStrategy()
        ]
    
    def run_backtest(self, config_data):
        """Run backtest with given configuration"""
        try:
            # Update configuration
            self.symbol = config_data.get('symbol', 'AAPL')
            backtest_days = config_data.get('backtest_days', 1825)
            self.period = f"{backtest_days}d"
            self.initial_capital = config_data.get('initial_capital', 100000)
            
            logger.info(f"🚀 Starting backtest for {self.symbol}")
            logger.info(f"📊 Parameters: {backtest_days} days, ${self.initial_capital} initial capital")
            
            # Create config object
            config = TradingConfig(
                symbol=self.symbol,
                initial_capital=self.initial_capital,
                backtest_days=backtest_days
            )
            
            # Get market data
            logger.info(f"📈 Loading market data for {config.symbol}...")
            data_provider = DataProvider()
            
            try:
                prices = data_provider.get_stock_data(config.symbol, backtest_days)
                logger.info(f"✅ Successfully loaded {len(prices)} prices")
            except Exception as data_error:
                logger.error(f"❌ Error loading market data: {str(data_error)}")
                return {
                    'success': False,
                    'error': f'Error loading market data: {str(data_error)}'
                }
            
            if len(prices) < 100:
                logger.warning(f"⚠️ Not enough data: {len(prices)} < 100")
                return {
                    'success': False,
                    'error': f'Insufficient market data ({len(prices)} days, minimum 100 required)'
                }
            
            # Cache prices for later use
            self.cached_prices = prices
            
            # Run backtest for each strategy
            backtest_engine = BacktestEngine(initial_capital=self.initial_capital)
            results = []
            
            for strategy in self.strategies:
                logger.info(f"🔄 Running backtest for {strategy.__class__.__name__}")
                result = backtest_engine.run_backtest(strategy, prices)
                
                logger.info(f"📊 {strategy.__class__.__name__}: Final=${result.final_value:.2f}, Return={result.return_percentage:.2f}%, Trades={result.total_trades}")
                
                result.id = len(results)
                results.append(result)
            
            # Sort by performance (return percentage)
            results.sort(key=lambda x: x.return_percentage, reverse=True)
            
            # Assign new IDs AFTER sorting
            for i, result in enumerate(results):
                result.id = i
            
            # Cache results
            self.cached_results = results
            
            # Convert results to dict format for JSON response
            results_data = []
            for i, result in enumerate(results):
                logger.info(f"📊 Dashboard: Strategy {i} = {result.strategy_name} with {result.return_percentage:.2f}% return")
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
            logger.error(f"❌ Backtest error: {e}")
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

@app.route('/api/health', methods=['GET'])
def api_health():
    """Health Check Endpoint"""
    return jsonify({
        'status': 'healthy ✅',
        'timestamp': datetime.now().isoformat(),
        'version': '5.0.0 - Vercel Deployment',
        'message': 'Trading Bot is running on Vercel!'
    })

@app.route('/api/config', methods=['GET'])
def api_config():
    """Get current configuration"""
    return jsonify({
        'success': True,
        'data': {
            'symbol': bot_api.symbol,
            'period': bot_api.period,
            'initial_capital': bot_api.initial_capital,
            'backtest_days': 1825
        }
    })

@app.route('/api/backtest', methods=['POST'])
def api_backtest():
    """API Endpoint for Backtest"""
    try:
        config_data = request.json
        result = bot_api.run_backtest(config_data)
        return jsonify(result)
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/symbols', methods=['GET'])
def api_get_symbols():
    """Get available trading symbols"""
    symbols = [
        {'symbol': 'AAPL', 'name': 'Apple Inc.', 'type': 'Stock'},
        {'symbol': 'MSFT', 'name': 'Microsoft Corporation', 'type': 'Stock'},
        {'symbol': 'TSLA', 'name': 'Tesla Inc.', 'type': 'Stock'},
        {'symbol': 'NVDA', 'name': 'NVIDIA Corporation', 'type': 'Stock'},
        {'symbol': 'SPY', 'name': 'SPDR S&P 500 ETF', 'type': 'ETF'},
        {'symbol': 'BTC-USD', 'name': 'Bitcoin (Fallback Data)', 'type': 'Crypto'}
    ]
    return jsonify({
        'success': True,
        'data': symbols
    })

# For Vercel deployment
application = app

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8081))
    print("🚀 Trading Bot - Vercel Edition")
    print(f"📊 Dashboard: http://localhost:{port}")
    print("💡 Run backtest first to see trading results")
    app.run(debug=True, host='0.0.0.0', port=port)