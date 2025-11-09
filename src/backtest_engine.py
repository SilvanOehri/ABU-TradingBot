"""
Backtesting Engine für Trading Strategien
"""

from typing import List, Tuple, Dict, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
from .strategies.base_strategy import BaseStrategy

@dataclass
class TradeRecord:
    """Einzelner Trade-Record"""
    date: str
    day_index: int
    signal: str
    price: float
    shares_before: float
    shares_after: float
    capital_before: float
    capital_after: float
    portfolio_value: float
    indicator_values: Dict[str, float] = None

@dataclass
class BacktestResult:
    """Ergebnis eines Backtests"""
    strategy_name: str
    description: str
    initial_capital: float
    final_value: float
    return_percentage: float
    total_trades: int
    portfolio_values: List[float]
    trade_history: List[TradeRecord]
    max_drawdown: float
    sharpe_ratio: float
    win_rate: float
    
    @property
    def profit_loss(self) -> float:
        """Gewinn/Verlust in absoluten Zahlen"""
        return self.final_value - self.initial_capital

class BacktestEngine:
    """
    Engine für das Backtesting von Trading Strategien
    """
    
    def __init__(self, initial_capital: float = 100000.0):
        self.initial_capital = initial_capital
    
    def run_backtest(self, strategy: BaseStrategy, prices: List[float], start_date: datetime = None) -> BacktestResult:
        """
        Führt einen Backtest für eine Strategie durch
        
        Args:
            strategy: Die zu testende Strategie
            prices: Liste der historischen Preise
            start_date: Startdatum für die Trade-Historie
            
        Returns:
            BacktestResult mit allen Ergebnissen
        """
        # Strategie zurücksetzen
        strategy.reset()
        
        capital = self.initial_capital
        shares = 0.0
        portfolio_values = []
        trade_history = []
        trades = 0
        
        # Datum für Trade-Historie berechnen
        if start_date is None:
            start_date = datetime.now() - timedelta(days=len(prices))
        
        # DEBUG: Add logging for first few days and trades
        debug_mode = False  # Set to True for detailed debugging
        
        for i in range(len(prices)):
            price = prices[i]
            signal = strategy.calculate_signal(prices[:i+1])
            
            # DEBUG: Log first 5 iterations
            if debug_mode and i < 5:
                print(f"DEBUG Day {i}: price={price:.2f}, signal={signal}, capital=${capital:.2f}, shares={shares:.4f}")
            
            if signal == 'buy' and capital > price:
                shares_before = shares
                capital_before = capital
                
                shares_to_buy = capital / price
                shares += shares_to_buy
                capital = 0
                trades += 1
                
                current_value = capital + (shares * price)
                trade_history.append(TradeRecord(
                    date=f"Day {i}",
                    day_index=i,
                    signal='buy',
                    price=price,
                    shares_before=shares_before,
                    shares_after=shares,
                    capital_before=capital_before,
                    capital_after=capital,
                    portfolio_value=current_value
                ))
                if debug_mode:
                    print(f"DEBUG:  BUY executed! Bought {shares_to_buy:.4f} shares at ${price:.2f}")
            elif signal == 'sell' and shares > 0:
                shares_before = shares
                capital_before = capital
                
                capital = shares * price
                trades += 1
                
                current_value = capital + (shares * price)
                trade_history.append(TradeRecord(
                    date=f"Day {i}",
                    day_index=i,
                    signal='sell',
                    price=price,
                    shares_before=shares_before,
                    shares_after=0,
                    capital_before=capital_before,
                    capital_after=capital,
                    portfolio_value=current_value
                ))
                if debug_mode:
                    print(f"DEBUG:  SELL executed! Sold {shares:.4f} shares at ${price:.2f}")
                shares = 0
            
            # Track portfolio value each day
            current_value = capital + (shares * price)
            portfolio_values.append(current_value)
        
        final_value = portfolio_values[-1] if portfolio_values else self.initial_capital
        return_pct = ((final_value - self.initial_capital) / self.initial_capital) * 100
        
        # Performance-Metriken berechnen
        max_drawdown = self._calculate_max_drawdown(portfolio_values)
        sharpe_ratio = self._calculate_sharpe_ratio(portfolio_values)
        win_rate = self._calculate_win_rate(trade_history)
        
        return BacktestResult(
            strategy_name=strategy.get_display_name(),
            description=strategy.description,
            initial_capital=self.initial_capital,
            final_value=final_value,
            return_percentage=return_pct,
            total_trades=trades,
            portfolio_values=portfolio_values,
            trade_history=trade_history,
            max_drawdown=max_drawdown,
            sharpe_ratio=sharpe_ratio,
            win_rate=win_rate
        )
    
    def compare_strategies(self, strategies: List[BaseStrategy], prices: List[float], start_date: datetime = None) -> List[BacktestResult]:
        """
        Vergleicht mehrere Strategien
        
        Args:
            strategies: Liste der zu vergleichenden Strategien
            prices: Historische Preise
            start_date: Startdatum für die Trade-Historie
            
        Returns:
            Liste der Backtest-Ergebnisse, sortiert nach Performance
        """
        results = []
        
        for strategy in strategies:
            result = self.run_backtest(strategy, prices, start_date)
            results.append(result)
        
        # Sortiere nach Rendite (beste zuerst)
        results.sort(key=lambda x: x.return_percentage, reverse=True)
        
        return results
    
    def _get_indicator_values(self, strategy: BaseStrategy, prices: List[float]) -> Dict[str, float]:
        """Holt Indikator-Werte für eine Strategie"""
        from .utils.technical_indicators import TechnicalIndicators
        
        if len(prices) < 2:
            return {}
        
        indicators = {}
        
        try:
            # Basis-Indikatoren
            if len(prices) >= 14:
                indicators['RSI'] = TechnicalIndicators.rsi(prices)
            if len(prices) >= 10:
                indicators['SMA_10'] = TechnicalIndicators.sma(prices, 10)
            if len(prices) >= 20:
                indicators['SMA_20'] = TechnicalIndicators.sma(prices, 20)
            if len(prices) >= 12:
                indicators['EMA_12'] = TechnicalIndicators.ema(prices, 12)
            if len(prices) >= 26:
                indicators['MACD'] = TechnicalIndicators.macd(prices)
                
        except Exception:
            pass  # Ignoriere Fehler bei Indikator-Berechnung
            
        return indicators
    
    def _calculate_max_drawdown(self, portfolio_values: List[float]) -> float:
        """Berechnet den maximalen Drawdown"""
        if len(portfolio_values) < 2:
            return 0.0
        
        peak = portfolio_values[0]
        max_drawdown = 0.0
        
        for value in portfolio_values:
            if value > peak:
                peak = value
            drawdown = (peak - value) / peak
            if drawdown > max_drawdown:
                max_drawdown = drawdown
        
        return max_drawdown * 100  # Als Prozent
    
    def _calculate_sharpe_ratio(self, portfolio_values: List[float]) -> float:
        """Berechnet die Sharpe Ratio (vereinfacht)"""
        if len(portfolio_values) < 2:
            return 0.0
        
        # Tägliche Renditen berechnen
        returns = []
        for i in range(1, len(portfolio_values)):
            daily_return = (portfolio_values[i] - portfolio_values[i-1]) / portfolio_values[i-1]
            returns.append(daily_return)
        
        if len(returns) == 0:
            return 0.0
        
        # Durchschnittliche Rendite und Standardabweichung
        avg_return = sum(returns) / len(returns)
        
        if len(returns) == 1:
            return 0.0
        
        variance = sum((r - avg_return) ** 2 for r in returns) / (len(returns) - 1)
        std_dev = variance ** 0.5
        
        if std_dev == 0:
            return 0.0
        
        # Sharpe Ratio (ohne Risikofreier Zinssatz)
        return (avg_return / std_dev) * (252 ** 0.5)  # Annualisiert
    
    def _calculate_win_rate(self, trade_history: List[TradeRecord]) -> float:
        """Berechnet die Gewinnrate basierend auf Portfolio-Wert-Änderungen"""
        if len(trade_history) < 2:
            return 0.0
        
        wins = 0
        total_trades = 0
        
        for i in range(1, len(trade_history)):
            if trade_history[i].signal in ['buy', 'sell']:
                total_trades += 1
                if trade_history[i].portfolio_value > trade_history[i-1].portfolio_value:
                    wins += 1
        
        return (wins / total_trades * 100) if total_trades > 0 else 0.0
