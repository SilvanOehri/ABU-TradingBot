# Trading Bot - Vercel Deployment

## Deployment zu Vercel

### Voraussetzungen
- GitHub Account
- Vercel Account (https://vercel.com)

### Schritte

1. **Code zu GitHub pushen:**
```bash
cd /Users/silvan/School/ABU-Tradingbot/trading-bot
git add .
git commit -m "Prepare for Vercel deployment"
git push origin main
```

2. **Vercel Deployment:**
   - Gehe zu https://vercel.com/new
   - Klicke "Import Git Repository"
   - Wähle `SilvanOehri/ABU-TradingBot`
   - Vercel erkennt automatisch die `vercel.json` Konfiguration
   - Klicke "Deploy"

3. **Fertig!** 
   - Vercel gibt dir eine URL wie: `https://abu-tradingbot.vercel.app`

### Lokale Entwicklung

```bash
# Installiere Dependencies
pip install -r requirements.txt

# Starte die App
python app_real_data.py
```

Die App läuft dann auf: http://localhost:8081

### Wichtige Dateien für Vercel

- `vercel.json` - Vercel Konfiguration
- `api/index.py` - Vercel Serverless Function Entry Point
- `runtime.txt` - Python Version
- `requirements.txt` - Python Dependencies

### Troubleshooting

**Problem: "Module not found"**
- Stelle sicher, dass alle Dependencies in `requirements.txt` sind

**Problem: "Cold start timeout"**
- Vercel Serverless Functions haben ein 10s Timeout
- Backtest könnte zu lange dauern für große Zeiträume
- Erwäge Redis/Cache für vorberechnete Ergebnisse

**Problem: "Static files not found"**
- Stelle sicher, dass `templates/` und `static/` Ordner im Repository sind
