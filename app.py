import json
import streamlit as st

from llm_handler import generate_hunter_playbook, generate_guardian_verdict
from main import assemble_hunter_payload
from fetcher import get_stock_data, get_raw_news
from engine import classify_market_state

# ─────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="STRATA · Market Engine",
    page_icon="◉",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=IBM+Plex+Mono:ital,wght@0,300;0,400;0,500;0,600;1,300&display=swap');

/* ── GROUND ─────────────────────────────────────────────────────────────── */
html, body, [class*="css"], .stApp {
    background-color: #080C14 !important;
    color: #C8D4E8 !important;
    font-family: 'IBM Plex Mono', monospace !important;
}

/* Scanline texture */
.stApp::after {
    content: '';
    position: fixed;
    inset: 0;
    background-image: repeating-linear-gradient(
        0deg, transparent, transparent 2px,
        rgba(0, 240, 255, 0.011) 2px,
        rgba(0, 240, 255, 0.011) 4px
    );
    pointer-events: none;
    z-index: 9999;
}

/* Radial glow origin */
.stApp::before {
    content: '';
    position: fixed;
    top: -120px; left: -80px;
    width: 600px; height: 500px;
    background: radial-gradient(ellipse,
        rgba(0, 240, 255, 0.055) 0%,
        rgba(100, 60, 255, 0.035) 45%,
        transparent 70%);
    pointer-events: none;
    z-index: 0;
}

/* ── SIDEBAR — STYLED & NON-OVERLAPPING ──────────────────────────────────── */
/* Removing position: fixed !important; to let Streamlit calculate the left panel offsets naturally. */
[data-testid="stSidebar"] {
    background: #060A11 !important;
    border-right: 1px solid rgba(0, 240, 255, 0.14) !important;
    display: flex !important;
    flex-direction: column !important;
}

/* Inner sidebar content — clean scrollbars */
[data-testid="stSidebar"] > div:first-child {
    display: flex !important;
    flex-direction: column !important;
    padding-bottom: 0 !important;
}

/* Custom minimal scrollbar for sidebar panel */
[data-testid="stSidebar"]::-webkit-scrollbar { width: 3px; }
[data-testid="stSidebar"]::-webkit-scrollbar-thumb { background: rgba(0, 240, 255, 0.1); }

[data-testid="stSidebar"] * {
    font-family: 'IBM Plex Mono', monospace !important;
}

/* ── BRAND MARK ──────────────────────────────────────────────────────────── */
.brand-mark {
    font-family: 'Syne', sans-serif !important;
    font-size: 1.7rem;
    font-weight: 800;
    letter-spacing: 0.04em;
    color: #00F0FF;
    line-height: 1;
    margin-bottom: 4px;
}
.brand-sub {
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.62rem;
    font-weight: 500;
    letter-spacing: 0.26em;
    color: rgba(0, 240, 255, 0.55);
    text-transform: uppercase;
    margin-bottom: 26px;
}

/* ── SIDEBAR DIVIDER ─────────────────────────────────────────────────────── */
.rule-cyan {
    border: none;
    border-top: 1px solid rgba(0, 240, 255, 0.16);
    margin: 18px 0;
}

/* ── NAV RADIO ───────────────────────────────────────────────────────────── */
div[role="radiogroup"] label {
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.72rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.14em !important;
    color: rgba(200, 212, 232, 0.65) !important;
    text-transform: uppercase;
    padding: 10px 14px !important;
    border-radius: 2px !important;
    border-left: 2px solid transparent !important;
    transition: all 0.15s !important;
}
div[role="radiogroup"] label:hover {
    color: #00F0FF !important;
    background: rgba(0, 240, 255, 0.05) !important;
}
div[role="radiogroup"] label[data-checked="true"],
div[role="radiogroup"] label[aria-checked="true"] {
    color: #00F0FF !important;
    background: rgba(0, 240, 255, 0.08) !important;
    border-left: 2px solid #00F0FF !important;
}

/* ── SIDEBAR SECTION HEADING ─────────────────────────────────────────────── */
.sb-section-head {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.62rem;
    font-weight: 600;
    letter-spacing: 0.24em;
    color: rgba(0, 240, 255, 0.7);
    text-transform: uppercase;
    margin-bottom: 10px;
}

