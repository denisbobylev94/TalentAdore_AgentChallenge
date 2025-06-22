import os
import requests
from langchain.tools import tool
from dotenv import load_dotenv

load_dotenv()

NEWS_API_KEY = os.getenv("NEWS_API_KEY")

# keyword lists
POSITIVE_KEYWORDS = [
    'gain', 'up', 'rise', 'surge', 'soar', 'rally', 'beat', 'strong', 'growth',
    'profit', 'bullish', 'optimistic', 'upgrade', 'buy', 'positive', 'boost',
    'momentum', 'recovery', 'record', 'high', 'expand', 'success', 'innovation',
    'lead', 'acquire', 'launch'
]

NEGATIVE_KEYWORDS = [
    'fall', 'drop', 'plunge', 'decline', 'slide', 'loss', 'miss', 'disappoint',
    'weak', 'risk', 'bearish', 'pessimistic', 'downgrade', 'sell', 'negative',
    'slow', 'warning', 'cut', 'lawsuit', 'volatile', 'uncertainty', 'struggle',
    'debt', 'investigation', 'reduction', 'recall'
]

@tool
def get_sentiment(symbol: str) -> str:
    """
    Sentiment analysis tool. Analyzes recent news headlines to determine market sentiment.
    
    Features:
    - Fetches recent news headlines
    - Basic keyword-based sentiment analysis
    - Clear positive/negative/neutral classification
    
    Args:
        symbol: Stock ticker symbol (e.g., 'AAPL', 'MSFT', 'GOOGL')
        
    Returns:
        Formatted sentiment analysis summary
    """
    if not NEWS_API_KEY:
        return """❌ NEWS API KEY REQUIRED:

"""

    try:
        symbol = symbol.upper()
        
        # Fetch news headlines
        url = "https://newsapi.org/v2/everything"
        params = {
            'q': f'{symbol} stock OR {symbol} company',
            'sortBy': 'relevancy',
            'language': 'en',
            'pageSize': 50,  # num of headlines
            'apiKey': NEWS_API_KEY
        }
        
        response = requests.get(url, params=params, timeout=10)
        
        # Error handling
        if response.status_code == 401:
            return "Error: Invalid NewsAPI key. Check your API key."
        
        if response.status_code == 429:
            return "Error: NewsAPI rate limit reached. Try again later."
        
        if response.status_code != 200:
            return f"Error: NewsAPI request failed with status {response.status_code}"
        
        data = response.json()
        
        if data.get('status') != 'ok':
            return f"Error: {data.get('message', 'NewsAPI error')}"
        
        articles = data.get('articles', [])
        
        if not articles:
            return f"No recent news found for {symbol}"
        
        # Extract headlines
        headlines = []
        for article in articles:
            title = article.get('title', '')
            if title and title != '[Removed]':
                headlines.append(title)
        
        if not headlines:
            return f"No valid headlines found for {symbol}"
        
        # Simple sentiment analysis
        positive_count = 0
        negative_count = 0
        neutral_count = 0
        
        analyzed_headlines = []
        
        for headline in headlines:
            text_lower = headline.lower()
            
            # Count keyword matches
            pos_matches = sum(1 for word in POSITIVE_KEYWORDS if word in text_lower)
            neg_matches = sum(1 for word in NEGATIVE_KEYWORDS if word in text_lower)
            
            # Determine sentiment
            if pos_matches > neg_matches:
                sentiment = "Positive"
                positive_count += 1
            elif neg_matches > pos_matches:
                sentiment = "Negative"
                negative_count += 1
            else:
                sentiment = "Neutral"
                neutral_count += 1
            
            analyzed_headlines.append((headline, sentiment))
        
        # Overall sentiment
        total = len(analyzed_headlines)
        if positive_count > negative_count:
            overall = "Positive"
        elif negative_count > positive_count:
            overall = "Negative"
        else:
            overall = "Neutral"
        
        # Format output
        result = f"""📰 SENTIMENT ANALYSIS: {symbol}

OVERALL SENTIMENT: {overall}
Headlines Analyzed: {total}

BREAKDOWN:
• Positive: {positive_count} ({positive_count/total*100:.0f}%)
• Negative: {negative_count} ({negative_count/total*100:.0f}%)
• Neutral: {neutral_count} ({neutral_count/total*100:.0f}%)

RECENT HEADLINES:"""
        
        # Show top 20 headlines with sentiment
        for i, (headline, sentiment) in enumerate(analyzed_headlines[:20]):
            result += f"\n• {headline} [{sentiment}]"
        
        return result
        
    except Exception as e:
        return f"❌ Error analyzing sentiment for {symbol}: {str(e)}"


