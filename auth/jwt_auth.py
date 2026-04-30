"""
JWT Authentication for CLI Trading Bot
"""
import hashlib
import os
from datetime import datetime, timedelta
from database.db import Database

try:
    from jose import jwt
except ImportError:
    try:
        import jwt
    except ImportError:
        jwt = None
    
class JWTAuth:
    """Handle JWT authentication for CLI"""
    
    def __init__(self):
        self.secret_key = os.getenv('JWT_SECRET_KEY', 'trading-bot-secret-key-2026')
        self.algorithm = 'HS256'
        self.token_expiry_hours = 120
        self.db = Database()
    
    def is_jwt_available(self):
        """Check if JWT library is available"""
        return jwt is not None
    
    def login(self, username: str, password: str) -> str:
        """Authenticate user and return JWT token"""
        conn = self.db.get_connection()
        cur = conn.cursor()
        
        # Hash password
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        cur.execute(
            "SELECT id, username, role FROM users WHERE username = ? AND password = ?",
            (username, password_hash)
        )
        
        user = cur.fetchone()
        cur.close()
        conn.close()
        
        if not user:
            return None
        
        # Create JWT token
        if jwt is None:
            print("Warning: JWT library not available")
            return "no-jwt-token"
        
        payload = {
            'user_id': user[0],
            'username': user[1],
            'role': user[2],
            'exp': datetime.utcnow() + timedelta(hours=self.token_expiry_hours)
        }
        
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    def verify_token(self, token: str) -> dict:
        """Verify and decode JWT token"""
        if jwt is None:
            return None
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    def create_user(self, username: str, password: str, role: str = 'user') -> bool:
        """Create a new user"""
        conn = self.db.get_connection()
        cur = conn.cursor()
        
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        try:
            cur.execute(
                "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                (username, password_hash, role)
            )
            conn.commit()
            return True
        except Exception as e:
            print(f"Error creating user: {e}")
            return False
        finally:
            cur.close()
            conn.close()
