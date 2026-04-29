"""
Trading Chart Pro v4 — Bodzilla IA
────────────────────────────────────
- Datos 100% via yfinance (funciona en Railway/cloud)
- API key SOLO desde variable de entorno ANTHROPIC_API_KEY
- Todos los activos: crypto, forex, stocks, commodities
- Chat interactivo que controla el chart

Instalar:  pip install streamlit anthropic yfinance pandas numpy
Correr:    streamlit run trading_chart_pro.py
"""
import streamlit as st
import anthropic
import yfinance as yf
import pandas as pd
import numpy as np
import json
import os
from datetime import datetime

st.set_page_config(
    page_title="Trading Chart Pro — Bodzilla IA",
    page_icon="📊", layout="wide",
    initial_sidebar_state="expanded"
)

# ── API KEY: SOLO desde variable de entorno ──────────────────────────────────
# En Railway: configurar ANTHROPIC_API_KEY en Variables
# Nunca se muestra ni pide al usuario
API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")

C = {
    "bg":"#080c10","bg2":"#0d1117","bg3":"#131b24","bg4":"#1a2535",
    "green":"#00d084","orange":"#ff7b00","blue":"#00aaff","red":"#ef4444",
    "text":"#d4e6f1","muted":"#4a6278","border":"#1e2d3d",
}

# ── ACTIVOS — todos via yfinance ─────────────────────────────────────────────
ASSETS = {
    "🪙 Crypto": [
        {"label":"BTC/USDT",  "yf":"BTC-USD"},
        {"label":"ETH/USDT",  "yf":"ETH-USD"},
        {"label":"SOL/USDT",  "yf":"SOL-USD"},
        {"label":"BNB/USDT",  "yf":"BNB-USD"},
        {"label":"XRP/USDT",  "yf":"XRP-USD"},
        {"label":"DOGE/USDT", "yf":"DOGE-USD"},
        {"label":"ADA/USDT",  "yf":"ADA-USD"},
        {"label":"AVAX/USDT", "yf":"AVAX-USD"},
        {"label":"LINK/USDT", "yf":"LINK-USD"},
        {"label":"DOT/USDT",  "yf":"DOT-USD"},
        {"label":"MATIC",     "yf":"MATIC-USD"},
        {"label":"LTC/USDT",  "yf":"LTC-USD"},
        {"label":"UNI/USDT",  "yf":"UNI-USD"},
        {"label":"ATOM/USDT", "yf":"ATOM-USD"},
        {"label":"FIL/USDT",  "yf":"FIL-USD"},
    ],
    "💱 Forex / Metales": [
        {"label":"XAUUSD",  "yf":"GC=F"},
        {"label":"XAGUSD",  "yf":"SI=F"},
        {"label":"EURUSD",  "yf":"EURUSD=X"},
        {"label":"GBPUSD",  "yf":"GBPUSD=X"},
        {"label":"USDJPY",  "yf":"USDJPY=X"},
        {"label":"AUDUSD",  "yf":"AUDUSD=X"},
        {"label":"USDCAD",  "yf":"USDCAD=X"},
        {"label":"USDCHF",  "yf":"USDCHF=X"},
        {"label":"NZDUSD",  "yf":"NZDUSD=X"},
        {"label":"USDMXN",  "yf":"USDMXN=X"},
        {"label":"USDCOP",  "yf":"USDCOP=X"},
        {"label":"PLATINUM","yf":"PL=F"},
        {"label":"PALLADIUM","yf":"PA=F"},
    ],
    "📈 Stocks USA": [
        {"label":"SPY",   "yf":"SPY"},
        {"label":"QQQ",   "yf":"QQQ"},
        {"label":"IWM",   "yf":"IWM"},
        {"label":"AAPL",  "yf":"AAPL"},
        {"label":"MSFT",  "yf":"MSFT"},
        {"label":"GOOGL", "yf":"GOOGL"},
        {"label":"AMZN",  "yf":"AMZN"},
        {"label":"NVDA",  "yf":"NVDA"},
        {"label":"TSLA",  "yf":"TSLA"},
        {"label":"META",  "yf":"META"},
        {"label":"NFLX",  "yf":"NFLX"},
        {"label":"AMD",   "yf":"AMD"},
        {"label":"COIN",  "yf":"COIN"},
        {"label":"MSTR",  "yf":"MSTR"},
        {"label":"PLTR",  "yf":"PLTR"},
    ],
    "🌍 Índices": [
        {"label":"S&P 500",  "yf":"^GSPC"},
        {"label":"NASDAQ",   "yf":"^IXIC"},
        {"label":"DOW",      "yf":"^DJI"},
        {"label":"DAX",      "yf":"^GDAXI"},
        {"label":"FTSE 100", "yf":"^FTSE"},
        {"label":"Nikkei",   "yf":"^N225"},
        {"label":"VIX",      "yf":"^VIX"},
        {"label":"COLCAP",   "yf":"^COLCAP"},
    ],
    "🛢️ Commodities": [
        {"label":"Crude Oil WTI", "yf":"CL=F"},
        {"label":"Brent Oil",     "yf":"BZ=F"},
        {"label":"Nat. Gas",      "yf":"NG=F"},
        {"label":"Copper",        "yf":"HG=F"},
        {"label":"Wheat",         "yf":"ZW=F"},
        {"label":"Corn",          "yf":"ZC=F"},
        {"label":"Soybean",       "yf":"ZS=F"},
        {"label":"Coffee",        "yf":"KC=F"},
        {"label":"Sugar",         "yf":"SB=F"},
        {"label":"Cotton",        "yf":"CT=F"},
    ],
}

TIMEFRAMES = {
    "5m":  {"yf_interval":"5m",  "yf_period":"5d"},
    "15m": {"yf_interval":"15m", "yf_period":"5d"},
    "1h":  {"yf_interval":"1h",  "yf_period":"30d"},
    "4h":  {"yf_interval":"1h",  "yf_period":"60d"},   # yfinance no tiene 4h nativo, usamos 1h y agrupamos
    "1D":  {"yf_interval":"1d",  "yf_period":"365d"},
    "1W":  {"yf_interval":"1wk", "yf_period":"1000d"},
}

# ── CSS ───────────────────────────────────────────────────────────────────────
def inject_css():
    st.markdown(f"""<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Syne:wght@400;700;800&display=swap');
html,body,[class*="css"]{{background:{C['bg']} !important;color:{C['text']} !important;font-family:'Space Mono',monospace !important;}}
h1,h2,h3{{font-family:'Syne',sans-serif !important;color:{C['green']} !important;}}
[data-testid="stMetricValue"]{{font-family:'Space Mono',monospace !important;font-size:1.05rem !important;color:{C['blue']} !important;}}
[data-testid="stMetricLabel"]{{font-family:'Space Mono',monospace !important;color:{C['muted']} !important;font-size:0.62rem !important;text-transform:uppercase;}}
[data-testid="stMetricDelta"]{{font-size:0.68rem !important;}}
[data-testid="stSidebar"]{{background:{C['bg2']} !important;border-right:1px solid {C['border']} !important;}}
[data-testid="stExpander"]{{background:{C['bg2']} !important;border:1px solid {C['border']} !important;border-radius:5px !important;}}
summary{{color:{C['text']} !important;font-size:0.73rem !important;}}
.stTabs [data-baseweb="tab"]{{background:{C['bg3']} !important;color:{C['muted']} !important;border-radius:5px 5px 0 0 !important;font-size:0.73rem !important;}}
.stTabs [aria-selected="true"]{{background:{C['bg4']} !important;color:{C['orange']} !important;border-top:2px solid {C['orange']} !important;}}
div[data-baseweb="select"]>div{{background:{C['bg3']} !important;border-color:{C['border']} !important;color:{C['text']} !important;font-size:0.76rem !important;}}
ul[data-baseweb="menu"]{{background:{C['bg3']} !important;}}
li[role="option"]{{color:{C['text']} !important;font-size:0.73rem !important;}}
li[role="option"]:hover{{background:{C['bg4']} !important;}}
.stButton>button{{background:{C['bg3']} !important;color:{C['text']} !important;border:1px solid {C['border']} !important;border-radius:4px !important;font-family:'Space Mono',monospace !important;font-size:0.68rem !important;padding:3px 7px !important;}}
.stButton>button:hover{{border-color:{C['blue']} !important;color:{C['blue']} !important;}}
[data-testid="baseButton-primary"]{{border-color:{C['green']} !important;color:{C['green']} !important;}}
::-webkit-scrollbar{{width:3px;}}::-webkit-scrollbar-track{{background:{C['bg']};}}::-webkit-scrollbar-thumb{{background:{C['bg4']};border-radius:2px;}}
.block-container{{padding-top:0.6rem !important;padding-bottom:0.2rem !important;}}
</style>""", unsafe_allow_html=True)

