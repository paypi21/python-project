class PortfolioView:
    """Handles the Command Line Interface (CLI) for the user."""

    @staticmethod
    def display_menu():
        print("\n" + "="*45)
        print("      Investment Portfolio Manager      ")
        print("="*45)
        print("1. Add or Update a Stock")
        print("2. View Entire Portfolio")
        print("3. Search for a Stock")
        print("4. Delete a Stock")
        print("5. Exit")
        print("6. Analyze Stock Sentiment (AI Bonus)")
        print("="*45)

    @staticmethod
    def get_user_choice():
        return input("Please select an option (1-6): ")

    @staticmethod
    def get_stock_input():
        print("\n--- Enter Stock Details ---")
        symbol = input("Enter stock symbol (e.g., AAPL): ")
        name = input("Enter company name: ")
        try:
            price = float(input("Enter stock price: "))
            quantity = int(input("Enter quantity: "))
            return symbol, name, price, quantity
        except ValueError:
            print("Error: Invalid numeric input.")
            return None

    @staticmethod
    def get_symbol_input(action: str):
        return input(f"\nEnter the stock symbol to {action}: ")

    @staticmethod
    def get_sentiment_input():
        """Prompts the user for a news headline to analyze."""
        print("\n--- AI Sentiment Analysis ---")
        symbol = input("Enter stock symbol (e.g., TSLA): ")
        headline = input("Enter a recent news headline: ")
        return symbol, headline

    @staticmethod
    def display_portfolio(stocks):
        print("\n--- Your Current Portfolio ---")
        if not stocks:
            print("Your portfolio is currently empty.")
            return
        
        print(f"{'Symbol':<10} | {'Name':<15} | {'Price':<10} | {'Quantity':<10} | {'Total Value':<12}")
        print("-" * 65)
        for stock in stocks:
            print(f"{stock.symbol:<10} | {stock.name:<15} | ${stock.price:<9.2f} | {stock.quantity:<10} | ${stock.calculate_value():<10.2f}")
        print("-" * 65)

    @staticmethod
    def display_single_stock(stock):
        if stock:
            print("\n--- Stock Found ---")
            print(f"Symbol: {stock.symbol}")
            print(f"Name: {stock.name}")
            print(f"Price: ${stock.price:.2f}")
            print(f"Quantity: {stock.quantity}")
            print(f"Total Value: ${stock.calculate_value():.2f}")
            print(f"Market: {stock.get_trading_market()}") 
        else:
            print("\n>> Stock not found.")

    @staticmethod
    def display_message(message):
        print(f"\n>> {message}")