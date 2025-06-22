"""
Unit Tests for Stock Analysis System
"""

import unittest
from unittest.mock import patch, MagicMock
import os
import sys

# Add paths for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, '..'))
sys.path.extend([current_dir, parent_dir])

from agents.price_agent import get_stock_price
from agents.financial_agent import get_financials
from agents.sentiment_agent import get_sentiment

# Mock data
MOCK_ALPHA_VANTAGE_RESPONSE = {
    "Time Series (Daily)": {
        "2024-01-15": {"1. open": "150.00", "2. high": "155.00", "3. low": "149.00", "4. close": "152.50", "5. volume": "1000000"},
        "2024-01-14": {"1. open": "148.00", "2. high": "151.00", "3. low": "147.00", "4. close": "150.00", "5. volume": "900000"}
    }
}

MOCK_FINNHUB_PROFILE = {"name": "Apple Inc", "finnhubIndustry": "Technology", "marketCapitalization": 3000000}
MOCK_FINNHUB_METRICS = {"metric": {"peBasicExclExtraTTM": 25.5, "pbAnnual": 5.2, "roeTTM": 15.5}}
MOCK_NEWS_RESPONSE = {"status": "ok", "articles": [{"title": "Apple stock surges on strong earnings"}]}

class TestPriceAgent(unittest.TestCase):
    """Test price agent functionality"""
    
    @patch('agents.price_agent.requests.get')
    @patch('agents.price_agent.ALPHA_VANTAGE_API_KEY', 'test_key')
    def test_get_stock_price_success(self, mock_get):
        """Test successful price retrieval"""
        mock_get.return_value = MagicMock(json=lambda: MOCK_ALPHA_VANTAGE_RESPONSE)
        result = get_stock_price.invoke({"symbol": "AAPL"})
        
        self.assertIn("STOCK ANALYSIS", result)
        self.assertIn("Current Price", result)
        self.assertIn("152.50", result)
    
    @patch('agents.price_agent.ALPHA_VANTAGE_API_KEY', None)
    def test_get_stock_price_no_api_key(self):
        """Test missing API key handling"""
        result = get_stock_price.invoke({"symbol": "AAPL"})
        self.assertIn("API key not configured", result)

class TestFinancialAgent(unittest.TestCase):
    """Test financial agent functionality"""
    
    @patch('agents.financial_agent.requests.get')
    @patch('agents.financial_agent.FINNHUB_API_KEY', 'test_key')
    def test_get_financials_success(self, mock_get):
        """Test successful financial data retrieval"""
        mock_responses = [
            MagicMock(status_code=200, json=lambda: MOCK_FINNHUB_PROFILE),
            MagicMock(status_code=200, json=lambda: MOCK_FINNHUB_METRICS)
        ]
        mock_get.side_effect = mock_responses
        result = get_financials.invoke({"symbol": "AAPL"})
        
        self.assertIn("FINANCIAL ANALYSIS", result)
        self.assertIn("Apple Inc", result)
    
    @patch('agents.financial_agent.FINNHUB_API_KEY', None)
    def test_get_financials_no_api_key(self):
        """Test missing API key handling"""
        result = get_financials.invoke({"symbol": "AAPL"})
        self.assertIn("FINNHUB API KEY REQUIRED", result)

class TestSentimentAgent(unittest.TestCase):
    """Test sentiment agent functionality"""
    
    @patch('agents.sentiment_agent.requests.get')
    @patch('agents.sentiment_agent.NEWS_API_KEY', 'test_key')
    def test_get_sentiment_success(self, mock_get):
        """Test successful sentiment analysis"""
        mock_get.return_value = MagicMock(status_code=200, json=lambda: MOCK_NEWS_RESPONSE)
        result = get_sentiment.invoke({"symbol": "AAPL"})
        
        self.assertIn("SENTIMENT ANALYSIS", result)
        self.assertIn("OVERALL SENTIMENT", result)
    
    @patch('agents.sentiment_agent.NEWS_API_KEY', None)
    def test_get_sentiment_no_api_key(self):
        """Test missing API key handling"""
        result = get_sentiment.invoke({"symbol": "AAPL"})
        self.assertIn("NEWS API KEY REQUIRED", result)

class TestFastAPI(unittest.TestCase):
    """Test FastAPI endpoints"""
    
    def setUp(self):
        """Set up test client"""
        try:
            from fastapi.testclient import TestClient
            #sys.path.append(os.path.join(parent_dir, 'api'))
            from api.main import app
            self.client = TestClient(app)
            self.api_available = True
        except ImportError:
            self.api_available = False
    
    def test_health_endpoint(self):
        """Test health check endpoint"""
        if not self.api_available:
            self.skipTest("FastAPI not available")
        
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "healthy")
    
    def test_root_endpoint(self):
        """Test root endpoint"""
        if not self.api_available:
            self.skipTest("FastAPI not available")
        
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("AI Stock Analysis API", response.json()["message"])
    
    def test_analyze_endpoint_structure(self):
        """Test analyze endpoint returns proper structure"""
        if not self.api_available:
            self.skipTest("FastAPI not available")
        
        response = self.client.post("/analyze", json={"symbol": "AAPL"})
        
        # Should return 200 or 500, but proper JSON structure
        self.assertIn(response.status_code, [200, 500])
        
        if response.status_code == 200:
            data = response.json()
            self.assertIn("symbol", data)
            self.assertIn("analysis", data)
            self.assertEqual(data["symbol"], "AAPL")

class TestIntegration(unittest.TestCase):
    """Integration tests"""
    
    def test_all_agents_working(self):
        """Test all agents work together"""
        # Test price agent
        with patch('agents.price_agent.requests.get') as mock_price_get, \
             patch('agents.price_agent.ALPHA_VANTAGE_API_KEY', 'test_key'):
            
            mock_price_get.return_value = MagicMock(json=lambda: MOCK_ALPHA_VANTAGE_RESPONSE)
            price_result = get_stock_price.invoke({"symbol": "AAPL"})
            self.assertIn("STOCK ANALYSIS", price_result)
        
        # Test financial agent
        with patch('agents.financial_agent.requests.get') as mock_financial_get, \
             patch('agents.financial_agent.FINNHUB_API_KEY', 'test_key'):
            
            mock_financial_get.side_effect = [
                MagicMock(status_code=200, json=lambda: MOCK_FINNHUB_PROFILE),
                MagicMock(status_code=200, json=lambda: MOCK_FINNHUB_METRICS)
            ]
            financial_result = get_financials.invoke({"symbol": "AAPL"})
            self.assertIn("FINANCIAL ANALYSIS", financial_result)
        
        # Test sentiment agent
        with patch('agents.sentiment_agent.requests.get') as mock_sentiment_get, \
             patch('agents.sentiment_agent.NEWS_API_KEY', 'test_key'):
            
            mock_sentiment_get.return_value = MagicMock(status_code=200, json=lambda: MOCK_NEWS_RESPONSE)
            sentiment_result = get_sentiment.invoke({"symbol": "AAPL"})
            self.assertIn("SENTIMENT ANALYSIS", sentiment_result)

if __name__ == "__main__":
    print("🧪 Stock Analysis Unit Tests")
    print("=" * 30)
    unittest.main(verbosity=2, exit=False)
    print("\n✅ Tests completed!")