# ── Fetch OHLCV via yfinance ──────────────────────────────────────────────────
@st.cache_data(ttl=300, show_spinner=False)
def fetch_ohlcv(label, yf_sym, tf):
    cfg = TIMEFRAMES[tf]
    try:
        t = yf.Ticker(yf_sym)
        df = t.history(period=cfg["yf_period"], interval=cfg["yf_interval"])
        if df.empty:
            return pd.DataFrame()
        df = df[["Open","High","Low","Close","Volume"]]
        # Normalizar timezone
        if df.index.tz is None:
            df.index = df.index.tz_localize("UTC")
        else:
            df.index = df.index.tz_convert("UTC")
        # Para 4h: agrupar velas 1h en bloques de 4
        if tf == "4h":
            df = df.resample("4h").agg({
                "Open":"first","High":"max","Low":"min",
                "Close":"last","Volume":"sum"
            }).dropna()
        df = df.dropna()
        df = df[~df.index.duplicated(keep="last")].sort_index()
        # Filtrar velas con precios cero o negativos
        df = df[(df["Close"] > 0) & (df["High"] > 0) & (df["Low"] > 0)]
        return df
    except Exception as e:
        return pd.DataFrame()

# ── Indicadores ───────────────────────────────────────────────────────────────
def calculate_indicators(df):
    if df.empty or len(df) < 20:
        return {}
    ind = {}
    # EMAs
    for p in [10, 55, 200]:
        ind[f"ema{p}"] = df["Close"].ewm(span=p, adjust=False).mean().round(8).tolist()
    # RSI
    delta = df["Close"].diff()
    gain  = delta.clip(lower=0).rolling(14).mean()
    loss  = (-delta.clip(upper=0)).rolling(14).mean()
    rsi   = 100 - (100 / (1 + gain / loss.replace(0, np.nan)))
    ind["rsi"]     = rsi.fillna(50).round(3).tolist()
    ind["rsi_cur"] = round(float(rsi.iloc[-1]), 1) if not np.isnan(rsi.iloc[-1]) else 50
    # ATR
    tr  = pd.concat([df["High"]-df["Low"],
                     (df["High"]-df["Close"].shift()).abs(),
                     (df["Low"] -df["Close"].shift()).abs()], axis=1).max(axis=1)
    atr = tr.rolling(14).mean()
    ind["atr"]     = atr.fillna(0).round(8).tolist()
    ind["atr_cur"] = float(atr.iloc[-1]) if not np.isnan(atr.iloc[-1]) else 0
    # ADX
    up   = df["High"].diff()
    down = -df["Low"].diff()
    pdm  = up.where((up > down) & (up > 0), 0).rolling(14).mean()
    ndm  = down.where((down > up) & (down > 0), 0).rolling(14).mean()
    atr14 = atr.rolling(14).mean()
    pdi  = 100 * pdm / atr14.replace(0, np.nan)
    ndi  = 100 * ndm / atr14.replace(0, np.nan)
    dx   = 100 * (pdi-ndi).abs() / (pdi+ndi).replace(0, np.nan)
    adx  = dx.rolling(14).mean()
    ind["adx_cur"] = round(float(adx.iloc[-1]), 1) if not np.isnan(adx.iloc[-1]) else 0
    ind["pdi_cur"] = round(float(pdi.iloc[-1]),  1) if not np.isnan(pdi.iloc[-1]) else 0
    ind["ndi_cur"] = round(float(ndi.iloc[-1]),  1) if not np.isnan(ndi.iloc[-1]) else 0
    # MACD
    ema12 = df["Close"].ewm(span=12, adjust=False).mean()
    ema26 = df["Close"].ewm(span=26, adjust=False).mean()
    macd  = ema12 - ema26
    sig   = macd.ewm(span=9, adjust=False).mean()
    ind["macd"]        = macd.round(8).tolist()
    ind["macd_signal"] = sig.round(8).tolist()
    ind["macd_cur"]    = round(float(macd.iloc[-1]), 6)
    # Bollinger
    bb_mid = df["Close"].rolling(20).mean()
    bb_std = df["Close"].rolling(20).std()
    ind["bb_upper"] = (bb_mid + 2*bb_std).round(8).tolist()
    ind["bb_lower"] = (bb_mid - 2*bb_std).round(8).tolist()
    ind["bb_mid"]   = bb_mid.round(8).tolist()
    # VWAP
    tp   = (df["High"] + df["Low"] + df["Close"]) / 3
    vwap = (tp * df["Volume"]).cumsum() / df["Volume"].cumsum()
    ind["vwap"] = vwap.round(8).tolist()
    # Squeeze
    kc_up  = bb_mid + 1.5*atr
    kc_lo  = bb_mid - 1.5*atr
    sqz_on  = ((bb_mid-2*bb_std) > kc_lo) & ((bb_mid+2*bb_std) < kc_up)
    sqz_off = ((bb_mid-2*bb_std) < kc_lo) & ((bb_mid+2*bb_std) > kc_up)
    ind["sqz_cur"] = "ON 🔴" if bool(sqz_on.iloc[-1]) else ("OFF 🟢" if bool(sqz_off.iloc[-1]) else "NEUTRAL")
    # OBs
    obs_bull, obs_bear = [], []
    lb = min(50, len(df)-2)
    for i in range(lb, len(df)-1):
        if df["Close"].iloc[i] < df["Open"].iloc[i]:
            fut = df.iloc[i+1:i+lb]
            mp  = df["High"].iloc[max(0,i-lb):i].max()
            if not fut.empty and (fut["Close"] > mp).any():
                obs_bull.append({"top":round(float(df["Open"].iloc[i]),8),
                                 "bot":round(float(df["Low"].iloc[i]), 8)})
        if df["Close"].iloc[i] > df["Open"].iloc[i]:
            fut = df.iloc[i+1:i+lb]
            mp  = df["Low"].iloc[max(0,i-lb):i].min()
            if not fut.empty and (fut["Close"] < mp).any():
                obs_bear.append({"top":round(float(df["High"].iloc[i]),8),
                                 "bot":round(float(df["Open"].iloc[i]),8)})
    ind["ob_bull"] = obs_bull[-3:]
    ind["ob_bear"] = obs_bear[-3:]
    # FVG
    fvg_bull, fvg_bear = [], []
    for i in range(2, len(df)):
        gb = df["Low"].iloc[i]   - df["High"].iloc[i-2]
        gs = df["Low"].iloc[i-2] - df["High"].iloc[i]
        av = ind["atr"][i] if i < len(ind["atr"]) else 0
        if gb > 0 and gb > av*0.3:
            fvg_bull.append({"top":round(float(df["Low"].iloc[i]),  8),
                             "bot":round(float(df["High"].iloc[i-2]),8)})
        if gs > 0 and gs > av*0.3:
            fvg_bear.append({"top":round(float(df["Low"].iloc[i-2]),8),
                             "bot":round(float(df["High"].iloc[i]),  8)})
    ind["fvg_bull"] = fvg_bull[-5:]
    ind["fvg_bear"] = fvg_bear[-5:]
    # Swing levels
    recent = df.tail(60)
    sh = recent["High"].rolling(5, center=True).max()
    sl = recent["Low"].rolling(5,  center=True).min()
    ind["swing_highs"] = sorted(set(round(float(v),8) for v in sh.dropna().tail(5)))
    ind["swing_lows"]  = sorted(set(round(float(v),8) for v in sl.dropna().tail(5)))
    # Fibonacci
    h = float(df["High"].tail(50).max())
    l = float(df["Low"].tail(50).min())
    ind["fib_high"]   = round(h, 8)
    ind["fib_low"]    = round(l, 8)
    ind["fib_levels"] = {str(lvl): round(h-(h-l)*lvl, 8)
                         for lvl in [0, 0.236, 0.382, 0.5, 0.618, 0.786, 1.0]}
    # Trendline points
    sh_pts = [(int(df.index[i].timestamp()), round(float(df["High"].iloc[i]),8))
              for i in range(len(df))
              if not np.isnan(df["High"].rolling(10, center=True).max().iloc[i])
              and df["High"].iloc[i] == df["High"].rolling(10, center=True).max().iloc[i]][-3:]
    sl_pts = [(int(df.index[i].timestamp()), round(float(df["Low"].iloc[i]),8))
              for i in range(len(df))
              if not np.isnan(df["Low"].rolling(10, center=True).min().iloc[i])
              and df["Low"].iloc[i] == df["Low"].rolling(10, center=True).min().iloc[i]][-3:]
    ind["tl_highs"] = sh_pts
    ind["tl_lows"]  = sl_pts
    # Price
    ind["price"]  = round(float(df["Close"].iloc[-1]), 8)
    ind["change"] = round(float((df["Close"].iloc[-1]/df["Close"].iloc[-2]-1)*100), 2)
    ind["high24"] = round(float(df["High"].tail(24).max()), 8)
    ind["low24"]  = round(float(df["Low"].tail(24).min()),  8)
    return ind

