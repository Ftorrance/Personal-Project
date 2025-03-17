import tkinter as tk
from tkinter import messagebox, ttk
from ttkthemes import ThemedStyle  # Modern styling
from database import add_stock, view_portfolio, calculate_portfolio_value
import matplotlib.pyplot as plt
import matplotlib.pyplot as plt
from data_fetch import get_historical_data, get_stock_price  # ✅ Import real-time price function

import time

# Create the main application window
root = tk.Tk()
root.title("Stock Portfolio Manager")
root.geometry("500x500")
root.configure(bg="white")  # Clean all-white background

# Apply a neutral theme
style = ThemedStyle(root)
style.set_theme("arc")  # Light modern theme with gray accents

# Custom fonts and colors
FONT = ("Arial", 12)
GRAY = "#d9d9d9"  # Light gray for input fields and buttons
WHITE = "#FFFFFF"  # Clean white for the background
BLACK = "#000000"  # Black text for visibility

# Apply styles
style.configure("TButton", font=FONT, background=GRAY, foreground="black", padding=8)
style.configure("TLabel", font=FONT, background=WHITE, foreground=BLACK)
style.configure("TEntry", font=FONT, background=GRAY, foreground=BLACK, padding=5)

# Create a styled frame for inputs
input_frame = ttk.Frame(root, padding=20, style="TFrame")
input_frame.pack(pady=10, padx=20, fill="both")

# Entry fields with light gray backgrounds
ttk.Label(input_frame, text="Stock Ticker:").grid(row=0, column=0, sticky="w", pady=5)
ticker_entry = tk.Entry(input_frame, font=FONT, bg=GRAY, fg=BLACK, relief="solid", borderwidth=1)
ticker_entry.grid(row=0, column=1, pady=5)

ttk.Label(input_frame, text="Number of Shares:").grid(row=1, column=0, sticky="w", pady=5)
shares_entry = tk.Entry(input_frame, font=FONT, bg=GRAY, fg=BLACK, relief="solid", borderwidth=1)
shares_entry.grid(row=1, column=1, pady=5)

ttk.Label(input_frame, text="Purchase Price (Optional):").grid(row=2, column=0, sticky="w", pady=5)
price_entry = tk.Entry(input_frame, font=FONT, bg=GRAY, fg=BLACK, relief="solid", borderwidth=1)
price_entry.grid(row=2, column=1, pady=5)

# Function to handle adding a stock
def add_stock_gui():
    ticker = ticker_entry.get().upper()
    shares = shares_entry.get()
    price = price_entry.get()

    if not ticker or not shares.isdigit():
        messagebox.showerror("Input Error", "Please enter a valid stock ticker and number of shares.")
        return

    shares = int(shares)
    price = float(price) if price else None

    add_stock(ticker, shares, price)
    messagebox.showinfo("Success", f"Added {shares} shares of {ticker}.")
    ticker_entry.delete(0, tk.END)
    shares_entry.delete(0, tk.END)
    price_entry.delete(0, tk.END)

# Function to display portfolio
def view_portfolio_gui():
    portfolio_window = tk.Toplevel(root)
    portfolio_window.title("Your Portfolio")

    text = tk.Text(portfolio_window, wrap="word", width=60, height=20, bg=WHITE, fg=BLACK, relief="solid", borderwidth=1)
    text.pack(padx=10, pady=10)

    import io
    import sys
    old_stdout = sys.stdout
    sys.stdout = buffer = io.StringIO()

    view_portfolio()

    sys.stdout = old_stdout
    text.insert("1.0", buffer.getvalue())

# Function to calculate portfolio value
def calculate_portfolio_value_gui():
    import io
    import sys
    old_stdout = sys.stdout
    sys.stdout = buffer = io.StringIO()

    calculate_portfolio_value()

    sys.stdout = old_stdout
    messagebox.showinfo("Portfolio Value", buffer.getvalue())

def plot_stock_performance():
    ticker = ticker_entry.get().upper()
    
    if not ticker:
        messagebox.showerror("Input Error", "Please enter a stock ticker.")
        return

    data = get_historical_data(ticker, period="6mo")  # Fetch last 6 months of data

    if data is None or data.empty:
        messagebox.showerror("Error", f"Could not retrieve data for {ticker}.")
        return

    plt.figure(figsize=(8, 4))
    plt.plot(data.index, data['Close'], marker='o', linestyle='-', color="#007BFF", label=f"{ticker} Price")
    plt.xlabel("Date")
    plt.ylabel("Closing Price ($)")
    plt.title(f"{ticker} Stock Performance (Last 6 Months)")
    plt.legend()
    plt.grid()
    plt.show()

def refresh_stock_prices():
    """Fetch and update the latest stock prices in real-time."""
    ticker = ticker_entry.get().upper()

    if not ticker:
        messagebox.showerror("Input Error", "Please enter a stock ticker.")
        return

    price = get_stock_price(ticker)  # Fetch real-time price

    if price is None:
        messagebox.showerror("Error", f"Could not retrieve data for {ticker}.")
        return

    messagebox.showinfo("Live Price Update", f"Current price of {ticker}: ${price:.2f}")

    # Automatically refresh every 10 seconds
    root.after(10000, refresh_stock_prices)  # 10,000 ms = 10 sec

# Create a frame for buttons
btn_frame = ttk.Frame(root, padding=20)
btn_frame.pack(pady=10, padx=20, fill="both")

# Styled buttons with light gray background
ttk.Button(btn_frame, text="Add Stock", command=add_stock_gui, style="TButton").pack(pady=5)
ttk.Button(btn_frame, text="View Portfolio", command=view_portfolio_gui, style="TButton").pack(pady=5)
ttk.Button(btn_frame, text="Calculate Portfolio Value", command=calculate_portfolio_value_gui, style="TButton").pack(pady=5)
ttk.Button(btn_frame, text="Show Stock Graph", command=plot_stock_performance, style="TButton").pack(pady=5)
ttk.Button(btn_frame, text="Refresh Prices", command=refresh_stock_prices, style="TButton").pack(pady=5)
ttk.Button(btn_frame, text="Exit", command=root.quit, style="TButton").pack(pady=5)

# Run the application
root.mainloop()


