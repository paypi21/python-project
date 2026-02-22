from models import Stock, PortfolioDB
from views import PortfolioView
from ai_service import SentimentAnalyzer

class MainController:
    """The main controller managing the REPL loop and connecting MVC components."""
    
    def __init__(self):
        self.db = PortfolioDB()
        self.view = PortfolioView()
        self.ai = SentimentAnalyzer()

    def run(self):
        print(f"System Check - MRO for Stock class: {Stock.mro()}")
        
        while True:
            self.view.display_menu()
            choice = self.view.get_user_choice()

            if choice == '1':
                self._handle_add_stock()
            elif choice == '2':
                self._handle_view_portfolio()
            elif choice == '3':
                self._handle_search_stock()
            elif choice == '4':
                self._handle_delete_stock()
            elif choice == '5':
                self.view.display_message("Exiting the system. Goodbye!")
                break
            elif choice == '6':
                self._handle_sentiment_analysis()
            else:
                self.view.display_message("Invalid choice. Please try again.")

    def _handle_add_stock(self):
        stock_data = self.view.get_stock_input()
        if stock_data:
            symbol, name, price, quantity = stock_data
            new_stock = Stock(symbol, name, price, quantity)
            self.db.add_or_update_stock(new_stock)
            self.view.display_message(f"Stock '{symbol}' processed successfully!")

    def _handle_view_portfolio(self):
        stocks = self.db.get_all_stocks()
        self.view.display_portfolio(stocks)

    def _handle_search_stock(self):
        symbol = self.view.get_symbol_input("search")
        stock = self.db.search_stock(symbol)
        self.view.display_single_stock(stock)

    def _handle_delete_stock(self):
        symbol = self.view.get_symbol_input("delete")
        success = self.db.delete_stock(symbol)
        if success:
            self.view.display_message(f"Stock '{symbol}' deleted successfully.")
        else:
            self.view.display_message(f"Stock '{symbol}' not found in portfolio.")

    def _handle_sentiment_analysis(self):
        """Handles the AI sentiment analysis feature via Ollama."""
        data = self.view.get_sentiment_input()
        if data:
            symbol, headline = data
            self.view.display_message("Analyzing sentiment with local AI... Please wait.")
            sentiment = self.ai.analyze_headline(symbol, headline)
            self.view.display_message(f"AI Sentiment Analysis for {symbol}: {sentiment}")

if __name__ == "__main__":
    controller = MainController()
    controller.run()