# ── System Prompt ─────────────────────────────────────────────────────────────
SYSTEM_PROMPT = """Eres Bodzilla IA, analista experto en trading ICT/SMC integrado en una plataforma de charts.

Responde SIEMPRE con JSON válido:
{"text": "Mensaje en español (máx 5 líneas)", "actions": [...]}

ACCIONES DISPONIBLES:

draw_hline — línea horizontal
{"type":"draw_hline","price":1234.5,"color":"#00d084","label":"Soporte","style":"solid","width":1}

draw_fibonacci — niveles Fibonacci
{"type":"draw_fibonacci","high":1300.0,"low":1200.0}

draw_support_resistance — soportes y resistencias
{"type":"draw_support_resistance","supports":[1200.0,1180.0],"resistances":[1300.0,1320.0]}

draw_trendline — línea de tendencia
{"type":"draw_trendline","p1_time":"2024-01-15T10:00:00","p1_price":1200.0,"p2_time":"2024-01-20T10:00:00","p2_price":1250.0,"color":"#ff7b00","label":"TL alcista"}

highlight_zone — zona sombreada
{"type":"highlight_zone","price_top":1300.0,"price_bot":1280.0,"color":"rgba(0,208,132,0.15)","label":"OB"}

toggle_indicator — activar/desactivar: ema10, ema55, ema200, vwap, bb
{"type":"toggle_indicator","indicator":"bb","visible":true}

add_ema — EMA personalizada
{"type":"add_ema","period":21,"color":"#ffdd00"}

change_asset — cambiar activo
{"type":"change_asset","symbol":"ETH/USDT"}

change_timeframe — cambiar TF
{"type":"change_timeframe","tf":"4h"}

clear_drawings — limpiar dibujos IA
{"type":"clear_drawings"}

REGLAS:
- Usa precios REALES del contexto
- Para S/R usa swing_highs y swing_lows del contexto
- Para Fibonacci usa fib_high y fib_low del contexto
- Colores: verde=#00d084, azul=#00aaff, naranja=#ff7b00, rojo=#ef4444
- Responde SIEMPRE en español
- NUNCA menciones Claude ni Anthropic — eres Bodzilla IA
- Si no hay acción: actions=[]"""

# ── Chat ──────────────────────────────────────────────────────────────────────
def chat_with_bodzilla(messages, ind, df, asset_label, tf):
    e10  = round(ind["ema10"][-1],  6) if ind.get("ema10")  else "N/A"
    e55  = round(ind["ema55"][-1],  6) if ind.get("ema55")  else "N/A"
    e200 = round(ind["ema200"][-1], 6) if ind.get("ema200") else "N/A"
    recent = "".join(
        f"  {ts.strftime('%m-%d %H:%M')} O:{r['Open']:.6g} H:{r['High']:.6g} "
        f"L:{r['Low']:.6g} C:{r['Close']:.6g}\n"
        for ts, r in df.tail(5).iterrows()
    )
    context = f"""CONTEXTO DEL CHART:
Activo: {asset_label} | TF: {tf} | Precio: {ind.get('price',0)} ({ind.get('change',0):+}%)
H24:{ind.get('high24',0)} | L24:{ind.get('low24',0)}
EMA10:{e10} | EMA55:{e55} | EMA200:{e200}
RSI:{ind.get('rsi_cur',50)} | ADX:{ind.get('adx_cur',0)} | SQZ:{ind.get('sqz_cur','—')} | MACD:{ind.get('macd_cur',0)}
OB Bull:{ind.get('ob_bull',[])} | OB Bear:{ind.get('ob_bear',[])}
FVG Bull:{ind.get('fvg_bull',[])} | FVG Bear:{ind.get('fvg_bear',[])}
BSL:{ind.get('swing_highs',[])} | SSL:{ind.get('swing_lows',[])}
Fib High:{ind.get('fib_high',0)} | Fib Low:{ind.get('fib_low',0)}
Niveles fib:{ind.get('fib_levels',{})}
TL Highs:{ind.get('tl_highs',[])} | TL Lows:{ind.get('tl_lows',[])}
Últimas 5 velas:
{recent}"""

    msgs_ctx = []
    for i, m in enumerate(messages):
        if i == len(messages)-1 and m["role"] == "user":
            msgs_ctx.append({"role":"user","content": context + "\n\nMensaje: " + m["content"]})
        else:
            msgs_ctx.append({"role":m["role"],"content":m["content"]})

    client = anthropic.Anthropic(api_key=API_KEY)
    resp = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=2000,
        system=SYSTEM_PROMPT,
        messages=msgs_ctx
    )
    raw = resp.content[0].text.strip()
    try:
        if raw.startswith("```"):
            parts = raw.split("```")
            raw = parts[1]
            if raw.startswith("json"): raw = raw[4:]
        data = json.loads(raw)
        return data.get("text",""), data.get("actions",[])
    except:
        return raw, []

