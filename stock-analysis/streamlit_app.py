import streamlit as st
import requests
import json 
import os

# Base URL for your FastAPI backend

FASTAPI_BASE_URL = os.getenv("FASTAPI_URL", "http://localhost:8000")

def fetch_stock_analysis(symbol: str):
    """
    Makes a POST request to your FastAPI endpoint to get stock analysis.
    """
    url = f"{FASTAPI_BASE_URL}/analyze"
    headers = {"Content-Type": "application/json"}
    payload = {"symbol": symbol}
    
    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        response.raise_for_status() # Raise an exception for HTTP errors
        return response.json()
    except requests.exceptions.ConnectionError:
        st.error(f"Could not connect to FastAPI backend at {FASTAPI_BASE_URL}.")
        return None
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching analysis: {e}")
        return None

st.set_page_config(
    page_title="Stock Analysis AI Assistant",
    page_icon="📈",
    layout="centered"
)

st.title("📈 Stock Analysis AI Assistant")
st.markdown("Enter a stock ticker symbol to get a comprehensive analysis powered by an AI agent.")

# Input for stock symbol
symbol = st.text_input("Enter Stock Symbol (e.g., AAPL, MSFT, GOOGL):", key="stock_symbol").upper()

# Button to trigger analysis
if st.button("Analyze Stock"):
    if symbol:
        with st.spinner(f"Analyzing {symbol} stock... This may take a moment."):
            analysis_data = fetch_stock_analysis(symbol)
            
            if analysis_data:
                st.subheader(f"Analysis for {analysis_data.get('symbol', 'N/A')}")
                
                # Check if the analysis content is in a specific key (e.g., 'analysis')
                analysis_text = analysis_data.get('analysis')
                
                if analysis_text:
                    # Streamlit's st.markdown renders Markdown content beautifully
                    st.markdown(analysis_text)
                else:
                    st.warning("Analysis data received but no 'analysis' key found. Displaying raw data:")
                    st.json(analysis_data) # Display raw JSON for debugging
            else:
                st.error("Failed to retrieve stock analysis. Please check the symbol and try again.")
    else:
        st.warning("Please enter a stock symbol to analyze.")

st.markdown("---")