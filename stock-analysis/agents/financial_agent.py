import os
import requests
from langchain.tools import tool
from dotenv import load_dotenv

load_dotenv()

FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY")

def check_api_response(response, endpoint_name):
    """Helper function to check API response for common errors"""
    if response.status_code == 401:
        return f"Error: Invalid Finnhub API key. Check your API key."
    
    if response.status_code == 429:
        return f"API rate limit reached. Please wait and try again (60 calls/minute limit)."
    
    if response.status_code == 403:
        return f"Error: Access forbidden. This endpoint may require premium subscription."
    
    if response.status_code != 200:
        return f"Error: {endpoint_name} API request failed with status {response.status_code}"
    
    return None 



@tool
def get_financials(symbol: str) -> str:
    """
    Financial analysis tool using Finnhub FREE tier.
    
    Gets key financial metrics:
    - Company info and current price
    - Essential valuation ratios (P/E, P/B)
    - Profitability metrics (margins, ROE)
    - Basic financial health indicators
    
    Args:
        symbol: Stock ticker symbol (e.g., 'AAPL', 'MSFT', 'GOOGL')
        
    Returns:
        Financial summary for the stock
    """
    if not FINNHUB_API_KEY:
        return """❌ FINNHUB API KEY REQUIRED:

"""

    try:
        symbol = symbol.upper()
        base_url = "https://finnhub.io/api/v1"
        
        # Get company profile
        profile_url = f"{base_url}/stock/profile2?symbol={symbol}&token={FINNHUB_API_KEY}"
        profile_response = requests.get(profile_url, timeout=10)
        
        # Error handling 
        error = check_api_response(profile_response, "Profile")
        if error:
            return error
        
        profile_data = profile_response.json()
        
        # Check for empty or invalid response
        if not profile_data:
            return f"Error: Empty response from Finnhub for symbol '{symbol}'"
        
        if isinstance(profile_data, dict) and 'error' in profile_data:
            return f"Error: {profile_data['error']}"
        
        if 'name' not in profile_data or not profile_data.get('name'):
            return f"Error: Invalid symbol '{symbol}' or symbol not found"
        
        # Get financial metrics
        financials_url = f"{base_url}/stock/metric?symbol={symbol}&metric=all&token={FINNHUB_API_KEY}"
        financials_response = requests.get(financials_url, timeout=10)

        # Error handling 
        error = check_api_response(financials_response, "Financials")
        if error:
            return error
        
        financials_data = financials_response.json()

        # Check for empty financials response
        if not financials_data:
            return f"Error: Empty financials response for symbol '{symbol}'"
        
        if isinstance(financials_data, dict) and 'error' in financials_data:
            return f"Error: {financials_data['error']}"

        # Extract basic info
        company_name = profile_data.get('name', symbol)
        industry = profile_data.get('finnhubIndustry', 'N/A')
        market_cap = profile_data.get('marketCapitalization', 0)
        
        # Extract key metrics
        metrics = financials_data.get('metric', {})
        pe_ratio = metrics.get('peBasicExclExtraTTM')
        price_book = metrics.get('pbAnnual')
        roe = metrics.get('roeTTM')
        net_margin = metrics.get('netProfitMarginTTM')
        current_ratio = metrics.get('currentRatioTTM')
        debt_equity = metrics.get('totalDebt/totalEquityTTM')
             
        # Simple formatting function
        def format_value(value, value_type='number'):
            if value is None or value == 'N/A':
                return 'N/A'
            try:
                num = float(value)
                if value_type == 'currency':
                    if abs(num) >= 1e9:
                        return f"${num/1e9:.1f}B"
                    elif abs(num) >= 1e6:
                        return f"${num/1e6:.1f}M"
                    else:
                        return f"${num:,.0f}"
                elif value_type == 'percentage':
                    return f"{num:.1f}%"
                else:
                    return f"{num:.2f}"
            except:
                return 'N/A'
        
        # Simple assessments
        valuation = "N/A"
        if pe_ratio:
            try:
                pe_val = float(pe_ratio)
                if pe_val > 25:
                    valuation = "Expensive"
                elif pe_val > 15:
                    valuation = "Fair"
                else:
                    valuation = "Cheap"
            except:
                pass
        
        profitability = "N/A"
        if net_margin:
            try:
                margin_val = float(net_margin)
                if margin_val > 15:
                    profitability = "Excellent"
                elif margin_val > 5:
                    profitability = "Good"
                else:
                    profitability = "Weak"
            except:
                pass
        
        # Format output
        result = f"""💼 FINANCIAL ANALYSIS: {symbol}

COMPANY INFO:
• Name: {company_name}
• Industry: {industry}
• Market Cap: {format_value(market_cap, 'currency')}

KEY METRICS:
• P/E Ratio: {format_value(pe_ratio)}
• Price-to-Book: {format_value(price_book)}
• Return on Equity: {format_value(roe, 'percentage')}
• Net Margin: {format_value(net_margin, 'percentage')}
• Current Ratio: {format_value(current_ratio)}
• Debt/Equity: {format_value(debt_equity)}

ASSESSMENT:
• Valuation: {valuation}
• Profitability: {profitability}
"""
        
        return result
        
    except Exception as e:
        return f"❌ Error analyzing {symbol}: {str(e)}"