# ── Chart HTML ────────────────────────────────────────────────────────────────
def build_chart_html(df, ind, label, tf, overlay_actions=None):
    if df.empty:
        return "<p style='color:#ef4444;padding:20px;font-family:Space Mono'>Sin datos disponibles para este activo.</p>"

    candles = [{"time":int(ts.timestamp()),
                "open": round(float(r["Open"]),  8),
                "high": round(float(r["High"]),  8),
                "low":  round(float(r["Low"]),   8),
                "close":round(float(r["Close"]), 8)}
               for ts, r in df.iterrows()]

    volumes = [{"time":  int(ts.timestamp()),
                "value": round(float(r["Volume"]), 4),
                "color": "rgba(0,208,132,0.4)" if r["Close"] >= r["Open"] else "rgba(239,68,68,0.4)"}
               for ts, r in df.iterrows()]

    def bl(key):
        vals = ind.get(key, [])
        if not vals: return "[]"
        return json.dumps([{"time":int(df.index[i].timestamp()),"value":v}
                           for i,v in enumerate(vals)
                           if i < len(df) and v and not (isinstance(v,float) and np.isnan(v))])

    p   = ind.get("price",  0)
    chg = ind.get("change", 0)
    cc  = "#00d084" if chg >= 0 else "#ef4444"
    cs2 = "+" if chg >= 0 else ""
    ov  = json.dumps(overlay_actions or [])

    return f"""<!DOCTYPE html><html><head><meta charset="UTF-8">
<script src="https://unpkg.com/lightweight-charts@4.1.1/dist/lightweight-charts.standalone.production.js"></script>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{background:#080c10;color:#d4e6f1;font-family:'Space Mono',monospace}}
#hdr{{display:flex;align-items:center;gap:10px;padding:6px 12px;background:#0d1117;border-bottom:1px solid #1e2d3d;flex-wrap:wrap}}
.sym{{font-family:Syne,sans-serif;font-size:0.95rem;font-weight:800;color:#00d084}}
.tf{{background:#131b24;padding:1px 6px;border-radius:3px;font-size:0.6rem;color:#4a6278;border:1px solid #1e2d3d}}
.px{{font-size:1.1rem;font-weight:700;color:#d4e6f1}}
.chg{{font-size:0.78rem;color:{cc};font-weight:700}}
.pill{{background:#131b24;border:1px solid #1e2d3d;border-radius:3px;padding:1px 6px;font-size:0.6rem;color:#4a6278}}
.pill b{{color:#d4e6f1}}
#ctrl{{display:flex;gap:4px;padding:4px 12px;background:#080c10;border-bottom:1px solid #1e2d3d;flex-wrap:wrap;align-items:center}}
.tb{{background:#131b24;border:1px solid #1e2d3d;border-radius:3px;padding:1px 7px;font-size:0.58rem;color:#4a6278;cursor:pointer;font-family:'Space Mono',monospace;transition:all 0.12s}}
.tb.g{{border-color:#00d084;color:#00d084;background:#0a1a10}}
.tb.b{{border-color:#00aaff;color:#00aaff;background:#0a1220}}
.tb.o{{border-color:#ff7b00;color:#ff7b00;background:#1a1000}}
.tb.r{{border-color:#ef4444;color:#ef4444;background:#1a0808}}
#cc{{width:100%;height:380px}}
#rc{{width:100%;height:65px;border-top:1px solid #1e2d3d}}
</style></head><body>
<div id="hdr">
  <span class="sym">{label}</span><span class="tf">{tf}</span>
  <span class="px">{p:,.8g}</span><span class="chg">{cs2}{chg}%</span>
  <span class="pill">RSI <b>{ind.get('rsi_cur',50)}</b></span>
  <span class="pill">ADX <b>{ind.get('adx_cur',0)}</b></span>
  <span class="pill">ATR <b>{round(ind.get('atr_cur',0),4)}</b></span>
  <span class="pill">SQZ <b>{ind.get('sqz_cur','—')}</b></span>
</div>
<div id="ctrl">
  <button class="tb g" id="be10"  onclick="tog('e10','g')">EMA10</button>
  <button class="tb b" id="be55"  onclick="tog('e55','b')">EMA55</button>
  <button class="tb o" id="be200" onclick="tog('e200','o')">EMA200</button>
  <button class="tb b" id="bvwap" onclick="tog('vwap','b')">VWAP</button>
  <button class="tb"   id="bbb"   onclick="togBB()">BB</button>
  <span style="color:#1e2d3d;margin:0 3px">|</span>
  <button class="tb g" id="bob"   onclick="togOvr('ob','g')">OB</button>
  <button class="tb b" id="bfvg"  onclick="togOvr('fvg','b')">FVG</button>
  <button class="tb o" id="bliq"  onclick="togOvr('liq','o')">Liquidez</button>
  <button class="tb"   id="bfib"  onclick="togOvr('fib','b')">Fib</button>
  <button class="tb"   id="btl"   onclick="togOvr('tl','o')">Trendlines</button>
  <button class="tb r" onclick="clearDyn()" style="margin-left:auto">🗑 IA</button>
</div>
<div id="cc"></div>
<div id="rc"></div>
<script>
const CA={json.dumps(candles)};const VO={json.dumps(volumes)};
const E10={bl('ema10')};const E55={bl('ema55')};const E200={bl('ema200')};
const VW={bl('vwap')};const BBU={bl('bb_upper')};const BBL={bl('bb_lower')};const BBM={bl('bb_mid')};
const RS={bl('rsi')};
const OBB={json.dumps(ind.get('ob_bull',[]))};const OBR={json.dumps(ind.get('ob_bear',[]))};
const FB={json.dumps(ind.get('fvg_bull',[]))};const FR={json.dumps(ind.get('fvg_bear',[]))};
const SH={json.dumps(ind.get('swing_highs',[]))};const SL={json.dumps(ind.get('swing_lows',[]))};
const FIBL={json.dumps(ind.get('fib_levels',{}))};
const TLH={json.dumps(ind.get('tl_highs',[]))};const TLL={json.dumps(ind.get('tl_lows',[]))};
const OV={ov};
const LS=LightweightCharts.LineStyle;
const ch=LightweightCharts.createChart(document.getElementById('cc'),{{
  width:document.getElementById('cc').offsetWidth,height:380,
  layout:{{background:{{color:'#080c10'}},textColor:'#4a6278'}},
  grid:{{vertLines:{{color:'#0c1520'}},horzLines:{{color:'#0c1520'}}}},
  crosshair:{{mode:LightweightCharts.CrosshairMode.Normal}},
  rightPriceScale:{{borderColor:'#1e2d3d'}},
  timeScale:{{borderColor:'#1e2d3d',timeVisible:true,secondsVisible:false}},
}});
const cnd=ch.addCandlestickSeries({{upColor:'#00d084',downColor:'#ef4444',borderUpColor:'#00d084',borderDownColor:'#ef4444',wickUpColor:'#00d084',wickDownColor:'#ef4444'}});
cnd.setData(CA);
const vs=ch.addHistogramSeries({{priceFormat:{{type:'volume'}},priceScaleId:'v'}});
ch.priceScale('v').applyOptions({{scaleMargins:{{top:0.85,bottom:0}}}});vs.setData(VO);
const e10s=ch.addLineSeries({{color:'#00d084',lineWidth:1.5,title:'E10',visible:true}});e10s.setData(E10);
const e55s=ch.addLineSeries({{color:'#00aaff',lineWidth:1.5,title:'E55',visible:true}});e55s.setData(E55);
const e200s=ch.addLineSeries({{color:'#ff7b00',lineWidth:2,title:'E200',visible:true}});e200s.setData(E200);
const vws=ch.addLineSeries({{color:'#4a9eff',lineWidth:1,lineStyle:LS.Dashed,visible:true}});vws.setData(VW);
const bbus=ch.addLineSeries({{color:'rgba(255,123,0,0.5)',lineWidth:1,visible:false}});bbus.setData(BBU);
const bbls=ch.addLineSeries({{color:'rgba(255,123,0,0.5)',lineWidth:1,visible:false}});bbls.setData(BBL);
const bbms=ch.addLineSeries({{color:'rgba(255,123,0,0.2)',lineWidth:1,lineStyle:LS.Dotted,visible:false}});bbms.setData(BBM);
document.getElementById('be10').classList.add('g');
document.getElementById('be55').classList.add('b');
document.getElementById('be200').classList.add('o');
document.getElementById('bvwap').classList.add('b');
const SM={{'e10':e10s,'e55':e55s,'e200':e200s,'vwap':vws}};
const SC={{'e10':'g','e55':'b','e200':'o','vwap':'b'}};
const SB={{'e10':'be10','e55':'be55','e200':'be200','vwap':'bvwap'}};
const obL=[],fvgL=[],liqL=[],fibL=[],tlSeries=[];
let bbVis=false,fibInit=false,tlInit=false;
const OVR={{ob:false,fvg:false,liq:false,fib:false,tl:false}};
OBB.forEach(o=>{{obL.push(cnd.createPriceLine({{price:o.top,color:'rgba(0,208,132,0)',lineWidth:1,lineStyle:0,axisLabelVisible:false}}));obL.push(cnd.createPriceLine({{price:o.bot,color:'rgba(0,208,132,0)',lineWidth:1,lineStyle:3,axisLabelVisible:false}}))}});
OBR.forEach(o=>{{obL.push(cnd.createPriceLine({{price:o.top,color:'rgba(239,68,68,0)',lineWidth:1,lineStyle:0,axisLabelVisible:false}}));obL.push(cnd.createPriceLine({{price:o.bot,color:'rgba(239,68,68,0)',lineWidth:1,lineStyle:3,axisLabelVisible:false}}))}});
FB.forEach(f=>{{fvgL.push(cnd.createPriceLine({{price:f.top,color:'rgba(0,170,255,0)',lineWidth:1,lineStyle:2,axisLabelVisible:false}}));fvgL.push(cnd.createPriceLine({{price:f.bot,color:'rgba(0,170,255,0)',lineWidth:1,lineStyle:3,axisLabelVisible:false}}))}});
FR.forEach(f=>{{fvgL.push(cnd.createPriceLine({{price:f.top,color:'rgba(255,123,0,0)',lineWidth:1,lineStyle:2,axisLabelVisible:false}}));fvgL.push(cnd.createPriceLine({{price:f.bot,color:'rgba(255,123,0,0)',lineWidth:1,lineStyle:3,axisLabelVisible:false}}))}});
SH.forEach(p=>liqL.push(cnd.createPriceLine({{price:p,color:'rgba(0,170,255,0)',lineWidth:1,lineStyle:3,axisLabelVisible:false}})));
SL.forEach(p=>liqL.push(cnd.createPriceLine({{price:p,color:'rgba(239,68,68,0)',lineWidth:1,lineStyle:3,axisLabelVisible:false}})));
function showL(arr,on){{arr.forEach(l=>{{try{{const c=l.options().color;const b=c.replace(/,[0-9.]+[)]$/,',');l.applyOptions({{color:b+(on?'0.7)':'0)')}})}}catch(e){{}}}})}}
function initFib(){{
  const fc={{'0':'rgba(255,255,255,0.5)','0.236':'rgba(0,208,132,0.7)','0.382':'rgba(0,170,255,0.8)','0.5':'rgba(255,255,255,0.5)','0.618':'rgba(255,123,0,0.8)','0.786':'rgba(0,170,255,0.7)','1.0':'rgba(255,255,255,0.5)'}};
  Object.entries(FIBL).forEach(([k,v])=>fibL.push(cnd.createPriceLine({{price:v,color:fc[k]||'rgba(255,255,255,0.4)',lineWidth:1,lineStyle:2,axisLabelVisible:true,title:'Fib '+k}})));
  fibInit=true;
}}
function initTL(){{
  if(TLH.length>=2){{const pts=TLH.slice(-2);const s=ch.addLineSeries({{color:'rgba(239,68,68,0.5)',lineWidth:1,lineStyle:LS.Dashed,title:'Res TL'}});s.setData([{{time:pts[0][0],value:pts[0][1]}},{{time:pts[1][0],value:pts[1][1]}}]);tlSeries.push(s);}}
  if(TLL.length>=2){{const pts=TLL.slice(-2);const s=ch.addLineSeries({{color:'rgba(0,208,132,0.5)',lineWidth:1,lineStyle:LS.Dashed,title:'Sup TL'}});s.setData([{{time:pts[0][0],value:pts[0][1]}},{{time:pts[1][0],value:pts[1][1]}}]);tlSeries.push(s);}}
  tlInit=true;
}}
function tog(k,cls){{const s=SM[k];const btn=document.getElementById(SB[k]);const wasOn=btn.classList.contains(cls);if(wasOn){{btn.classList.remove(cls);s.applyOptions({{visible:false}});}}else{{btn.classList.add(cls);s.applyOptions({{visible:true}});}}}}
function togBB(){{bbVis=!bbVis;const btn=document.getElementById('bbb');if(bbVis){{btn.classList.add('o');[bbus,bbls,bbms].forEach(s=>s.applyOptions({{visible:true}}));}}else{{btn.classList.remove('o');[bbus,bbls,bbms].forEach(s=>s.applyOptions({{visible:false}}));}}}}
function togOvr(k,cls){{OVR[k]=!OVR[k];const btn=document.getElementById('b'+k);if(OVR[k])btn.classList.add(cls);else btn.classList.remove(cls);if(k==='ob')showL(obL,OVR[k]);if(k==='fvg')showL(fvgL,OVR[k]);if(k==='liq')showL(liqL,OVR[k]);if(k==='fib'){{if(!fibInit)initFib();showL(fibL,OVR[k]);}}if(k==='tl'){{if(!tlInit)initTL();tlSeries.forEach(s=>s.applyOptions({{visible:OVR[k]}}));}}}}
let dynLines=[],dynSeries=[];
function clearDyn(){{dynLines.forEach(l=>{{try{{cnd.removePriceLine(l)}}catch(e){{}}}});dynSeries.forEach(s=>{{try{{ch.removeSeries(s)}}catch(e){{}}}});dynLines=[];dynSeries=[];}}
function applyActions(actions){{actions.forEach(a=>{{try{{
  if(a.type==='draw_hline'){{const ls=a.style==='dashed'?LS.Dashed:LS.Solid;dynLines.push(cnd.createPriceLine({{price:a.price,color:a.color||'#00d084',lineWidth:a.width||1,lineStyle:ls,axisLabelVisible:true,title:a.label||''}}));}}
  else if(a.type==='draw_fibonacci'){{const h=a.high,l=a.low;const fc={{'0':'rgba(255,255,255,0.5)','0.236':'rgba(0,208,132,0.7)','0.382':'rgba(0,170,255,0.8)','0.5':'rgba(255,255,255,0.5)','0.618':'rgba(255,123,0,0.8)','0.786':'rgba(0,170,255,0.7)','1.0':'rgba(255,255,255,0.5)'}};[0,0.236,0.382,0.5,0.618,0.786,1.0].forEach(f=>{{const price=h-(h-l)*f;dynLines.push(cnd.createPriceLine({{price,color:fc[String(f)]||'#00aaff',lineWidth:1,lineStyle:2,axisLabelVisible:true,title:'Fib '+f}}));}});}}
  else if(a.type==='draw_support_resistance'){{(a.supports||[]).forEach(p=>dynLines.push(cnd.createPriceLine({{price:p,color:'rgba(0,208,132,0.85)',lineWidth:1,lineStyle:0,axisLabelVisible:true,title:'Soporte'}})));(a.resistances||[]).forEach(p=>dynLines.push(cnd.createPriceLine({{price:p,color:'rgba(239,68,68,0.85)',lineWidth:1,lineStyle:0,axisLabelVisible:true,title:'Resistencia'}})));}}
  else if(a.type==='highlight_zone'){{dynLines.push(cnd.createPriceLine({{price:a.price_top,color:a.color||'rgba(0,208,132,0.5)',lineWidth:1,lineStyle:2,axisLabelVisible:true,title:a.label||''}}));dynLines.push(cnd.createPriceLine({{price:a.price_bot,color:a.color||'rgba(0,208,132,0.3)',lineWidth:1,lineStyle:2,axisLabelVisible:false,title:''}}));}}
  else if(a.type==='draw_trendline'){{const s=ch.addLineSeries({{color:a.color||'#ff7b00',lineWidth:1.5,lineStyle:LS.Dashed,title:a.label||'TL'}});const t1=a.p1_time?Math.floor(new Date(a.p1_time).getTime()/1000):0;const t2=a.p2_time?Math.floor(new Date(a.p2_time).getTime()/1000):0;if(t1&&t2)s.setData([{{time:t1,value:a.p1_price}},{{time:t2,value:a.p2_price}}]);dynSeries.push(s);}}
  else if(a.type==='add_ema'){{const closes=CA.map(c=>c.close);const k=2/(a.period+1);let ev=[closes[0]];for(let i=1;i<closes.length;i++)ev.push(closes[i]*k+ev[i-1]*(1-k));const ns=ch.addLineSeries({{color:a.color||'#ffdd00',lineWidth:1.5,title:'EMA'+a.period}});ns.setData(CA.map((c,i)=>({{time:c.time,value:ev[i]}})));dynSeries.push(ns);}}
  else if(a.type==='toggle_indicator'){{const imap={{'ema10':e10s,'ema55':e55s,'ema200':e200s,'vwap':vws}};const cm={{'ema10':'g','ema55':'b','ema200':'o','vwap':'b'}};const bm={{'ema10':'be10','ema55':'be55','ema200':'be200','vwap':'bvwap'}};if(a.indicator==='bb'){{bbVis=a.visible;[bbus,bbls,bbms].forEach(s=>s.applyOptions({{visible:a.visible}}));const btn=document.getElementById('bbb');if(a.visible)btn.classList.add('o');else btn.classList.remove('o');}}else if(imap[a.indicator]){{imap[a.indicator].applyOptions({{visible:a.visible}});const btn=document.getElementById(bm[a.indicator]);if(a.visible)btn.classList.add(cm[a.indicator]);else btn.classList.remove(cm[a.indicator]);}}}}
  else if(a.type==='clear_drawings'){{clearDyn();}}
}}catch(err){{console.warn(a.type,err);}}}})}}
if(OV&&OV.length)applyActions(OV);
const rc=LightweightCharts.createChart(document.getElementById('rc'),{{width:document.getElementById('rc').offsetWidth,height:65,layout:{{background:{{color:'#080c10'}},textColor:'#4a6278'}},grid:{{vertLines:{{color:'#0c1520'}},horzLines:{{color:'#0c1520'}}}},rightPriceScale:{{borderColor:'#1e2d3d',scaleMargins:{{top:0.05,bottom:0.05}}}},timeScale:{{borderColor:'#1e2d3d',visible:false}}}});
const rss=rc.addLineSeries({{color:'#00aaff',lineWidth:1.5}});rss.setData(RS);
rss.createPriceLine({{price:70,color:'rgba(239,68,68,0.4)',lineWidth:1,lineStyle:3}});
rss.createPriceLine({{price:30,color:'rgba(0,208,132,0.4)',lineWidth:1,lineStyle:3}});
ch.timeScale().subscribeVisibleLogicalRangeChange(r=>{{if(r)rc.timeScale().setVisibleLogicalRange(r)}});
rc.timeScale().subscribeVisibleLogicalRangeChange(r=>{{if(r)ch.timeScale().setVisibleLogicalRange(r)}});
window.addEventListener('resize',()=>{{ch.applyOptions({{width:document.getElementById('cc').offsetWidth}});rc.applyOptions({{width:document.getElementById('rc').offsetWidth}});}});
ch.timeScale().fitContent();
</script></body></html>"""

