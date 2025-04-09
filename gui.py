import tkinter as tk
from tkinter import messagebox, ttk
from ttkthemes import ThemedStyle  # Modern styling
from database import add_stock, view_portfolio, calculate_portfolio_value
import matplotlib.pyplot as plt
import matplotlib.pyplot as plt
from data_fetch import get_historical_data, get_stock_price  # ✅ Import real-time price function
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
from data_fetch import get_historical_data
from database import add_stock, view_portfolio, calculate_portfolio_value
import time
import sqlite3  # ✅ Import SQLite to fetch portfolio data
import matplotlib.pyplot
from tkinter import simpledialog

# Create the main application window
import tkinter as tk
from tkinter import ttk

base_root = tk.Tk()  # this is the actual window
base_root.title("Stock Portfolio Manager")
base_root.geometry("1000x800")  # Optional: make it taller for scroll space

main_canvas = tk.Canvas(base_root)
main_scrollbar = ttk.Scrollbar(base_root, orient="vertical", command=main_canvas.yview)
base_root.configure(bg="white")  # Clean all-white background
scrollable_frame = ttk.Frame(main_canvas)

scrollable_frame.bind(
    "<Configure>",
    lambda e: main_canvas.configure(
        scrollregion=main_canvas.bbox("all")
    )
)

main_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
main_canvas.configure(yscrollcommand=main_scrollbar.set)

main_canvas.pack(side="left", fill="both", expand=True)
main_scrollbar.pack(side="right", fill="y")

# ✅ Redirect root so you don’t have to rewrite the rest of your layout
root = scrollable_frame



def _on_mousewheel(event):
    main_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

main_canvas.bind_all("<MouseWheel>", _on_mousewheel)

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
    price = float(price) if price else 0  # Default to 0 if no price is entered

    add_stock(ticker, shares, price)
    messagebox.showinfo("Success", f"Added {shares} shares of {ticker}.")
    ticker_entry.delete(0, tk.END)
    shares_entry.delete(0, tk.END)
    price_entry.delete(0, tk.END)

    update_portfolio_table()  # ✅ Refresh portfolio table
    update_graph()  # ✅ Refresh stock performance graph
    update_portfolio_performance()  # ✅ Refresh portfolio value graph
    update_market_comparison()  # ✅ Refresh comparison graph


def update_portfolio_table():
    """Fetch portfolio data, combine duplicate stocks, and update the table."""
    conn = sqlite3.connect("portfolio.db")
    cursor = conn.cursor()

    # Fetch all stocks from the database
    cursor.execute("SELECT ticker, shares, purchase_price FROM portfolio")
    portfolio = cursor.fetchall()
    conn.close()

    if not portfolio:
        return  # No data, nothing to display

    # Dictionary to store consolidated stock data
    stock_summary = {}

    for ticker, shares, price in portfolio:
        if price is None:
            price = 0  # Handle missing prices

        if ticker in stock_summary:
            # Update total shares & recalculate average price
            total_shares = stock_summary[ticker]["shares"] + shares
            avg_price = ((stock_summary[ticker]["shares"] * stock_summary[ticker]["avg_price"]) + (shares * price)) / total_shares
            stock_summary[ticker]["shares"] = total_shares
            stock_summary[ticker]["avg_price"] = avg_price
        else:
            stock_summary[ticker] = {"shares": shares, "avg_price": price}

    # Clear existing table data
    portfolio_tree.delete(*portfolio_tree.get_children())

    # Update table with condensed data
    for ticker, data in stock_summary.items():
        total_value = data["shares"] * get_stock_price(ticker)  # Get real-time stock price
        portfolio_tree.insert("", "end", values=(ticker, data["shares"], f"${data['avg_price']:.2f}", f"${total_value:.2f}"))
    # Calculate total portfolio value
    total_portfolio_value = sum(data["shares"] * get_stock_price(ticker) for ticker, data in stock_summary.items())

    # Update the displayed portfolio value
    portfolio_value_label.config(text=f"Total Portfolio Value: ${total_portfolio_value:.2f}")

def remove_stock():
    """Allow the user to remove a specific number of shares instead of deleting the entire stock entry."""
    selected_item = portfolio_tree.selection()  # Get selected row
    if not selected_item:
        messagebox.showerror("Error", "Please select a stock to remove shares from.")
        return

    # Get stock details from the selected row
    item_values = portfolio_tree.item(selected_item, "values")
    ticker_to_remove = item_values[0]
    current_shares = int(item_values[1])

    # Ask the user how many shares they want to remove
    shares_to_remove = simpledialog.askinteger("Remove Shares", f"How many shares of {ticker_to_remove} do you want to remove?", minvalue=1, maxvalue=current_shares)
    
    if shares_to_remove is None:  # User canceled the input
        return

    if shares_to_remove > current_shares:
        messagebox.showerror("Error", "You cannot remove more shares than you own.")
        return

    conn = sqlite3.connect("portfolio.db")
    cursor = conn.cursor()

    if shares_to_remove == current_shares:
        # Remove the entire stock entry if all shares are being removed
        cursor.execute("DELETE FROM portfolio WHERE ticker = ?", (ticker_to_remove,))
    else:
        # Update the stock entry with the new number of shares
        cursor.execute("UPDATE portfolio SET shares = shares - ? WHERE ticker = ?", (shares_to_remove, ticker_to_remove))

    conn.commit()
    conn.close()

    # Refresh the portfolio table and total value
    update_portfolio_table()
    update_graph()
    update_portfolio_performance()
    update_market_comparison()  # ✅ Refresh comparison graph

    messagebox.showinfo("Success", f"Removed {shares_to_remove} shares of {ticker_to_remove}.")

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

