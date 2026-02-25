import requests

class SentimentAnalyzer:
    def __init__(self, model_name="llama3.2"):
        self.api_url = "http://localhost:11434/api/generate"
        self.model_name = model_name

    def analyze_portfolio_stock(self, symbol: str, headlines: list) -> str:
        if not headlines:
            return "No recent news found to analyze."

        news_text = "\n- ".join(headlines)
        
        # הפרומפט החדש: מבקשים ניתוח סנטימנט במקום ייעוץ פיננסי
        prompt = (
            f"Analyze the sentiment of the following news headlines for the company {symbol}:\n"
            f"{news_text}\n\n"
            f"Task: Based ONLY on these headlines, what is the general sentiment? "
            f"Start your response with EXACTLY ONE of these words: POSITIVE, NEGATIVE, or MIXED. "
            f"Then, write exactly ONE short sentence in Hebrew summarizing what the news says. "
            f"Do NOT give financial advice. Do NOT ask any follow-up questions."
        )
        
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0.1} # טמפרטורה נמוכה כדי שיהיה ממוקד ולא יקשקש
        }
        
        try:
            response = requests.post(self.api_url, json=payload, timeout=45)
            response.raise_for_status()
            return response.json().get("response", "").strip()
        except Exception as e:
            return f"Error connecting to AI: {str(e)}"