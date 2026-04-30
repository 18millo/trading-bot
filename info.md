# MT5 Trading Bot - ENB Strategy System

## 📋 Project Overview

A CLI-based automated trading bot implementing the **ENB Strategy (Engulfing + Market Structure + Liquidity Model)** for MetaTrader 5. Designed for presentation and demonstration on Linux with MT5 running via Wine.

**Key Features:**
- **Command-line Interface** - No web interface, pure CLI
- **MT5 Integration** - Connects to MetaTrader 5 via Wine on Linux
- **ENB Strategy** - Institutional-grade price action trading system
- **Backtesting** - Historical simulation with PDF reports
- **Automated Trading** - Run bot continuously with signal detection
- **PDF Reports** - Detailed performance reports with win rates
- **JWT Authentication** - Secure CLI access
- **SQLite Database** - Lightweight, no PostgreSQL required

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────┐
│           CLI INTERFACE (trading-bot)          │
│  - Authentication (JWT tokens)                 │
│  - Commands: login, trade, run, backtest, etc │
└────────────────────┬──────────────────────────┘
                     │
        ┌────────────┴────────────┐
        ▼                         ▼
┌─────────────┐    ┌──────────────────────────┐
│  DATABASE   │    │    TRADING ENGINE         │
│  SQLite     │    │  - ENB Strategy Engine   │
│  - users    │    │  - MT5 Connector (Wine)  │
│  - trades   │    │  - Trade Execution        │
└─────────────┘    └──────────────────────────┘
                     │
                     ▼
            ┌─────────────────┐
            │  MetaTrader 5   │
            │  (via Wine)     │
            └─────────────────┘
```

---

## 🚀 Installation Guide

### Prerequisites

- Python 3.11+
- MetaTrader 5 terminal installed via Wine on Linux
- SQLite (built-in with Python)

### Quick Setup

```bash
cd /home/millo/Documents/python-projects/trading-bot

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your MT5 credentials
```

### MT5 Setup on Linux (Wine)

1. Install Wine if not installed:
```bash
sudo apt install wine
```

2. Install MetaTrader 5 via Wine:
```bash
wine /path/to/mt5setup.exe
```

3. Update `.env` with MT5 path:
```
MT5_WINE_PATH=/home/millo/.wine/drive_c/Program Files/MetaTrader 5/terminal64.exe
```

---

## 🧪 Testing the Bot

### 1. Login to the Bot

```bash
./trading-bot login --username admin --password admin123
```

### 2. Check Status

```bash
./trading-bot status
```

### 3. Test MT5 Connection

```bash
./trading-bot mt5 --connect
./trading-bot mt5 --info EURUSD
```

### 4. Run Backtest

```bash
./trading-bot backtest --symbol EURUSD --timeframe M15 --days 30
```

This generates a PDF report with:
- Total trades
- Win rate
- Profit/loss
- Strategy performance

### 5. Manual Trade (ENB Strategy)

```bash
./trading-bot trade --symbol EURUSD --timeframe M15
```

The bot analyzes the market using ENB strategy and executes a trade if signal detected.

### 6. Run Automated Bot

```bash
./trading-bot run --symbol EURUSD --timeframe M15 --interval 60 --max-trades 5
```

This runs the bot continuously, checking for signals every 60 seconds.

Press Ctrl+C to stop.

### 7. Generate PDF Report

```bash
./trading-bot report --symbol EURUSD --days 30
```

### 8. Check Positions

```bash
./trading-bot positions
./trading-bot positions --close <ticket_number>
```

---

## 📊 ENB Strategy Configuration

The bot uses a single ENB strategy combining:

1. **Market Structure** - HH/HL for bullish, LH/LL for bearish
2. **Liquidity Sweep** - Price sweeps previous high/low
3. **Engulfing Candle** - Strong candle confirmation

```json
{
  "name": "ENB Strategy - Market Structure + Liquidity + Engulfing",
  "structure": {
    "enabled": true,
    "method": "SWING",
    "trend_definition": "HH_HL_LH_LL"
  },
  "liquidity": {
    "enabled": true,
    "require_sweep": true
  },
  "entry": {
    "require_engulfing": true,
    "body_engulf_required": true
  },
  "risk": {
    "risk_per_trade": 1,
    "rr_ratio": 2
  }
}
```

View current config:
```bash
./trading-bot strategy --show-config
```

---

## 📄 PDF Report Features

Every backtest/report generates a PDF with:
- **Summary Statistics** - Total trades, win rate, profit/loss
- **Strategy Configuration** - ENB parameters used
- **Recent Trades Table** - Last 20 trades with entry/exit prices
- **Win Rate Analysis** - Accurate performance metrics
- **Timestamp** - When report was generated

---

## 🎯 Commands Reference

| Command | Description |
|---------|-------------|
| `login` | Authenticate with username/password |
| `status` | Check MT5 and database status |
| `trade` | Execute single trade with ENB strategy |
| `run` | Run automated trading bot |
| `backtest` | Run historical backtest with PDF report |
| `positions` | Show or close open positions |
| `report` | Generate PDF trading report |
| `strategy` | View strategy configuration |
| `mt5` | MT5 connection commands |

---

## ✅ Presentation Checklist

1. **Start the bot** - `./trading-bot status`
2. **Show MT5 connection** - `./trading-bot mt5 --connect`
3. **Display strategy config** - `./trading-bot strategy --show-config`
4. **Run backtest** - `./trading-bot backtest --symbol EURUSD --timeframe M15 --days 30`
5. **Show PDF report** - Open generated PDF with win rates
6. **Explain ENB logic** - Structure + Liquidity + Engulfing
7. **Demo live trading** - `./trading-bot run --symbol EURUSD --timeframe M15`
8. **Show positions** - `./trading-bot positions`

---

## 🔧 Troubleshooting

### MT5 Connection Failed
```bash
# Check if MT5 is running via Wine
wine "C:\Program Files\MetaTrader 5\terminal64.exe"

# Verify credentials in .env
MT5_LOGIN=your_login
MT5_PASSWORD=your_password
MT5_SERVER=your_server
```

### Database Errors
```bash
# Database is SQLite, stored in trading_bot.db
# Delete and recreate if needed:
rm trading_bot.db
./trading-bot status  # This will recreate the database
```

### PDF Generation Fails
```bash
# Install reportlab
pip install reportlab
```

---

## 📞 Support

For issues:
1. Check MT5 is running via Wine
2. Verify .env configuration
3. Check database connection with `./trading-bot status`
4. Review terminal output for error messages

---

**Last Updated:** April 2026  
**Version:** 2.0 - CLI MT5 Trading Bot  
**Author:** Trading Bot Project
