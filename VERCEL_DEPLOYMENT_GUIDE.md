# 🤖 Vercel Deployment - Trading Bot mit Finnhub

## 🚀 Schritt-für-Schritt Anleitung:

### 1. **Finnhub API Key holen (KOSTENLOS)**
- Gehe zu: https://finnhub.io/register
- Registriere dich kostenlos
- Kopiere deinen API Key (z.B. `c123abc456def789`)

### 2. **Code zu GitHub pushen**
```bash
cd /Users/silvan/School/ABU-Tradingbot/trading-bot
git add .
git commit -m "Finnhub integration for Vercel deployment"
git push origin main
```

### 3. **Vercel Deployment**
- Gehe zu: https://vercel.com/
- Login mit GitHub
- Klicke "New Project"
- Wähle dein `ABU-TradingBot` Repository
- **WICHTIG:** Root Directory auf `trading-bot` setzen

### 4. **Environment Variables setzen**
In Vercel Dashboard → Settings → Environment Variables:
```
Name: FINNHUB_API_KEY
Value: dein_api_key_hier
Environment: Production, Preview, Development
```

### 5. **Deploy!**
- Klicke "Deploy"
- Warte 2-3 Minuten
- Deine Website ist live! 🎉

---

## ✅ **Was funktioniert jetzt:**
- **Echte Marktdaten** von Finnhub (Tesla ~445$, Bitcoin ~89.500$)
- **60 kostenlose Requests/Minute** (perfekt für Trading Bot)
- **Keine Rate Limiting Probleme** wie bei Yahoo Finance
- **Alle 9 Trading Strategien** mit echten Daten
- **Deutsche Benutzeroberfläche**
- **Responsive Design** für Mobile/Desktop

## 🔧 **Technische Details:**
- Python Flask App
- Finnhub API für Marktdaten
- Vercel Serverless Functions
- 30 Sekunden Timeout (perfekt für Backtests)

## 🆘 **Troubleshooting:**
- **Fehler "Module not found":** Checke requirements.txt
- **API Fehler:** Überprüfe FINNHUB_API_KEY Environment Variable
- **Timeout:** Vercel hat 30s Limit, Trading Bot ist optimiert dafür

## 💰 **Kosten:**
- **Vercel:** Kostenlos für Hobby-Projekte
- **Finnhub:** Kostenlos (60 requests/minute)
- **Gesamt:** 0€/Monat 🎉

Deine Trading Bot Website ist bereit für professionelles Deployment!