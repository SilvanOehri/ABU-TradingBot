# Trading Bot Deployment auf Render.com

## Schnellstart

1. Gehe zu [Render.com](https://render.com) und melde dich mit GitHub an

2. Klicke auf "New" → "Web Service"

3. Wähle dein Repository: `SilvanOehri/ABU-TradingBot`

4. Konfiguration:
   - **Name**: `trading-bot`
   - **Region**: Frankfurt (EU Central)
   - **Branch**: `main`
   - **Root Directory**: `trading-bot`
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python app_real_data.py`
   - **Instance Type**: Free

5. Klicke auf "Create Web Service"

## Fertig!

Deine App wird automatisch deployed und ist unter der URL erreichbar:
```
https://trading-bot-XXXX.onrender.com
```

## Features

- Automatisches Deployment bei Git Push
- HTTPS inklusive
- 512 MB RAM (genug für die App)
- Bessere Yahoo Finance Kompatibilität
- Kostenlos für Hobby-Projekte

## Lokale Entwicklung

```bash
cd trading-bot
pip install -r requirements.txt
python app_real_data.py
```

Öffne: http://localhost:8081

## Troubleshooting

**Problem: "Application failed to respond"**
- Lösung: Warte 2-3 Minuten nach dem ersten Deployment

**Problem: "Keine Daten für Symbol"**
- Lösung: Verwende BTC-USD, AAPL, MSFT oder ETH-USD

**Problem: "Build failed"**
- Lösung: Prüfe dass alle Dateien committed sind
- Stelle sicher dass requirements.txt korrekt ist
