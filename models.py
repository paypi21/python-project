import sqlite3

class Asset:
    """Base class representing a generic financial asset. Demonstrates vertical inheritance."""
    def __init__(self, symbol: str, name: str):
        self._symbol = symbol.upper()
        self.name = name

    @property
    def symbol(self):
        return self._symbol

    def calculate_value(self):
        """Demonstrates polymorphism: to be overridden by subclasses."""
        raise NotImplementedError("Subclasses must implement this method.")

class Tradable:
    """A mixin class to demonstrate multiple inheritance and MRO."""
    def get_trading_market(self):
        return "Global Stock Exchange"

class Stock(Asset, Tradable):
    """An entity class representing a stock, inheriting from Asset and Tradable."""
    def __init__(self, symbol: str, name: str, price: float, quantity: int):
        # Initialize parent class (Asset)
        super().__init__(symbol, name)
        self.price = price
        self.quantity = quantity

    def calculate_value(self):
        """Polymorphism: calculates the total value of this specific stock holding."""
        return self.price * self.quantity

    def __repr__(self):
        return f"Stock(symbol='{self.symbol}', name='{self.name}', price={self.price}, quantity={self.quantity})"

    def __add__(self, other):
        if isinstance(other, Stock) and self.symbol == other.symbol:
            new_quantity = self.quantity + other.quantity
            avg_price = ((self.price * self.quantity) + (other.price * other.quantity)) / new_quantity
            return Stock(self.symbol, self.name, avg_price, new_quantity)
        raise ValueError("Can only add stocks of the same type.")

class PortfolioDB:
    """Manages the SQLite database operations."""
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
                    symbol TEXT PRIMARY KEY,
                    name TEXT,
                    price REAL,
                    quantity INTEGER
                )
            ''')
            conn.commit()

    def add_or_update_stock(self, stock: Stock):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM stocks WHERE symbol = ?', (stock.symbol,))
            existing_row = cursor.fetchone()

            if existing_row:
                existing_stock = Stock(existing_row[0], existing_row[1], existing_row[2], existing_row[3])
                updated_stock = existing_stock + stock
                cursor.execute('''
                    UPDATE stocks 
                    SET price = ?, quantity = ? 
                    WHERE symbol = ?
                ''', (updated_stock.price, updated_stock.quantity, updated_stock.symbol))
            else:
                cursor.execute('''
                    INSERT INTO stocks (symbol, name, price, quantity)
                    VALUES (?, ?, ?, ?)
                ''', (stock.symbol, stock.name, stock.price, stock.quantity))
            conn.commit()

    def get_all_stocks(self):
        stocks = []
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM stocks')
            rows = cursor.fetchall()
            for row in rows:
                stocks.append(Stock(row[0], row[1], row[2], row[3]))
        return stocks

    def search_stock(self, symbol: str):
        """Searches for a specific stock by symbol."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM stocks WHERE symbol = ?', (symbol.upper(),))
            row = cursor.fetchone()
            if row:
                return Stock(row[0], row[1], row[2], row[3])
        return None

    def delete_stock(self, symbol: str):
        """Deletes a stock from the database."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM stocks WHERE symbol = ?', (symbol.upper(),))
            conn.commit()
            return cursor.rowcount > 0
