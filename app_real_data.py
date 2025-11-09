from flask import Flask, render_template, request, jsonify
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
from datetime import datetime, timedelta
import logging
import os

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
    return response

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
            BuyAndHoldStrategy()
        ]
    
    def run_backtest(self, config_data):
        """Run backtest with given configuration"""
        try:
            # Update configuration
            self.symbol = config_data.get('symbol', 'BTC-USD')
            backtest_days = config_data.get('backtest_days', 1825)
            self.period = f"{backtest_days}d"
            self.initial_capital = config_data.get('initial_capital', 100000)
            
            logger.info(f" Starte Backtest für {self.symbol}")
            logger.info(f" Parameter: {backtest_days} Tage, ${self.initial_capital} Startkapital")
            
            # Create config object
            config = TradingConfig(
                symbol=self.symbol,
                initial_capital=self.initial_capital,
                backtest_days=backtest_days
            )
            
            # Get market data
            logger.info(f" Lade Marktdaten für {config.symbol}...")
            data_provider = DataProvider()
            
            try:
                prices = data_provider.get_stock_data(config.symbol, backtest_days)
                logger.info(f" {len(prices)} Preise erfolgreich geladen")
            except Exception as data_error:
                logger.error(f" Fehler beim Laden der Marktdaten: {str(data_error)}")
                return {
                    'success': False,
                    'error': f'Fehler beim Laden der Marktdaten: {str(data_error)}'
                }
            
            if len(prices) < 100:
                logger.warning(f" Zu wenig Daten: {len(prices)} < 100")
                return {
                    'success': False,
                    'error': f'Nicht genügend Marktdaten verfügbar ({len(prices)} Tage, mindestens 100 erforderlich)'
                }
            
            # Cache prices for later use
            self.cached_prices = prices
            
            # Run backtest for each strategy
            backtest_engine = BacktestEngine(initial_capital=self.initial_capital)
            results = []
            
            for strategy in self.strategies:
                logger.info(f"Running backtest for {strategy.__class__.__name__}")
                result = backtest_engine.run_backtest(strategy, prices)
                
                # DEBUG: Log the result details
                logger.info(f"   {strategy.__class__.__name__}: Final=${result.final_value:.2f}, Return={result.return_percentage:.2f}%, Trades={result.total_trades}")
                
                # Assign strategy ID
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
                logger.info(f"Dashboard: Strategy {i} = {result.strategy_name} mit {result.return_percentage:.2f}% Rendite")
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

@app.route('/strategy/<int:strategy_id>/fast')
def strategy_details_fast(strategy_id):
    """ ULTRA FAST Strategy details page - INSTANT LOADING"""
    return render_template('strategy_details_fast.html', strategy_id=strategy_id)

@app.route('/strategy/<int:strategy_id>/chart')
def strategy_chart(strategy_id):
    """ Strategy Chart View - NUR CHARTS"""
    return render_template('strategy_chart.html', strategy_id=strategy_id)

@app.route('/compare')
def compare_strategies():
    """ Strategy Comparison Page"""
    return render_template('strategy_comparison.html')

# API Routes
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

