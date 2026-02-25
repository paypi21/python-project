import flet as ft
import flet_charts as fch 

class TradePanel:
    def __init__(self, controller):
        self.controller = controller
        self.symbol_dd = ft.Dropdown(
            label="Select Stock", width=300,
            options=[ft.dropdown.Option(s) for s in controller.market.company_names.keys()]
        )
        self.symbol_dd.on_change = self.controller.handle_selection
        self.qty_input = ft.TextField(label="Quantity", value="1", width=300)
        self.name_display = ft.TextField(label="Company Name", read_only=True, bgcolor="grey100", width=300)
        self.price_display = ft.TextField(label="Execution Price ($)", read_only=True, bgcolor="grey100", width=300)
        
        self.content = ft.Column([
            ft.Text("Trade Center", size=28, weight="bold"),
            ft.Text("Buy new stocks to add to your portfolio.", color="grey700"),
            ft.Divider(),
            self.symbol_dd, self.name_display, self.qty_input, self.price_display,
            ft.ElevatedButton("Buy at Market Price", icon="store", 
                              on_click=self.controller.handle_add, bgcolor="green", color="white", width=300)
        ])

class PortfolioPanel:
    def __init__(self, controller):
        self.controller = controller
        self.table = ft.DataTable(
            show_checkbox_column=True,
            columns=[ft.DataColumn(ft.Text(h)) for h in ["Symbol", "Name", "Avg Cost", "Live Price", "Qty", "Total Value", "P/L %"]],
            rows=[]
        )
        self.selected_sym = None
        self.chart = fch.PieChart(sections=[], sections_space=2, center_space_radius=40, height=220)
        self.delete_qty_input = ft.TextField(label="Qty to Delete", value="All", width=120)
        self.benchmark_text = ft.Text("S&P 500 (SPY): Loading...", size=16, weight="bold", color="grey700")
        
        self.content = ft.Column([
            ft.Row([ft.Text("My Portfolio & Analytics", size=28, weight="bold"), self.benchmark_text], alignment="spaceBetween"),
            ft.Text("Manage your assets, track P/L, and view diversification.", color="grey700"),
            ft.Divider(),
            ft.Container(content=ft.Column([self.table], scroll="always"), height=150),
            ft.Row([self.delete_qty_input, ft.ElevatedButton("Delete Selected Stock", icon="delete", on_click=self.controller.handle_delete, bgcolor="red", color="white")]),
            ft.Divider(),
            ft.Text("Portfolio Diversification", size=18, weight="bold"),
            ft.Container(content=self.chart) 
        ], visible=False, expand=True, scroll="auto")
        
    def update_data(self, stocks, page, live_prices=None, spy_change=0.0):
        if live_prices is None: live_prices = {}
        spy_color = "green" if spy_change >= 0 else "red"
        spy_sign = "+" if spy_change > 0 else ""
        self.benchmark_text.value = f"S&P 500 (SPY): {spy_sign}{spy_change:.2f}%"
        self.benchmark_text.color = spy_color
        self.table.rows = []
        self.selected_sym = None 
        chart_sections = []
        colors = ["blue", "red", "green", "orange", "purple", "pink", "teal", "cyan"]
        total_val = sum(live_prices.get(s.symbol, s.price) * s.quantity for s in stocks)
        for i, s in enumerate(stocks):
            live_price = live_prices.get(s.symbol, s.price)
            current_val = live_price * s.quantity
            pl_pct = ((live_price / s.price) - 1) * 100 if s.price > 0 else 0
            pl_color = "green" if pl_pct >= 0 else "red"
            self.table.rows.append(ft.DataRow(cells=[ft.DataCell(ft.Text(s.symbol)), ft.DataCell(ft.Text(s.name)), ft.DataCell(ft.Text(f"${s.price:.2f}")), ft.DataCell(ft.Text(f"${live_price:.2f}")), ft.DataCell(ft.Text(str(s.quantity))), ft.DataCell(ft.Text(f"${current_val:.2f}")), ft.DataCell(ft.Text(f"{pl_pct:+.2f}%", color=pl_color, weight="bold"))], on_select_change=lambda e, sym=s.symbol: self.set_selection(e, sym, page)))
            if total_val > 0:
                pct = (current_val / total_val) * 100
                chart_sections.append(fch.PieChartSection(pct, color=colors[i % len(colors)], radius=50, title=f"{s.symbol}\n{pct:.1f}%", title_style=ft.TextStyle(size=12, color="white", weight="bold")))
        self.chart.sections = chart_sections
        if page: page.update()

    def set_selection(self, e, sym, page):
        is_checked = str(e.data).lower() == "true"
        for row in self.table.rows: row.selected = False
        e.control.selected = is_checked
        self.selected_sym = sym if is_checked else None
        if page: page.update()

class AIPanel:
    def __init__(self, controller):
        self.controller = controller
        self.symbol_dd = ft.Dropdown(label="Select Portfolio Stock", width=400)
        self.news_input = ft.TextField(label="Paste News Headline Here", multiline=True, width=400)
        self.ai_result_display = ft.Text("", size=18, weight="bold")
        self.content = ft.Column([
            ft.Text("AI Sentiment Analysis", size=28, weight="bold"),
            ft.Text("Check how breaking news affects your owned stocks.", color="grey700"),
            ft.Divider(),
            self.symbol_dd, self.news_input,
            ft.ElevatedButton("Analyze News", icon="computer", on_click=self.controller.handle_ai, bgcolor="blue", color="white", width=400),
            ft.Divider(), self.ai_result_display
        ], visible=False)
        def update_options(self, stocks, page):
            self.symbol_dd.options = [ft.dropdown.Option(s.symbol) for s in stocks]
            if page: page.update()

# --- רכיב חדש: פאנל היסטוריה ---
class HistoryPanel:
    def __init__(self, controller):
        self.controller = controller
        self.table = ft.DataTable(
            columns=[ft.DataColumn(ft.Text(h)) for h in ["Date", "Symbol", "Action", "Qty", "Price"]],
            rows=[]
        )
        self.content = ft.Column([
            ft.Text("Transaction History", size=28, weight="bold"),
            ft.Text("Full ledger of your buys and sells.", color="grey700"),
            ft.Divider(),
            ft.Container(content=ft.Column([self.table], scroll="always"), expand=True)
        ], visible=False, expand=True)

    def update_data(self, transactions, page):
        self.table.rows = []
        for t in transactions:
            color = "green" if t[1] == "BUY" else "red"
            self.table.rows.append(ft.DataRow(cells=[
                ft.DataCell(ft.Text(t[4])), # Date
                ft.DataCell(ft.Text(t[0])), # Symbol
                ft.DataCell(ft.Text(t[1], color=color, weight="bold")), # Action
                ft.DataCell(ft.Text(str(t[2]))), # Qty
                ft.DataCell(ft.Text(f"${t[3]:.2f}")) # Price
            ]))
        if page: page.update()