import yfinance as yf
import pandas as pd
import pandas_ta as ta
import urllib.request
import xml.etree.ElementTree as ET

def get_stock_data(symbol):
    """
    Downloads 1 year of daily historical data and calculates core metrics,
    including Classic Daily Pivot Point levels, Volume, and Relative Volume (RVOL).
    """
    df = yf.download(symbol, period="1y", auto_adjust=True)
    if df.empty:
        return None
    
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    close = df["Close"].squeeze()
    high = df["High"].squeeze()
    low = df["Low"].squeeze()
    volume = df["Volume"].squeeze()

    # Core indicators
    df["RSI"] = ta.rsi(close, length=14)
    df["ATR"] = ta.atr(high, low, close, length=14)
    df["EMA20"] = ta.ema(close, length=20)
    df["EMA50"] = ta.ema(close, length=50)
    df["EMA200"] = ta.ema(close, length=200)

    # Relative Volume (RVOL) calculations: Volume / 20-day SMA of Volume
    df["Vol_SMA20"] = volume.rolling(window=20).mean()
    df["RVOL"] = volume / df["Vol_SMA20"]

    macd_df = ta.macd(close)
    if macd_df is not None:
        df["MACD"] = macd_df.iloc[:, 0]
    else:
        df["MACD"] = None

    latest = df.iloc[-1]
    
    # Clean helper for scalar value extraction
    def clean_val(val):
        if isinstance(val, pd.Series):
            val = val.iloc[0]
        return float(val) if not pd.isna(val) else None

    # --- PIVOT POINT (SUPPORT & RESISTANCE) CALCULATIONS ---
    # Classic daily pivots are calculated using the previous completed session's High, Low, and Close
    prev_session = df.iloc[-2] if len(df) > 1 else df.iloc[-1]
    
    def get_raw_scalar(series, col_name):
        val = series[col_name]
        if isinstance(val, pd.Series):
            val = val.iloc[0]
        return float(val)

    p_high = get_raw_scalar(prev_session, "High")
    p_low = get_raw_scalar(prev_session, "Low")
    p_close = get_raw_scalar(prev_session, "Close")

    # Pivot Point Formulas
    pp = (p_high + p_low + p_close) / 3.0
    r1 = (2.0 * pp) - p_low
    s1 = (2.0 * pp) - p_high
    r2 = pp + (p_high - p_low)
    s2 = pp - (p_high - p_low)
    r3 = p_high + 2.0 * (pp - p_low)
    s3 = p_low - 2.0 * (p_high - pp)

    return {
        "close": round(clean_val(latest["Close"]), 2),
        "rsi": round(clean_val(latest["RSI"]), 2) if clean_val(latest["RSI"]) is not None else None,
        "ema20": round(clean_val(latest["EMA20"]), 2) if clean_val(latest["EMA20"]) is not None else None,
        "ema50": round(clean_val(latest["EMA50"]), 2) if clean_val(latest["EMA50"]) is not None else None,
        "ema200": round(clean_val(latest["EMA200"]), 2) if clean_val(latest["EMA200"]) is not None else None,
        "atr": round(clean_val(latest["ATR"]), 2) if clean_val(latest["ATR"]) is not None else None,
        "macd": round(clean_val(latest["MACD"]), 4) if clean_val(latest["MACD"]) is not None else None,
        # Volume metrics
        "volume": int(clean_val(latest["Volume"])) if clean_val(latest["Volume"]) is not None else None,
        "rvol": round(clean_val(latest["RVOL"]), 2) if clean_val(latest["RVOL"]) is not None else None,
        # Daily Classic Pivots
        "pivot": round(pp, 2),
        "r1": round(r1, 2),
        "r2": round(r2, 2),
        "r3": round(r3, 2),
        "s1": round(s1, 2),
        "s2": round(s2, 2),
        "s3": round(s3, 2),
        "open_interest": None  # Placeholder for derivatives/options integration
    }

def _parse_rss_feed(url, tag_label, max_results=3):
    """ Helper function to parse Google News RSS feeds and extract distinct metadata """
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=5) as response:
            xml_data = response.read()
            
        root = ET.fromstring(xml_data)
        articles = []
        
        for item in root.findall('.//item')[:max_results]:
            title = item.find('title').text if item.find('title') is not None else "No Title Available"
            publisher = item.find('source').text if item.find('source') is not None else "Google News"
            pub_date = item.find('pubDate').text if item.find('pubDate') is not None else "Recent"
            
            summary_text = f"Context Type: [{tag_label}] | Released: {pub_date} | Market tracking feed active."
            
            articles.append({
                "title": title,
                "publisher": publisher,
                "summary": summary_text
            })
        return articles
    except Exception:
        return []

def get_raw_news(symbol):
    """
    Extracts a balanced, multi-tier blend of Ticker-Specific and 
    Global Macro news context, dynamically tailoring the macro feed 
    based on the ticker's home market.
    """
    combined_news = []
    
    # ─── TIER 1: FETCH TICKER-SPECIFIC HEADLINES (3 ITEMS) ───
    search_term = symbol.split('.')[0]
    ticker_url = f"https://news.google.com/rss/search?q={search_term}+stock&hl=en-IN&gl=IN&ceid=IN:en"
    ticker_news = _parse_rss_feed(ticker_url, tag_label="TICKER_SPECIFIC", max_results=3)
    combined_news.extend(ticker_news)
    
    # ─── TIER 2: DYNAMIC GLOBAL MACRO OVERLAY (2 ITEMS) ───
    if symbol.endswith(".NS"):
        macro_query = "Indian+stock+market+macro+nifty"
        geo_params = "&hl=en-IN&gl=IN&ceid=IN:en"
    else:
        macro_query = "US+stock+market+macro+SP500+inflation"
        geo_params = "&hl=en-US&gl=US&ceid=US:en"
        
    macro_url = f"https://news.google.com/rss/search?q={macro_query}{geo_params}"
    macro_news = _parse_rss_feed(macro_url, tag_label="GLOBAL_MACRO", max_results=2)
    combined_news.extend(macro_news)
    
    # Emergency Fallback if tracking layers yield no headlines
    if not combined_news:
        combined_news.append({
            "title": f"Market Data Monitoring Active for {symbol}",
            "publisher": "System Engine Core",
            "summary": "Context Type: [SYSTEM] | Continuous asset liquidity tracking layer operational."
        })
        
    return combined_news

if __name__ == "__main__":
    print("Testing Upgraded Multi-Tier Fetcher Module with Pivot Points and RVOL...")
    test_metrics = get_stock_data("PNB.NS")
    print("\n--- Upgraded Technical Metrics & Pivots ---")
    import pprint
    pprint.pprint(test_metrics)