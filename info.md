# MT5 Trading Bot - ENB Strategy System (CLI)

## 📋 Project Overview

A CLI-based automated trading bot implementing the **ENB Strategy (Engulfing + Market Structure + Liquidity + Support/Resistance)** for MetaTrader 5. Designed for presentation and demonstration on Linux with MT5 running via Wine.

**Key Features:**
- **Command-line Interface** - Pure CLI, no web interface
- **MT5 Integration** - Connects to MetaTrader 5 via Wine on Linux
- **ENB Strategy + S/R** - Enhanced with Support/Resistance detection from 1H candles
- **1-Minute Entries** - Trade execution on 1min timeframe
- **Backtesting** - Historical simulation with PDF reports (S/R levels included)
- **Forward Testing** - Live market simulation with S/R detection
- **Automated Trading** - Run bot continuously with signal detection
- **PDF Reports** - Detailed performance reports with win rates and S/R levels
- **JWT Authentication** - Secure CLI access with auto-login
- **User Creation** - Simple account creation with automatic login
- **SQLite Database** - Lightweight, no PostgreSQL required

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────┐
│           CLI INTERFACE (trading-bot)          │
│  - Authentication (JWT tokens, auto-saved)          │
│  - Commands: login, create-user, backtest, etc │
└────────────────────┬──────────────────────────┘
                     │
        ┌────────────┴────────────┐
        ▼                         ▼
┌─────────────┐    ┌──────────────────────────┐
│  DATABASE   │    │    TRADING ENGINE         │
│  PostgreSQL │    │  - ENB Strategy Engine   │
│  - users    │    │  - S/R Detection (1H)    │
│  - trades   │    │  - MT5 Connector (Wine)  │
└─────────────┘    │  - Trade Execution (1min)  │
                    └──────────────────────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │  MetaTrader 5   │
                    │  (via Wine)     │
                    └─────────────────┘
```

**Database:** PostgreSQL (user: millo, password: #Sbm@29624970, database: capstone, host: localhost)

---

## 💻 Code Structure & Explanation

### Core Files:

#### 1. `cli.py` (18KB) - Main Entry Point
```python
# Creates CLI interface using argparse
# Handles all commands: login, backtest, forwardtest, etc.
# Manages authentication flow (auto-login after user creation)
# Routes commands to appropriate handlers
```

**Key Functions:**
- `create_parser()` - Defines all CLI commands and arguments
- `handle_login()` - Authenticates user, saves token to `~/.trading_bot_token`
- `handle_create_user()` - Creates new user (no admin role), auto-logs in
- `handle_backtest()` - Runs backtest with S/R detection (1H for levels, 1min for entries)
- `handle_forwardtest()` - Live market simulation with S/R filtering
- `get_enb_config()` - Returns ENB + S/R strategy configuration

**Authentication Flow:**
```python
# 1. Check if command requires auth (login, create-user, status, mt5 don't)
# 2. Try to read token from ~/.trading_bot_token
# 3. Verify token (simple check or JWT verification)
# 4. Allow command execution if authenticated
```

---

#### 2. `strategies/engine.py` (12KB) - ENB Strategy + S/R Detection
```python
# Core strategy engine implementing ICT concepts:
# - Market Structure (1min)
# - Liquidity Sweeps (1min)
# - Engulfing Entries (1min)
# - Support/Resistance Detection (1H candles)
```

**Key Functions:**
- `detect_market_structure(candles, min_swing)` - Finds HH/HL (bullish) or LH/LL (bearish)
- `detect_liquidity_sweep(candles)` - Detects stop hunts (previous high/low sweeps)
- `detect_engulfing(candles)` - Finds strong engulfing candles for entry
- `detect_support_resistance(candles_1h)` - **NEW!** Finds S/R levels from 1H candles
- `is_near_level(price, levels, threshold)` - Checks if price is near S/R level
- `evaluate_strategy(candles_1min, candles_1h, config)` - **Main function** that combines all

**How S/R Detection Works:**
```python
# 1. Get 1-hour candles (more reliable S/R levels)
candles_1h = mt5.get_candles(symbol, 'H1', count=days*24)

# 2. Find swing highs (resistance) and swing lows (support)
for each candle in 1H:
    if candle.high > all neighbors: add to swing_highs
    if candle.low < all neighbors: add to swing_lows

# 3. Cluster nearby levels (within 5 pips)
# 4. Return top 5 support and resistance levels

