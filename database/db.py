"""
Database module for CLI Trading Bot
SQLite version for simplicity - no PostgreSQL required
"""
import os
import sqlite3
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

class Database:
    """Handle database connections and initialization - SQLite for simplicity"""
    
    def __init__(self):
        self.db_path = os.getenv("DB_PATH", "trading_bot.db")
        self._init_db()
    
    def _init_db(self):
        """Initialize database with required tables"""
        conn = self.get_connection()
        cur = conn.cursor()
        
        # Create users table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                role TEXT DEFAULT 'user',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create trades table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticket INTEGER,
                symbol TEXT NOT NULL,
                direction TEXT NOT NULL,
                entry_price REAL,
                exit_price REAL,
                stop_loss REAL,
                take_profit REAL,
                lot_size REAL DEFAULT 0.1,
                status TEXT DEFAULT 'OPEN',
                profit_loss REAL,
                strategy_name TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create trading_sessions table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS trading_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                end_time TIMESTAMP,
                total_trades INTEGER DEFAULT 0,
                profit_loss REAL DEFAULT 0
            )
        """)
        
        # Insert default admin user if not exists
        cur.execute("SELECT COUNT(*) FROM users WHERE username = 'admin'")
        if cur.fetchone()[0] == 0:
            import hashlib
            admin_password = hashlib.sha256('admin123'.encode()).hexdigest()
            cur.execute(
                "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                ('admin', admin_password, 'admin')
            )
            print("✅ Created default admin user (admin/admin123)")
        
        conn.commit()
        cur.close()
        conn.close()
    
    def get_connection(self):
        """Get database connection"""
        try:
            conn = sqlite3.connect(self.db_path)
            return conn
        except Exception as e:
            print(f"Database connection error: {e}")
            return None
    
    def test_connection(self):
        """Test database connection"""
        try:
            conn = self.get_connection()
            if conn:
                cur = conn.cursor()
                cur.execute("SELECT 1")
                cur.close()
                conn.close()
                return True
            return False
        except Exception:
            return False
    
    def record_trade(self, trade_result, signal, symbol, strategy_name):
        """Record a trade in the database"""
        conn = self.get_connection()
        if not conn:
            return False
        
        cur = conn.cursor()
        
        try:
            cur.execute("""
                INSERT INTO trades 
                (ticket, symbol, direction, entry_price, stop_loss, take_profit, lot_size, status, strategy_name, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, 'OPEN', ?, ?)
            """, (
                trade_result.get('ticket'),
                symbol,
                signal['signal'],
                trade_result.get('price'),
                trade_result.get('sl'),
                trade_result.get('tp'),
                trade_result.get('volume', 0.1),
                strategy_name,
                datetime.now()
            ))
            
            conn.commit()
            return True
        except Exception as e:
            print(f"Error recording trade: {e}")
            return False
        finally:
            cur.close()
            conn.close()