/* ── SIDEBAR SYMBOL GUIDE CARD ───────────────────────────────────────────── */
.sb-lookup {
    background: rgba(0, 240, 255, 0.04);
    border: 1px solid rgba(0, 240, 255, 0.14);
    border-radius: 2px;
    padding: 14px 16px;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.68rem;
    font-weight: 400;
    color: rgba(200, 212, 232, 0.72);
    line-height: 2;
}
.sb-lookup .sb-head {
    font-size: 0.6rem;
    font-weight: 600;
    letter-spacing: 0.22em;
    color: rgba(0, 240, 255, 0.65);
    text-transform: uppercase;
    margin-bottom: 8px;
}
.sb-lookup b {
    color: #00F0FF;
    font-weight: 600;
}

/* Sidebar version stamp */
.sb-version {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.58rem;
    font-weight: 500;
    letter-spacing: 0.18em;
    color: rgba(0, 240, 255, 0.32);
    text-transform: uppercase;
    margin-top: 24px;
}

/* ── SIDEBAR LINKS ───────────────────────────────────────────────────────── */
[data-testid="stSidebar"] a {
    color: #00F0FF !important;
    font-size: 0.72rem !important;
    font-weight: 500 !important;
    text-decoration: underline !important;
    text-underline-offset: 3px !important;
    text-decoration-color: rgba(0,240,255,0.35) !important;
}
[data-testid="stSidebar"] a:hover {
    text-decoration-color: #00F0FF !important;
}

/* ── PAGE HEADER ─────────────────────────────────────────────────────────── */
.pg-module {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.65rem;
    font-weight: 600;
    letter-spacing: 0.28em;
    color: rgba(0, 240, 255, 0.75);
    text-transform: uppercase;
    margin-bottom: 8px;
}
.pg-title {
    font-family: 'Syne', sans-serif;
    font-size: 3rem;
    font-weight: 800;
    letter-spacing: -0.03em;
    color: #E8F0FC;
    line-height: 1;
    margin-bottom: 8px;
}
.pg-desc {
    font-family: 'IBM Plex Mono', monospace;
    font-style: italic;
    font-size: 0.82rem;
    font-weight: 400;
    color: rgba(200, 212, 232, 0.58);
    margin-bottom: 36px;
    letter-spacing: 0.02em;
}

/* ── INPUTS ──────────────────────────────────────────────────────────────── */
input[type="text"], input[type="number"], .stTextInput input {
    background: #0C1220 !important;
    border: 1px solid rgba(0, 240, 255, 0.2) !important;
    border-radius: 2px !important;
    color: #E8F0FC !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.9rem !important;
    font-weight: 500 !important;
    padding: 10px 14px !important;
    transition: border-color 0.2s !important;
}
input:focus {
    border-color: #00F0FF !important;
    box-shadow: 0 0 0 2px rgba(0, 240, 255, 0.09) !important;
}
label[data-testid="stWidgetLabel"] {
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.63rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.2em !important;
    color: rgba(0, 240, 255, 0.65) !important;
    text-transform: uppercase !important;
}

/* ── PRIMARY BUTTON ──────────────────────────────────────────────────────── */
button[kind="primary"] {
    background: transparent !important;
    border: 1px solid #00F0FF !important;
    color: #00F0FF !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.72rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.2em !important;
    text-transform: uppercase !important;
    border-radius: 2px !important;
    padding: 12px 24px !important;
    transition: background 0.18s, color 0.18s !important;
}
button[kind="primary"]:hover {
    background: rgba(0, 240, 255, 0.1) !important;
    color: #ffffff !important;
}