# 5. In evaluate_strategy():
#    - Only execute BUY if price is near support
#    - Only execute SELL if price is near resistance
```

**Data Flow:**
```
1H Candles → detect_support_resistance() → support_levels[], resistance_levels[]
                                                        ↓
1min Candles → evaluate_strategy(1min, 1H) → Check if price near S/R
                                                        ↓
                                              Execute trade if ALL align:
                                              1. Market Structure ✓
                                              2. Liquidity Sweep ✓
                                              3. Engulfing Candle ✓
                                              4. Near S/R Level ✓
```

---

#### 3. `trading/mt5_cli.py` (9KB) - MT5 Connector for Wine/Linux
```python
# Handles connection to MetaTrader 5 running via Wine on Linux
# Provides methods to get candles, place orders, check positions
```

**Key Functions:**
- `connect()` - Initializes MT5, logs in with credentials from `.env`
- `get_candles(symbol, timeframe, count)` - Fetches candle data from MT5
- `place_order(symbol, type, volume, sl, tp)` - Executes buy/sell orders
- `get_open_positions()` - Returns all open trades
- `close_position(ticket)` - Closes a specific position

**Linux/Wine Specifics:**
```python
# MT5 runs via Wine on Linux
mt5_path = os.getenv("MT5_WINE_PATH", "")
if mt5_path and os.path.exists(mt5_path):
    mt5.initialize(path=mt5_path)  # Tell MT5 where terminal is
```

---

#### 4. `auth/jwt_auth.py` (3KB) - Authentication
```python
# Handles JWT token creation and verification
# Supports both python-jose and PyJWT libraries
# Auto-creates admin user if not exists
```

**Key Functions:**
- `login(username, password)` - Authenticates user, returns JWT token
- `verify_token(token)` - Verifies token validity
- `create_user(username, password)` - Creates new user (user role only, no admin)

---

#### 5. `database/db.py` (4KB) - SQLite Database
```python
# Lightweight SQLite database (no PostgreSQL needed)
# Stores users and trades
```

**Tables:**
- `users` - id, username, password (SHA256 hashed), role
- `trades` - id, ticket, symbol, direction, entry/exit prices, SL/TP, status

**Auto-Initialization:**
```python
# On first run, creates tables and default admin user
# No manual database setup needed
```

---

#### 6. `report_generator.py` (11KB) - PDF Reports
```python
# Generates professional PDF reports with:
# - Strategy performance (win rate, profit/loss)
# - Support/Resistance levels used
# - Recent trades table
# - Transparent performance metrics
```

**Report Sections:**
1. Summary Statistics (total trades, win rate, profit)
2. Strategy Configuration (ENB + S/R settings)
3. Support/Resistance Levels (from 1H candles)
4. Recent Trades Table (last 20 trades)

---

## 🔧 Technologies Used

| Component | Technology | Why? |
|-----------|-------------|------|
| **CLI Framework** | Python argparse | Built-in, no extra dependencies |
| **Authentication** | JWT (python-jose/PyJWT) | Secure, stateless tokens |
| **Database** | SQLite | Lightweight, no server needed |
| **MT5 Integration** | MetaTrader5 Python API | Official API, works via Wine |
| **PDF Reports** | reportlab | Professional PDF generation |
| **Strategy** | Custom ENB + S/R | ICT concepts, institutional logic |
| **S/R Detection** | Custom algorithm | 1H candles, level clustering |

---
┌─────────────────────────────────────────────────┐
│           CLI INTERFACE (trading-bot)          │
│  - Authentication (JWT tokens, auto-saved)      │
│  - Commands: login, create-user, backtest, etc │
└────────────────────┬──────────────────────────┘
                     │
        ┌────────────┴────────────┐
        ▼                         ▼
┌─────────────┐    ┌──────────────────────────┐
│  DATABASE   │    │    TRADING ENGINE         │
│  SQLite     │    │  - ENB Strategy Engine   │
│  - users    │    │  - S/R Detection (1H)    │
│  - trades   │    │  - MT5 Connector (Wine)  │
└─────────────┘    │  - Trade Execution (1min)  │
                    └──────────────────────────┘
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
- PostgreSQL 15+ (database: capstone, user: millo)
- MetaTrader 5 terminal installed via Wine on Linux

### Supported Markets

**The bot works with ANY market available in MetaTrader 5:**
- **Forex**: EURUSD, GBPUSD, USDJPY, etc.
- **Gold/Silver**: XAUUSD, XAGUSD
- **Indices**: US30, NASDAQ, SPX500, etc.
- **Commodities**: Oil, Natural Gas, etc.
- **Crypto**: BTCUSD, ETHUSD (if available in your MT5)

Just provide the symbol name as used in your MT5 terminal!

### Quick Setup

```bash
cd /home/millo/Documents/python-projects/trading-bot

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env  # (if exists)
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

