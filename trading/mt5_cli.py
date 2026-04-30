"""
MT5 Connector for CLI - Linux/Wine Compatible
Connects to MetaTrader 5 running via Wine on Linux
"""
import os
import time
from typing import Dict, List, Optional
from datetime import datetime
from strategies.engine import Candle

class MT5CLI:
    """MT5 connector optimized for CLI and Wine/Linux environment"""
    
    def __init__(self, login: int = None, password: str = None, server: str = None):
        self.login = login or int(os.getenv("MT5_LOGIN", "0"))
        self.password = password or os.getenv("MT5_PASSWORD", "")
        self.server = server or os.getenv("MT5_SERVER", "MetaQuotes-Demo")
        self.connected = False
        self.mt5 = None
        self._account_info = None
    
    def connect(self) -> bool:
        """Connect to MT5 terminal via Wine"""
        try:
            import MetaTrader5 as mt5
            self.mt5 = mt5
            
            # Initialize MT5 - adjust path for Wine if needed
            mt5_path = os.getenv("MT5_WINE_PATH", "")
            init_params = {}
            
            if mt5_path and os.path.exists(mt5_path):
                init_params["path"] = mt5_path
            
            if not mt5.initialize(**init_params):
                print(f"❌ MT5 initialization failed: {mt5.last_error()}")
                return False
            
            # Login if credentials provided
            if self.login and self.password and self.server:
                authorized = mt5.login(
                    login=self.login,
                    password=self.password,
                    server=self.server
                )
                if not authorized:
                    print(f"❌ MT5 login failed: {mt5.last_error()}")
                    mt5.shutdown()
                    return False
            
            self.connected = True
            self._account_info = mt5.account_info()
            
            print(f"✅ MT5 connected successfully")
            if self._account_info:
                print(f"   Account: {self._account_info.login}")
                print(f"   Server: {self.server}")
                print(f"   Balance: ${self._account_info.balance:.2f}")
            
            return True
            
        except ImportError:
            print("❌ MetaTrader5 not installed")
            print("   Install: pip install MetaTrader5")
            print("   Note: On Linux with Wine, ensure MT5 terminal is installed")
            return False
        except Exception as e:
            print(f"❌ MT5 connection error: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from MT5"""
        if self.mt5 and self.connected:
            self.mt5.shutdown()
            self.connected = False
            self._account_info = None
    
    def get_account_info(self) -> Optional[Dict]:
        """Get account information"""
        if not self.connected:
            return None
        
        info = self.mt5.account_info()
        if info:
            return {
                "login": info.login,
                "balance": info.balance,
                "equity": info.equity,
                "margin": info.margin,
                "free_margin": info.margin_free,
                "profit": info.profit,
                "currency": info.currency
            }
        return None
    
    def get_symbol_info(self, symbol: str) -> Optional[Dict]:
        """Get symbol information"""
        if not self.connected:
            return None
        
        info = self.mt5.symbol_info(symbol)
        if info:
            return {
                "symbol": info.name,
                "bid": info.bid,
                "ask": info.ask,
                "spread": info.spread,
                "digits": info.digits,
                "point": info.point
            }
        return None
    
    def get_candles(self, symbol: str, timeframe: str = "M15", count: int = 100) -> List[Candle]:
        """Get candle data from MT5"""
        if not self.connected:
            return []
        
        # Convert timeframe string to MT5 constant
        timeframe_map = {
            "M1": self.mt5.TIMEFRAME_M1,
            "M5": self.mt5.TIMEFRAME_M5,
            "M15": self.mt5.TIMEFRAME_M15,
            "M30": self.mt5.TIMEFRAME_M30,
            "H1": self.mt5.TIMEFRAME_H1,
            "H4": self.mt5.TIMEFRAME_H4,
            "D1": self.mt5.TIMEFRAME_D1
        }
        
        tf = timeframe_map.get(timeframe, self.mt5.TIMEFRAME_M15)
        
        # Get rates
        rates = self.mt5.copy_rates_from_pos(symbol, tf, 0, count)
        
        if rates is None or len(rates) == 0:
            return []
        
        candles = []
        for rate in rates:
            candles.append(Candle(
                open=float(rate['open']),
                high=float(rate['high']),
                low=float(rate['low']),
                close=float(rate['close']),
                volume=float(rate['tick_volume']),
                timestamp=datetime.fromtimestamp(rate['time'])
            ))
        
        return candles
    
    def place_order(self, symbol: str, order_type: str, volume: float = 0.1,
                    sl: float = None, tp: float = None) -> Optional[Dict]:
        """Place a buy/sell order"""
        if not self.connected:
            return None
        
        tick = self.mt5.symbol_info_tick(symbol)
        if not tick:
            print(f"❌ Failed to get tick data for {symbol}")
            return None
        
        request = {
            "action": self.mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": volume,
            "type_filling": self.mt5.ORDER_FILLING_IOC,
            "magic": 202604,
            "comment": "ENB Trading Bot",
        }
        
        if order_type.upper() == "BUY":
            request["type"] = self.mt5.ORDER_TYPE_BUY
            request["price"] = tick.ask
            if sl:
                request["sl"] = sl
            if tp:
                request["tp"] = tp
        else:
            request["type"] = self.mt5.ORDER_TYPE_SELL
            request["price"] = tick.bid
            if sl:
                request["sl"] = sl
            if tp:
                request["tp"] = tp
        
        result = self.mt5.order_send(request)
        
        if result.retcode != self.mt5.TRADE_RETCODE_DONE:
            print(f"❌ Order failed: {result.comment} (retcode: {result.retcode})")
            return None
        
        print(f"✅ Order executed: {order_type} {symbol} @ {result.price}")
        
        return {
            "ticket": result.order,
            "symbol": symbol,
            "type": order_type,
            "volume": volume,
            "price": result.price,
            "sl": sl,
            "tp": tp
        }
    
    def close_position(self, ticket: int) -> bool:
        """Close an open position by ticket"""
        if not self.connected:
            return False
        
        positions = self.mt5.positions_get(ticket=ticket)
        if not positions:
            print(f"❌ Position {ticket} not found")
            return False
        
        position = positions[0]
        
        request = {
            "action": self.mt5.TRADE_ACTION_DEAL,
            "symbol": position.symbol,
            "volume": position.volume,
            "type": self.mt5.ORDER_TYPE_SELL if position.type == self.mt5.POSITION_TYPE_BUY 
                   else self.mt5.ORDER_TYPE_BUY,
            "position": ticket,
            "price": self.mt5.symbol_info_tick(position.symbol).bid if position.type == self.mt5.POSITION_TYPE_BUY 
                     else self.mt5.symbol_info_tick(position.symbol).ask,
            "magic": 202604,
            "comment": "ENB Bot Close",
        }
        
        result = self.mt5.order_send(request)
        
        if result.retcode == self.mt5.TRADE_RETCODE_DONE:
            print(f"✅ Position {ticket} closed")
            return True
        else:
            print(f"❌ Failed to close position: {result.comment}")
            return False
    
    def get_open_positions(self) -> List[Dict]:
        """Get all open positions"""
        if not self.connected:
            return []
        
        positions = self.mt5.positions_get()
        if not positions:
            return []
        
        return [{
            "ticket": p.ticket,
            "symbol": p.symbol,
            "type": "BUY" if p.type == 0 else "SELL",
            "volume": p.volume,
            "price_open": p.price_open,
            "price_current": p.price_current,
            "profit": p.profit,
            "sl": p.sl,
            "tp": p.tp
        } for p in positions]
