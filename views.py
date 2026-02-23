import flet as ft

class PortfolioView:
    def __init__(self, page: ft.Page, controller):
        self.page = page
        self.controller = controller
        self.page.title = "Real-Time Stock Manager"
        self.page.bgcolor = "bluegrey50"
        
        # Inputs
        self.pid_input = ft.TextField(label="Portfolio ID", width=150)
        self.symbol_dd = ft.Dropdown(
            label="Select Stock", width=250,
            options=[ft.dropdown.Option(s) for s in ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "NVDA", "META", "NFLX"]]
        )
        self.qty_input = ft.TextField(label="Quantity", value="1", width=250)
        
        # Read-only displays for price confirmation
        self.price_display = ft.TextField(label="Execution Price ($)", read_only=True, bgcolor="grey100", width=250)
        self.news_input = ft.TextField(label="Stock News Headline", multiline=True)
        
        # Table with clear selection
        self.table = ft.DataTable(
            show_checkbox_column=True,
            columns=[ft.DataColumn(ft.Text(h)) for h in ["Symbol", "Name", "Price", "Qty", "Total Value"]],
            rows=[]
        )
        self.selected_sym = None

    def build(self):
        header = ft.Container(
            content=ft.Row([
                ft.Text("Investment Dashboard", size=24, weight="bold", color="white"),
                self.pid_input,
                ft.ElevatedButton("Load Portfolio", on_click=self.controller.handle_load, bgcolor="orange")
            ], alignment="spaceBetween"),
            bgcolor="blue900", padding=20, border_radius=10
        )

        self.page.add(
            header,
            ft.Row([
                ft.Column([
                    ft.Text("Trade Center", size=18, weight="bold"),
                    self.symbol_dd,
                    self.qty_input,
                    self.price_display, # Now visible during buy
                    ft.ElevatedButton("Buy at Market Price", icon="shopping_cart", 
                                      on_click=self.controller.handle_add, bgcolor="green", color="white"),
                    ft.Divider(),
                    ft.Text("AI Sentiment", size=18, weight="bold"),
                    self.news_input,
                    ft.ElevatedButton("Analyze News", icon="psychology", on_click=self.controller.handle_ai, bgcolor="blue", color="white")
                ], width=300),
                ft.Column([
                    ft.Text("My Portfolio (Select row to delete)", size=18, weight="bold"),
                    ft.Container(content=ft.Column([self.table], scroll="always"), height=500),
                    ft.ElevatedButton("Delete Selected Stock", icon="delete", on_click=self.controller.handle_delete, bgcolor="red", color="white")
                ], expand=True)
            ], spacing=30)
        )

    def update_table(self, stocks):
        self.table.rows = []
        for s in stocks:
            self.table.rows.append(
                ft.DataRow(
                    cells=[ft.DataCell(ft.Text(s.symbol)), ft.DataCell(ft.Text(s.name)),
                           ft.DataCell(ft.Text(f"${s.price:.2f}")), ft.DataCell(ft.Text(str(s.quantity))),
                           ft.DataCell(ft.Text(f"${s.calculate_value():.2f}"))],
                    on_select_change=lambda e, sym=s.symbol: self.set_selection(e, sym)
                )
            )
        self.page.update()

    def set_selection(self, e, sym):
        # This part ensures the Checkbox visually toggles
        e.control.selected = e.data == "true"
        self.selected_sym = sym if e.control.selected else None
        self.page.update()