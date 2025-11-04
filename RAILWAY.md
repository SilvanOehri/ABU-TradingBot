# Railway Deployment für ABU Trading Bot

## Automatisches Deployment

Railway erkennt automatisch:
- ✅ Python als Runtime
- ✅ `requirements.txt` für Dependencies
- ✅ `Procfile` für Start-Command
- ✅ PORT aus Environment-Variable

## Deployment Schritte

### 1. Code zu GitHub pushen

```bash
git add .
git commit -m "Railway deployment ready"
git push origin main
```

### 2. Railway Setup

1. Gehe zu: **https://railway.app**
2. Klicke **"Login with GitHub"**
3. Klicke **"New Project"**
4. Wähle **"Deploy from GitHub repo"**
5. Wähle: **SilvanOehri/ABU-TradingBot**
6. Railway startet automatisch das Deployment

### 3. Konfiguration (optional)

Railway erkennt alles automatisch. Falls nötig:
- Start Command: `python app_real_data.py`
- Build Command: `pip install -r requirements.txt`

### 4. Domain

Railway gibt dir automatisch eine URL:
```
https://abu-tradingbot-production.up.railway.app
```

Du kannst auch eine Custom Domain hinzufügen.

## Features

- ✅ Automatisches Deployment bei jedem Git Push
- ✅ 8 GB RAM (kostenlos)
- ✅ 500 GB Bandwidth
- ✅ Keine Size Limits
- ✅ Environment Variables Support
- ✅ Build & Deploy Logs
- ✅ Auto-Restart bei Crashes

## Lokale Entwicklung

```bash
python app_real_data.py
```

App läuft auf: http://localhost:8081

## Support

Railway Docs: https://docs.railway.app
