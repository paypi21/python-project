import flet as ft
import flet_charts as fch 
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
        if self.pid:
            self.refresh()
        else:
            self.msg("Enter Portfolio ID first.")

    def refresh(self):
        if self.pid:
            self.msg("Fetching data...")
            stocks = self.db.get_all_stocks(self.pid)
            transactions = self.db.get_transactions(self.pid)
            
            live_prices = {}
            for s in stocks:
                try:
                    live_prices[s.symbol] = self.market.fetch_live_price(s.symbol)
                except:
                    live_prices[s.symbol] = s.price
            
            _, spy_change = self.market.get_daily_change("SPY")
            self.view.update_table(stocks, live_prices, spy_change, transactions)
            self.msg(f"Portfolio {self.pid} loaded.")

    def handle_show_chart(self, symbol):
        panel = self.view.portfolio_panel
        panel.trend_chart_title.value = f"Loading 30-Day Trend for {symbol}..."
        panel.trend_chart_container.visible = True
        self.view.page.update()
        
        data_points = self.market.fetch_history_chart_data(symbol)
        
        if not data_points:
            panel.trend_chart_title.value = f"No chart data available for {symbol}"
            self.view.page.update()
            return

        chart_points = [fch.LineChartDataPoint(x, y) for x, y in data_points]
        
        prices = [y for x, y in data_points]
        min_price = min(prices) * 0.98 
        max_price = max(prices) * 1.02 
        
        price_step = (max_price - min_price) / 4
        y_labels = [
            fch.ChartAxisLabel(
                value=min_price + (i * price_step),
                label=ft.Text(f"${min_price + (i * price_step):.1f}", size=12, weight="bold", color="grey700")
            ) for i in range(5)
        ]
        
        x_labels = []
        total_days = len(data_points)
        for x, y in data_points:
            if x % 5 == 0 or x == total_days - 1:
                days_ago = total_days - 1 - x
                label_str = "Today" if days_ago == 0 else f"-{days_ago}d"
                x_labels.append(
                    fch.ChartAxisLabel(
                        value=x,
                        label=ft.Text(label_str, size=12, color="grey700")
                    )
                )

        panel.trend_chart.data_series = [
            fch.LineChartData(
                points=chart_points,
                stroke_width=3,
                color="blue900",
                curved=True, 
                rounded_stroke_cap=True
            )
        ]
        
        # --- התיקון: שינינו מ-labels_size ל-label_size ---
        panel.trend_chart.left_axis = fch.ChartAxis(labels=y_labels, label_size=50)
        panel.trend_chart.bottom_axis = fch.ChartAxis(labels=x_labels, label_size=30)
        panel.trend_chart.horizontal_grid_lines = fch.ChartGridLines(color="grey300", width=1, dash_pattern=[3, 3])
        
        panel.trend_chart.min_y = min_price
        panel.trend_chart.max_y = max_price
        
        panel.trend_chart_title.value = f"{symbol} - 30 Day Price Trend"
        self.view.page.update()

    def handle_selection(self, e):
        sym = self.view.trade_panel.symbol_dd.value
        if not sym: return
        self.view.trade_panel.name_display.value = self.market.get_company_name(sym)
        self.view.trade_panel.price_display.value = "Fetching..."
        self.view.page.update()
        try:
            price = self.market.fetch_live_price(sym)
            self.view.trade_panel.price_display.value = f"{price:.2f}"
        except:
            self.view.trade_panel.price_display.value = "Error"
        self.view.page.update()

    def handle_add(self, e):
        sym = self.view.trade_panel.symbol_dd.value
        qty = self.view.trade_panel.qty_input.value
        if not self.pid or not sym: return self.msg("Missing ID or Symbol")
        try:
            price = self.market.fetch_live_price(sym)
            new_stock = Stock(sym, self.market.get_company_name(sym), price, int(qty))
            self.db.add_or_update_stock(new_stock, self.pid)
            self.refresh()
            self.msg(f"Bought {qty} {sym}")
        except Exception as err:
            self.msg(f"Error: {err}")

    def handle_delete(self, e):
        selected = self.view.portfolio_panel.selected_sym
        qty_str = self.view.portfolio_panel.delete_qty_input.value
        if selected and self.pid:
            qty = int(qty_str) if qty_str.isdigit() else None
            self.db.delete_stock(selected, self.pid, qty)
            self.refresh()
            self.msg("Transaction recorded.")
        else:
            self.msg("Select a stock first.")

    def handle_ai(self, e):
        selected = self.view.ai_panel.symbol_dd.value
        if not selected:
            return self.msg("Please select a stock from your portfolio.")
        
        self.view.ai_panel.ai_result_display.value = f"Fetching live news for {selected}..."
        self.view.ai_panel.ai_result_display.color = "orange700"
        self.view.page.update()
        
        try:
            headlines, sources = self.market.fetch_stock_news(selected)
            if not headlines:
                self.view.ai_panel.ai_result_display.value = f"No recent news found for {selected}."
                self.view.ai_panel.ai_result_display.color = "red700"
                self.view.page.update()
                return
            
            sources_text = ", ".join(sources)
            self.view.ai_panel.ai_result_display.value = f"Analyzing {len(headlines)} headlines from: {sources_text}..."
            self.view.page.update()
            
            advice = self.ai.analyze_portfolio_stock(selected, headlines)
            final_output = f"{advice}\n\n(מקורות המידע שנותחו: {sources_text})"
            
            if "POSITIVE" in advice.upper():
                self.view.ai_panel.ai_result_display.color = "green700"
            elif "NEGATIVE" in advice.upper():
                self.view.ai_panel.ai_result_display.color = "red700"
            else:
                self.view.ai_panel.ai_result_display.color = "blue700"

            self.view.ai_panel.ai_result_display.value = final_output
            self.view.page.update()
            
        except Exception as err:
            self.view.ai_panel.ai_result_display.value = f"Error: {str(err)}"
            self.view.ai_panel.ai_result_display.color = "red700"
            self.view.page.update()

    def msg(self, text):
        self.view.page.snack_bar = ft.SnackBar(ft.Text(text))
        self.view.page.snack_bar.open = True
        self.view.page.update()

if __name__ == "__main__":
    ft.app(target=MainController().start)