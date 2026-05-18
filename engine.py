def classify_market_state(metrics):
    """
    Takes the clean technical metrics dictionary and applies strict rule-based
    logic to determine the trading state and an engine score (1-10).
    """
    if not metrics or metrics.get("close") is None:
        return {"state": "UNKNOWN", "score": 0.0}

    # Extract values from the metrics dictionary
    close = metrics["close"]
    rsi = metrics["rsi"]
    ema20 = metrics["ema20"]
    ema50 = metrics["ema50"]
    ema200 = metrics["ema200"]
    macd = metrics["macd"]

    # Default neutral baseline setup
    state = "BASE"
    score = 5.0

    # Guard against missing technical calculations
    if None in [rsi, ema20, ema50, ema200]:
        return {"state": "INSUFFICIENT_DATA", "score": 5.0}

    # --- RULE LOGIC CONFIGURATION ---

    # 1. MOMENTUM STATE
    if close > ema20 > ema50 and rsi > 55:
        state = "MOMENTUM"
        score = 8.0
        if macd and macd > 0:
            score += 1.0  # Add structural confirmation strength

    # 2. FALLING STATE
    elif close < ema20 < ema50:
        state = "FALLING"
        score = 3.0
        if rsi < 30:
            state = "EXHAUSTION"  # Deeply oversold cascade
            score = 4.0

    # 3. REVERSAL STATE (Price cross over short term trend)
    elif close > ema20 and rsi > 45:
        state = "REVERSAL"
        score = 6.5

    # 4. BASE STATE (Sideways/Chop)
    else:
        state = "BASE"
        score = 5.0

    return {
        "assigned_state": state,
        "engine_score": round(score, 1)
    }