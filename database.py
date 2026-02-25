import sqlite3
from datetime import datetime
from models import Stock 

class PortfolioDB:
    def __init__(self, db_name="portfolio.db"):
        self.db_name = db_name
        self._create_tables()

    def _get_connection(self):
        return sqlite3.connect(self.db_name)

    def _create_tables(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            # טבלת המניות הנוכחיות
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS stocks (
                    symbol TEXT, portfolio_id TEXT, name TEXT,
                    price REAL, quantity INTEGER,
                    PRIMARY KEY (symbol, portfolio_id)
                )
            ''')
            # טבלה חדשה: היסטוריית עסקאות
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    portfolio_id TEXT,
                    symbol TEXT,
                    type TEXT,
                    quantity INTEGER,
                    price REAL,
                    timestamp TEXT
                )
            ''')
            conn.commit()

    def add_or_update_stock(self, stock, portfolio_id):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            # רישום העסקה בהיסטוריה
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute('INSERT INTO transactions (portfolio_id, symbol, type, quantity, price, timestamp) VALUES (?, ?, ?, ?, ?, ?)',
                         (portfolio_id, stock.symbol, "BUY", stock.quantity, stock.price, now))
            
            # עדכון המצב הקיים
            cursor.execute('SELECT * FROM stocks WHERE symbol=? AND portfolio_id=?', (stock.symbol, portfolio_id))
            row = cursor.fetchone()
            if row:
                existing = Stock(row[0], row[2], row[3], row[4])
                updated = existing + stock
                cursor.execute('UPDATE stocks SET price=?, quantity=? WHERE symbol=? AND portfolio_id=?',
                             (updated.price, updated.quantity, updated.symbol, portfolio_id))
            else:
                cursor.execute('INSERT INTO stocks VALUES (?, ?, ?, ?, ?)',
                             (stock.symbol, portfolio_id, stock.name, stock.price, stock.quantity))
            conn.commit()

    def get_all_stocks(self, portfolio_id):
        stocks = []
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM stocks WHERE portfolio_id=?', (portfolio_id,))
            for row in cursor.fetchall():
                stocks.append(Stock(row[0], row[2], row[3], row[4]))
        return stocks

    def get_transactions(self, portfolio_id):
        """שליפת כל היסטוריית העסקאות של התיק"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT symbol, type, quantity, price, timestamp FROM transactions WHERE portfolio_id=? ORDER BY timestamp DESC', (portfolio_id,))
            return cursor.fetchall()

    def delete_stock(self, symbol, portfolio_id, qty_to_remove=None):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            cursor.execute('SELECT quantity, price FROM stocks WHERE symbol=? AND portfolio_id=?', (symbol, portfolio_id))
            row = cursor.fetchone()
            if not row: return False
            
            current_qty, current_price = row
            actual_remove = qty_to_remove if qty_to_remove and qty_to_remove < current_qty else current_qty
            
            # רישום המכירה בהיסטוריה
            cursor.execute('INSERT INTO transactions (portfolio_id, symbol, type, quantity, price, timestamp) VALUES (?, ?, ?, ?, ?, ?)',
                         (portfolio_id, symbol, "SELL", actual_remove, current_price, now))
            
            if actual_remove >= current_qty:
                cursor.execute('DELETE FROM stocks WHERE symbol=? AND portfolio_id=?', (symbol, portfolio_id))
            else:
                cursor.execute('UPDATE stocks SET quantity=? WHERE symbol=? AND portfolio_id=?', (current_qty - actual_remove, symbol, portfolio_id))
            
            conn.commit()
            return True