# ── Auto análisis ─────────────────────────────────────────────────────────────
@st.cache_data(ttl=180, show_spinner=False)
def get_auto_analysis(label, tf, ind_json, df_json):
    try:
        ind = json.loads(ind_json)
        df  = pd.read_json(df_json)
        e10  = round(ind["ema10"][-1],  6) if ind.get("ema10")  else "N/A"
        e55  = round(ind["ema55"][-1],  6) if ind.get("ema55")  else "N/A"
        e200 = round(ind["ema200"][-1], 6) if ind.get("ema200") else "N/A"
        recent = "".join(f"  C:{r['Close']:.6g}\n" for _, r in df.tail(3).iterrows())
        prompt = f"""Analiza {label} {tf}. Precio:{ind.get('price',0)} ({ind.get('change',0):+}%)
EMA10:{e10} EMA55:{e55} EMA200:{e200} RSI:{ind.get('rsi_cur',50)} ADX:{ind.get('adx_cur',0)} SQZ:{ind.get('sqz_cur','—')}
OB Bull:{ind.get('ob_bull',[])} OB Bear:{ind.get('ob_bear',[])}
BSL:{ind.get('swing_highs',[])} SSL:{ind.get('swing_lows',[])}
Velas recientes: {recent}
Responde JSON: {{"text":"análisis ## BIAS / ## ESTRUCTURA / ## NIVELES CLAVE / ## SEÑAL / ## PLAN","actions":[]}}"""
        client = anthropic.Anthropic(api_key=API_KEY)
        resp = client.messages.create(
            model="claude-haiku-4-5-20251001", max_tokens=1200,
            system=SYSTEM_PROMPT,
            messages=[{"role":"user","content":prompt}]
        )
        raw = resp.content[0].text.strip()
        if raw.startswith("```"):
            parts = raw.split("```"); raw = parts[1]
            if raw.startswith("json"): raw = raw[4:]
        data = json.loads(raw)
        return data.get("text",""), data.get("actions",[])
    except Exception as e:
        return f"Error al analizar: {e}", []

