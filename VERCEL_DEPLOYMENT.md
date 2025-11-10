# Vercel Deployment Guide

## 🚀 Deployment auf Vercel

### Schritt 1: Vercel Account erstellen
1. Gehe zu [vercel.com](https://vercel.com)
2. Registriere dich mit deinem GitHub Account
3. Verbinde dein GitHub Repository

### Schritt 2: Project importieren
1. Klicke "New Project"
2. Importiere dein `ABU-TradingBot` Repository
3. Wähle "Other" als Framework

### Schritt 3: Build-Konfiguration
- Build Command: `pip install -r requirements.txt`
- Output Directory: leer lassen
- Install Command: `pip install -r requirements.txt`

### Schritt 4: Environment Variables
Setze diese Umgebungsvariablen in Vercel:
- `PYTHONPATH` = `./src:.`
- `PYTHON_VERSION` = `3.11.0`

### Schritt 5: Deploy
1. Klicke "Deploy"
2. Warte bis das Deployment fertig ist
3. Teste die URL

## 📁 Wichtige Dateien für Vercel
- `vercel.json` - Vercel Konfiguration
- `vercel_app.py` - Optimierte App für Vercel
- `requirements.txt` - Python Dependencies
- `runtime.txt` - Python Version

## 🔧 Alternative: Netlify
Falls Vercel nicht funktioniert, kannst du auch Netlify verwenden:

1. Gehe zu [netlify.com](https://netlify.com)
2. Verbinde dein GitHub Repository
3. Build Command: `pip install -r requirements.txt && python vercel_app.py`
4. Publish Directory: leer lassen

## 💡 Tipps
- Vercel hat bessere Python Support als Render
- Die App verwendet Fallback-Daten wenn Yahoo Finance nicht funktioniert
- Mock-Daten werden generiert für Demo-Zwecke

## 🎯 Was funktioniert jetzt:
✅ Alle Trading-Strategien
✅ Backtest-Engine
✅ Mock-Daten als Fallback
✅ Dashboard und Charts
✅ API Endpoints

## 🔗 Nach dem Deployment:
Deine App wird verfügbar sein unter:
`https://your-project.vercel.app`

### API Endpoints:
- `GET /` - Dashboard
- `GET /api/health` - Health Check
- `POST /api/backtest` - Run Backtest
- `GET /api/symbols` - Available Symbols