import json
import os
from dotenv import load_dotenv

from fetcher import get_stock_data, get_raw_news
from engine import classify_market_state
from llm_handler import generate_hunter_playbook

# Load environment variables from .env file at the very beginning
load_dotenv()

def assemble_hunter_payload(symbol):
    """Build a unified hunter payload from stock metrics, engine outputs, and news."""
    technical_metrics = get_stock_data(symbol)
    engine_result = classify_market_state(technical_metrics)
    news_items = get_raw_news(symbol)

    payload = {
        "meta": {
            "ticker": symbol,
            "mode": os.getenv("RUN_MODE", "production")
        },
        "engine_outputs": {
            "state": engine_result.get("assigned_state") or engine_result.get("state"),
            "score": engine_result.get("engine_score") or engine_result.get("score")
        },
        "technical_metrics": technical_metrics if technical_metrics is not None else {},
        "unstructured_news": news_items
    }

    return payload


if __name__ == "__main__":
    symbol = "PNB.NS"
    print(f"Executing End-to-End Hunter Pipeline for {symbol}...")
    
    # 1. Compile the master payload packet
    payload = assemble_hunter_payload(symbol)
    
    # 2. Pipe the structured payload packet to the GenAI SDK layer
    print("Piping data packet to Gemini Layer for synthesis...")
    try:
        final_playbook = generate_hunter_playbook(payload)
        
        print("\n" + "="*70)
        print("🎯 TARGET SYSTEM DISPLAY OUTPUT")
        print("="*70)
        print(final_playbook)
        print("="*70)
        
    except Exception as e:
        print(f"\n❌ Execution Failed: {e}")
        print("Ensure your GEMINI_API_KEY inside the .env file is valid and look for any syntax issues in llm_handler.py.")