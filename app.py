import json
import streamlit as st

from llm_handler import generate_hunter_playbook, generate_guardian_verdict
from main import assemble_hunter_payload
from fetcher import get_stock_data, get_raw_news
from engine import classify_market_state

st.set_page_config(
    page_title="Agentic Market Engine",
    layout="wide",
)

def _display_metric_cards(metrics):
    first_row = st.columns(4)
    first_row[0].metric("Close", _safe_metric(metrics.get("close")))
    first_row[1].metric("RSI", _safe_metric(metrics.get("rsi")))
    first_row[2].metric("ATR", _safe_metric(metrics.get("atr")))
    first_row[3].metric("MACD", _safe_metric(metrics.get("macd")))

    second_row = st.columns(3)
    second_row[0].metric("EMA 20", _safe_metric(metrics.get("ema20")))
    second_row[1].metric("EMA 50", _safe_metric(metrics.get("ema50")))
    second_row[2].metric("EMA 200", _safe_metric(metrics.get("ema200")))

def _safe_metric(value):
    return "N/A" if value is None else value

def _display_news(news_items):
    if not news_items:
        st.info("No raw news items were returned for this ticker.")
        return

    for index, article in enumerate(news_items, start=1):
        title = article.get("title") or f"News item {index}"
        publisher = article.get("publisher") or "Unknown publisher"
        summary = article.get("summary") or "No summary provided."

        with st.expander(title):
            st.caption(publisher)
            st.write(summary)

def _run_hunter_mode():
    st.title("🎯 Agentic Market Hunter Engine")
    st.caption("Scan quantitative indicators and synthesize real-time macro news playbooks.")

    symbol = st.text_input(
        "Enter Ticker Symbol",
        value="PNB.NS",
        placeholder="Example: PNB.NS, TSLA, RELIANCE.NS",
    ).strip().upper()

    if not st.button("Analyze Ticker", type="primary"):
        st.info("Enter a ticker symbol above and click Analyze Ticker to begin exploration loop.")
        return

    if not symbol:
        st.error("Please enter a valid ticker symbol.")
        return

    with st.spinner(f"Compiling comprehensive market payload for {symbol}..."):
        payload = assemble_hunter_payload(symbol)

    engine_outputs = payload.get("engine_outputs", {})
    technical_metrics = payload.get("technical_metrics", {})
    news_items = payload.get("unstructured_news", [])

    st.subheader("Engine Snapshot")
    state_cols = st.columns(2)
    state_cols[0].metric("Market State", engine_outputs.get("state", "UNKNOWN"))
    state_cols[1].metric("Engine Score", engine_outputs.get("score", "N/A"))

    st.subheader("Technical Metrics")
    if technical_metrics:
        _display_metric_cards(technical_metrics)
    else:
        st.warning("No technical metrics were returned for this ticker.")

    st.subheader("Raw News Feed Intelligence")
    _display_news(news_items)

    with st.expander("Payload Master JSON Packet"):
        st.code(json.dumps(payload, indent=2), language="json")

    st.subheader("Tactical Hunter Playbook")
    with st.spinner("Streaming playbook generation from Gemini..."):
        try:
            playbook = generate_hunter_playbook(payload)
            st.markdown(playbook)
        except Exception as exc:
            st.error(f"Gemini playbook generation failed: {exc}")
            st.caption("Check GEMINI_API_KEY inside your .env file or retry if request limits spiked.")