/* ── DATA TILES ──────────────────────────────────────────────────────────── */
.dtile {
    background: #0C1220;
    border: 1px solid rgba(0, 240, 255, 0.12);
    border-radius: 2px;
    padding: 20px 22px;
    margin-bottom: 12px;
    position: relative;
}
/* Top-left corner bracket */
.dtile::before {
    content: '';
    position: absolute; top: -1px; left: -1px;
    width: 14px; height: 14px;
    border-top: 2px solid #00F0FF;
    border-left: 2px solid #00F0FF;
}
/* Bottom-right corner bracket */
.dtile::after {
    content: '';
    position: absolute; bottom: -1px; right: -1px;
    width: 14px; height: 14px;
    border-bottom: 2px solid rgba(0, 240, 255, 0.3);
    border-right: 2px solid rgba(0, 240, 255, 0.3);
}
.dtile-label {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.6rem;
    font-weight: 600;
    letter-spacing: 0.22em;
    color: rgba(0, 240, 255, 0.62);
    text-transform: uppercase;
    margin-bottom: 10px;
}
.dtile-value {
    font-family: 'Syne', sans-serif;
    font-size: 1.7rem;
    font-weight: 700;
    color: #F0F6FF;
    letter-spacing: -0.02em;
    line-height: 1;
}
.dtile-sub {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.66rem;
    font-weight: 400;
    color: rgba(200, 212, 232, 0.45);
    margin-top: 6px;
}

/* ── CLASSIC PIVOT LADDER STYLING ────────────────────────────────────────── */
.pivot-ladder {
    background: #0C1220;
    border: 1px solid rgba(0, 240, 255, 0.12);
    border-radius: 2px;
    padding: 22px;
    margin-bottom: 24px;
    position: relative;
}
.pivot-ladder::before {
    content: '';
    position: absolute; top: -1px; left: -1px;
    width: 14px; height: 14px;
    border-top: 2px solid #00F0FF;
    border-left: 2px solid #00F0FF;
}
.pivot-ladder-title {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.62rem;
    font-weight: 600;
    letter-spacing: 0.22em;
    color: rgba(0, 240, 255, 0.65);
    text-transform: uppercase;
    margin-bottom: 16px;
}
.pivot-row {
    display: flex;
    justify-content: space-between;
    padding: 6px 0;
    border-bottom: 1px solid rgba(200, 212, 232, 0.05);
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.76rem;
}
.pivot-row:last-child {
    border-bottom: none;
}
.pivot-pp {
    background: rgba(0, 240, 255, 0.06);
    padding: 6px 8px;
    border-radius: 1px;
    font-weight: 600;
}