def update_portfolio_performance():
    """Calculate total portfolio value over time and update the portfolio performance graph."""
    conn = sqlite3.connect("portfolio.db")
    cursor = conn.cursor()

    # Fetch all stock purchases
    cursor.execute("SELECT ticker, shares, purchase_price FROM portfolio")
    portfolio = cursor.fetchall()
    conn.close()

    if not portfolio:
        return  # No data, nothing to plot

    total_invested = sum(shares * price for _, shares, price in portfolio if price is not None)  # Total money invested

    # Fetch historical data for each stock and calculate total value over time
    total_value_over_time = pd.Series(dtype=float)  # ✅ Ensure this is a Pandas Series

    for ticker, shares, _ in portfolio:
        data = get_historical_data(ticker, period="6mo")
        if data is not None and not data.empty:
            if total_value_over_time.empty:  # ✅ Fix: Properly initialize if it's empty
                total_value_over_time = data["Close"] * shares
            else:
                total_value_over_time = total_value_over_time.add(data["Close"] * shares, fill_value=0)

    # Clear existing graph
    ax_portfolio.clear()
    ax_portfolio.set_title("Total Portfolio Performance")
    ax_portfolio.set_xlabel("Date")
    ax_portfolio.set_ylabel("Total Value ($)")

    # Plot total portfolio value
    ax_portfolio.plot(total_value_over_time.index, total_value_over_time, label="Portfolio Value", color="blue")

    # Plot total amount invested as a dotted line
    ax_portfolio.axhline(y=total_invested, color="red", linestyle="dotted", label="Total Invested")

    ax_portfolio.legend()
    canvas_portfolio.draw()

    # Clear existing graph
    ax_portfolio.clear()
    ax_portfolio.set_title("Total Portfolio Performance")
    ax_portfolio.set_xlabel("Date")
    ax_portfolio.set_ylabel("Total Value ($)")

    # Plot total portfolio value
    ax_portfolio.plot(total_value_over_time.index, total_value_over_time, label="Portfolio Value", color="blue")

    # Plot total amount invested as a dotted line
    ax_portfolio.axhline(y=total_invested, color="red", linestyle="dotted", label="Total Invested")

    ax_portfolio.legend()
    canvas_portfolio.draw()





def update_graph():
    """Fetch portfolio data and update the stock performance graph with a single line per stock."""
    conn = sqlite3.connect("portfolio.db")
    cursor = conn.cursor()

    # Fetch all unique stock tickers from the database
    cursor.execute("SELECT DISTINCT ticker FROM portfolio")
    tickers = [row[0] for row in cursor.fetchall()]
    conn.close()

    # Clear the existing graph
    ax.clear()
    ax.set_title("Stock Performance (Last 6 Months)")
    ax.set_xlabel("Date")
    ax.set_ylabel("Stock Price ($)")

    # Fetch and plot stock performance for each unique ticker
    for ticker in tickers:
        data = get_historical_data(ticker, period="6mo")
        if data is not None and not data.empty:
            ax.plot(data.index, data["Close"], label=ticker)  # ✅ One line per ticker

    ax.legend()
    canvas.draw()

def update_market_comparison():
    """Compare portfolio performance to market indices."""
    indices = {
        "^GSPC": "S&P 500",
        "^IXIC": "NASDAQ",
        "^DJI": "Dow Jones"
    }

    # Get portfolio historical value
    conn = sqlite3.connect("portfolio.db")
    cursor = conn.cursor()
    cursor.execute("SELECT ticker, shares FROM portfolio")
    portfolio = cursor.fetchall()
    conn.close()

    portfolio_value = pd.Series(dtype=float)

    for ticker, shares in portfolio:
        data = get_historical_data(ticker, period="6mo")
        if data is not None and not data.empty:
            value = data["Close"] * shares
            portfolio_value = portfolio_value.add(value, fill_value=0) if not portfolio_value.empty else value

    # Normalize portfolio value to start at 100
    normalized_portfolio = (portfolio_value / portfolio_value.iloc[0]) * 100

    # Start the graph
    ax_compare.clear()
    ax_compare.set_title("Portfolio vs Market Indices (Normalized)")
    ax_compare.set_xlabel("Date")
    ax_compare.set_ylabel("Performance (Indexed to 100)")

    ax_compare.plot(normalized_portfolio.index, normalized_portfolio, label="Portfolio", linewidth=2)

    # Plot each index
    for symbol, label in indices.items():
        data = get_historical_data(symbol, period="6mo")
        if data is not None and not data.empty:
            norm_index = (data["Close"] / data["Close"].iloc[0]) * 100
            ax_compare.plot(data.index, norm_index, label=label, linestyle="--")

    ax_compare.legend()
    canvas_compare.draw()
    
