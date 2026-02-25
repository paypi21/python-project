class Asset:
    """Base class for financial assets."""
    def __init__(self, symbol: str, name: str):
        self._symbol = symbol.upper()
        self.name = name
    @property
    def symbol(self): return self._symbol
    def calculate_value(self): raise NotImplementedError()

class Tradable:
    """Mixin for exchange trading."""
    def get_trading_market(self): return "US Stock Exchange"

class Stock(Asset, Tradable):
    """Stock entity with support for quantity and price averaging."""
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