def _run_guardian_mode():
    st.title("🛡️ Active Trade Guardian Shield")
    st.caption("Monitor open positions, track live price deviations, and cross-examine news context for holding justifications.")

    col1, col2 = st.columns(2)
    with col1:
        g_symbol = st.text_input("Active Position Ticker", value="PNB.NS").strip().upper()
        entry_price = st.number_input("Your Average Entry Price", min_value=0.01, value=105.0, step=0.1)
    with col2:
        risk_profile = st.slider("Max Acceptable Account Risk (%)", min_value=0.5, max_value=5.0, value=2.0, step=0.5)
        position_size = st.number_input("Total Quantity of Shares Held", min_value=1, value=500, step=1)

    if st.button("Activate Guardian Scan", type="primary"):
        with st.spinner(f"Pulling real-time exchange feeds and contextual news for {g_symbol}..."):
            current_data = get_stock_data(g_symbol)
            raw_news = get_raw_news(g_symbol)
            
        if not current_data or current_data.get("close") is None:
            st.error("Could not fetch real-time market data for the specified active position ticker.")
            return
            
        # Classify operational state from current indicators
        engine_outputs = classify_market_state(current_data)
        live_close = current_data["close"]
        pnl_per_share = live_close - entry_price
        total_pnl = pnl_per_share * position_size
        pnl_percent = (pnl_per_share / entry_price) * 100
        
        # Calculate mathematical stop bounds
        hard_stop_level = round(entry_price * (1 - (risk_profile / 100)), 2)
        capital_at_risk = round((entry_price - hard_stop_level) * position_size, 2)

        st.subheader("Position Performance Matrix")
        m_col1, m_col2, m_col3 = st.columns(3)
        m_col1.metric("Live Market Price", f"{live_close}")
        
        if total_pnl >= 0:
            m_col2.metric("Unrealized P&L", f"+{round(total_pnl, 2)}", f"+{round(pnl_percent, 2)}%")
        else:
            m_col2.metric("Unrealized P&L", f"{round(total_pnl, 2)}", f"{round(pnl_percent, 2)}%")
            
        m_col3.metric("Hard Math Stop-Loss", f"{hard_stop_level}")

        # Assemble the advanced context payload for AI cross-examination
        guardian_payload = {
            "position_meta": {
                "ticker": g_symbol,
                "entry_price": entry_price,
                "quantity": position_size,
                "risk_allowance_percent": risk_profile
            },
            "math_boundaries": {
                "live_close": live_close,
                "unrealized_pnl_total": round(total_pnl, 2),
                "unrealized_pnl_percent": round(pnl_percent, 2),
                "mathematical_stop_breached": live_close <= hard_stop_level
            },
            "technical_metrics": current_data,
            "engine_state": engine_outputs,
            "unstructured_news": raw_news
        }

        st.subheader("🤖 Intelligent Guardian Risk Evaluation")
        with st.spinner("Piping situational metrics to Risk Officer for contextual holding assessment..."):
            try:
                guardian_analysis = generate_guardian_verdict(guardian_payload)
                st.markdown(guardian_analysis)
            except Exception as e:
                st.error(f"Guardian contextual evaluation timed out: {e}")
                st.caption("The network layer might be congested. Please re-trigger the scan block.")

        with st.expander("Guardian Mathematical Risk Parameters"):
            st.write(f"* **Max Allocated Currency Value at Risk:** {capital_at_risk}")
            st.write(f"* **Asset Average True Range (Volatility Index):** {current_data.get('atr')}")

def main():
    with st.sidebar:
        st.header("App Navigation")
        selected_mode = st.radio(
            "Choose workflow workflow",
            ["Hunter Mode", "Guardian Mode"],
            label_visibility="collapsed",
        )
        
        st.markdown("---")
        st.header("🌐 Ticker Lookup Wizard")
        st.caption("Don't know the symbol for your target asset? Find the correct string instantly:")
        
        st.markdown("[🔍 Search Official Yahoo Tickers](https://finance.yahoo.com/lookup)")
        st.info("Tip: Indian equities require the '.NS' exchange suffix (e.g., PNB.NS, RELIANCE.NS). US assets use standard tags (e.g., TSLA, AAPL).")

    if selected_mode == "Hunter Mode":
        _run_hunter_mode()
    else:
        _run_guardian_mode()

if __name__ == "__main__":
    main()