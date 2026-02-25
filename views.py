import flet as ft
from components import TradePanel, PortfolioPanel, AIPanel, HistoryPanel

class PortfolioView:
    def __init__(self, page: ft.Page, controller):
        self.page = page
        self.controller = controller
        self.page.title = "Real-Time Stock Manager"
        self.page.bgcolor = "bluegrey50"
        self.pid_input = ft.TextField(label="Portfolio ID", width=150, height=45)
        
        self.trade_panel = TradePanel(controller)
        self.portfolio_panel = PortfolioPanel(controller)
        self.ai_panel = AIPanel(controller)
        self.history_panel = HistoryPanel(controller)
        
        self.trade_panel.content.visible = True
        
        self.content_area = ft.Container(
            content=ft.Column([
                self.trade_panel.content,
                self.portfolio_panel.content,
                self.ai_panel.content,
                self.history_panel.content
            ], expand=True),
            expand=True, padding=20
        )

        self.nav_buttons = [
            ft.ElevatedButton("Trade", icon="store", on_click=lambda e: self.switch_tab(0), bgcolor="blue900", color="white"),
            ft.ElevatedButton("Portfolio", icon="pie_chart", on_click=lambda e: self.switch_tab(1), bgcolor="bluegrey200", color="black"),
            ft.ElevatedButton("AI Analysis", icon="computer", on_click=lambda e: self.switch_tab(2), bgcolor="bluegrey200", color="black"),
            ft.ElevatedButton("History", icon="list", on_click=lambda e: self.switch_tab(3), bgcolor="bluegrey200", color="black"),
        ]
        self.top_nav = ft.Row(self.nav_buttons, alignment="center", spacing=20)

    def switch_tab(self, index):
        self.trade_panel.content.visible = (index == 0)
        self.portfolio_panel.content.visible = (index == 1)
        self.ai_panel.content.visible = (index == 2)
        self.history_panel.content.visible = (index == 3)
        for i, btn in enumerate(self.nav_buttons):
            btn.bgcolor = "blue900" if i == index else "bluegrey200"
            btn.color = "white" if i == index else "black"
        self.page.update()

    def build(self):
        header = ft.Container(content=ft.Row([ft.Text("Investment Dashboard", size=24, weight="bold", color="white"), ft.Row([self.pid_input, ft.ElevatedButton("Load Portfolio", on_click=self.controller.handle_load, bgcolor="orange", height=45)])], alignment="spaceBetween"), bgcolor="blue900", padding=15, border_radius=10)
        main_layout = ft.Column([header, ft.Container(content=self.top_nav, padding=10), ft.Divider(), self.content_area], expand=True)
        self.page.add(main_layout)

    def update_table(self, stocks, live_prices=None, spy_change=0.0, transactions=None):
        self.portfolio_panel.update_data(stocks, self.page, live_prices, spy_change)
        
        # --- התיקון: מעדכנים עכשיו גם את תפריט ה-AI ---
        self.ai_panel.update_options(stocks, self.page)
        
        if transactions:
            self.history_panel.update_data(transactions, self.page)
