import sqlite3

class Asset:
    def __init__(self, symbol: str, name: str):
        self._symbol = symbol.upper()
        self.name = name
    @property
    def symbol(self): return self._symbol
    def calculate_value(self): raise NotImplementedError()

class Stock(Asset):
    def __init__(self, symbol: str, name: str, price: float, quantity: int):
        super().__init__(symbol, name)
        self.price = float(price)
        self.quantity = int(quantity)
    def calculate_value(self): return self.price * self.quantity
    def __add__(self, other):
        if isinstance(other, Stock) and self.symbol == other.symbol:
            new_qty = self.quantity + other.quantity
            avg_p = ((self.price * self.quantity) + (other.price * other.quantity)) / new_qty
            return Stock(self.symbol, self.name, avg_p, new_qty)
        return self

class PortfolioDB:
    def __init__(self, db_name="portfolio.db"):
        self.db_name = db_name
        self._create_table()

    def _get_connection(self):
        return sqlite3.connect(self.db_name)

    def _create_table(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS stocks (
                    symbol TEXT, portfolio_id TEXT, name TEXT,
                    price REAL, quantity INTEGER,
                    PRIMARY KEY (symbol, portfolio_id)
                )
            ''')
            conn.commit()

    def add_or_update_stock(self, stock, portfolio_id):
        with self._get_connection() as conn:
            cursor = conn.cursor()
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

    def delete_stock(self, symbol, portfolio_id):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM stocks WHERE symbol=? AND portfolio_id=?', (symbol, portfolio_id))
            conn.commit()
            return cursor.rowcount > 0