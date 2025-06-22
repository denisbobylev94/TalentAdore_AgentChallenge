# ==============================================================================
# AI STOCK ANALYSIS API
# ==============================================================================
# This FastAPI application provides a REST API for stock analysis
# using AI coordination of multiple financial data sources (Alpha Vantage, 
# Finnhub, and NewsAPI) through OpenAI's language models.
#
# Date: 21.06.2025
# Version: 1.0.0
# ==============================================================================

import sys
import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agents.coordinator_agent import analyze_stock
load_dotenv()

# Create FastAPI application instance with metadata
app = FastAPI(
    title="AI Stock Analysis API",
    description="Professional stock analysis using AI coordination of multiple financial data sources",
    version="1.0.0"
)

class StockRequest(BaseModel):
    """
    Request model for stock analysis endpoint.
    
    This defines the structure of data that clients must send when requesting
    stock analysis. 
    
    Attributes:
        symbol (str): Stock ticker symbol (e.g., 'AAPL', 'MSFT', 'GOOGL')
                     Must be a string, cannot be empty
    
    Example valid request:
        {"symbol": "AAPL"}
    """
    symbol: str

# API ENDPOINTS
@app.get("/")
def root():
    """
    Root endpoint providing API information and usage instructions.
    
    This endpoint serves as a welcome page and quick reference for the API.
    It's accessible via GET request to the base URL.
    
    Returns:
        dict: Basic API information including usage instructions
    """
    return {
        "message": "AI Stock Analysis API",
        "description": "Comprehensive stock analysis using AI coordination",
        "usage": "POST /analyze with JSON: {'symbol': 'AAPL'}",
        "documentation": "/docs",
        "data_sources": ["Alpha Vantage", "Finnhub", "NewsAPI"],
        "ai_model": "OpenAI GPT-4"
    }

@app.post("/analyze")
def analyze(request: StockRequest):
    """
    Main stock analysis endpoint.
    
    This endpoint accepts a stock symbol and returns a comprehensive analysis
    using AI coordination of multiple financial data sources:
    - Alpha Vantage: Current price, technical indicators, moving averages
    - Finnhub: Financial ratios, company fundamentals, valuation metrics
    - NewsAPI: Market sentiment analysis from recent news headlines
    
    The AI agent coordinates these tools and provides:
    - Executive summary
    - Current market data and technical analysis
    - Financial health assessment
    - Market sentiment analysis
    - Investment recommendation (Buy/Hold/Sell)
    - Key risks and opportunities
    
    Args:
        request (StockRequest): Request object containing the stock symbol
    
    Returns:
        dict: Analysis results containing:
            - symbol: The analyzed stock symbol (uppercase)
            - analysis: Complete AI-generated analysis report
    
    Raises:
        HTTPException: 500 error if analysis fails due to:
            - Missing or invalid API keys
            - Network connectivity issues
            - Invalid stock symbol
            - AI model errors
    
    Example:
        Request:  POST /analyze {"symbol": "AAPL"}
        Response: {"symbol": "AAPL", "analysis": "📊 STOCK ANALYSIS..."}
    """
    try:
        # Convert symbol to uppercase and remove whitespace for consistency

        symbol = request.symbol.upper().strip()
        
        # Call the AI coordinator agent to perform comprehensive analysis
        # This function coordinates multiple tools and APIs to generate the analysis
        result = analyze_stock(symbol)
        
        # Return successful response with analysis results
        return {
            "symbol": symbol,
            "analysis": result
        }
        
    except Exception as e:
        # Handle any errors that occur during analysis
        # This could include:
        # - API key configuration issues
        # - Network connectivity problems
        # - Invalid stock symbols
        # - AI model errors
        # - Rate limiting from external APIs
        
        # Log the error for debugging
        print(f"Error analyzing stock {request.symbol}: {str(e)}")
        
        # Return HTTP 500 error with error details
        raise HTTPException(
            status_code=500,
            detail=f"Failed to analyze stock {request.symbol}: {str(e)}"
        )

@app.get("/health")
def health_check():
    """
    Health check endpoint to verify API status.
    
    This endpoint allows clients and monitoring systems to check if the API
    is running and responsive. It doesn't perform
    any complex operations.
    
    Returns:
        dict: Health status information
    """
    return {
        "status": "healthy",
        "message": "AI Stock Analysis API is operational"
    }

