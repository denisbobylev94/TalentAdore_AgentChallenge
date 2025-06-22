import os
import requests
from langchain.tools import tool
from dotenv import load_dotenv

load_dotenv()

#ALPHA_VANTAGE_API_KEY = "IQIOB633OU2NIIEW"
ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")


@tool
def get_stock_price(symbol: str) -> str:
    """
    Stock price tool.
    Gets basic stock price data and simple analysis using Alpha Vantage free tier.
    
    Features:
    - Current price and daily change
    - Simple moving averages (20-day, 50-day)
    - Basic trend analysis
    
    Args:
        symbol: Stock ticker symbol (e.g., 'AAPL', 'MSFT', 'GOOGL')
        
    Returns:
        Formatted string with essential stock information
    """
    if not ALPHA_VANTAGE_API_KEY:
        return "Error: Alpha Vantage API key not configured."

    try:
        symbol = symbol.upper()
        
        # Get daily stock data 
        url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&outputsize=compact&apikey={ALPHA_VANTAGE_API_KEY}"
        response = requests.get(url, timeout=10)
        data = response.json()
        
        # Error handling
        if "Error Message" in data:
            return f"Error: Invalid symbol '{symbol}'"
        
        if "Note" in data:
            return f"API rate limit reached. Please wait and try again."
        
        if "Time Series (Daily)" not in data:
            return f"No data available for {symbol}"
        
        # Get price data
        time_series = data["Time Series (Daily)"]
        dates = sorted(time_series.keys(), reverse=True)
        
        if len(dates) < 2:
            return f"Insufficient data for {symbol}"
        
        # Current and previous day data
        latest_date = dates[0]
        latest_data = time_series[latest_date]
        previous_data = time_series[dates[1]]
        
        current_price = float(latest_data["4. close"])
        previous_close = float(previous_data["4. close"])
        day_high = float(latest_data["2. high"])
        day_low = float(latest_data["3. low"])
        volume = int(latest_data["5. volume"])
        
        # Calculate daily change
        daily_change = current_price - previous_close
        daily_change_pct = (daily_change / previous_close) * 100
        
        # Simple moving averages
        closes = [float(time_series[date]["4. close"]) for date in dates[:50]]
        
        sma_20 = sum(closes[:20]) / 20 if len(closes) >= 20 else None
        sma_50 = sum(closes[:50]) / 50 if len(closes) >= 50 else None
        
        # Basic trend analysis
        trend = "Neutral"
        if sma_20 and sma_50:
            if current_price > sma_20 and sma_20 > sma_50:
                trend = "Bullish"
            elif current_price < sma_20 and sma_20 < sma_50:
                trend = "Bearish"
        
        # Format moving averages safely
        sma_20_formatted = f"${sma_20:.2f}" if sma_20 else "N/A"
        sma_50_formatted = f"${sma_50:.2f}" if sma_50 else "N/A"
        
        # Format output
        result = f"""📊 STOCK ANALYSIS: {symbol}
        
                        PRICE INFORMATION:
                        • Current Price: ${current_price:.2f}
                        • Daily Change: ${daily_change:+.2f} ({daily_change_pct:+.2f}%)
                        • Day Range: ${day_low:.2f} - ${day_high:.2f}
                        • Volume: {volume:,}

                        TECHNICAL ANALYSIS:
                        • 20-Day Average: {sma_20_formatted}
                        • 50-Day Average: {sma_50_formatted}
                        • Trend: {trend}

                        Data as of: {latest_date}
            """
        
        return result
        
    except Exception as e:
        return f"Error retrieving data for {symbol}: {str(e)}"