### Supported Markets for Presentation

**Recommended for impressive demos:**
- **XAUUSD (Gold)** - High volatility, great price moves
- **US30 (Dow Jones)** - Popular index, strong trends
- **NASDAQ** - Tech index, good for ENB strategy
- **EURUSD** - Classic forex pair, liquid market

### 1. Create User (First Time - No Auth Required)
```bash
./trading-bot create-user --username presenter --password demo123
```

**Output:**
```
✅ User 'presenter' created successfully
✅ Automatically logged in as 'presenter'
✅ Token saved. You can now run commands directly!
```

### 2. Direct Access (No Manual Token Export Needed)
After user creation, token is auto-saved to `~/.trading_bot_token`. Just run commands directly:

```bash
./trading-bot status
./trading-bot backtest --symbol EURUSD --timeframe-1h H1 --timeframe-entry M1 --days 30
```

### 3. Check Status

```bash
./trading-bot status
```

### 4. Test MT5 Connection

```bash
./trading-bot mt5 --connect
./trading-bot mt5 --info EURUSD
```

### 5. Run Backtest (Enhanced with S/R) - ANY MARKET!

```bash
# Gold (XAUUSD) - High volatility, impressive for presentation
./trading-bot backtest \
  --symbol XAUUSD \
  --timeframe-1h H1 \
  --timeframe-entry M1 \
  --days 30

# US30 (Dow Jones) - Popular index
./trading-bot backtest \
  --symbol US30 \
  --timeframe-1h H1 \
  --timeframe-entry M1 \
  --days 30

# EURUSD - Classic forex pair
./trading-bot backtest \
  --symbol EURUSD \
  --timeframe-1h H1 \
  --timeframe-entry M1 \
  --days 30

# NASDAQ - Tech index
./trading-bot backtest \
  --symbol NASDAQ \
  --timeframe-1h H1 \
  --timeframe-entry M1 \
  --days 30
```

This generates a PDF report with:
- Total trades
- Win rate (accurate calculation)
- Profit/loss
- **Support levels used (from 1H)**
- **Resistance levels used (from 1H)**
- Recent trades table

### 6. Run Forward Test (Live Market Simulation with S/R)

```bash
./trading-bot forwardtest --symbol EURUSD --timeframe-1h H1 --timeframe-entry M1 --duration 24
```

This runs a forward test for 24 hours:
- Detects S/R levels from 1H candles
- Executes entries on 1-minute timeframe
- Only trades when price is near S/R levels
- Generates PDF report with results

### 7. Manual Trade (Single)

```bash
./trading-bot trade --symbol EURUSD
```

The bot analyzes the market using ENB + S/R strategy and executes a trade if signal detected.

### 8. Run Automated Bot

```bash
./trading-bot run --symbol EURUSD --timeframe M1 --interval 60 --max-trades 5
```

This runs the bot continuously:
- Checks for signals every 60 seconds
- Uses 1H for S/R, 1min for entries
- Executes trades when ENB + S/R conditions align
- Maximum 5 open trades at a time
- Press Ctrl+C to stop

### 9. Generate PDF Report

```bash
./trading-bot report --symbol EURUSD --days 30
```

### 10. Check Positions

```bash
./trading-bot positions
./trading-bot positions --close <ticket_number>
```

---

## 📊 ENB Strategy + Support/Resistance Configuration

The bot uses an enhanced ENB strategy combining:

1. **Market Structure** - HH/HL for bullish, LH/LL for bearish (1min)
2. **Liquidity Sweep** - Price sweeps previous high/low (1min)
3. **Engulfing Candle** - Strong candle confirmation (1min)
4. **Support/Resistance** - Detected from 1-hour candles
5. **Entry Filter** - Only execute when price is near S/R levels