/* ── STATE CHIPS ─────────────────────────────────────────────────────────── */
.chip {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 7px 16px 7px 12px;
    border-radius: 1px;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.7rem;
    font-weight: 600;
    letter-spacing: 0.14em;
    text-transform: uppercase;
}
.chip-momentum   { background: rgba(0,255,140,0.08);   color: #00FF8C; border: 1px solid rgba(0,255,140,0.3); }
.chip-exhaustion { background: rgba(255,185,0,0.08);   color: #FFB900; border: 1px solid rgba(255,185,0,0.3); }
.chip-falling    { background: rgba(255,60,80,0.08);   color: #FF3C50; border: 1px solid rgba(255,60,80,0.3); }
.chip-unknown    { background: rgba(200,212,232,0.05); color: rgba(200,212,232,0.6); border: 1px solid rgba(200,212,232,0.18); }

/* ── SECTION LABEL ───────────────────────────────────────────────────────── */
.sec-label {
    display: flex;
    align-items: center;
    gap: 12px;
    margin: 36px 0 18px 0;
}
.sec-label-text {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.63rem;
    font-weight: 600;
    letter-spacing: 0.28em;
    color: rgba(0, 240, 255, 0.72);
    text-transform: uppercase;
    white-space: nowrap;
}
.sec-label-line {
    flex: 1;
    height: 1px;
    background: linear-gradient(90deg, rgba(0,240,255,0.22) 0%, transparent 100%);
}

/* ── SPEC PANEL ──────────────────────────────────────────────────────────── */
.spec-panel {
    background: #0A0F1A;
    border: 1px solid rgba(0, 240, 255, 0.12);
    border-radius: 2px;
    padding: 20px 22px;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.74rem;
    font-weight: 400;
    color: rgba(200, 212, 232, 0.62);
    line-height: 2.1;
}
.spec-panel .spec-idx {
    color: #00F0FF;
    font-weight: 600;
    margin-right: 10px;
}
.spec-panel .spec-head {
    font-size: 0.6rem;
    font-weight: 600;
    letter-spacing: 0.24em;
    color: rgba(0, 240, 255, 0.6);
    text-transform: uppercase;
    border-bottom: 1px solid rgba(0, 240, 255, 0.12);
    padding-bottom: 8px;
    margin-bottom: 14px;
}

/* ── VERDICT STRIPS ──────────────────────────────────────────────────────── */
.vstrip-ok {
    border-left: 3px solid #00FF8C;
    background: rgba(0, 255, 140, 0.05);
    padding: 14px 18px;
    border-radius: 0 2px 2px 0;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.76rem;
    font-weight: 500;
    color: #00FF8C;
    letter-spacing: 0.06em;
    margin-bottom: 24px;
}
.vstrip-danger {
    border-left: 3px solid #FF3C50;
    background: rgba(255, 60, 80, 0.05);
    padding: 14px 18px;
    border-radius: 0 2px 2px 0;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.76rem;
    font-weight: 500;
    color: #FF3C50;
    letter-spacing: 0.06em;
    margin-bottom: 24px;
}

/* ── EXPANDERS ───────────────────────────────────────────────────────────── */
details {
    background: #090D18 !important;
    border: 1px solid rgba(0, 240, 255, 0.09) !important;
    border-radius: 2px !important;
    margin-top: 10px;
}
summary {
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.7rem !important;
    font-weight: 500 !important;
    letter-spacing: 0.12em !important;
    color: rgba(0, 240, 255, 0.62) !important;
    padding: 10px 16px !important;
}

/* ── TABS ────────────────────────────────────────────────────────────────── */
button[data-baseweb="tab"] {
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.67rem !important;
    font-weight: 500 !important;
    letter-spacing: 0.16em !important;
    text-transform: uppercase !important;
    color: rgba(200, 212, 232, 0.5) !important;
    background: transparent !important;
    border-bottom: 2px solid transparent !important;
    padding: 8px 20px !important;
}
button[data-baseweb="tab"][aria-selected="true"] {
    color: #00F0FF !important;
    font-weight: 600 !important;
    border-bottom: 2px solid #00F0FF !important;
}
[data-baseweb="tab-list"] {
    border-bottom: 1px solid rgba(0, 240, 255, 0.12) !important;
    gap: 0 !important;
    background: transparent !important;
}

/* ── STREAMLIT METRIC OVERRIDE ───────────────────────────────────────────── */
[data-testid="stMetric"] { background: transparent !important; border: none !important; padding: 0 !important; }
[data-testid="stMetricLabel"] {
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.6rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.2em !important;
    color: rgba(0, 240, 255, 0.62) !important;
    text-transform: uppercase !important;
}
[data-testid="stMetricValue"] {
    font-family: 'Syne', sans-serif !important;
    font-size: 1.5rem !important;
    font-weight: 700 !important;
    color: #F0F6FF !important;
}
[data-testid="stMetricDelta"] {
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.66rem !important;
    font-weight: 400 !important;
}

/* ── ALERTS ──────────────────────────────────────────────────────────────── */
[data-testid="stAlert"] {
    background: #0C1220 !important;
    border: 1px solid rgba(0, 240, 255, 0.14) !important;
    border-radius: 2px !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.76rem !important;
    font-weight: 400 !important;
    color: rgba(200, 212, 232, 0.72) !important;
}

/* ── CODE ────────────────────────────────────────────────────────────────── */
code, pre {
    font-family: 'IBM Plex Mono', monospace !important;
    background: #060A11 !important;
    border: 1px solid rgba(0, 240, 255, 0.09) !important;
    color: rgba(0, 240, 255, 0.75) !important;
    font-size: 0.72rem !important;
    border-radius: 2px !important;
}

/* ── SLIDER ──────────────────────────────────────────────────────────────── */
[data-testid="stSlider"] [role="slider"] {
    background: #00F0FF !important;
    border: 2px solid #00F0FF !important;
}

/* ── SCROLLBAR (main area only) ──────────────────────────────────────────── */
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: #080C14; }
::-webkit-scrollbar-thumb { background: rgba(0, 240, 255, 0.22); border-radius: 2px; }

/* ── FOOTER ──────────────────────────────────────────────────────────────── */
.pg-footer {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.58rem;
    font-weight: 500;
    letter-spacing: 0.2em;
    color: rgba(0, 240, 255, 0.25);
    text-transform: uppercase;
    text-align: center;
    padding: 48px 0 16px;
}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def _safe(v):
    return "—" if v is None else v


def _chip(state: str) -> str:
    s = str(state).upper()
    if "MOMENTUM"   in s: return '<span class="chip chip-momentum">▲ Momentum</span>'
    if "EXHAUSTION" in s: return '<span class="chip chip-exhaustion">◆ Exhaustion</span>'
    if "FALLING"    in s: return '<span class="chip chip-falling">▼ Falling</span>'
    return                       f'<span class="chip chip-unknown">● {s}</span>'


def _tile(label: str, value, sub: str = ""):
    sub_html = f'<div class="dtile-sub">{sub}</div>' if sub else ""
    st.markdown(
        f'<div class="dtile">'
        f'<div class="dtile-label">{label}</div>'
        f'<div class="dtile-value">{_safe(value)}</div>'
        f'{sub_html}'
        f'</div>',
        unsafe_allow_html=True,
    )


def _section(title: str):
    st.markdown(
        f'<div class="sec-label">'
        f'<span class="sec-label-text">{title}</span>'
        f'<span class="sec-label-line"></span>'
        f'</div>',
        unsafe_allow_html=True,
    )


# ─────────────────────────────────────────────────────────────────────────────
# TECHNICAL DASHBOARD
# ─────────────────────────────────────────────────────────────────────────────
def _display_technical_dashboard(metrics: dict):
    if not metrics:
        st.warning("No technical indicators loaded for this asset.")
        return

    _section("Market Metrics")
    c1, c2, c3, c4 = st.columns(4)
    with c1: _tile("Latest Close",  metrics.get("close"))
    with c2: _tile("RSI (14)",       metrics.get("rsi"),   "Relative strength")
    with c3: _tile("ATR (14)",       metrics.get("atr"),   "Avg true range")
    with c4: _tile("MACD",          metrics.get("macd"),  "Momentum")

    _section("Volume Indicators")
    v1, v2 = st.columns(2)
    with v1: 
        _tile("Daily Volume", f"{metrics.get('volume', 0):,}" if metrics.get("volume") else "—", "Shares traded today")
    with v2:
        rvol = metrics.get("rvol")
        rvol_desc = "Low Participation"
        if rvol and rvol >= 2.0:
            rvol_desc = "⚡ Heavy Breakout Volume"
        elif rvol and rvol >= 1.0:
            rvol_desc = "Steady Participation"
        _tile("Relative Volume (RVOL)", rvol, f"Volume vs 20D SMA · {rvol_desc}")

    _section("Moving Averages & Daily Supports")
    # Placing the EMA cards on the left, and the color-coded Pivot Ladder on the right
    col_tech, col_ladder = st.columns([5, 5], gap="large")
    
    with col_tech:
        st.markdown("<div style='margin-bottom:12px;'><b>Exponential Moving Averages</b></div>", unsafe_allow_html=True)
        _tile("EMA 20",  metrics.get("ema20"),  "Short-term momentum")
        _tile("EMA 50",  metrics.get("ema50"),  "Medium-term trend")
        _tile("EMA 200", metrics.get("ema200"), "Primary systemic support")

    with col_ladder:
        st.markdown(
            f'<div class="pivot-ladder">'
            f'<div class="pivot-ladder-title">Classic Daily Pivot Point Ladder</div>'
            f'<div class="pivot-row" style="color: #FF3C50; font-weight: 600;"><span>Resistance 3 (R3)</span><span>{_safe(metrics.get("r3"))}</span></div>'
            f'<div class="pivot-row" style="color: #FF3C50; opacity: 0.85;"><span>Resistance 2 (R2)</span><span>{_safe(metrics.get("r2"))}</span></div>'
            f'<div class="pivot-row" style="color: #FF3C50; opacity: 0.70;"><span>Resistance 1 (R1)</span><span>{_safe(metrics.get("r1"))}</span></div>'
            f'<div class="pivot-row pivot-pp" style="color: #00F0FF;"><span>Central Pivot (PP)</span><span>{_safe(metrics.get("pivot"))}</span></div>'
            f'<div class="pivot-row" style="color: #00FF8C; opacity: 0.70;"><span>Support 1 (S1)</span><span>{_safe(metrics.get("s1"))}</span></div>'
            f'<div class="pivot-row" style="color: #00FF8C; opacity: 0.85;"><span>Support 2 (S2)</span><span>{_safe(metrics.get("s2"))}</span></div>'
            f'<div class="pivot-row" style="color: #00FF8C; font-weight: 600;"><span>Support 3 (S3)</span><span>{_safe(metrics.get("s3"))}</span></div>'
            f'</div>',
            unsafe_allow_html=True
        )


# ─────────────────────────────────────────────────────────────────────────────
# NEWS INTELLIGENCE
# ─────────────────────────────────────────────────────────────────────────────
def _display_news_intelligence(news_items: list):
    if not news_items:
        st.info("No contextual headlines available.")
        return

    ticker_news = [n for n in news_items if "TICKER_SPECIFIC" in n.get("summary", "")]
    macro_news  = [n for n in news_items if "GLOBAL_MACRO"    in n.get("summary", "")]
    if not ticker_news and not macro_news:
        ticker_news, macro_news = news_items[:3], news_items[3:]

    tab1, tab2 = st.tabs(["TICKER CATALYSTS", "MACRO ENVIRONMENT"])
    with tab1:
        if ticker_news:
            for art in ticker_news:
                with st.expander(f"→  {art.get('title', 'Untitled')}"):
                    st.caption(f"SOURCE · {art.get('publisher', 'Financial Feed')}")
                    st.write(art.get("summary", ""))
        else:
            st.caption("No company-specific catalysts found.")
    with tab2:
        if macro_news:
            for art in macro_news:
                with st.expander(f"→  {art.get('title', 'Untitled')}"):
                    st.caption(f"SOURCE · {art.get('publisher', 'Macro Feed')}")
                    st.write(art.get("summary", ""))
        else:
            st.caption("No macro indicators found.")


# ─────────────────────────────────────────────────────────────────────────────
# HUNTER MODE
# ─────────────────────────────────────────────────────────────────────────────
def _run_hunter_mode():
    st.markdown('<div class="pg-module">◉ Module Alpha</div>', unsafe_allow_html=True)
    st.markdown('<div class="pg-title">Hunter Engine</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="pg-desc">Quantitative state classification · momentum & '
        'mean-reversion zone discovery.</div>',
        unsafe_allow_html=True,
    )

    col_L, col_R = st.columns([4, 6], gap="large")
    with col_L:
        symbol = st.text_input(
            "Target Symbol", value="PNB.NS",
            placeholder="PNB.NS · TSLA · RELIANCE.NS",
        ).strip().upper()
        run_btn = st.button("Initialize Discovery Loop ▶", type="primary", use_container_width=True)

    with col_R:
        st.markdown(
            '<div class="spec-panel">'
            '<div class="spec-head">System Architecture</div>'
            '<span class="spec-idx">01</span>Autonomous state classification via technical indices<br>'
            '<span class="spec-idx">02</span>Multi-tier news ingestion · company + macro signals<br>'
            '<span class="spec-idx">03</span>Playbook synthesis via Gemini reasoning layer'
            '</div>',
            unsafe_allow_html=True,
        )

    if not run_btn:
        st.markdown('<hr class="rule-cyan">', unsafe_allow_html=True)
        st.info("Enter a ticker symbol and click  Initialize Discovery Loop.")
        return

    if not symbol:
        st.error("A valid ticker symbol is required.")
        return

    with st.spinner(f"Compiling payload for {symbol} …"):
        payload = assemble_hunter_payload(symbol)

    engine_outputs    = payload.get("engine_outputs", {})
    technical_metrics = payload.get("technical_metrics", {})
    news_items        = payload.get("unstructured_news", [])
    state             = engine_outputs.get("state", "UNKNOWN")
    score             = engine_outputs.get("score", "N/A")

    _section("Engine Snapshot")
    s1, s2 = st.columns(2)
    with s1:
        st.markdown(
            f'<div class="dtile">'
            f'<div class="dtile-label">Classified Market State</div>'
            f'<div style="margin-top:8px;">{_chip(state)}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
    with s2:
        _tile("Conviction Score", score, "Out of 10.0")

    _display_technical_dashboard(technical_metrics)

    _section("Contextual Intelligence Stream")
    _display_news_intelligence(news_items)

    with st.expander("◉  Raw JSON Payload"):
        st.code(json.dumps(payload, indent=2), language="json")

    _section("Tactical Playbook · Gemini Synthesis")
    with st.spinner("Streaming playbook …"):
        try:
            st.markdown(generate_hunter_playbook(payload))
        except Exception as exc:
            st.error(f"Playbook generation error: {exc}")
            st.caption("Verify GEMINI_API_KEY or retry if congested.")

    st.markdown(
        '<div class="pg-footer">STRATA · Market Intelligence Engine · Portfolio Edition v2.5</div>',
        unsafe_allow_html=True,
    )


# ─────────────────────────────────────────────────────────────────────────────
# GUARDIAN MODE
# ─────────────────────────────────────────────────────────────────────────────
def _run_guardian_mode():
    st.markdown('<div class="pg-module">◉ Module Beta</div>', unsafe_allow_html=True)
    st.markdown('<div class="pg-title">Guardian Shield</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="pg-desc">Active position defense · deviation tracking · '
        'contextual hold / liquidate evaluation.</div>',
        unsafe_allow_html=True,
    )

    col_L, col_R = st.columns([4, 6], gap="large")
    with col_L:
        g_symbol      = st.text_input("Active Asset Ticker", value="PNB.NS").strip().upper()
        entry_price   = st.number_input("Entry Purchase Price", min_value=0.01, value=105.0, step=0.1)
        risk_profile  = st.slider("Stop-Loss Buffer (%)", min_value=0.5, max_value=5.0, value=2.0, step=0.5)
        position_size = st.number_input("Shares Held", min_value=1, value=500, step=1)
        run_btn       = st.button("Activate Guardian Scan ▶", type="primary", use_container_width=True)

    with col_R:
        st.markdown(
            '<div class="spec-panel">'
            '<div class="spec-head">Defense Protocol</div>'
            '<span class="spec-idx">01</span>Real-time deviation tracking vs. entry average<br>'
            '<span class="spec-idx">02</span>Precise mathematical stop-loss boundary<br>'
            '<span class="spec-idx">03</span>Technical + news sentiment cross-examination<br>'
            '<span class="spec-idx">04</span>Strategic HOLD vs. LIQUIDATE risk verdict'
            '</div>',
            unsafe_allow_html=True,
        )

    if not run_btn:
        st.markdown('<hr class="rule-cyan">', unsafe_allow_html=True)
        st.info("Configure position parameters and click  Activate Guardian Scan.")
        return

    with st.spinner(f"Acquiring live matrices for {g_symbol} …"):
        current_data = get_stock_data(g_symbol)
        raw_news     = get_raw_news(g_symbol)

    if not current_data or current_data.get("close") is None:
        st.error(f"Could not retrieve live data for {g_symbol}. Verify the symbol.")
        return

    engine_outputs  = classify_market_state(current_data)
    live_close      = current_data["close"]
    pnl_ps          = live_close - entry_price
    total_pnl       = pnl_ps * position_size
    pnl_pct         = (pnl_ps / entry_price) * 100
    hard_stop       = round(entry_price * (1 - risk_profile / 100), 2)
    capital_at_risk = round((entry_price - hard_stop) * position_size, 2)
    stop_breached   = live_close <= hard_stop

    _section("Position Matrix")
    c1, c2, c3 = st.columns(3)
    with c1: _tile("Live Price",      live_close,          f"{round(live_close - entry_price, 2):+.2f} from entry")
    with c2: _tile("Unrealized P&L",  f"{total_pnl:+.2f}", f"{pnl_pct:+.2f}%")
    with c3: _tile("Hard Stop Level", hard_stop,           f"−{risk_profile}% buffer")

    if stop_breached:
        st.markdown(
            '<div class="vstrip-danger">⚠  BOUNDARY BREACHED — Evaluating contextual cushions …</div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<div class="vstrip-ok">✓  RISK BUFFER NOMINAL — Within acceptable safety parameters.</div>',
            unsafe_allow_html=True,
        )

    # Display Pivot Points inside Guardian Mode as well so the user can see support buffers visually
    st.markdown("<div style='margin-top:20px;'></div>", unsafe_allow_html=True)
    _display_technical_dashboard(current_data)

    guardian_payload = {
        "position_meta": {
            "ticker": g_symbol, "entry_price": entry_price,
            "quantity": position_size, "risk_allowance_percent": risk_profile,
        },
        "math_boundaries": {
            "live_close": live_close,
            "unrealized_pnl_total": round(total_pnl, 2),
            "unrealized_pnl_percent": round(pnl_pct, 2),
            "mathematical_stop_breached": stop_breached,
        },
        "technical_metrics": current_data,
        "engine_state": engine_outputs,
        "unstructured_news": raw_news,
    }

    _section("Risk Officer Audit · Contextual Intelligence")
    with st.spinner("Compiling audit …"):
        try:
            st.markdown(generate_guardian_verdict(guardian_payload))
        except Exception as e:
            st.error(f"Audit engine unreachable: {e}")

    with st.expander("◉  Mathematical Risk Parameters"):
        p1, p2 = st.columns(2)
        with p1:
            st.write(f"**Capital at Risk:** `{capital_at_risk}`")
            st.write(f"**Stop Calculation:** `Entry × (1 − {risk_profile}%)`")
        with p2:
            st.write(f"**ATR:** `{current_data.get('atr', '—')}`")
            st.write(f"**State Signal:** `{engine_outputs.get('state', 'UNKNOWN')}`")

    st.markdown(
        '<div class="pg-footer">STRATA · Market Intelligence Engine · Portfolio Edition v2.5</div>',
        unsafe_allow_html=True,
    )


# ─────────────────────────────────────────────────────────────────────────────
# MAIN  ·  SIDEBAR + ROUTING
# ─────────────────────────────────────────────────────────────────────────────
def main():
    with st.sidebar:
        # Brand
        st.markdown(
            '<div class="brand-mark">STRATA</div>'
            '<div class="brand-sub">Market Intelligence Engine</div>',
            unsafe_allow_html=True,
        )
        st.markdown('<hr class="rule-cyan">', unsafe_allow_html=True)

        # Mode selector
        selected_mode = st.radio(
            "Mode", ["Hunter Mode", "Guardian Mode"],
            label_visibility="collapsed",
        )

        st.markdown('<hr class="rule-cyan">', unsafe_allow_html=True)

        # Ticker directory
        st.markdown(
            '<div class="sb-section-head">Ticker Directory</div>',
            unsafe_allow_html=True,
        )
        st.markdown("[⬡ Yahoo Finance Lookup](https://finance.yahoo.com/lookup)")

        st.markdown('<hr class="rule-cyan">', unsafe_allow_html=True)

        # Symbol guide
        st.markdown(
            '<div class="sb-lookup">'
            '<div class="sb-head">Symbol Guide</div>'
            '<b>Indian Exchanges</b> → append .NS<br>'
            'PNB.NS · RELIANCE.NS · TCS.NS<br><br>'
            '<b>US Markets</b> → standard code<br>'
            'TSLA · AAPL · NVDA'
            '</div>',
            unsafe_allow_html=True,
        )

        # Version stamp — pinned to bottom feel via margin-top
        st.markdown(
            '<div class="sb-version">v2.5 · Portfolio Edition</div>',
            unsafe_allow_html=True,
        )

    if selected_mode == "Hunter Mode":
        _run_hunter_mode()
    else:
        _run_guardian_mode()


if __name__ == "__main__":
    main()