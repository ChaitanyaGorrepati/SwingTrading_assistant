import yfinance as yf
import pandas as pd
import pandas_ta as ta


def analyze_stock(symbol):
    # Download stock data
    df = yf.download(symbol, period="6mo", auto_adjust=True)

    # Check if data exists
    if df.empty:
        return f"No data found for {symbol}"

    # Ensure Close column is a Series
    close = df["Close"].squeeze()

    # RSI
    df["RSI"] = ta.rsi(close, length=14)

    # MACD
    macd = ta.macd(close)

    if macd is None:
        return "MACD calculation failed"

    df["MACD"] = macd.iloc[:, 0]

    # Latest row
    latest = df.iloc[-1]

    return {
        "Stock": symbol,
    "Close": round(latest["Close"].item(), 2),
"RSI": round(latest["RSI"].item(), 2),
"MACD": round(latest["MACD"].item(), 2),
    }


print(analyze_stock("PNB.NS"))