import requests

class SentimentAnalyzer:
    """Handles communication with the local Ollama LLM container for sentiment analysis."""
    
    def __init__(self, model_name="llama3.2"):
        self.api_url = "http://localhost:11434/api/generate"
        self.model_name = model_name

    def analyze_headline(self, stock_symbol: str, headline: str) -> str:
        """Sends a prompt to the local LLM to classify the sentiment of a financial news headline."""
        # Stronger, more specific prompt for the AI
        prompt = (
            f"You are an expert financial analyst. Analyze the sentiment of this news headline for the stock '{stock_symbol}'.\n"
            f"Headline: '{headline}'\n"
            f"Is this good news that would increase the stock price (POSITIVE), bad news (NEGATIVE), or neither (NEUTRAL)? "
            f"Respond with EXACTLY ONE WORD from this list: POSITIVE, NEGATIVE, NEUTRAL. Do not add any other words."
        )
        
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.0  # Forces the AI to be deterministic and analytical
            }
        }
        
        try:
            response = requests.post(self.api_url, json=payload, timeout=45)
            response.raise_for_status()
            result = response.json()
            
            # Extract and clean the AI's response
            raw_text = result.get("response", "").strip().upper()
            
            # Double check to ensure we only return the exact keyword
            if "POSITIVE" in raw_text:
                return "POSITIVE"
            elif "NEGATIVE" in raw_text:
                return "NEGATIVE"
            else:
                return "NEUTRAL"
                
        except requests.exceptions.RequestException as e:
            return f"CONNECTION_ERROR: Could not connect to the local AI container."