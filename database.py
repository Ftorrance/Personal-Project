
import sqlite3

# Connect to database (or create it if it doesn't exist)
conn = sqlite3.connect("portfolio.db")
cursor = conn.cursor()

# Create table for storing stock holdings
cursor.execute('''
    CREATE TABLE IF NOT EXISTS portfolio (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ticker TEXT NOT NULL,
        shares INTEGER NOT NULL,
        purchase_price REAL,
        date_added TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
''')

conn.commit()
conn.close()

def add_stock(ticker, shares, purchase_price=None):
    """Add a stock to the portfolio."""
    conn = sqlite3.connect("portfolio.db")
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO portfolio (ticker, shares, purchase_price)
        VALUES (?, ?, ?)
    ''', (ticker.upper(), shares, purchase_price))
    
    conn.commit()
    conn.close()
    print(f"Added {shares} shares of {ticker.upper()} to portfolio.")

def view_portfolio():
    """Retrieve and display all stocks in the portfolio."""
    conn = sqlite3.connect("portfolio.db")
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM portfolio")
    rows = cursor.fetchall()
    
    conn.close()
    
    print("\nYour Portfolio:")
    for row in rows:
        print(row)

from data_fetch import get_stock_price  # Import the stock price function

def calculate_portfolio_value():
    """Calculate the total value of the portfolio using live stock prices."""
    conn = sqlite3.connect("portfolio.db")
    cursor = conn.cursor()
    
    cursor.execute("SELECT ticker, shares FROM portfolio")
    holdings = cursor.fetchall()
    conn.close()

    if not holdings:
        print("Your portfolio is empty.")
        return

    total_value = 0
    print("\nPortfolio Summary:")
    print(f"{'Ticker':<10}{'Shares':<10}{'Current Price':<15}{'Total Value':<15}")
    print("=" * 50)

    for ticker, shares in holdings:
        price = get_stock_price(ticker)
        if price:
            stock_value = shares * price
            total_value += stock_value
            print(f"{ticker:<10}{shares:<10}${price:<15.2f}${stock_value:<15.2f}")
        else:
            print(f"Could not retrieve price for {ticker}")

    print("=" * 50)
    print(f"Total Portfolio Value: ${total_value:.2f}")


if __name__ == "__main__":
    while True:
        print("\nPortfolio Manager:")
        print("1. Add a stock")
        print("2. View portfolio")
        print("3. Calculate portfolio value")
        print("4. Exit")
        choice = input("Enter choice: ")

        if choice == "1":
            ticker = input("Enter stock ticker: ").upper()
            shares = int(input("Enter number of shares: "))
            price = input("Enter purchase price (optional, press Enter to skip): ")
            price = float(price) if price else None
            add_stock(ticker, shares, price)

        elif choice == "2":
            view_portfolio()

        elif choice == "3":
            calculate_portfolio_value()

        elif choice == "4":
            break

        else:
            print("Invalid choice. Try again.")