```json
{
  "name": "ENB Strategy - Market Structure + Liquidity + Engulfing + S/R",
  "type": "ENGULFING_STRUCTURE_LIQUIDITY_SUP RESISTANCE",
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
  "support_resistance": {
    "enabled": true,
    "num_levels": 5,
    "threshold": 0.0005
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

### How S/R Detection Works:
1. **1H Timeframe** - Analyzes 1-hour candles to find swing highs (resistance) and swing lows (support)
2. **Level Clustering** - Groups nearby price levels
3. **1min Entries** - Only executes trades when price is near identified S/R levels
4. **For BUY** - Looks for price near support levels
5. **For SELL** - Looks for price near resistance levels

---

## 📄 PDF Report Features

Every backtest/forwardtest generates a PDF with:
- **Summary Statistics** - Total trades, win rate, profit/loss
- **Strategy Configuration** - ENB + S/R parameters used
- **Support Levels** - Detected from 1H candles
- **Resistance Levels** - Detected from 1H candles
- **Recent Trades Table** - Last 20 trades with entry/exit prices
- **Win Rate Analysis** - Accurate performance metrics
- **Timestamp** - When report was generated

---

## 🎯 Commands Reference

| Command | Description | Auth Required? |
|---------|-------------|------------------|
| `create-user --username X --password Y` | Create account & auto-login | **No** |
| `login --username X --password Y` | Login existing user | **No** |
| `status` | Check MT5 and DB status | No |
| `trade` | Execute single trade | **Yes (auto)** |
| `run` | Run automated bot | **Yes (auto)** |
| `backtest --symbol EURUSD --timeframe-1h H1 --timeframe-entry M1 --days 30` | Backtest with S/R | **Yes (auto)** |
| `forwardtest --symbol EURUSD --duration 24` | Forward test live sim | **Yes (auto)** |
| `positions` | Show or close positions | **Yes (auto)** |
| `report --symbol EURUSD --days 30` | Generate PDF report | **Yes (auto)** |
| `strategy --show-config` | View strategy config | **Yes (auto)** |
| `mt5 --connect` | MT5 connection commands | No |

**Note:** After `create-user` or `login`, token is auto-saved. No manual `export TRADING_BOT_TOKEN` needed.

---

## ✅ Presentation Checklist

1. **Create user** (no auth needed):
   ```bash
   ./trading-bot create-user --username presenter --password demo123
   ```

2. **Show direct access** (no token export needed):
   ```bash
   ./trading-bot status
   ```

3. **Show strategy config**:
   ```bash
   ./trading-bot strategy --show-config
   ```

4. **Run backtest** (with S/R detection):
   ```bash
   ./trading-bot backtest --symbol EURUSD --timeframe-1h H1 --timeframe-entry M1 --days 30
   ```

5. **Show PDF report** (opens automatically):
   ```bash
   xdg-open backtest_report_*.pdf
   ```

6. **Explain ENB + S/R logic**:
   - Market Structure (1min)
   - Liquidity Sweep (1min)
   - Engulfing Entry (1min)
   - Support/Resistance (1H for levels)
   - Entry Filter (near S/R on 1min)

7. **Demo forward test** (briefly):
   ```bash
   ./trading-bot forwardtest --symbol EURUSD --duration 1
   ```

8. **Show positions**:
   ```bash
   ./trading-bot positions
   ```

---

## 🔧 Troubleshooting

### Issue: MT5 Connection Failed
**Solution:**
```bash
# Check if MT5 is running via Wine
ps aux | grep terminal

# Verify credentials in .env
cat .env | grep MT5

# Try connecting manually
./trading-bot mt5 --connect
```

### Issue: No Trading Signals
**Solution:**
- Check timeframe (1H for S/R, M1 for entries)
- Verify symbol is available in MT5
- Review ENB strategy config
- Ensure price is near S/R levels

### Issue: PDF Generation Fails
**Solution:**
```bash
pip install reportlab
```

### Issue: Authentication Errors
**Solution:**
```bash
# Recreate user (auto-logs in)
./trading-bot create-user --username myuser --password mypass123

# Or login again
./trading-bot login --username myuser --password mypass123
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

## 📞 Support

For issues:
1. Check MT5 is running via Wine
2. Verify .env configuration
3. Run `./trading-bot status` to check connections
4. Review terminal output for error messages
5. Ensure token file exists: `cat ~/.trading_bot_token`

---

## 🎯 Quick Tips

1. **Start with user creation** - Auto-login saves time
2. **Use backtest first** - Validate strategy before live trading
3. **Check S/R levels** - View strategy config to see detected levels
4. **Monitor win rate** - If below 50%, revise strategy
5. **Check reports** - PDF reports show accurate performance
6. **Stick to the strategy** - Don't override ENB + S/R signals
7. **Use demo account** - MT5 demo is free and safe

---

**Last Updated:** April 2026  
**Version:** 3.0 - CLI MT5 Trading Bot with S/R Detection  
**Author:** Trading Bot Project
