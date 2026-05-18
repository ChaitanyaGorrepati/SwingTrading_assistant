import json
import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

def generate_hunter_playbook(payload_json):
    """
    Generate a tactical swing-trading playbook from engine outputs, technical
    metrics, and raw news using a clean, dedicated client session.
    """
    if isinstance(payload_json, str):
        payload_text = payload_json
    else:
        payload_text = json.dumps(payload_json, indent=2, sort_keys=True)

    system_prompt = """
You are a professional financial risk officer and tactical market hunter.
Your job is to convert a quantitative trading payload into a clean, disciplined swing-trading playbook.

Rules:
- Treat the mathematical inputs as the absolute source of truth.
- Do not invent stock prices, technical figures, or news that is not in the payload.
- Categorize the unstructured news cleanly into Global Macro, Sector, and Ticker-Specific groups.
- Explicitly emphasize risk management parameters before outlining trade execution steps.
- This is decision-support analysis, not financial advice.

STRICT TYPOGRAPHY & TEXT RULES:
1. When describing math formulas in plain text sentences, use normal text and regular words. Never combine math operators (+, -, *, =, /) sequentially inside standard paragraphs (e.g., write "Total Risk equals Capital times Risk percentage" instead of cramming symbols together).
2. Never repeat variable lines back-to-back.
3. For the final calculation example, write it out on its own isolated line using explicit double-dollar LaTeX block math format like this:
$$Number\\ of\\ Shares = \\frac{Total\\ Capital \\times \\% Risk}{Risk\\ Per\\ Share}$$
""".strip()

    user_prompt = f"""
Process this hunter payload precisely and return the structured playbook.

Payload:
{payload_text}
""".strip()

    client = genai.Client()

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=[
            {
                "role": "user",
                "parts": [{"text": f"{system_prompt}\n\n{user_prompt}"}],
            }
        ],
        config=types.GenerateContentConfig(
            temperature=0.1,
            top_p=0.95
        )
    )

    return response.text


def generate_guardian_verdict(payload_json):
    """
    Evaluates an active open trade breakdown against mathematical metrics 
    and real-time news context to issue a definitive HOLD vs LIQUIDATE risk advice.
    """
    if isinstance(payload_json, str):
        payload_text = payload_json
    else:
        payload_text = json.dumps(payload_json, indent=2, sort_keys=True)

    system_instruction = """
You are a Senior Institutional Financial Risk Officer overseeing active fund allocations.
Your job is to examine an open, active trading position that is facing price deviations and issue a definitive, customized situational response.

Core Rules:
1. Do not just look at the math stop-loss blindly. Cross-examine the technical indicators with the incoming raw news headlines.
2. If the stop-loss is breached, but the stock is deeply oversold (low RSI), the engine is in EXHAUSTION, or there is heavy buying interest/positive macro news present, explain why a structural recovery is probable and justify a strategic 'HOLD' cushion.
3. If the trend is fundamentally broken, macro events are deteriorating, and there is no institutional backing, issue an immediate 'LIQUIDATE' execution alert to save capital.
4. Keep your formatting razor-sharp: start with a clear, bold "GUARDIAN ACTION VERDICT" header, followed by a crisp contextual analysis paragraph, and a clear risk-mitigation bullet list.
""".strip()

    client = genai.Client()

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=[
            {
                "role": "user",
                "parts": [{"text": f"Analyze this active position risk matrix and output the evaluation:\n\n{payload_text}"}],
            }
        ],
        config=types.GenerateContentConfig(
            system_instruction=system_instruction,
            temperature=0.15,
            top_p=0.95
        )
    )
    return response.text