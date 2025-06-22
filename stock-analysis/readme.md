# Stock Analysis System

AI-powered stock analysis using multiple financial data sources.

## What it does

This system analyzes stocks by combining:
- **Price data** from Alpha Vantage
- **Financial metrics** from Finnhub  
- **News sentiment** from NewsAPI
- **AI analysis** from OpenAI GPT-4

## Quick Start

### 1. Install dependencies
```
pip install -r requirements.txt
```

### 2. Set up API keys
Create a `.env` file:
```
OPENAI_API_KEY=your_openai_key
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_key
FINNHUB_API_KEY=your_finnhub_key
NEWS_API_KEY=your_news_api_key
```

**Get free API keys:**
- OpenAI: https://platform.openai.com
- Alpha Vantage: https://www.alphavantage.co
- Finnhub: https://finnhub.io
- NewsAPI: https://newsapi.org

### 3. Run the application

**Option A: Web interface (Recommended)**
```
# Terminal 1: Start the API server
uvicorn api.main:app --reload

# Terminal 2: Start the web interface  
streamlit run streamlit_app.py
```
Then open http://localhost:8501

**Option B: API only**
```
uvicorn api.main:app --reload
```
Then open http://localhost:8000/docs for API documentation

**Option C: Direct Python**
```python
from agents.coordinator_agent import analyze_stock
result = analyze_stock("AAPL")
print(result)
```

## Project Structure

```
stock-analysis/
├── agents/                 # AI agents for different data sources
│   ├── price_agent.py      # Alpha Vantage (stock prices)
│   ├── financial_agent.py  # Finnhub (financial data)
│   ├── sentiment_agent.py  # NewsAPI (news sentiment)
│   └── coordinator_agent.py # AI coordination
├── api/
│   └── main.py             # FastAPI web server
├── unittest/
│   └── test_stock_analysis.py # Tests
├── streamlit_app.py        # Web dashboard
├── readme.md               
└── requirements.txt        # Dependencies
```

## API Usage

### Analyze a stock
```PowerShell
Invoke-WebRequest -Uri "http://localhost:8000/analyze" -Method POST -ContentType "application/json" -Body '{"symbol":"AAPL"}'
```

### Response
```json
{
  "symbol": "AAPL",
  "analysis": "Stock analysis report with price data, financials, sentiment, and recommendation..."
}
```

## Testing

```
cd unittest
python test_stock_analysis.py
```

## Tool Example Output

```
🎯 STOCK ANALYSIS REPORT: AAPL

CURRENT MARKET DATA:
• Current Price: $152.50 (+1.63%)
• Trend: Bullish

FINANCIAL HEALTH:
• P/E Ratio: 25.5
• ROE: 15.5%
• Assessment: Strong

MARKET SENTIMENT:
• Overall: Positive (65% positive news)

RECOMMENDATION: BUY
Confidence: High
```

## How it works

1. **User requests** stock analysis for a symbol (e.g., "AAPL")
2. **AI Coordinator** calls three specialized agents:
   - Price Agent → gets current/historical prices
   - Financial Agent → gets company fundamentals
   - Sentiment Agent → analyzes recent news
3. **GPT-4 analyzes** all the data together
4. **Returns recommendation** with Buy/Hold/Sell advice

## Technologies Used

- **Python 3.8+**
- **FastAPI** - Web API
- **LangChain** - AI agent framework
- **OpenAI GPT-4** - AI analysis
- **Streamlit** - Web interface
- **Multiple APIs** - Financial data sources

## Requirements

- Python 3.14.1 
- Internet connection
- API keys (all have free tiers)

## Troubleshooting

**"API key not configured"**
→ Check your `.env` file has all required keys

**"Rate limit exceeded"** 
→ Wait, free tiers have limits, please check the limits from Alpha Vantage, Finnhub and NewsAPI documentation

**"Module not found"**
→ Run `pip install -r requirements.txt`

**Tests failing**
→ Make sure you're in the right directory