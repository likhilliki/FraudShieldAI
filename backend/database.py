import sqlite3
import os
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

DATABASE_PATH = 'fraudshield.db'

def init_db():
    """Initialize the database with required tables"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        # Create intermediaries table for SEBI registry
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS intermediaries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT,
                registration_number TEXT,
                category TEXT,
                status TEXT,
                registered_date TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create announcements table for NSE/BSE filings
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS announcements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_name TEXT NOT NULL,
                ticker TEXT,
                title TEXT,
                content TEXT,
                filing_date TEXT,
                source TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create history table for verification logs
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                type TEXT NOT NULL,
                content TEXT NOT NULL,
                risk_score INTEGER,
                risk_level TEXT,
                reasons TEXT,
                ai_explanation TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create market_data table for stock information
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS market_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticker TEXT NOT NULL,
                date TEXT,
                price REAL,
                volume INTEGER,
                price_change REAL,
                volume_change REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        logger.info("Database initialized successfully")
        
        # Create indexes for better performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_intermediaries_name ON intermediaries(name)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_announcements_ticker ON announcements(ticker)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_history_type ON history(type)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_market_data_ticker ON market_data(ticker)')
        
        conn.commit()
        conn.close()
        
    except Exception as e:
        logger.error(f"Database initialization error: {str(e)}")
        raise

def get_db_connection():
    """Get database connection"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        conn.row_factory = sqlite3.Row  # Enable column access by name
        return conn
    except Exception as e:
        logger.error(f"Database connection error: {str(e)}")
        raise

def insert_intermediary(name: str, email: str = None, reg_number: str = None, 
                       category: str = None, status: str = "Active"):
    """Insert SEBI intermediary data"""
    try:
        conn = get_db_connection()
        conn.execute('''
            INSERT OR REPLACE INTO intermediaries 
            (name, email, registration_number, category, status, registered_date)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (name, email, reg_number, category, status, datetime.utcnow().isoformat()))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Error inserting intermediary: {str(e)}")
        return False

def search_intermediary(name: str):
    """Search for intermediary by name"""
    try:
        conn = get_db_connection()
        cursor = conn.execute('''
            SELECT * FROM intermediaries 
            WHERE name LIKE ? OR email LIKE ?
            ORDER BY name
        ''', (f'%{name}%', f'%{name}%'))
        
        results = cursor.fetchall()
        conn.close()
        return [dict(row) for row in results]
    except Exception as e:
        logger.error(f"Error searching intermediary: {str(e)}")
        return []

def insert_announcement(company_name: str, ticker: str = None, title: str = None,
                       content: str = None, filing_date: str = None, source: str = "NSE"):
    """Insert corporate announcement"""
    try:
        conn = get_db_connection()
        conn.execute('''
            INSERT INTO announcements 
            (company_name, ticker, title, content, filing_date, source)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (company_name, ticker, title, content, filing_date, source))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Error inserting announcement: {str(e)}")
        return False

def search_announcements(query: str, ticker: str = None):
    """Search corporate announcements"""
    try:
        conn = get_db_connection()
        
        if ticker:
            cursor = conn.execute('''
                SELECT * FROM announcements 
                WHERE ticker = ? AND (title LIKE ? OR content LIKE ?)
                ORDER BY filing_date DESC
            ''', (ticker, f'%{query}%', f'%{query}%'))
        else:
            cursor = conn.execute('''
                SELECT * FROM announcements 
                WHERE company_name LIKE ? OR title LIKE ? OR content LIKE ?
                ORDER BY filing_date DESC
            ''', (f'%{query}%', f'%{query}%', f'%{query}%'))
        
        results = cursor.fetchall()
        conn.close()
        return [dict(row) for row in results]
    except Exception as e:
        logger.error(f"Error searching announcements: {str(e)}")
        return []

def insert_market_data(ticker: str, price: float, volume: int, 
                      price_change: float = 0, volume_change: float = 0):
    """Insert market data"""
    try:
        conn = get_db_connection()
        conn.execute('''
            INSERT INTO market_data 
            (ticker, date, price, volume, price_change, volume_change)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (ticker, datetime.utcnow().isoformat(), price, volume, price_change, volume_change))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Error inserting market data: {str(e)}")
        return False

def get_market_data(ticker: str, days: int = 30):
    """Get recent market data for ticker"""
    try:
        conn = get_db_connection()
        cursor = conn.execute('''
            SELECT * FROM market_data 
            WHERE ticker = ?
            ORDER BY date DESC
            LIMIT ?
        ''', (ticker, days))
        
        results = cursor.fetchall()
        conn.close()
        return [dict(row) for row in results]
    except Exception as e:
        logger.error(f"Error getting market data: {str(e)}")
        return []

def get_database_stats():
    """Get database statistics"""
    try:
        conn = get_db_connection()
        
        stats = {}
        
        # Count intermediaries
        cursor = conn.execute('SELECT COUNT(*) FROM intermediaries')
        stats['intermediaries'] = cursor.fetchone()[0]
        
        # Count announcements
        cursor = conn.execute('SELECT COUNT(*) FROM announcements')
        stats['announcements'] = cursor.fetchone()[0]
        
        # Count history entries
        cursor = conn.execute('SELECT COUNT(*) FROM history')
        stats['verifications'] = cursor.fetchone()[0]
        
        # Count market data
        cursor = conn.execute('SELECT COUNT(*) FROM market_data')
        stats['market_records'] = cursor.fetchone()[0]
        
        conn.close()
        return stats
        
    except Exception as e:
        logger.error(f"Error getting database stats: {str(e)}")
        return {}

if __name__ == "__main__":
    # Initialize database for testing
    init_db()
    
    # Insert some test data
    insert_intermediary("Test Advisor", "test@example.com", "REG123", "Investment Advisor")
    insert_announcement("Test Company", "TEST", "Dividend Announcement", "Company announces dividend", "2024-01-15")
    
    # Test searches
    print("Intermediaries:", search_intermediary("Test"))
    print("Announcements:", search_announcements("dividend"))
    print("Stats:", get_database_stats())