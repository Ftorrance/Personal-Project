#%%
import yfinance as yf

def get_stock_price(ticker):
    """Fetch the latest stock price for a given ticker."""
    stock = yf.Ticker(ticker)
    try:
        price = stock.history(period="1d")["Close"].iloc[-1]
        return price
    except Exception as e:
        print(f"Error fetching stock price for {ticker}: {e}")
        return None

if __name__ == "__main__":
    ticker = input("Enter stock ticker symbol (e.g., AAPL, TSLA, MSFT): ").upper()
    price = get_stock_price(ticker)
    
    if price:
        print(f"Current price of {ticker}: ${price:.2f}")
    else:
        print("Failed to fetch stock data.")

import yfinance as yf
import pandas as pd

def get_stock_price(ticker):
    """Fetch the latest stock price for a given ticker."""
    stock = yf.Ticker(ticker)
    try:
        price = stock.history(period="1d")["Close"].iloc[-1]
        return price
    except Exception as e:
        print(f"Error fetching stock price for {ticker}: {e}")
        return None

def get_historical_data(ticker, period="1mo"):
    """Fetch historical stock price data for a given period."""
    stock = yf.Ticker(ticker)
    try:
        hist = stock.history(period=period)
        return hist[['Close']]  # Returning only the closing price
    except Exception as e:
        print(f"Error fetching historical data for {ticker}: {e}")
        return None

if __name__ == "__main__":
    ticker = input("Enter stock ticker symbol (e.g., AAPL, TSLA, MSFT): ").upper()
    
    # Fetch real-time price
    price = get_stock_price(ticker)
    if price:
        print(f"Current price of {ticker}: ${price:.2f}")
    
    # Fetch historical data
    period = input("Enter historical period (e.g., '1mo', '3mo', '6mo', '1y', '5y'): ")
    historical_data = get_historical_data(ticker, period)
    
    if historical_data is not None:
        print(f"\nHistorical Data for {ticker} - Last {period}:")
        print(historical_data.tail())  # Show last few rows of historical data

# %%
