#!/usr/bin/env python3
"""
MT5 Trading Bot CLI - ENB Strategy System
A command-line interface for automated trading using MetaTrader 5 on Linux via Wine
"""
import argparse
import sys
import json
from datetime import datetime
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from auth.jwt_auth import JWTAuth
from trading.mt5_cli import MT5CLI
from strategies.engine import evaluate_strategy, Candle
from database.db import Database
from report_generator import PDFReportGenerator

def create_parser():
    """Create CLI argument parser"""
    parser = argparse.ArgumentParser(
        description='MT5 Trading Bot - ENB Strategy System',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s login --username admin --password admin123
  %(prog)s status
  %(prog)s trade --symbol EURUSD --timeframe M15
  %(prog)s backtest --symbol EURUSD --timeframe H1 --days 90
  %(prog)s run --symbol EURUSD --timeframe M15 --interval 60
  %(prog)s positions
  %(prog)s report --symbol EURUSD --days 30
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Login command
    login_parser = subparsers.add_parser('login', help='Login to trading bot')
    login_parser.add_argument('--username', required=True, help='Username')
    login_parser.add_argument('--password', required=True, help='Password')
    
    # Status command
    status_parser = subparsers.add_parser('status', help='Check bot and MT5 status')
    
    # Trade command (manual single trade)
    trade_parser = subparsers.add_parser('trade', help='Execute a manual trade')
    trade_parser.add_argument('--symbol', required=True, help='Trading symbol (e.g., EURUSD)')
    trade_parser.add_argument('--timeframe', default='M15', help='Timeframe (M5, M15, M30, H1, H4)')
    trade_parser.add_argument('--volume', type=float, default=0.1, help='Lot size')
    
    # Run command (automated bot)
    run_parser = subparsers.add_parser('run', help='Run automated trading bot')
    run_parser.add_argument('--symbol', required=True, help='Trading symbol')
    run_parser.add_argument('--timeframe', default='M15', help='Timeframe')
    run_parser.add_argument('--interval', type=int, default=60, help='Check interval in seconds')
    run_parser.add_argument('--max-trades', type=int, default=5, help='Max open trades')
    
    # Backtest command
    backtest_parser = subparsers.add_parser('backtest', help='Run strategy backtest')
    backtest_parser.add_argument('--symbol', required=True, help='Trading symbol')
    backtest_parser.add_argument('--timeframe', default='M15', help='Timeframe')
    backtest_parser.add_argument('--days', type=int, default=90, help='Days to backtest')
    backtest_parser.add_argument('--output', help='Output PDF report path')
    
    # Positions command
    positions_parser = subparsers.add_parser('positions', help='Show open positions')
    positions_parser.add_argument('--close', type=int, help='Close position by ticket number')
    
    # Report command
    report_parser = subparsers.add_parser('report', help='Generate PDF report')
    report_parser.add_argument('--symbol', required=True, help='Trading symbol')
    report_parser.add_argument('--days', type=int, default=30, help='Days to analyze')
    report_parser.add_argument('--output', help='Output PDF path')
    
    # Strategy command
    strategy_parser = subparsers.add_parser('strategy', help='Strategy operations')
    strategy_parser.add_argument('--show-config', action='store_true', help='Show ENB strategy configuration')
    
    # MT5 command
    mt5_parser = subparsers.add_parser('mt5', help='MT5 connection commands')
    mt5_parser.add_argument('--connect', action='store_true', help='Connect to MT5')
    mt5_parser.add_argument('--disconnect', action='store_true', help='Disconnect from MT5')
    mt5_parser.add_argument('--info', help='Get symbol info')
    
    return parser

def handle_login(args):
    """Handle login command"""
    auth = JWTAuth()
    token = auth.login(args.username, args.password)
    if token:
        print(f"✅ Login successful")
        print(f"Token: {token}")
        return 0
    else:
        print("❌ Login failed")
        return 1

def handle_status(args):
    """Handle status command"""
    print("=" * 50)
    print("MT5 Trading Bot - Status")
    print("=" * 50)
    
    # Check MT5 connection
    mt5 = MT5CLI()
    if mt5.connect():
        print("✅ MT5: Connected")
        account_info = mt5.get_account_info()
        if account_info:
            print(f"   Account: {account_info.get('login', 'N/A')}")
            print(f"   Balance: ${account_info.get('balance', 0):.2f}")
            print(f"   Equity: ${account_info.get('equity', 0):.2f}")
        mt5.disconnect()
    else:
        print("❌ MT5: Not connected")
    
    # Check database
    db = Database()
    if db.test_connection():
        print("✅ Database: Connected")
    else:
        print("❌ Database: Not connected")
    
    print("=" * 50)
    return 0

def handle_trade(args):
    """Handle manual trade command using ENB strategy"""
    mt5 = MT5CLI()
    
    if not mt5.connect():
        print("❌ Failed to connect to MT5")
        return 1
    
    try:
        print(f"📊 Analyzing {args.symbol} on {args.timeframe} using ENB Strategy...")
        candles = mt5.get_candles(args.symbol, args.timeframe, count=100)
        
        if not candles or len(candles) < 50:
            print("❌ Insufficient candle data")
            return 1
        
        config = get_enb_config()
        signal = evaluate_strategy(candles, config)
        
        if signal:
            print(f"✅ Signal detected: {signal['signal']} (Confidence: {signal['confidence']})")
            print(f"   Triggers: {', '.join([k for k, v in signal['triggers'].items() if v])}")
            
            # Place the trade
            current_price = candles[-1].close
            sl, tp = calculate_sl_tp(current_price, signal['signal'], config)
            
            print(f"📈 Placing {signal['signal']} order for {args.symbol}...")
            result = mt5.place_order(
                symbol=args.symbol,
                order_type=signal['signal'],
                volume=args.volume,
                sl=sl,
                tp=tp
            )
            
            if result:
                print(f"✅ Trade executed successfully")
                print(f"   Ticket: {result['ticket']}")
                print(f"   Price: {result['price']}")
                print(f"   SL: {result.get('sl', 'N/A')}")
                print(f"   TP: {result.get('tp', 'N/A')}")
                
                # Record in database
                db = Database()
                db.record_trade(result, signal, args.symbol, 'ENB_Strategy')
            else:
                print("❌ Trade execution failed")
                return 1
        else:
            print("❌ No trading signal detected")
            return 0
    
    finally:
        mt5.disconnect()
    
    return 0

def handle_run(args):
    """Handle automated bot run"""
    print(f"🤖 Starting automated trading bot for {args.symbol}")
    print(f"   Timeframe: {args.timeframe}")
    print(f"   Check interval: {args.interval} seconds")
    print(f"   Max trades: {args.max_trades}")
    print("   Press Ctrl+C to stop\n")
    
    mt5 = MT5CLI()
    db = Database()
    
    if not mt5.connect():
        print("❌ Failed to connect to MT5")
        return 1
    
    try:
        while True:
            positions = mt5.get_open_positions()
            if len(positions) >= args.max_trades:
                print(f"⚠️  Max trades ({args.max_trades}) reached, waiting...")
                time.sleep(args.interval)
                continue
            
            candles = mt5.get_candles(args.symbol, args.timeframe, count=100)
            if not candles or len(candles) < 50:
                print("⚠️  Insufficient data, waiting...")
                time.sleep(args.interval)
                continue
            
            config = get_enb_config()
            signal = evaluate_strategy(candles, config)
            
            if signal:
                print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Signal: {signal['signal']} ({signal['confidence']})")
                
                current_price = candles[-1].close
                sl, tp = calculate_sl_tp(current_price, signal['signal'], config)
                
                result = mt5.place_order(
                    symbol=args.symbol,
                    order_type=signal['signal'],
                    volume=0.1,
                    sl=sl,
                    tp=tp
                )
                
                if result:
                    print(f"   ✅ Trade opened: Ticket {result['ticket']}")
                    db.record_trade(result, signal, args.symbol, 'ENB_Strategy')
                else:
                    print("   ❌ Trade failed")
            
            time.sleep(args.interval)
    
    except KeyboardInterrupt:
        print("\n🛑 Bot stopped by user")
        return 0
    finally:
        mt5.disconnect()
    
    return 0

def handle_backtest(args):
    """Handle backtest command with PDF report"""
    print(f"🔍 Running backtest for {args.symbol} on {args.timeframe}...")
    print(f"   Period: Last {args.days} days")
    
    mt5 = MT5CLI()
    if not mt5.connect():
        print("❌ Failed to connect to MT5")
        return 1
    
    try:
        candles = mt5.get_candles(args.symbol, args.timeframe, count=args.days * 24)
        
        if not candles or len(candles) < 50:
            print("❌ Insufficient data for backtest")
            return 1
        
        config = get_enb_config()
        
        trades = []
        for i in range(50, len(candles)):
            signal = evaluate_strategy(candles[:i], config)
            if signal:
                entry_price = candles[i].close
                sl, tp = calculate_sl_tp(entry_price, signal['signal'], config)
                
                # Simulate exit (simplified - check next candles for SL/TP hit)
                exit_price, profit = simulate_trade(candles[i:], entry_price, sl, tp, signal['signal'])
                
                trades.append({
                    'entry_time': candles[i].timestamp,
                    'signal': signal['signal'],
                    'confidence': signal['confidence'],
                    'entry_price': entry_price,
                    'exit_price': exit_price,
                    'sl': sl,
                    'tp': tp,
                    'profit': profit,
                    'triggers': signal['triggers']
                })
        
        # Calculate statistics
        total_trades = len(trades)
        winning_trades = sum(1 for t in trades if t['profit'] > 0)
        losing_trades = sum(1 for t in trades if t['profit'] <= 0)
        win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
        total_profit = sum(t['profit'] for t in trades)
        
        print(f"\n📊 Backtest Results:")
        print(f"   Total signals: {total_trades}")
        print(f"   Winning trades: {winning_trades}")
        print(f"   Losing trades: {losing_trades}")
        print(f"   Win rate: {win_rate:.2f}%")
        print(f"   Total profit: ${total_profit:.2f}")
        
        # Generate PDF report
        if args.output or True:
            output_path = args.output or f"backtest_report_{args.symbol}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            generator = PDFReportGenerator()
            generator.generate_backtest_report(trades, {
                'symbol': args.symbol,
                'timeframe': args.timeframe,
                'days': args.days,
                'total_trades': total_trades,
                'winning_trades': winning_trades,
                'losing_trades': losing_trades,
                'win_rate': win_rate,
                'total_profit': total_profit
            }, output_path)
            print(f"   📄 Report saved: {output_path}")
    
    finally:
        mt5.disconnect()
    
    return 0

def handle_positions(args):
    """Handle positions command"""
    mt5 = MT5CLI()
    
    if not mt5.connect():
        print("❌ Failed to connect to MT5")
        return 1
    
    try:
        if args.close:
            if mt5.close_position(args.close):
                print(f"✅ Position {args.close} closed")
            else:
                print(f"❌ Failed to close position {args.close}")
        else:
            positions = mt5.get_open_positions()
            
            if not positions:
                print("📭 No open positions")
            else:
                print(f"📊 Open Positions ({len(positions)}):")
                print("-" * 80)
                for pos in positions:
                    print(f"Ticket: {pos['ticket']} | {pos['symbol']} | {pos['type']} | "
                          f"Volume: {pos['volume']} | Profit: ${pos['profit']:.2f}")
                print("-" * 80)
    
    finally:
        mt5.disconnect()
    
    return 0

def handle_report(args):
    """Handle report generation command"""
    print(f"📄 Generating report for {args.symbol} (last {args.days} days)...")
    
    mt5 = MT5CLI()
    if not mt5.connect():
        print("❌ Failed to connect to MT5")
        return 1
    
    try:
        candles = mt5.get_candles(args.symbol, 'M15', count=args.days * 24)
        
        if not candles or len(candles) < 50:
            print("❌ Insufficient data for report")
            return 1
        
        config = get_enb_config()
        db = Database()
        
        # Analyze recent signals
        signals = []
        for i in range(50, len(candles)):
            signal = evaluate_strategy(candles[:i], config)
            if signal:
                signals.append({
                    'time': candles[i].timestamp,
                    'signal': signal['signal'],
                    'confidence': signal['confidence']
                })
        
        output_path = args.output or f"trading_report_{args.symbol}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        generator = PDFReportGenerator()
        generator.generate_trading_report(signals, args.symbol, args.days, output_path)
        print(f"✅ Report saved: {output_path}")
    
    finally:
        mt5.disconnect()
    
    return 0

def handle_strategy(args):
    """Handle strategy command"""
    if args.show_config:
        config = get_enb_config()
        print("📊 ENB Strategy Configuration:")
        print(json.dumps(config, indent=2))
    return 0

def handle_mt5(args):
    """Handle MT5 commands"""
    mt5 = MT5CLI()
    
    if args.connect:
        if mt5.connect():
            print("✅ MT5 connected successfully")
            mt5.disconnect()
        else:
            print("❌ MT5 connection failed")
            return 1
    
    if args.disconnect:
        mt5.disconnect()
        print("✅ MT5 disconnected")
    
    if args.info:
        if mt5.connect():
            info = mt5.get_symbol_info(args.info)
            if info:
                print(f"📊 Symbol Info: {args.info}")
                for key, value in info.items():
                    print(f"   {key}: {value}")
            else:
                print(f"❌ Failed to get info for {args.info}")
            mt5.disconnect()
        else:
            print("❌ Failed to connect to MT5")
            return 1
    
    return 0

def get_enb_config():
    """Get ENB strategy configuration - Market Structure + Liquidity + Engulfing"""
    return {
        "name": "ENB Strategy - Market Structure + Liquidity + Engulfing",
        "type": "ENGULFING_STRUCTURE_LIQUIDITY",
        "structure": {
            "enabled": True,
            "method": "SWING",
            "trend_definition": "HH_HL_LH_LL",
            "min_swing_strength": 10
        },
        "liquidity": {
            "enabled": True,
            "require_sweep": True,
            "type": "previous_high_low"
        },
        "entry": {
            "require_engulfing": True,
            "body_engulf_required": True,
            "body_strength_min": 0.6
        },
        "confirmation": {
            "require_bos": False
        },
        "risk": {
            "risk_per_trade": 1,
            "rr_ratio": 2
        }
    }

def calculate_sl_tp(entry_price, direction, config):
    """Calculate Stop Loss and Take Profit prices"""
    rr_ratio = config.get('risk', {}).get('rr_ratio', 2)
    
    # Simple ATR-based calculation (can be improved)
    spread = 0.0002  # Approximate spread for EURUSD
    
    if direction == 'BUY':
        sl = entry_price - (spread * 50)  # 50 pips SL
        tp = entry_price + (spread * 50 * rr_ratio)  # RR ratio TP
    else:  # SELL
        sl = entry_price + (spread * 50)
        tp = entry_price - (spread * 50 * rr_ratio)
    
    return round(sl, 5), round(tp, 5)

def simulate_trade(candles, entry_price, sl, tp, direction):
    """Simulate trade exit for backtesting"""
    import time
    
    for candle in candles[1:]:
        if direction == 'BUY':
            if candle.low <= sl:
                return sl, -abs(entry_price - sl) * 100000 * 0.1
            elif candle.high >= tp:
                return tp, abs(tp - entry_price) * 100000 * 0.1
        else:  # SELL
            if candle.high >= sl:
                return sl, -abs(sl - entry_price) * 100000 * 0.1
            elif candle.low <= tp:
                return tp, abs(entry_price - tp) * 100000 * 0.1
    
    # If no SL/TP hit, use last candle as exit
    exit_price = candles[-1].close
    if direction == 'BUY':
        profit = (exit_price - entry_price) * 100000 * 0.1
    else:
        profit = (entry_price - exit_price) * 100000 * 0.1
    
    return exit_price, profit

def main():
    """Main entry point"""
    parser = create_parser()
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 0
    
    # Import time here to avoid early import issues
    global time
    import time
    
    commands = {
        'login': handle_login,
        'status': handle_status,
        'trade': handle_trade,
        'run': handle_run,
        'backtest': handle_backtest,
        'positions': handle_positions,
        'report': handle_report,
        'strategy': handle_strategy,
        'mt5': handle_mt5
    }
    
    handler = commands.get(args.command)
    if handler:
        return handler(args)
    else:
        parser.print_help()
        return 0

if __name__ == '__main__':
    sys.exit(main())
