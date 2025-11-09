# Trading Bot - School Project

A comprehensive trading bot with multiple strategies for automated backtesting using Yahoo Finance data.

**Developed by:** Silvan  
**Project:** ABU School Project  
**Date:** November 2025  

---

## Features

- 9 Trading Strategies (RSI, SMA, EMA, MACD, Bollinger, Stochastic, Momentum, Mean Reversion, Buy & Hold)
- Historical data from Yahoo Finance
- Real-time backtesting engine
- Web-based dashboard with Chart.js visualizations
- Strategy comparison and performance metrics

## Quick Start

### Local Development

```bash
cd trading-bot
pip install -r requirements.txt
python app_real_data.py
```

Open: http://localhost:8081

### Deployment on Render.com

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed instructions.

Quick steps:
1. Go to [Render.com](https://render.com)
2. Connect your GitHub repository
3. Create a new Web Service
4. Use: `python app_real_data.py` as start command

## Project Structure

```
trading-bot/
├── app_real_data.py          # Main Flask application
├── src/
│   ├── strategies/           # Trading strategies
│   ├── backtest_engine.py    # Backtesting logic
│   ├── data_provider.py      # Yahoo Finance integration
│   └── config.py             # Configuration
├── static/                   # CSS and JavaScript
├── templates/                # HTML templates
├── requirements.txt          # Python dependencies
└── render.yaml              # Render.com configuration
```

## Technologies

- **Backend**: Flask (Python)
- **Data**: Yahoo Finance (yfinance)
- **Frontend**: HTML, CSS, JavaScript
- **Charts**: Chart.js
- **Deployment**: Render.com

## Trading Strategies

1. **RSI** - Relative Strength Index
2. **SMA** - Simple Moving Average Crossover
3. **EMA** - Exponential Moving Average
4. **MACD** - Moving Average Convergence Divergence
5. **Bollinger Bands** - Volatility-based strategy
6. **Stochastic** - Momentum oscillator
7. **Momentum** - Price velocity strategy
8. **Mean Reversion** - Statistical arbitrage
9. **Buy & Hold** - Baseline benchmark

## Configuration

Edit `src/config.py` to customize:
- Trading symbols (BTC-USD, AAPL, MSFT, etc.)
- Initial capital
- Backtest period (days)
- Strategy parameters

## Important Notes

- For educational purposes only
- Not financial advice
- Use at your own risk
- Always do your own research

---

**Developed for ABU School Project**