# ── Render helpers ────────────────────────────────────────────────────────────
def render_bubble(role, text):
    if role == "user":
        st.markdown(f"""<div style="display:flex;justify-content:flex-end;margin:3px 0;">
          <div style="background:{C['bg4']};border:1px solid {C['border']};border-radius:10px 10px 2px 10px;
          padding:6px 10px;max-width:92%;font-size:0.7rem;color:{C['text']};word-break:break-word;">{text}</div>
        </div>""", unsafe_allow_html=True)
    else:
        st.markdown(f"""<div style="display:flex;justify-content:flex-start;margin:3px 0;">
          <div style="background:{C['bg3']};border-left:2px solid {C['green']};
          border-radius:10px 10px 10px 2px;padding:6px 10px;max-width:95%;font-size:0.7rem;
          color:{C['text']};word-break:break-word;">{text}</div>
        </div>""", unsafe_allow_html=True)

def render_action_badge(action):
    icons = {"draw_hline":"📏","draw_fibonacci":"📐","draw_support_resistance":"🎯",
             "draw_trendline":"📈","toggle_indicator":"⚡","add_ema":"➕",
             "change_asset":"🔄","change_timeframe":"⏱","clear_drawings":"🗑","highlight_zone":"🔲"}
    labels = {"draw_hline":f"Línea @ {action.get('price','')}",
              "draw_fibonacci":f"Fibonacci",
              "draw_support_resistance":f"S/R ({len(action.get('supports',[]))}+{len(action.get('resistances',[]))})",
              "draw_trendline":f"TL: {action.get('label','')}",
              "toggle_indicator":f"{action.get('indicator','')} {'ON' if action.get('visible') else 'OFF'}",
              "add_ema":f"EMA {action.get('period','')}",
              "change_asset":f"→ {action.get('symbol','')}",
              "change_timeframe":f"→ {action.get('tf','')}",
              "clear_drawings":"Limpiado","highlight_zone":f"Zona {action.get('label','')}"}
    t = action.get("type","")
    st.markdown(f"""<div style="display:inline-block;background:{C['bg4']};border:1px solid {C['green']}33;
    border-radius:10px;padding:1px 7px;font-size:0.6rem;color:{C['green']};margin:1px;">
    {icons.get(t,'⚙')} {labels.get(t,t)}</div>""", unsafe_allow_html=True)

