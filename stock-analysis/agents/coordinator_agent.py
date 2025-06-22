import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.exceptions import OutputParserException

# Import tools
from agents.price_agent import get_stock_price  # Alpha Vantage tool
from agents.financial_agent import get_financials  # Finnhub tool
from agents.sentiment_agent import get_sentiment  # NewsAPI tool

load_dotenv()

def analyze_stock(symbol: str) -> str:
    """
    Stock analysis coordinator
    
    Key features:
    - Handles all agent's tools
    - Error handling for API issues

    Args:
        symbol: Stock ticker symbol to analyze
        
    Returns:
        Structured analysis or error message
    """
    
    # 1.LLM configuration
    llm_for_agent = ChatOpenAI(
        temperature=0.1,  
        model="gpt-4o",
        openai_api_key=os.getenv("OPENAI_API_KEY")
    )

    # 2. Define available tools
    tools = [
        get_stock_price,    # Alpha Vantage (price/technical analysis)
        get_financials,     # Finnhub (financial metrics/ratios)
        get_sentiment,      # NewsAPI (market sentiment from news)
    ]

    # 3. Prompt
    prompt = ChatPromptTemplate.from_messages([
        ("system", f"""You are an expert financial analyst AI. Your task is to provide a simple stock analysis for the requested symbol.

            **TOOL USAGE GUIDELINES:**
            1. **get_stock_price**: Current price, daily changes, moving averages, technical trends (Alpha Vantage)
            2. **get_financials**: Company info, financial ratios, fundamental analysis (Finnhub)  
            3. **get_sentiment**: Market sentiment from recent news headlines (NewsAPI)

            **ERROR HANDLING PROTOCOL:**
            - If a tool returns an error message (contains "Error:", "API key", "rate limit"), acknowledge it clearly
            - Do NOT retry failed tools immediately
            - Continue analysis with available data
            - Clearly state what data is missing and why

            **OUTPUT STRUCTURE:**
            1. **Executive Summary** (2-3 sentences)
            2. **Current Market Data** (price, changes, trends)
            3. **Financial Health** (key ratios and metrics)
            4. **Market Sentiment** (news-based sentiment analysis)
            5. **Analysis & Recommendation** (Buy/Hold/Sell with reasoning)
            6. **Key Risks & Opportunities**
            7. **Data Quality Note** (mention any missing data)

            **PROFESSIONAL TONE:**
            - Use clear, confident language
            - Provide specific numbers and percentages
            - Give actionable insights
            - No standard disclaimers needed"""),
                    
                    ("human", "{input}"),
                    ("placeholder", "{agent_scratchpad}"),
                ])

    # 4. Create agent with configuration
    agent = create_tool_calling_agent(llm_for_agent, tools, prompt)

    # 5. Make AgentExecutor
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=False,
        handle_parsing_errors=True,
        max_iterations=5,  # Prevent infinite loops
        early_stopping_method="generate"  # Stop when final answer is generated
    )

    # 6. Analysis query
    user_query = f"""
    Analyze the stock {symbol} using all available tools.
    
    Please:
    1. Get current price data and technical analysis
    2. Get financial metrics and company fundamentals  
    3. Check recent market sentiment from news
    4. Provide a complete investment analysis with Buy/Hold/Sell recommendation
    
    Use all three tools and provide analysis based on whatever data you can gather.
    """

    try:
        # 7. Execute analysis
        result = agent_executor.invoke({
            "input": user_query
        })
        
        # Add simple header with analysis details
        header = f"""
            🎯 STOCK ANALYSIS REPORT: {symbol.upper()}
            Data Sources: Alpha Vantage + Finnhub + NewsAPI
            Generated: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M')}
            """
        return header + result["output"]
    except OutputParserException as ope:
        return f"""❌ ANALYSIS ERROR: {symbol.upper()}

                    The AI agent encountered a parsing error while processing your request.
                    
                    Error Details: {str(ope)}

                    SUGGESTED SOLUTIONS:
                    1. Try again with another query
                    2. Check if your API keys are properly configured:
                    - OPENAI_API_KEY (for the AI agent)
                    - ALPHA_VANTAGE_API_KEY (for price data)  
                    - FINNHUB_API_KEY (for financial data)
                    - NEWS_API_KEY (for sentiment analysis)
                    3. Verify the stock symbol is correct

                    You can also try using the tools directly:
                    - get_stock_price.invoke({{"symbol": "{symbol}"}})
                    - get_financials.invoke({{"symbol": "{symbol}"}})
                    - get_sentiment.invoke({{"symbol": "{symbol}"}})"""

    except Exception as e:
        return f"""❌ UNEXPECTED ERROR: {symbol.upper()}

                An unexpected error occurred during the stock analysis.

                Error Details: {str(e)}

                TROUBLESHOOTING:
                1. Verify your API keys are configured:
                - OPENAI_API_KEY (for AI coordination)
                - ALPHA_VANTAGE_API_KEY (for price data)
                - FINNHUB_API_KEY (for financial data)  
                - NEWS_API_KEY (for sentiment analysis)
                2. Check your internet connection
                3. Ensure the stock symbol is valid"""
    
