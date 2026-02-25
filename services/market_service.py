import yfinance as yf
import urllib.request
import xml.etree.ElementTree as ET

class MarketService:
    def __init__(self):
        self.company_names = {
            "AAPL": "Apple Inc.", "MSFT": "Microsoft Corp.", "GOOGL": "Alphabet Inc.",
            "AMZN": "Amazon.com Inc.", "TSLA": "Tesla Inc.", "NVDA": "NVIDIA Corp.",
            "META": "Meta Platforms", "NFLX": "Netflix Inc.", "V": "Visa Inc.", "JNJ": "Johnson & Johnson"
        }

    def get_company_name(self, symbol: str) -> str:
        return self.company_names.get(symbol.upper(), symbol.upper())

    def fetch_live_price(self, symbol: str) -> float:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period="1d")
        if not hist.empty:
            return float(hist['Close'].iloc[-1])
        return 0.0
        
    def get_daily_change(self, symbol: str):
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period="2d")
        if len(hist) >= 2:
            current = float(hist['Close'].iloc[-1])
            prev = float(hist['Close'].iloc[-2])
            return current, ((current - prev) / prev) * 100
        elif len(hist) == 1:
            return float(hist['Close'].iloc[-1]), 0.0
        return 0.0, 0.0

    def fetch_stock_news(self, symbol: str):
        headlines = []
        publishers = set()
        try:
            ticker = yf.Ticker(symbol)
            news = ticker.news
            if news:
                for n in news[:5]:
                    if n.get('title'):
                        headlines.append(n['title'])
                        publishers.add(n.get('publisher', 'Yahoo Finance'))
        except Exception as e:
            pass 

        if not headlines:
            try:
                url = f"https://feeds.finance.yahoo.com/rss/2.0/headline?s={symbol}"
                req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req, timeout=10) as response:
                    xml_data = response.read()
                root = ET.fromstring(xml_data)
                for item in root.findall('./channel/item')[:5]:
                    title = item.find('title')
                    if title is not None and title.text:
                        headlines.append(title.text)
                if headlines:
                    publishers.add("Yahoo Finance RSS")
            except Exception as e:
                pass
                
        return headlines, list(publishers)

    # --- הפונקציה החדשה לגרף ההיסטורי ---
    def fetch_history_chart_data(self, symbol: str):
        """מושך נתוני סגירה של 30 הימים האחרונים בשביל הגרף"""
        try:
            ticker = yf.Ticker(symbol)
            # מושכים היסטוריה של חודש אחד (1mo)
            hist = ticker.history(period="1mo")
            if hist.empty:
                return []
            
            prices = hist['Close'].tolist()
            # מחזיר רשימה של נקודות: (מספר היום, מחיר המניה)
            return [(i, float(price)) for i, price in enumerate(prices)]
        except Exception as e:
            print(f"Error fetching history chart for {symbol}: {e}")
            return []