def render_block(text):
    sec_colors = {"BIAS":C["green"],"ESTRUCTURA":C["blue"],"NIVELES CLAVE":C["orange"],
                  "SEÑAL":C["green"],"PLAN":C["blue"],"ALERTAS":C["orange"]}
    for line in text.strip().split("\n"):
        line = line.strip()
        if not line: continue
        if line.startswith("## "):
            sec = line[3:]; col = sec_colors.get(sec, C["green"])
            st.markdown(f'<div style="font-family:Syne;font-size:0.76rem;font-weight:700;color:{col};border-left:2px solid {col};padding-left:6px;margin:7px 0 3px;">{sec}</div>', unsafe_allow_html=True)
        elif "**:" in line:
            parts = line.split(":**", 1); k = parts[0].replace("**","").strip(); v = parts[1].strip() if len(parts)>1 else ""
            st.markdown(f'<div style="font-size:0.7rem;margin:2px 0;"><span style="color:{C["muted"]}">{k}:</span> <span style="color:{C["text"]};font-weight:700">{v}</span></div>', unsafe_allow_html=True)
        elif line.startswith("-"):
            st.markdown(f'<div style="font-size:0.68rem;color:{C["text"]};padding-left:6px;margin:1px 0;"><span style="color:{C["orange"]}">›</span> {line[1:].strip()}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div style="font-size:0.68rem;color:{C["text"]};margin:1px 0;">{line}</div>', unsafe_allow_html=True)

