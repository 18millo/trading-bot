# 🤖 MT5 Trading Bot User Guide

## ENB Strategy CLI Trading Bot - How to Use

---

## 📋 Quick Start

### 1. Make Bot Executable
```bash
cd /home/millo/Documents/python-projects/trading-bot
chmod +x trading-bot
```

### 2. Login to the Bot
```bash
./trading-bot login --username admin --password admin123
```

---

## 📈 ENB Strategy Explained

ENB stands for **Engulfing + Market Structure + Liquidity** - an institutional-grade trading model based on ICT concepts.

### How It Works:
1. **Market Structure** - Detects HH/HL (bullish) or LH/LL (bearish)
2. **Liquidity Sweep** - Waits for price to sweep previous highs/lows (stop hunt)
3. **Engulfing Candle** - Strong candle confirmation after liquidity grab

### View Current Configuration:
```bash
./trading-bot strategy --show-config
```

---

## 🧪 Running a Backtest

### What is Backtesting?
Backtesting simulates trades using historical data from MT5 to validate your strategy before risking real money.

### Steps:
```bash
./trading-bot backtest --symbol EURUSD --timeframe M15 --days 30
```

This will:
1. Fetch historical data from MT5
2. Simulate trades using ENB logic
3. Generate a PDF report with:
   - Total trades
   - Win rate (accurate calculation)
   - Profit/loss
   - Recent trades table

### Example Output:
```
📊 Backtest Results:
   Total signals: 24
   Winning trades: 15
   Losing trades: 9
   Win rate: 62.50%
   Total profit: $1245.50
   📄 Report saved: backtest_report_EURUSD_20260430_102530.pdf
```

---

## 🔴 Live Trading

### Single Trade (Manual):
```bash
./trading-bot trade --symbol EURUSD --timeframe M15
```

The bot analyzes the market using ENB strategy and executes a trade if signal detected.

### Automated Bot (Continuous):
```bash
./trading-bot run --symbol EURUSD --timeframe M15 --interval 60 --max-trades 5
```

This runs the bot continuously:
- Checks for signals every 60 seconds
- Executes trades when ENB conditions align
- Maximum 5 open trades at a time
- Press Ctrl+C to stop

---

## 📊 Checking Positions

### View Open Positions:
```bash
./trading-bot positions
```

Output:
```
📊 Open Positions (2):
--------------------------------------------------------------------------------
Ticket: 123456 | EURUSD | BUY | Volume: 0.1 | Profit: $12.50
Ticket: 123457 | GBPUSD | SELL | Volume: 0.1 | Profit: $-5.20
--------------------------------------------------------------------------------
```

### Close a Position:
```bash
./trading-bot positions --close 123456
```

---

## 📄 Generating Reports

### PDF Trading Report:
```bash
./trading-bot report --symbol EURUSD --days 30
```

Generates a PDF with:
- Trading activity summary
- Signal breakdown (BUY vs SELL)
- Strategy performance metrics
- Timestamp

---

## 🔧 MT5 Connection Commands

### Connect to MT5:
```bash
./trading-bot mt5 --connect
```

### Get Symbol Info:
```bash
./trading-bot mt5 --info EURUSD
```

### Disconnect from MT5:
```bash
./trading-bot mt5 --disconnect
```

---

## 📊 Risk Management Features

The bot includes built-in risk controls:

| Rule | Default Value | Purpose |
|------|---------------|---------|
| Risk Per Trade | 1% | Consistent position sizing |
| Risk:Reward Ratio | 1:2 | Profitable risk management |
| Max Open Trades | 5 (configurable) | Limits exposure |
| Automated SL/TP | Yes | Protects capital |

---

## 🛡️ Security Features

- **JWT Authentication** - Secure CLI access with token expiry
- **SQLite Database** - Lightweight, no PostgreSQL required
- **Password Hashing** - SHA256 hashed passwords
- **MT5 Credentials** - Stored in .env file (restricted access)

---

## 🔧 Troubleshooting

### Issue: MT5 Connection Failed
**Solution:**
```bash
# Check if MT5 is running via Wine
wine "C:\Program Files\MetaTrader 5\terminal64.exe"

# Verify .env credentials
cat .env | grep MT5
```

### Issue: No Trading Signals
**Solution:**
- Check timeframe (M15 recommended)
- Verify symbol is available in MT5
- Review ENB strategy config

### Issue: PDF Generation Fails
**Solution:**
```bash
pip install reportlab
```

### Issue: Database Errors
**Solution:**
```bash
# Database is SQLite (trading_bot.db)
# Delete and recreate if needed:
rm trading_bot.db
./trading-bot status  # Recreates database
```

---

## 📋 All Commands Reference

| Command | Description | Example |
|---------|-------------|---------|
| `login` | Authenticate user | `./trading-bot login --username admin --password admin123` |
| `status` | Check MT5 and DB status | `./trading-bot status` |
| `trade` | Execute single trade | `./trading-bot trade --symbol EURUSD` |
| `run` | Run automated bot | `./trading-bot run --symbol EURUSD --interval 60` |
| `backtest` | Run backtest with PDF | `./trading-bot backtest --symbol EURUSD --days 30` |
| `positions` | Show/open positions | `./trading-bot positions` |
| `report` | Generate PDF report | `./trading-bot report --symbol EURUSD` |
| `strategy` | View strategy config | `./trading-bot strategy --show-config` |
| `mt5` | MT5 connection commands | `./trading-bot mt5 --connect` |

---

## 🎯 Quick Tips

1. **Start with backtesting** - Never trade live without validating
2. **Use demo account** - MT5 demo is free and safe
3. **Monitor win rate** - If below 50%, revise strategy
4. **Check reports** - PDF reports show accurate performance
5. **Stick to the strategy** - Don't override ENB signals

---

## 📞 Support

For issues:
1. Check MT5 is running via Wine
2. Verify .env configuration
3. Run `./trading-bot status` to check connections
4. Review terminal output for error messages

---

**Happy Trading! 🚀**
