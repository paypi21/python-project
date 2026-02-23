import flet as ft
import yfinance as yf
from models import Stock, PortfolioDB
from views import PortfolioView
from ai_service import SentimentAnalyzer

class MainController:
    def __init__(self):
        self.db = PortfolioDB()
        self.ai = SentimentAnalyzer()
        self.view = None
        self.pid = None

    def start(self, page: ft.Page):
        self.view = PortfolioView(page, self)
        self.view.build()

    def handle_load(self, e):
        self.pid = self.view.pid_input.value
        if self.pid:
            self.refresh()
            self.msg(f"Portfolio {self.pid} loaded.")
        else:
            self.msg("Enter Portfolio ID first.")

    def refresh(self):
        if self.pid:
            stocks = self.db.get_all_stocks(self.pid)
            self.view.update_table(stocks)

    def handle_add(self, e):
        sym = self.view.symbol_dd.value
        qty = self.view.qty_input.value
        
        if not self.pid: return self.msg("Load a Portfolio ID first!")
        if not sym or not qty: return self.msg("Select stock and quantity.")

        self.msg(f"Contacting Market API for {sym}...")
        try:
            ticker = yf.Ticker(sym)
            # Fetch real price
            price = ticker.fast_info['last_price']
            name = ticker.info.get('longName') or sym
            
            # UPDATE UI PRICE BEFORE SAVING
            self.view.price_display.value = f"{price:.2f}"
            self.view.page.update()
            
            # Save to database
            new_stock = Stock(sym, name, price, int(qty))
            self.db.add_or_update_stock(new_stock, self.pid)
            
            self.refresh()
            self.msg(f"Success! Bought {sym} at ${price:.2f}")
        except Exception as err:
            self.msg(f"Error: {err}")

    def handle_delete(self, e):
        if self.view.selected_sym and self.pid:
            self.db.delete_stock(self.view.selected_symbol if hasattr(self.view, 'selected_symbol') else self.view.selected_sym, self.pid)
            self.refresh()
            self.view.selected_sym = None
            self.msg("Stock deleted.")
        else:
            self.msg("Please select (check) a row to delete.")

    def handle_ai(self, e):
        if not self.view.selected_sym or not self.view.news_input.value:
            return self.msg("Select a stock and enter a headline.")
        
        self.msg("AI analyzing...")
        res = self.ai.analyze_headline(self.view.selected_sym, self.view.news_input.value)
        self.view.page.dialog = ft.AlertDialog(title=ft.Text(f"AI Sentiment: {res}"), open=True)
        self.view.page.update()

    def msg(self, text):
        self.view.page.snack_bar = ft.SnackBar(ft.Text(text))
        self.view.page.snack_bar.open = True
        self.view.page.update()

if __name__ == "__main__":
    ft.app(target=MainController().start)