# Market Comparison Graph Frame
comparison_graph_frame = ttk.Frame(root, padding=10)
comparison_graph_frame.pack(pady=10, padx=10, fill="both", expand=True)

# Create Matplotlib Figure for Market Comparison
fig_compare, ax_compare = plt.subplots(figsize=(10, 4))
canvas_compare = FigureCanvasTkAgg(fig_compare, master=comparison_graph_frame)
canvas_compare.get_tk_widget().pack(fill="both", expand=True)

# Create a frame for buttons
btn_frame = ttk.Frame(root, padding=20)
btn_frame.pack(pady=10, padx=20, fill="both")

# Frame for portfolio display and graph
portfolio_frame = ttk.Frame(root, padding=10)
portfolio_frame.pack(pady=10, padx=10, fill="both", expand=True)


# Create a Frame for Graphs to Place Them Side by Side
graphs_frame = ttk.Frame(root, padding=10)
graphs_frame.pack(pady=10, padx=10, fill="both", expand=True)

# Stock Performance Graph (Left)
graph_frame = ttk.Frame(graphs_frame, padding=10)
graph_frame.grid(row=0, column=0, sticky="nsew")

# Portfolio Performance Graph (Right)
portfolio_graph_frame = ttk.Frame(graphs_frame, padding=10)
portfolio_graph_frame.grid(row=0, column=1, sticky="nsew")


# Create Matplotlib Figure for Stock Performance Graph
fig, ax = plt.subplots(figsize=(5, 3))  # Adjust width
canvas = FigureCanvasTkAgg(fig, master=graph_frame)
canvas.get_tk_widget().pack(fill="both", expand=True)

# Create Matplotlib Figure for Portfolio Performance Graph
fig_portfolio, ax_portfolio = plt.subplots(figsize=(5, 3))  # Adjust width
canvas_portfolio = FigureCanvasTkAgg(fig_portfolio, master=portfolio_graph_frame)
canvas_portfolio.get_tk_widget().pack(fill="both", expand=True)

# Allow Both Graphs to Expand Evenly
graphs_frame.columnconfigure(0, weight=1)
graphs_frame.columnconfigure(1, weight=1)


# Portfolio Frame (Table)
portfolio_frame = ttk.Frame(root, padding=10)
portfolio_frame.pack(pady=10, padx=10, fill="both", expand=True)
# Portfolio Table
portfolio_tree = ttk.Treeview(portfolio_frame, columns=("Ticker", "Total Shares", "Avg Price ($)", "Total Value ($)"), show="headings")

portfolio_tree.heading("Ticker", text="Ticker")
portfolio_tree.heading("Total Shares", text="Total Shares")
portfolio_tree.heading("Avg Price ($)", text="Avg Price ($)")
portfolio_tree.heading("Total Value ($)", text="Total Value ($)")

portfolio_tree.pack(fill="both", expand=True)

# Portfolio Value Frame
portfolio_value_frame = ttk.Frame(root, padding=10)
portfolio_value_frame.pack(pady=10, padx=10, fill="both", expand=True)

# Label to Display Total Portfolio Value
portfolio_value_label = ttk.Label(portfolio_value_frame, text="Total Portfolio Value: $0.00", font=("Arial", 14, "bold"))
portfolio_value_label.pack()


# Styled buttons with light gray background
ttk.Button(btn_frame, text="Add Stock", command=add_stock_gui, style="TButton").pack(pady=5)
ttk.Button(btn_frame, text="View Portfolio", command=view_portfolio_gui, style="TButton").pack(pady=5)
ttk.Button(btn_frame, text="Show Stock Graph", command=plot_stock_performance, style="TButton").pack(pady=5)
ttk.Button(btn_frame, text="Refresh Prices", command=refresh_stock_prices, style="TButton").pack(pady=5)
ttk.Button(btn_frame, text="Exit", command=root.quit, style="TButton").pack(pady=5)
# Button to Remove Selected Stock
ttk.Button(btn_frame, text="Remove Shares", command=remove_stock, style="TButton").pack(pady=5)

# Run the application
update_portfolio_table()  # ✅ Load portfolio data when GUI starts
update_graph()  # ✅ Load stock performance graph on startup
update_portfolio_performance()  # ✅ Load total portfolio performance graph on startup
update_market_comparison()  # ✅ Load comparison graph on startup

base_root.mainloop()