@app.route('/api/strategy/<int:strategy_id>', methods=['GET'])
def api_get_strategy_details(strategy_id):
    """ API mit ECHTEN 5-Jahre Backtest-Daten"""
    
    try:
        # Prüfe ob Backtest-Ergebnisse vorhanden sind
        if not bot_api.cached_results:
            return jsonify({
                'success': False,
                'error': 'Bitte führe zuerst einen Backtest durch. Gehe zum Dashboard und klicke "Backtest starten".'
            }), 400
        
        # Prüfe ob Strategy ID gültig ist
        if strategy_id >= len(bot_api.cached_results):
            return jsonify({
                'success': False,
                'error': f'Strategie-ID {strategy_id} nicht gefunden. Verfügbare IDs: 0-{len(bot_api.cached_results)-1}'
            }), 400
        
        # Hole die ECHTEN Backtest-Ergebnisse
        result = bot_api.cached_results[strategy_id]
        
        # ECHTE Trade-Historie konvertieren
        trade_history = []
        if hasattr(result, 'trade_history') and result.trade_history:
            logger.info(f"Konvertiere {len(result.trade_history)} echte Trades für {result.strategy_name}")
            
            for i, trade_record in enumerate(result.trade_history):
                # Berechne Änderung seit erstem Trade
                first_price = result.trade_history[0].price if result.trade_history else trade_record.price
                change = trade_record.price - first_price
                
                trade_history.append({
                    'date': trade_record.date,
                    'signal': trade_record.signal,
                    'price': round(trade_record.price, 2),
                    'shares_before': round(trade_record.shares_before, 4),
                    'shares_after': round(trade_record.shares_after, 4),
                    'capital_before': round(trade_record.capital_before, 2),
                    'capital_after': round(trade_record.capital_after, 2),
                    'portfolio_value': round(trade_record.portfolio_value, 2),
                    'change': round(change, 2),
                    'day_index': i
                })
        else:
            logger.warning(f"Keine Trade-Historie für {result.strategy_name} gefunden")
            return jsonify({
                'success': False,
                'error': f'Keine Trade-Historie für {result.strategy_name} verfügbar'
            }), 400
        
        # ECHTE Statistiken aus dem Backtest
        buy_trades = [t for t in trade_history if t['signal'] == 'buy']
        sell_trades = [t for t in trade_history if t['signal'] == 'sell']
        hold_trades = [t for t in trade_history if t['signal'] == 'hold']
        
        # Gewinnende/verlierende Trades basierend auf Portfolio-Entwicklung
        winning_trades = 0
        losing_trades = 0
        
        for i, trade in enumerate(trade_history):
            if trade['signal'] in ['buy', 'sell'] and i > 0:
                prev_portfolio = trade_history[i-1]['portfolio_value']
                current_portfolio = trade['portfolio_value']
                if current_portfolio > prev_portfolio:
                    winning_trades += 1
                else:
                    losing_trades += 1
        
        # Biggest win/loss
        portfolio_changes = []
        for i in range(1, len(trade_history)):
            change = trade_history[i]['portfolio_value'] - trade_history[i-1]['portfolio_value']
            portfolio_changes.append(change)
        
        biggest_win = max(portfolio_changes) if portfolio_changes else 0
        biggest_loss = min(portfolio_changes) if portfolio_changes else 0
        
        # RESPONSE mit allen ECHTEN Daten - DEBUGGING
        response_data = {
            'strategy_name': result.strategy_name,
            'description': result.description if hasattr(result, 'description') else '',
            'final_value': result.final_value,
            'return_percentage': result.return_percentage,
            'portfolio_values': result.portfolio_values,
            'total_trades': result.total_trades,
            'profit_loss': result.profit_loss,
            'max_drawdown': getattr(result, 'max_drawdown', -10.0),
            'sharpe_ratio': getattr(result, 'sharpe_ratio', 1.0),
            'win_rate': getattr(result, 'win_rate', 0.5),
            'trade_history': trade_history,
            'statistics': {
                'winning_trades': winning_trades,
                'losing_trades': losing_trades,
                'biggest_win': round(biggest_win, 2),
                'biggest_loss': round(biggest_loss, 2),
                'total_buy_trades': len(buy_trades),
                'total_sell_trades': len(sell_trades),
                'total_hold_days': len(hold_trades),
                'total_days': len(trade_history),
                'trades_per_month': round((result.total_trades / len(trade_history)) * 30, 1) if trade_history else 0
            },
            # DEBUG INFO
            'debug_info': {
                'strategy_id': strategy_id,
                'result_id': getattr(result, 'id', 'unknown'),
                'initial_capital': result.initial_capital,
                'calculated_return': round(((result.final_value - result.initial_capital) / result.initial_capital) * 100, 2),
                'stored_return': round(result.return_percentage, 2),
                'values_match': abs(((result.final_value - result.initial_capital) / result.initial_capital) * 100 - result.return_percentage) < 0.01
            }
        }
        
        logger.info(f" Echte Daten für {result.strategy_name}: {len(trade_history)} Tage, {result.total_trades} Trades, {result.return_percentage:.2f}% Rendite")
        logger.info(f" DEBUG: Strategy ID {strategy_id} → Final: ${result.final_value:.2f}, Return: {result.return_percentage:.2f}%")
        logger.info(f" DEBUG: Calculated return: {((result.final_value - result.initial_capital) / result.initial_capital) * 100:.2f}%")
        
        return jsonify({
            'success': True,
            'data': response_data
        })
        
    except Exception as e:
        logger.error(f"Strategy details error: {e}")
        return jsonify({
            'success': False,
            'error': f'Fehler beim Laden der Strategie-Details: {str(e)}'
        }), 500

@app.route('/api/compare', methods=['POST'])
def api_compare_strategies():
    """ Compare multiple strategies"""
    try:
        data = request.json
        strategy_ids = data.get('strategy_ids', [])
        
        if not strategy_ids:
            return jsonify({
                'success': False,
                'error': 'Keine Strategien zum Vergleich ausgewählt'
            })
        
        # Check if we have cached results
        if not bot_api.cached_results:
            return jsonify({
                'success': False,
                'error': 'Bitte führen Sie zuerst einen Backtest durch'
            })
        
        # Get selected strategies
        selected_strategies = []
        for strategy_id in strategy_ids:
            if 0 <= strategy_id < len(bot_api.cached_results):
                result = bot_api.cached_results[strategy_id]
                selected_strategies.append({
                    'id': result.id,
                    'strategy_name': result.strategy_name,
                    'final_value': result.final_value,
                    'return_percentage': result.return_percentage,
                    'portfolio_values': result.portfolio_values,
                    'total_trades': result.total_trades,
                    'profit_loss': result.profit_loss,
                    'max_drawdown': getattr(result, 'max_drawdown', 0),
                    'sharpe_ratio': getattr(result, 'sharpe_ratio', 0),
                    'win_rate': getattr(result, 'win_rate', 0)
                })
        
        return jsonify({
            'success': True,
            'data': {
                'strategies': selected_strategies,
                'symbol': bot_api.symbol,
                'initial_capital': bot_api.initial_capital
            }
        })
        
    except Exception as e:
        logger.error(f"Compare error: {e}")
        return jsonify({
            'success': False,
            'error': f'Fehler beim Vergleichen der Strategien: {str(e)}'
        }), 500

@app.route('/api/symbols', methods=['GET'])
def api_get_symbols():
    """Get available trading symbols"""
    symbols = [
        {'symbol': 'BTC-USD', 'name': 'Bitcoin', 'type': 'Crypto'},
        {'symbol': 'ETH-USD', 'name': 'Ethereum', 'type': 'Crypto'},
        {'symbol': 'AAPL', 'name': 'Apple Inc.', 'type': 'Stock'},
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
        'version': '4.0.0 - Echte 5-Jahre Backtest-Daten'
    })

if __name__ == '__main__':
    # Use PORT from environment (for deployment) or default to 8081
    port = int(os.environ.get('PORT', 8081))
    
    # Check if running in production
    is_production = os.environ.get('RENDER') is not None
    
    print("Trading Bot - 5 Year Backtest Data")
    print(f"Dashboard: http://localhost:{port}")
    print("Run backtest first to see all trading results")
    
    if is_production:
        print("Running on Render (Production Mode)")
    
    app.run(debug=not is_production, host='0.0.0.0', port=port)