# ── MAIN ──────────────────────────────────────────────────────────────────────
def main():
    inject_css()

    if "chat_messages"   not in st.session_state: st.session_state.chat_messages = []
    if "overlay_actions" not in st.session_state: st.session_state.overlay_actions = []
    if "sel"             not in st.session_state: st.session_state.sel = ASSETS["🪙 Crypto"][0]
    if "timeframe"       not in st.session_state: st.session_state.timeframe = "1h"
    if "_send_pending"   not in st.session_state: st.session_state._send_pending = False
    if "_pending_msg"    not in st.session_state: st.session_state._pending_msg = ""

    # Header
    st.markdown(f"""<div style="display:flex;align-items:center;gap:10px;padding-bottom:6px;border-bottom:1px solid {C['border']};margin-bottom:6px;">
      <span style="font-family:Syne,sans-serif;font-size:1.35rem;font-weight:800;color:{C['green']};">TRADING CHART PRO</span>
      <span style="font-family:Syne,sans-serif;font-size:0.75rem;color:{C['orange']};">Bodzilla IA</span>
      <span style="margin-left:auto;font-size:0.6rem;color:{C['muted']};">ICT · SMC · Interactive</span>
    </div>""", unsafe_allow_html=True)

    # ── SIDEBAR ────────────────────────────────────────────────────────────────
    with st.sidebar:
        # Sin input de API key — viene de variable de entorno
        if not API_KEY:
            st.markdown(f'<div style="background:{C["bg3"]};border:1px solid {C["red"]};border-radius:4px;padding:6px 10px;font-size:0.7rem;color:{C["red"]};margin-bottom:6px;">⚠ Configura ANTHROPIC_API_KEY en Railway Variables</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div style="background:{C["bg3"]};border:1px solid {C["green"]}44;border-radius:4px;padding:4px 10px;font-size:0.65rem;color:{C["green"]};margin-bottom:6px;">🟢 Bodzilla IA activa</div>', unsafe_allow_html=True)

        st.session_state.timeframe = st.selectbox(
            "TF", list(TIMEFRAMES.keys()),
            index=list(TIMEFRAMES.keys()).index(st.session_state.timeframe),
            label_visibility="collapsed"
        )

        st.markdown(f'<div style="border-top:1px solid {C["border"]};margin:5px 0 4px;"></div>', unsafe_allow_html=True)
        st.markdown(f'<div style="font-family:Syne,sans-serif;color:{C["green"]};font-size:0.78rem;font-weight:700;margin-bottom:3px;">🤖 Bodzilla IA</div>', unsafe_allow_html=True)

        # Quick commands
        QUICK = [
            ("📊 Análisis", "Dame un análisis completo con bias, niveles clave y señal"),
            ("🎯 S/R",      "Traza los soportes y resistencias más importantes"),
            ("📐 Fibonacci", "Dibuja los niveles de Fibonacci del último swing"),
            ("📈 Trendlines","Traza las líneas de tendencia alcista y bajista"),
            ("⚡ LONG/SHORT","¿Hay setup de LONG o SHORT en este momento?"),
            ("🧹 Limpiar",   "Limpia todas las líneas del chart"),
        ]
        qc1, qc2 = st.columns(2)
        for i, (lbl, cmd) in enumerate(QUICK):
            with (qc1 if i%2==0 else qc2):
                if st.button(lbl, key=f"qc{i}", use_container_width=True):
                    st.session_state._pending_msg = cmd
                    st.session_state._send_pending = True

        st.markdown(f'<div style="border-top:1px solid {C["border"]};margin:4px 0 3px;"></div>', unsafe_allow_html=True)

        # Chat history
        for msg in st.session_state.chat_messages[-16:]:
            render_bubble(msg["role"], msg["content"])
            if msg.get("actions"):
                for act in msg["actions"]: render_action_badge(act)

        # Chat input
        user_input = st.text_input("msg", placeholder="Escribe o pide una acción...",
                                    key="chat_input", label_visibility="collapsed")
        sc, cc2 = st.columns([3,1])
        with sc:
            send_btn = st.button("Enviar ↵", use_container_width=True, type="primary")
        with cc2:
            if st.button("🗑", use_container_width=True):
                st.session_state.chat_messages = []
                st.session_state.overlay_actions = []
                st.rerun()

        st.markdown(f'<div style="border-top:1px solid {C["border"]};margin:5px 0 4px;"></div>', unsafe_allow_html=True)

        # Assets
        st.markdown(f'<div style="font-family:Syne,sans-serif;color:{C["orange"]};font-size:0.72rem;font-weight:700;margin-bottom:3px;">📂 ACTIVOS</div>', unsafe_allow_html=True)
        for cat, assets in ASSETS.items():
            with st.expander(cat, expanded=(cat == "🪙 Crypto")):
                for a in assets:
                    active = st.session_state.sel["label"] == a["label"]
                    if st.button(a["label"], key=f"a_{a['label']}", use_container_width=True,
                                  type="primary" if active else "secondary"):
                        st.session_state.sel = a
                        st.cache_data.clear()
                        st.rerun()

    # ── Fetch data ─────────────────────────────────────────────────────────────
    asset = st.session_state.sel
    tf    = st.session_state.timeframe

    with st.spinner(f"Cargando {asset['label']}..."):
        df = fetch_ohlcv(asset["label"], asset["yf"], tf)

    if df.empty:
        st.error(f"Sin datos para {asset['label']} en {tf}. Prueba otro timeframe.")
        return

    ind = calculate_indicators(df)

    # ── Procesar chat ──────────────────────────────────────────────────────────
    do_send = False; msg_to_send = ""
    if st.session_state._send_pending:
        do_send = True; msg_to_send = st.session_state._pending_msg
        st.session_state._send_pending = False; st.session_state._pending_msg = ""
    elif send_btn and user_input.strip():
        do_send = True; msg_to_send = user_input.strip()

    if do_send and msg_to_send and API_KEY:
        st.session_state.chat_messages.append({"role":"user","content":msg_to_send})
        api_msgs = [{"role":m["role"],"content":m["content"]}
                    for m in st.session_state.chat_messages if m["role"] in ("user","assistant")]
        text, actions = chat_with_bodzilla(api_msgs, ind, df, asset["label"], tf)
        st.session_state.chat_messages.append({"role":"assistant","content":text,"actions":actions})
        for act in actions:
            if act.get("type") == "change_asset":
                for cat_assets in ASSETS.values():
                    for a in cat_assets:
                        if a["label"] == act.get("symbol",""):
                            st.session_state.sel = a; st.cache_data.clear()
            elif act.get("type") == "change_timeframe":
                ntf = act.get("tf","")
                if ntf in TIMEFRAMES: st.session_state.timeframe = ntf; st.cache_data.clear()
            elif act.get("type") == "clear_drawings":
                st.session_state.overlay_actions = []
            else:
                st.session_state.overlay_actions.append(act)
        st.rerun()

    # ── Métricas ───────────────────────────────────────────────────────────────
    m1,m2,m3,m4,m5,m6 = st.columns(6)
    with m1: st.metric("Precio",   f"{ind.get('price',0):,.8g}",   f"{ind.get('change',0):+.2f}%")
    with m2:
        rv = ind.get('rsi_cur', 50)
        st.metric("RSI", f"{rv:.1f}", "OB" if rv>70 else "OV" if rv<30 else "Neutral")
    with m3:
        av = ind.get('adx_cur', 0)
        st.metric("ADX", f"{av:.1f}", "Trend" if av>25 else "Range")
    with m4: st.metric("ATR",     f"{ind.get('atr_cur',0):.4g}")
    with m5: st.metric("Squeeze", ind.get("sqz_cur","—"))
    with m6: st.metric("H24",     f"{ind.get('high24',0):,.8g}")

    st.markdown("<div style='margin:3px 0'></div>", unsafe_allow_html=True)

    # ── Chart ──────────────────────────────────────────────────────────────────
    st.components.v1.html(
        build_chart_html(df, ind, asset["label"], tf, st.session_state.overlay_actions),
        height=465, scrolling=False
    )

    st.markdown(f'<div style="border-top:1px solid {C["border"]};margin:6px 0 4px;"></div>', unsafe_allow_html=True)

    # ── Tabs ───────────────────────────────────────────────────────────────────
    tab_auto, tab_smc, tab_liq, tab_raw = st.tabs(["🤖 Análisis Auto","🧱 OB & FVG","⚡ Liquidez","📋 OHLCV"])

    with tab_auto:
        if not API_KEY:
            st.markdown(f'<div style="background:{C["bg3"]};border:1px solid {C["orange"]};border-radius:4px;padding:8px 12px;font-size:0.76rem;color:{C["orange"]};">⚠ Configura ANTHROPIC_API_KEY en Railway Variables</div>', unsafe_allow_html=True)
        else:
            hc, bc = st.columns([5,1])
            with bc:
                if st.button("🔄", use_container_width=True): st.cache_data.clear(); st.rerun()
            with hc:
                st.markdown(f'<div style="font-size:0.62rem;color:{C["muted"]};">{asset["label"]} · {tf} · {datetime.now().strftime("%H:%M:%S")}</div>', unsafe_allow_html=True)
            with st.spinner("Bodzilla IA analizando..."):
                ind_s = json.dumps({k:v for k,v in ind.items() if not isinstance(v,list) or k in
                                    ["ob_bull","ob_bear","fvg_bull","fvg_bear","swing_highs","swing_lows"]})
                text, _ = get_auto_analysis(asset["label"], tf, ind_s, df.tail(20).to_json())
                secs = text.split("\n## ")
                lk = ["BIAS","ESTRUCTURA","NIVELES CLAVE"]
                rk = ["SEÑAL","PLAN","ALERTAS"]
                lt = "\n## ".join([""] + [s for s in secs if any(s.startswith(k) for k in lk)]).strip()
                rt = "\n## ".join([""] + [s for s in secs if any(s.startswith(k) for k in rk)]).strip()
                ca, cb = st.columns(2)
                with ca: render_block(lt if lt else text)
                with cb:
                    if rt: render_block(rt)

    with tab_smc:
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f'<div style="color:{C["green"]};font-size:0.68rem;font-weight:700;margin-bottom:4px;">▲ OB BULLISH</div>', unsafe_allow_html=True)
            for ob in ind.get("ob_bull",[]):
                st.markdown(f'<div style="background:{C["bg3"]};border-left:2px solid {C["green"]};border-radius:3px;padding:3px 8px;margin:2px 0;font-size:0.68rem;">Top:{ob["top"]} | Bot:{ob["bot"]}</div>', unsafe_allow_html=True)
            st.markdown(f'<div style="color:{C["blue"]};font-size:0.68rem;font-weight:700;margin:5px 0 3px;">≋ FVG BULL</div>', unsafe_allow_html=True)
            for f in ind.get("fvg_bull",[]):
                st.markdown(f'<div style="background:{C["bg3"]};border-left:2px solid {C["blue"]};border-radius:3px;padding:3px 8px;margin:2px 0;font-size:0.68rem;">{f["bot"]} — {f["top"]}</div>', unsafe_allow_html=True)
        with c2:
            st.markdown(f'<div style="color:{C["red"]};font-size:0.68rem;font-weight:700;margin-bottom:4px;">▼ OB BEARISH</div>', unsafe_allow_html=True)
            for ob in ind.get("ob_bear",[]):
                st.markdown(f'<div style="background:{C["bg3"]};border-left:2px solid {C["red"]};border-radius:3px;padding:3px 8px;margin:2px 0;font-size:0.68rem;">Top:{ob["top"]} | Bot:{ob["bot"]}</div>', unsafe_allow_html=True)
            st.markdown(f'<div style="color:{C["orange"]};font-size:0.68rem;font-weight:700;margin:5px 0 3px;">≋ FVG BEAR</div>', unsafe_allow_html=True)
            for f in ind.get("fvg_bear",[]):
                st.markdown(f'<div style="background:{C["bg3"]};border-left:2px solid {C["orange"]};border-radius:3px;padding:3px 8px;margin:2px 0;font-size:0.68rem;">{f["bot"]} — {f["top"]}</div>', unsafe_allow_html=True)

    with tab_liq:
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f'<div style="color:{C["blue"]};font-size:0.68rem;font-weight:700;margin-bottom:4px;">▲ BSL</div>', unsafe_allow_html=True)
            for lvl in sorted(ind.get("swing_highs",[]), reverse=True):
                st.markdown(f'<div style="background:{C["bg3"]};border-left:2px solid {C["blue"]};border-radius:3px;padding:3px 8px;margin:2px 0;font-size:0.68rem;">⚡ {lvl}</div>', unsafe_allow_html=True)
        with c2:
            st.markdown(f'<div style="color:{C["red"]};font-size:0.68rem;font-weight:700;margin-bottom:4px;">▼ SSL</div>', unsafe_allow_html=True)
            for lvl in sorted(ind.get("swing_lows",[])):
                st.markdown(f'<div style="background:{C["bg3"]};border-left:2px solid {C["red"]};border-radius:3px;padding:3px 8px;margin:2px 0;font-size:0.68rem;">⚡ {lvl}</div>', unsafe_allow_html=True)

    with tab_raw:
        st.dataframe(df.tail(100).sort_index(ascending=False).round(8),
                     use_container_width=True, hide_index=False)


if __name__ == "__main__":
    main()
