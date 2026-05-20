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
- Incorporate the computed daily Pivot Points (PP), Resistance levels (R1, R2, R3), and Support levels (S1, S2, S3) into your trade setup targets, entry triggers, and key support/resistance zones.
- Explicitly emphasize risk management parameters before outlining trade execution steps.
- This is decision-support analysis, not financial advice.

STRICT TYPOGRAPHY & TEXT RULES:
1. When describing math formulas in plain text sentences, use normal text and regular words.
2. Never combine math operators (+, -, *, =, /) sequentially inside standard paragraphs.
3. Never repeat variable lines back-to-back.
4. For the final calculation example, write it on its own isolated line using explicit LaTeX block math.

EXECUTIVE SUMMARY BOX RULE:
At the very end of your response, you MUST generate a clean Markdown executive summary box using this exact structure:

---

### 📊 EXECUTIVE TRADE SUMMARY

| Metric | Final Assessment |
|---|---|
| Trade Bias | [Bullish / Bearish / Neutral] |
| Risk Grade | [Low / Medium / High] |
| Entry Quality | [Strong / Moderate / Weak] |
| News Sentiment | [Positive / Mixed / Negative] |
| Tactical Action | [Execute / Wait / Avoid] |

---

Do not skip this section.
""".strip()

    user_prompt = f"""
Process this hunter payload precisely and return the structured playbook with the final strategy summary index. Ensure the playbook clearly references the Daily Pivot Levels (PP, R1, R2, R3, S1, S2, S3) for concrete validation targets.

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

1. Do not just look at the math stop-loss blindly.
Cross-examine the technical indicators with the incoming raw news headlines.

2. Check if the asset's current close price is trading near, testing, or consolidating at major support floors (S1, S2, S3). 
If the math stop-loss is breached, but the stock is holding above a key historical S1/S2/S3 level, is deeply oversold (low RSI), or the engine is in EXHAUSTION, justify a strategic HOLD to allow the asset to test this technical floor before initiating liquidation.

3. If the trend is fundamentally broken, price breaches major support floors (S3) with high-conviction momentum, macro events are deteriorating, and there is no institutional backing, issue an immediate LIQUIDATE execution alert.

4. Keep formatting razor-sharp:
- Start with a bold "GUARDIAN ACTION VERDICT" header
- Follow with concise contextual analysis
- End with a clean risk-mitigation bullet section

EXECUTIVE VERDICT BOX RULE:
At the very end of your output, you MUST generate this exact Markdown summary box:

---

### 📊 EXECUTIVE DECISION SHIELD

| Category | Final Verdict |
|---|---|
| Position Status | [HOLD / LIQUIDATE] |
| Technical Condition | [Stable / Weak / Broken] |
| Momentum State | [Strong / Neutral / Exhausted] |
| News Environment | [Supportive / Mixed / Deteriorating] |
| Institutional Confidence | [High / Moderate / Low] |
| Risk Escalation | [Low / Medium / Severe] |

---

Do not skip this section.
""".strip()

    client = genai.Client()

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=[
            {
                "role": "user",
                "parts": [
                    {
                        "text": (
                            "Analyze this active position risk matrix "
                            f"and output the evaluation:\n\n{payload_text}"
                        )
                    }
                ],
            }
        ],
        config=types.GenerateContentConfig(
            system_instruction=system_instruction,
            temperature=0.15,
            top_p=0.95
        )
    )

    return response.text