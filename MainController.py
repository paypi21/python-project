import flet as ft
from models import Stock
from database import PortfolioDB
from views import PortfolioView
from ai_service import SentimentAnalyzer
from services.market_service import MarketService

class MainController:
    def __init__(self):
        self.db = PortfolioDB()
        self.ai = SentimentAnalyzer()
        self.market = MarketService()
        self.view = None
        self.pid = None

    def start(self, page: ft.Page):
        self.view = PortfolioView(page, self)
        self.view.build()

    def handle_load(self, e):
        self.pid = self.view.pid_input.value
        if self.pid: self.refresh()
        else: self.msg("Enter Portfolio ID first.")

    def refresh(self):
        if self.pid:
            self.msg("Fetching data...")
            stocks = self.db.get_all_stocks(self.pid)
            transactions = self.db.get_transactions(self.pid) # שליפת היסטוריה
            live_prices = {s.symbol: self.market.fetch_live_price(s.symbol) for s in stocks}
            _, spy_change = self.market.get_daily_change("SPY")
            self.view.update_table(stocks, live_prices, spy_change, transactions)
            self.msg(f"Portfolio {self.pid} loaded.")

    def handle_selection(self, e):
        sym = self.view.trade_panel.symbol_dd.value
        if sym:
            self.view.trade_panel.name_display.value = self.market.get_company_name(sym)
            self.view.trade_panel.price_display.value = "Fetching live price..."
            self.view.page.update()
            price = self.market.fetch_live_price(sym)
            self.view.trade_panel.price_display.value = f"{price:.2f}"
            self.view.page.update()

    def handle_add(self, e):
        sym = self.view.trade_panel.symbol_dd.value
        qty = self.view.trade_panel.qty_input.value
        if not self.pid or not sym: return self.msg("Missing ID or Symbol")
        try:
            price = self.market.fetch_live_price(sym)
            self.db.add_or_update_stock(Stock(sym, self.market.get_company_name(sym), price, int(qty)), self.pid)
            self.refresh()
            self.msg(f"Bought {qty} {sym}")
        except Exception as err: self.msg(f"Error: {err}")

    def handle_delete(self, e):
        selected = self.view.portfolio_panel.selected_sym
        qty_str = self.view.portfolio_panel.delete_qty_input.value
        if selected and self.pid:
            qty = int(qty_str) if qty_str.isdigit() else None
            self.db.delete_stock(selected, self.pid, qty)
            self.refresh()
            self.msg("Transaction recorded.")

    def handle_ai(self, e):
        # לוגיקה קיימת של AI... (נשאר ללא שינוי)
        pass

    def msg(self, text):
        self.view.page.snack_bar = ft.SnackBar(ft.Text(text))
        self.view.page.snack_bar.open = True
        self.view.page.update()

if __name__ == "__main__":
    ft.app(target=MainController().start)