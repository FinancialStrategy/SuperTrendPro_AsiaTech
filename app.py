# -*- coding: utf-8 -*-
"""
STREAMLIT CLOUD SAFE VERSION: original analytics preserved; interactive institutional UI added.
MK FinTECH LabGEN @2026 Istanbul
Multi-Universe AI / Chip / US Major Stocks Executive Report + SupertrendPro Institutional Engine
Real Yahoo Finance data | No synthetic prices | No ETF portfolio constituents
"""

# ============================================================
# 0. COLAB PACKAGE SETUP
# ============================================================
import sys, subprocess, importlib.util, warnings, re, math, gc
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
warnings.filterwarnings("ignore")

def ensure_package(import_name, pip_name=None):
    pip_name = pip_name or import_name
    if importlib.util.find_spec(import_name) is None:
        print(f"[INSTALL] {pip_name}")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", pip_name])

# Streamlit Cloud installs dependencies from requirements.txt before app startup.
# Runtime package installation is deliberately disabled to keep reruns deterministic.
REQUIRED_PACKAGES = [
    ("yfinance", "yfinance"), ("plotly", "plotly"), ("scipy", "scipy"),
    ("statsmodels", "statsmodels"), ("sklearn", "scikit-learn"),
    ("xlsxwriter", "XlsxWriter"), ("quantstats", "quantstats"),
]

# ============================================================
# 1. IMPORTS
# ============================================================
import numpy as np
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
import plotly.express as px
import plotly.io as pio
from plotly.subplots import make_subplots
from scipy.optimize import minimize
from scipy.stats import norm, skew, kurtosis, jarque_bera
import statsmodels.api as sm
import quantstats as qs
import streamlit as st
import streamlit.components.v1 as components
import tempfile
import os

# ============================================================
# 2. CONFIGURATION
# ============================================================
REPORT_TITLE = "Multi-Universe AI / Chip / Asia + US Major Stocks Executive Risk Report — SupertrendPro Institutional Integrated"
AUTHOR_LINE = "MK FinTECH LabGEN @2026 Istanbul, Murat KONUKLAR"
NEWS_SOURCE_URL = "https://www.investing.com/news/stock-market-news/korea-sinks-as-ai-chip-selloff-deepens-japan-suppliers-tumble-4772256"
NEWS_SOURCE_TITLE = "Korea sinks as AI-chip selloff deepens; Japan suppliers tumble"
NEWS_SOURCE_URL_2 = "https://www.investing.com/news/stock-market-news/asia-stocks-fall-as-ai-valuation-fears-overshadow-samsungs-blockbuster-earnings-4778205"
NEWS_SOURCE_TITLE_2 = "Asia stocks fall as AI valuation fears overshadow Samsung's blockbuster earnings"
NEWS_SOURCE_URL_3 = "https://www.investing.com/news/stock-market-news/sk-hynix-shares-slide-nearly-11-in-seoul-after-bumper-nasdaq-debut-4787404"
NEWS_SOURCE_TITLE_3 = "SK Hynix shares slide nearly 14% in Seoul after bumper Nasdaq debut"

# SupertrendPro Institutional integration controls
INSTITUTIONAL_ENGINE_VERSION = "2.0.0"
INSTITUTIONAL_MIN_OBS = 260
INSTITUTIONAL_FORWARD_HORIZON = 60
INSTITUTIONAL_TRANSACTION_COST_BPS = 8.0
INSTITUTIONAL_SLIPPAGE_BPS = 4.0
INSTITUTIONAL_DETAIL_CHART_LIMIT = 14

# Cross-listing metadata. Ratios are underlying ordinary shares represented by one ADR.
# FX direction is explicitly defined to avoid synthetic or implicit currency conversion.
CROSS_LISTING_PAIRS = {
    "SK Hynix — Seoul vs Nasdaq ADR": {
        "local": "000660.KS", "adr": "SKHY", "fx": "KRW=X",
        "ordinary_per_adr": 0.10, "fx_mode": "LOCAL_PER_USD",
        "local_currency": "KRW", "adr_currency": "USD",
        "note": "10 SKHY ADRs represent one SK Hynix common share."
    },
    "TSMC — Taiwan vs NYSE ADR": {
        "local": "2330.TW", "adr": "TSM", "fx": "TWD=X",
        "ordinary_per_adr": 5.0, "fx_mode": "LOCAL_PER_USD",
        "local_currency": "TWD", "adr_currency": "USD",
        "note": "One TSM ADR represents five TSMC ordinary shares."
    },
    "ASML — Amsterdam vs Nasdaq Registry Share": {
        "local": "ASML.AS", "adr": "ASML", "fx": "EURUSD=X",
        "ordinary_per_adr": 1.0, "fx_mode": "USD_PER_LOCAL",
        "local_currency": "EUR", "adr_currency": "USD",
        "note": "ASML Nasdaq registry share / ordinary-share ratio is treated as 1:1."
    },
}
INITIAL_CAPITAL_USD = 10_000_000.0
YEARS_BACK, TRADING_DAYS, ROLLING_VOL_WINDOW, ROLLING_BETA_WINDOW = 5, 252, 63, 252
MAX_SINGLE_NAME_WEIGHT = 0.15
RISK_FREE_TICKER = "^IRX"

SOX_TICKER = "^SOX"
SOX_HISTORY_START = "2018-01-01"
SOX_BAND_WINDOW = 20
SOX_TOP_BREACH_ROWS = 40
QS_HISTORY_START = "2018-01-01"
NIKKEI_TICKER = "^N225"
TOPIX_QS_TICKER = "1306.T"
IN_COLAB = False
OUTPUT_DIR = Path(os.environ.get("MULTI_UNIVERSE_OUTPUT_DIR", tempfile.gettempdir())) / "multi_universe_ai_chip_streamlit"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
NIKKEI_QS_HTML = str(OUTPUT_DIR / "QS_Engine_Nikkei_225_Index_Report.html")
TOPIX_QS_HTML = str(OUTPUT_DIR / "QS_Engine_TOPIX_1306T_Benchmark_Proxy_Report.html")
REPORT_OUTPUT = str(OUTPUT_DIR / "Multi_Universe_AI_Chip_Asia_US_SupertrendPro_Institutional_QS_ENGINE.html")
EXCEL_OUTPUT = str(OUTPUT_DIR / "Multi_Universe_AI_Chip_Asia_US_SupertrendPro_Institutional_QS_ENGINE_Analytics.xlsx")

TOPIX_BENCHMARK_PROXY = "1306.T"
TOPIX_BENCHMARK_PROXY_NOTE = "ETF exception applies only to TOPIX benchmark: 1306.T NEXT FUNDS TOPIX ETF is used solely as a benchmark proxy because ^TOPX was unavailable from Yahoo Finance; it is never used as a portfolio constituent."

PLOT_TEMPLATE = "plotly_white"
PLOT_CONFIG = {
    "displayModeBar": True,
    "displaylogo": False,
    "responsive": True,
    "scrollZoom": False,
    "toImageButtonOptions": {
        "format": "png",
        "filename": "mk_full_width_chart",
        "height": 1400,
        "width": 2400,
        "scale": 2
    },
}

# Full-width institutional chart settings.
CHART_FULL_HEIGHT = 920
CHART_EXTRA_LARGE_HEIGHT = 1080
CHART_MATRIX_HEIGHT = 1120
CHART_BAR_MIN_HEIGHT = 920

US_MAJOR_UNIVERSE = {
"NVDA":{"name":"NVIDIA Corporation","sector":"Information Technology","theme":"AI / GPU"},
"AAPL":{"name":"Apple Inc.","sector":"Information Technology","theme":"AI Devices"},
"MSFT":{"name":"Microsoft Corporation","sector":"Information Technology","theme":"AI Cloud"},
"AMZN":{"name":"Amazon.com, Inc.","sector":"Consumer Discretionary","theme":"AWS / AI Infrastructure"},
"GOOGL":{"name":"Alphabet Inc. Class A","sector":"Communication Services","theme":"AI / Cloud"},
"META":{"name":"Meta Platforms, Inc.","sector":"Communication Services","theme":"AI Infrastructure"},
"AVGO":{"name":"Broadcom Inc.","sector":"Information Technology","theme":"Semiconductors / Networking"},
"TSLA":{"name":"Tesla, Inc.","sector":"Consumer Discretionary","theme":"EV / Autonomy"},
"BRK-B":{"name":"Berkshire Hathaway Inc. Class B","sector":"Financials","theme":"Diversified Holding"},
"JPM":{"name":"JPMorgan Chase & Co.","sector":"Financials","theme":"Banking"},
"LLY":{"name":"Eli Lilly and Company","sector":"Health Care","theme":"Biopharma"},
"V":{"name":"Visa Inc.","sector":"Financials","theme":"Payments"},
"MA":{"name":"Mastercard Incorporated","sector":"Financials","theme":"Payments"},
"UNH":{"name":"UnitedHealth Group Incorporated","sector":"Health Care","theme":"Managed Care"},
"HD":{"name":"The Home Depot, Inc.","sector":"Consumer Discretionary","theme":"Retail"},
"PG":{"name":"The Procter & Gamble Company","sector":"Consumer Staples","theme":"Staples"},
"COST":{"name":"Costco Wholesale Corporation","sector":"Consumer Staples","theme":"Retail"},
"NFLX":{"name":"Netflix, Inc.","sector":"Communication Services","theme":"Streaming / AI"},
"ORCL":{"name":"Oracle Corporation","sector":"Information Technology","theme":"Cloud / Database"},
"XOM":{"name":"Exxon Mobil Corporation","sector":"Energy","theme":"Energy"},
"JNJ":{"name":"Johnson & Johnson","sector":"Health Care","theme":"Health Care"},
"WMT":{"name":"Walmart Inc.","sector":"Consumer Staples","theme":"Retail"},
"ABBV":{"name":"AbbVie Inc.","sector":"Health Care","theme":"Biopharma"},
"BAC":{"name":"Bank of America Corporation","sector":"Financials","theme":"Banking"}}

ARTICLE_SHOCK_UNIVERSE = {
"005930.KS":{"name":"Samsung Electronics Co., Ltd.","sector":"Semiconductors","theme":"Memory / AI Supply Chain","country":"South Korea","article_role":"KOSPI heavyweight chipmaker mentioned as falling"},
"000660.KS":{"name":"SK Hynix Inc.","sector":"Semiconductors","theme":"HBM / Memory / AI Supply Chain","country":"South Korea","article_role":"KOSPI heavyweight chipmaker mentioned as falling"},
"META":{"name":"Meta Platforms, Inc.","sector":"Communication Services","theme":"AI Infrastructure / Hyperscaler","country":"United States","article_role":"Cloud infrastructure reports cited as AI spending concern"},
"AAPL":{"name":"Apple Inc.","sector":"Information Technology","theme":"Technology / Memory Demand","country":"United States","article_role":"Memory-chip supplier evaluation report cited"},
"MU":{"name":"Micron Technology, Inc.","sector":"Semiconductors","theme":"Memory","country":"United States","article_role":"US memory maker mentioned as falling more than 10%"},
"SNDK":{"name":"SanDisk Corporation","sector":"Technology Hardware / Storage","theme":"Storage / Memory","country":"United States","article_role":"Storage company mentioned as falling more than 10%"},
"285A.T":{"name":"Kioxia Holdings Corporation","sector":"Semiconductors","theme":"NAND Memory","country":"Japan","article_role":"Japan chip-related name mentioned as tumbling"},
"4062.T":{"name":"Ibiden Co., Ltd.","sector":"Semiconductor Components","theme":"Substrate / AI Supply Chain","country":"Japan","article_role":"Japan chip supplier mentioned as falling"},
"6981.T":{"name":"Murata Manufacturing Co., Ltd.","sector":"Electronic Components","theme":"Components / AI Supply Chain","country":"Japan","article_role":"Japan supplier mentioned as falling"},
"5801.T":{"name":"Furukawa Electric Co., Ltd.","sector":"Electronic Components / Materials","theme":"Cables / Components","country":"Japan","article_role":"Japan supplier mentioned as falling"},
"5706.T":{"name":"Mitsui Mining and Smelting Co., Ltd.","sector":"Materials / Electronics Supply Chain","theme":"Materials / AI Supply Chain","country":"Japan","article_role":"Japan supplier mentioned as falling"},
"2330.TW":{"name":"Taiwan Semiconductor Manufacturing Company","sector":"Semiconductors","theme":"Foundry / AI Supply Chain","country":"Taiwan","article_role":"TSMC mentioned as extending recent losses"},
"9984.T":{"name":"SoftBank Group Corp.","sector":"Technology Investment","theme":"AI Investment / OpenAI Exposure","country":"Japan","article_role":"AI investment financing report mentioned"},
"2371.T":{"name":"Kakaku.com, Inc.","sector":"Internet Services","theme":"Online price-comparison technology","country":"Japan","article_role":"Online price-comparison operator mentioned","source_article":"Article 1"},
"2317.TW":{"name":"Hon Hai Precision Industry Co., Ltd. / Foxconn","sector":"Electronics Manufacturing / AI Servers","theme":"NVIDIA AI server assembly partner / AI hardware supply chain","country":"Taiwan","article_role":"Nvidia largest AI server assembly partner mentioned in second article","source_article":"Article 2"},
"2454.TW":{"name":"MediaTek Inc.","sector":"Semiconductors","theme":"Mobile / edge AI semiconductors","country":"Taiwan","article_role":"Taiwan semiconductor name mentioned as falling in second article","source_article":"Article 2"},
"011070.KS":{"name":"LG Innotek Co., Ltd.","sector":"Electronic Components","theme":"Camera modules / electronic components / AI hardware supply chain","country":"South Korea","article_role":"Korean technology component supplier mentioned as falling in related chip-share article","source_article":"Article 2"},
"SKHY":{"name":"SK hynix Inc. American Depositary Shares","sector":"Semiconductors","theme":"HBM / Memory / Nasdaq ADR","country":"United States / South Korea","article_role":"New Nasdaq ADR highlighted after blockbuster debut; short listing history is handled in the event monitor","source_article":"Article 3"},
"TSM":{"name":"Taiwan Semiconductor Manufacturing Company Limited ADR","sector":"Semiconductors","theme":"Foundry / AI Supply Chain / US ADR","country":"United States / Taiwan","article_role":"TSMC US ADR identified as a key sector earnings bellwether","source_article":"Article 3"},
"ASML.AS":{"name":"ASML Holding N.V. — Euronext Amsterdam","sector":"Semiconductor Equipment","theme":"Advanced Lithography / EUV","country":"Netherlands","article_role":"ASML Amsterdam ordinary shares identified as a key sector earnings bellwether","source_article":"Article 3"}}

US_TECH_AI_CHIP_UNIVERSE = {
"NVDA":{"name":"NVIDIA Corporation","sector":"Semiconductors","theme":"AI GPU"},
"MSFT":{"name":"Microsoft Corporation","sector":"Software / Cloud","theme":"AI Cloud"},
"AAPL":{"name":"Apple Inc.","sector":"Technology Hardware","theme":"AI Devices"},
"GOOGL":{"name":"Alphabet Inc. Class A","sector":"Internet / Cloud","theme":"AI Platform"},
"META":{"name":"Meta Platforms, Inc.","sector":"Internet / AI Infrastructure","theme":"AI Infrastructure"},
"AMZN":{"name":"Amazon.com, Inc.","sector":"Cloud / E-commerce","theme":"AWS / AI"},
"AVGO":{"name":"Broadcom Inc.","sector":"Semiconductors","theme":"Networking / Custom Silicon"},
"AMD":{"name":"Advanced Micro Devices, Inc.","sector":"Semiconductors","theme":"AI Accelerators"},
"MU":{"name":"Micron Technology, Inc.","sector":"Semiconductors","theme":"HBM / Memory"},
"ORCL":{"name":"Oracle Corporation","sector":"Software / Cloud","theme":"Cloud / Database / AI"},
"QCOM":{"name":"QUALCOMM Incorporated","sector":"Semiconductors","theme":"Mobile AI"},
"TXN":{"name":"Texas Instruments Incorporated","sector":"Semiconductors","theme":"Analog Semiconductors"},
"AMAT":{"name":"Applied Materials, Inc.","sector":"Semiconductor Equipment","theme":"WFE"},
"LRCX":{"name":"Lam Research Corporation","sector":"Semiconductor Equipment","theme":"Etch / Deposition"},
"KLAC":{"name":"KLA Corporation","sector":"Semiconductor Equipment","theme":"Metrology"},
"INTC":{"name":"Intel Corporation","sector":"Semiconductors","theme":"CPU / Foundry / AI"},
"CRM":{"name":"Salesforce, Inc.","sector":"Software","theme":"Enterprise AI"},
"NOW":{"name":"ServiceNow, Inc.","sector":"Software","theme":"Workflow AI"},
"PLTR":{"name":"Palantir Technologies Inc.","sector":"Software / AI Analytics","theme":"AI Analytics"},
"SNPS":{"name":"Synopsys, Inc.","sector":"EDA Software","theme":"Chip Design"},
"CDNS":{"name":"Cadence Design Systems, Inc.","sector":"EDA Software","theme":"Chip Design"},
"MRVL":{"name":"Marvell Technology, Inc.","sector":"Semiconductors","theme":"Data Center Silicon"},
"ANET":{"name":"Arista Networks, Inc.","sector":"Networking Hardware","theme":"AI Data Center Networking"},
"SMCI":{"name":"Super Micro Computer, Inc.","sector":"AI Servers","theme":"AI Server Infrastructure"},
"TSM":{"name":"Taiwan Semiconductor Manufacturing Company Limited ADR","sector":"Semiconductors","theme":"Foundry / AI Supply Chain / US ADR"},
"ASML":{"name":"ASML Holding N.V. Nasdaq Registry Shares","sector":"Semiconductor Equipment","theme":"Advanced Lithography / EUV / US Listing"},
"SKHY":{"name":"SK hynix Inc. American Depositary Shares","sector":"Semiconductors","theme":"HBM / Memory / New Nasdaq ADR"}}

INDEX_BENCHMARKS = {
"^GSPC":{"name":"S&P 500 Index","region":"United States"}, "^IXIC":{"name":"Nasdaq Composite Index","region":"United States"},
"^NDX":{"name":"Nasdaq 100 Index","region":"United States"}, "^SOX":{"name":"Philadelphia Semiconductor Index","region":"United States"},
"^KS11":{"name":"KOSPI Composite Index","region":"South Korea"}, "^N225":{"name":"Nikkei 225 Index","region":"Japan"},
"1306.T":{"name":"NEXT FUNDS TOPIX ETF — TOPIX Benchmark Proxy (ETF Exception Only for TOPIX)","region":"Japan","benchmark_type":"ETF proxy exception"}, "^AXJO":{"name":"S&P/ASX 200 Index","region":"Australia"},
"^NSEI":{"name":"Nifty 50 Index","region":"India"}, "^JKSE":{"name":"Jakarta Composite Index","region":"Indonesia"},
"000001.SS":{"name":"Shanghai Composite Index","region":"China"}, "000300.SS":{"name":"CSI 300 Index","region":"China"},
"NQ=F":{"name":"Nasdaq 100 Futures","region":"US Futures"}, "ES=F":{"name":"S&P 500 Futures","region":"US Futures"}}

UNIVERSE_CONFIGS = {
"US Major Stocks 10M Portfolio":{"universe":US_MAJOR_UNIVERSE,"primary_benchmark":"^GSPC","benchmarks":["^GSPC","^IXIC"],"min_observations":756,"capital_mode":"whole_share_usd","description":"Original US major single-stock 10M USD portfolio. Existing feature set preserved."},
"Article Shock Universe — AI Chip Selloff":{"universe":ARTICLE_SHOCK_UNIVERSE,"primary_benchmark":"^KS11","benchmarks":["^KS11","^N225","1306.T","^IXIC","^NDX","^SOX","^GSPC","^AXJO","^NSEI","^JKSE","000001.SS","000300.SS","NQ=F","ES=F"],"min_observations":60,"capital_mode":"equal_weight_return_index","description":"Companies mentioned across the three Investing.com AI-chip articles, including SKHY, TSM and ASML.AS. Mixed currencies; analyzed as actual-return equal-weight basket. New listings remain in the event monitor when long-history requirements are not met."},
"US Technology + AI + Chip 20+ Universe":{"universe":US_TECH_AI_CHIP_UNIVERSE,"primary_benchmark":"^IXIC","benchmarks":["^IXIC","^SOX","^NDX","^GSPC"],"min_observations":504,"capital_mode":"whole_share_usd","description":"US-listed technology, AI infrastructure, semiconductor and chip ecosystem single stocks, including TSM, ASML and new SKHY ADR. No ETFs."}}

# ============================================================
# 3. METRIC HELPERS
# ============================================================
def pct(x,digits=2):
    return "—" if pd.isna(x) or np.isinf(x) else f"{x*100:,.{digits}f}%"
def num(x,digits=3):
    return "—" if pd.isna(x) or np.isinf(x) else f"{x:,.{digits}f}"
def money(x,digits=0):
    return "—" if pd.isna(x) or np.isinf(x) else f"${x:,.{digits}f}"
def safe_div(a,b):
    return np.nan if b is None or pd.isna(b) or abs(b)<1e-12 else a/b
def max_drawdown(r):
    w=(1+r.dropna()).cumprod()
    if w.empty: return np.nan,pd.Series(dtype=float)
    dd=w/w.cummax()-1
    return dd.min(),dd
def annualized_return(r):
    r=r.dropna(); return np.nan if len(r)==0 else (1+r).prod()**(TRADING_DAYS/len(r))-1
def annualized_vol(r):
    r=r.dropna(); return np.nan if len(r)<2 else r.std(ddof=1)*np.sqrt(TRADING_DAYS)
def downside_deviation(r):
    r=r.dropna(); return np.nan if len(r)<2 else np.sqrt(np.mean(np.minimum(r,0)**2))*np.sqrt(TRADING_DAYS)
def historical_var_cvar(r,conf=.95,horizon=1):
    r=r.dropna()
    if horizon>1: r=((1+r).rolling(horizon).apply(np.prod,raw=True)-1).dropna()
    if len(r)<30: return np.nan,np.nan
    q=np.quantile(r,1-conf); tail=r[r<=q]
    return -q, -tail.mean() if len(tail)>0 else np.nan
def parametric_var_cvar(r,conf=.95,horizon=1):
    r=r.dropna()
    if len(r)<30: return np.nan,np.nan
    mu=r.mean()*horizon; sig=r.std(ddof=1)*np.sqrt(horizon); z=norm.ppf(1-conf)
    return -(mu+sig*z), -(mu-sig*norm.pdf(z)/(1-conf))
def regression_alpha_beta(p,b,rf):
    df=pd.concat([p,b,rf],axis=1).dropna(); df.columns=["p","b","rf"]
    if len(df)<60: return np.nan,np.nan,np.nan
    model=sm.OLS(df.p-df.rf, sm.add_constant(df.b-df.rf)).fit()
    return model.params.get("const",np.nan)*TRADING_DAYS, model.params.iloc[1], model.rsquared
def compute_return_metrics(r, b=None, rf=None):
    r=r.dropna(); rf=pd.Series(0,index=r.index) if rf is None else rf.reindex(r.index)
    df=pd.concat([r,rf],axis=1).dropna(); df.columns=["r","rf"]; r=df.r; rf=df.rf; ex=r-rf
    ann_ret=annualized_return(r); ann_vol=annualized_vol(r); mdd,_=max_drawdown(r)
    var95,cvar95=historical_var_cvar(r,.95); var99,cvar99=historical_var_cvar(r,.99)
    pvar95,pcvar95=parametric_var_cvar(r,.95); pvar99,pcvar99=parametric_var_cvar(r,.99)
    avg_gain=r[r>0].mean() if (r>0).any() else np.nan; avg_loss=r[r<0].mean() if (r<0).any() else np.nan
    jb_p=jarque_bera(r)[1] if len(r)>20 else np.nan
    out={"Annualized Return":ann_ret,"Annualized Volatility":ann_vol,"Sharpe Ratio":safe_div(ex.mean()*TRADING_DAYS,ann_vol),"Sortino Ratio":safe_div(ex.mean()*TRADING_DAYS,downside_deviation(r)),"Calmar Ratio":safe_div(ann_ret,abs(mdd)),"Max Drawdown":mdd,"Downside Deviation":downside_deviation(r),"VaR 95% 1D Hist":var95,"CVaR 95% 1D Hist":cvar95,"VaR 99% 1D Hist":var99,"CVaR 99% 1D Hist":cvar99,"VaR 95% 1D Normal":pvar95,"CVaR 95% 1D Normal":pcvar95,"VaR 99% 1D Normal":pvar99,"CVaR 99% 1D Normal":pcvar99,"Win Rate":(r>0).mean(),"Payoff Ratio":safe_div(avg_gain,abs(avg_loss)),"Profit Factor":safe_div(r[r>0].sum(),abs(r[r<0].sum())),"Skewness":skew(r),"Excess Kurtosis":kurtosis(r,fisher=True),"Tail Ratio 95/5":safe_div(abs(np.quantile(r,.95)),abs(np.quantile(r,.05))),"Jarque-Bera p-value":jb_p,"Observations":len(r)}
    if b is not None:
        x=pd.concat([r,b.reindex(r.index),rf],axis=1).dropna(); x.columns=["r","b","rf"]
        if len(x)>60:
            active=x.r-x.b; alpha,beta,r2=regression_alpha_beta(x.r,x.b,x.rf)
            out.update({"Tracking Error":annualized_vol(active),"Information Ratio":safe_div(active.mean()*TRADING_DAYS,annualized_vol(active)),"Alpha Annualized":alpha,"Beta":beta,"R-squared":r2,"Up Capture":safe_div(x.loc[x.b>0,"r"].mean(),x.loc[x.b>0,"b"].mean()),"Down Capture":safe_div(x.loc[x.b<0,"r"].mean(),x.loc[x.b<0,"b"].mean())})
    return out

# ============================================================
# 4. DATA DOWNLOAD AND PREP
# ============================================================
def extract_close(raw,symbols):
    close=pd.DataFrame()
    if raw is None or raw.empty: return close
    if isinstance(raw.columns,pd.MultiIndex):
        if "Close" in raw.columns.get_level_values(1):
            for s in symbols:
                if (s,"Close") in raw.columns: close[s]=raw[(s,"Close")]
        elif "Close" in raw.columns.get_level_values(0):
            for s in symbols:
                if ("Close",s) in raw.columns: close[s]=raw[("Close",s)]
    elif "Close" in raw.columns and len(symbols)==1:
        close[symbols[0]]=raw["Close"]
    if not close.empty:
        close.index=pd.to_datetime(close.index); close=close.sort_index()
    return close
def extract_ohlcv_map(raw, symbols):
    """Extract per-symbol adjusted OHLCV frames from a multi-ticker Yahoo response.

    No missing prices are synthetically filled. Each frame retains only observed
    Open, High, Low, Close and Volume rows and is used by the integrated
    SupertrendPro Institutional engine.
    """
    out = {}
    if raw is None or raw.empty:
        return out
    required = ["Open", "High", "Low", "Close", "Volume"]
    for symbol in symbols:
        try:
            if isinstance(raw.columns, pd.MultiIndex):
                lvl0 = raw.columns.get_level_values(0)
                lvl1 = raw.columns.get_level_values(1)
                if symbol in lvl0:
                    d = raw[symbol].copy()
                elif symbol in lvl1:
                    d = raw.xs(symbol, axis=1, level=1).copy()
                else:
                    continue
            else:
                if len(symbols) != 1:
                    continue
                d = raw.copy()
            if not all(c in d.columns for c in required):
                continue
            d = d[required].copy()
            d.index = pd.to_datetime(d.index)
            if getattr(d.index, "tz", None) is not None:
                d.index = d.index.tz_localize(None)
            d = d.loc[~d.index.duplicated(keep="last")].sort_index()
            d = d.replace([np.inf, -np.inf], np.nan).dropna(how="any")
            d = d[(d["Close"] > 0) & (d["High"] >= d["Low"]) & (d["Volume"] >= 0)]
            if not d.empty:
                out[symbol] = d
        except Exception:
            continue
    return out

def download_all():
    today=pd.Timestamp.today().normalize(); start=today-pd.DateOffset(years=YEARS_BACK); end=today+pd.DateOffset(days=1)
    symbols=[]
    for cfg in UNIVERSE_CONFIGS.values(): symbols += list(cfg["universe"].keys()) + cfg["benchmarks"]
    for pair in CROSS_LISTING_PAIRS.values():
        symbols += [pair["local"], pair["adr"], pair["fx"]]
    symbols=list(dict.fromkeys(symbols+[RISK_FREE_TICKER]))
    print(f"[DATA] Downloading {len(symbols)} Yahoo Finance tickers with adjusted daily OHLCV...")
    raw=yf.download(symbols,start=start,end=end,interval="1d",auto_adjust=True,actions=False,group_by="ticker",threads=True,progress=False)
    close=extract_close(raw,symbols)
    ohlcv_map=extract_ohlcv_map(raw,symbols)
    if close.empty: raise RuntimeError("No Yahoo Finance data downloaded.")
    if RISK_FREE_TICKER not in close.columns: raise RuntimeError(f"Missing {RISK_FREE_TICKER}. No synthetic RF fallback used.")
    return close, ohlcv_map


def download_sox_history():
    """
    Downloads Philadelphia Semiconductor Index (^SOX) from 2018 onward.
    No proxy and no synthetic fallback are used for SOX diagnostics.
    """
    today = pd.Timestamp.today().normalize()
    end = today + pd.DateOffset(days=1)
    print(f"[SOX] Downloading Philadelphia Semiconductor Index {SOX_TICKER} from {SOX_HISTORY_START}...")
    raw = yf.download(
        SOX_TICKER,
        start=SOX_HISTORY_START,
        end=end,
        interval="1d",
        auto_adjust=True,
        actions=False,
        group_by="ticker",
        threads=True,
        progress=False,
    )

    if raw is None or raw.empty:
        raise RuntimeError(f"SOX diagnostics failed: Yahoo Finance returned no data for {SOX_TICKER}. No synthetic fallback is used.")

    if isinstance(raw.columns, pd.MultiIndex):
        close = extract_close(raw, [SOX_TICKER])
        if SOX_TICKER not in close.columns:
            raise RuntimeError(f"SOX diagnostics failed: close column missing for {SOX_TICKER}.")
        sox_close = close[SOX_TICKER].dropna()
    else:
        if "Close" not in raw.columns:
            raise RuntimeError(f"SOX diagnostics failed: close column missing for {SOX_TICKER}.")
        sox_close = raw["Close"].dropna()
        sox_close.index = pd.to_datetime(sox_close.index)

    sox_close = sox_close.sort_index()
    if sox_close.empty or sox_close.index.min() > pd.Timestamp("2018-03-01"):
        raise RuntimeError(f"SOX diagnostics failed: insufficient 2018 history for {SOX_TICKER}. No synthetic fallback is used.")

    return sox_close


def compute_sox_diagnostics():
    """
    Daily SOX log return diagnostics with 20D rolling mean +/- 2 sigma bands.
    Upper breach: log_return > rolling_mean + 2*rolling_sigma
    Lower breach: log_return < rolling_mean - 2*rolling_sigma
    """
    close = download_sox_history()
    log_ret = np.log(close / close.shift(1)).dropna()
    roll_mean = log_ret.rolling(SOX_BAND_WINDOW).mean()
    roll_sigma = log_ret.rolling(SOX_BAND_WINDOW).std(ddof=1)
    upper = roll_mean + 2.0 * roll_sigma
    lower = roll_mean - 2.0 * roll_sigma

    diag = pd.DataFrame({
        "SOX Close": close.reindex(log_ret.index),
        "Daily Log Return": log_ret,
        "Rolling Mean 20D": roll_mean,
        "Rolling Sigma 20D": roll_sigma,
        "Upper Band Mean+2Sigma": upper,
        "Lower Band Mean-2Sigma": lower,
    }).dropna()

    diag["Upper Breach"] = diag["Daily Log Return"] > diag["Upper Band Mean+2Sigma"]
    diag["Lower Breach"] = diag["Daily Log Return"] < diag["Lower Band Mean-2Sigma"]
    diag["Breach Type"] = np.where(diag["Upper Breach"], "Upper", np.where(diag["Lower Breach"], "Lower", "None"))
    diag["Upper Breach Magnitude"] = np.where(diag["Upper Breach"], diag["Daily Log Return"] - diag["Upper Band Mean+2Sigma"], np.nan)
    diag["Lower Breach Magnitude"] = np.where(diag["Lower Breach"], diag["Lower Band Mean-2Sigma"] - diag["Daily Log Return"], np.nan)
    diag["Breach Magnitude"] = diag[["Upper Breach Magnitude", "Lower Breach Magnitude"]].max(axis=1)

    breaches = diag[diag["Breach Type"].ne("None")].copy()
    breaches = breaches.reset_index().rename(columns={"index": "Date"})
    breaches["Direction"] = np.where(breaches["Breach Type"].eq("Upper"), "Positive upside return shock", "Negative downside return shock")
    breaches = breaches[[
        "Date", "Breach Type", "Direction", "Daily Log Return",
        "Rolling Mean 20D", "Rolling Sigma 20D",
        "Upper Band Mean+2Sigma", "Lower Band Mean-2Sigma",
        "Breach Magnitude", "SOX Close"
    ]].sort_values("Breach Magnitude", ascending=False)

    upper_breaches = breaches[breaches["Breach Type"].eq("Upper")]
    lower_breaches = breaches[breaches["Breach Type"].eq("Lower")]

    summary = pd.DataFrame([
        {"Metric": "Ticker", "Value": SOX_TICKER},
        {"Metric": "Index Name", "Value": "Philadelphia Semiconductor Index"},
        {"Metric": "History Start Requested", "Value": SOX_HISTORY_START},
        {"Metric": "Actual First Diagnostic Date", "Value": diag.index.min().strftime("%Y-%m-%d") if not diag.empty else "N/A"},
        {"Metric": "Actual Last Diagnostic Date", "Value": diag.index.max().strftime("%Y-%m-%d") if not diag.empty else "N/A"},
        {"Metric": "Band Window", "Value": f"{SOX_BAND_WINDOW} trading days"},
        {"Metric": "Total Observations After Bands", "Value": int(len(diag))},
        {"Metric": "Upper Band Breaches", "Value": int(diag["Upper Breach"].sum())},
        {"Metric": "Lower Band Breaches", "Value": int(diag["Lower Breach"].sum())},
        {"Metric": "Total Band Breaches", "Value": int(diag["Upper Breach"].sum() + diag["Lower Breach"].sum())},
        {"Metric": "Largest Upper Breach Date", "Value": upper_breaches["Date"].iloc[0].strftime("%Y-%m-%d") if not upper_breaches.empty else "N/A"},
        {"Metric": "Largest Lower Breach Date", "Value": lower_breaches["Date"].iloc[0].strftime("%Y-%m-%d") if not lower_breaches.empty else "N/A"},
    ])

    return {"close": close, "diag": diag, "breaches": breaches, "summary": summary}

def prepare_universe(uname,cfg,close):
    valid=[]; dq=[]; excl=[]; u=cfg["universe"]
    for t,m in u.items():
        if t not in close.columns:
            excl.append({"Ticker":t,"Name":m["name"],"Reason":"No close price returned by Yahoo Finance"}); continue
        s=close[t].dropna(); dq.append({"Universe":uname,"Ticker":t,"Name":m["name"],"Sector":m.get("sector","N/A"),"Theme":m.get("theme","N/A"),"Country":m.get("country","United States"),"Observations Raw":len(s),"Missing % Raw":close[t].isna().mean(),"First Date":s.index.min(),"Last Date":s.index.max()})
        if len(s)>=cfg["min_observations"]: valid.append(t)
        else: excl.append({"Ticker":t,"Name":m["name"],"Reason":f"Insufficient observations: {len(s)} < {cfg['min_observations']}"})
    bmarks=[]; bex=[]
    for b in cfg["benchmarks"]:
        if b in close.columns and close[b].dropna().shape[0]>=60: bmarks.append(b)
        else: bex.append({"Benchmark":b,"Name":INDEX_BENCHMARKS.get(b,{}).get("name",b),"Reason":"Unavailable or insufficient Yahoo Finance data"})
    primary=cfg["primary_benchmark"] if cfg["primary_benchmark"] in bmarks else (bmarks[0] if bmarks else None)
    if primary is None: raise RuntimeError(f"{uname}: no valid benchmark. No synthetic fallback.")
    if len(valid)<2: raise RuntimeError(f"{uname}: fewer than 2 valid stocks. No synthetic fallback.")
    prices=close[valid].dropna(how="any"); returns=prices.pct_change().dropna(how="any")
    rf=(close[RISK_FREE_TICKER].dropna()/100)/TRADING_DAYS; br=close[primary].dropna().pct_change().dropna()
    common=pd.concat([returns,br.rename("Primary_Benchmark"),rf.rename("RF_Daily")],axis=1).dropna(how="any")
    returns=common[valid]; prices=prices.reindex(common.index).dropna(how="any"); br=common["Primary_Benchmark"]; rf=common["RF_Daily"]
    brs={b: close[b].dropna().pct_change().dropna().reindex(returns.index).dropna() for b in bmarks}
    return {"name":uname,"cfg":cfg,"valid":valid,"prices":prices,"returns":returns,"primary":primary,"primary_return":br,"benchmark_returns":brs,"rf":rf,"data_quality":pd.DataFrame(dq),"exclusions":pd.DataFrame(excl),"benchmark_exclusions":pd.DataFrame(bex),"start":returns.index.min(),"end":returns.index.max()}

def construct_portfolio(ud):
    cfg=ud["cfg"]; u=cfg["universe"]; prices=ud["prices"]; returns=ud["returns"]; tickers=list(prices.columns); n=len(tickers); w=pd.Series(1/n,index=tickers)
    if cfg["capital_mode"]=="whole_share_usd":
        first=prices.iloc[0]; target=INITIAL_CAPITAL_USD*w; shares=np.floor(target/first).astype(int); invested=shares*first; cash=INITIAL_CAPITAL_USD-invested.sum(); values=prices.mul(shares,axis=1); nav=values.sum(axis=1)+cash; ret=nav.pct_change().dropna(); latest=values.iloc[-1]; curw=latest/(latest.sum()+cash)
        hold=pd.DataFrame({"Ticker":tickers,"Company":[u[t]["name"] for t in tickers],"Sector":[u[t].get("sector","N/A") for t in tickers],"Theme":[u[t].get("theme","N/A") for t in tickers],"Country":[u[t].get("country","United States") for t in tickers],"Initial Price":first.values,"Target Weight":w.values,"Target Dollars":target.values,"Whole Shares":shares.values,"Invested Dollars":invested.values,"Residual Cash Allocation":cash/n,"Latest Price":prices.iloc[-1].values,"Latest Market Value":latest.values,"Current Weight":curw.values}).sort_values("Current Weight",ascending=False)
        note="Whole-share 10M USD implementation with residual cash."
    else:
        ret=returns.mul(w,axis=1).sum(axis=1); nav=INITIAL_CAPITAL_USD*(1+ret).cumprod(); curw=w; cash=0.0
        hold=pd.DataFrame({"Ticker":tickers,"Company":[u[t]["name"] for t in tickers],"Sector":[u[t].get("sector","N/A") for t in tickers],"Theme":[u[t].get("theme","N/A") for t in tickers],"Country":[u[t].get("country","N/A") for t in tickers],"Article Role":[u[t].get("article_role","N/A") for t in tickers],"Target Weight":w.values,"Current Weight":w.values,"Latest Price":prices.iloc[-1].values,"Latest Market Value":np.nan}).sort_values("Ticker")
        note="Equal-weight actual-return basket. Mixed currencies; no synthetic FX conversion or USD whole-share implementation."
    return {"weights":w,"cash":cash,"portfolio_value":nav,"portfolio_return":ret,"current_weights":curw,"holdings":hold,"mode_note":note}

# ============================================================
# 5. ANALYTICS
# ============================================================
def asset_metrics(ud):
    rows=[]; u=ud["cfg"]["universe"]
    for t in ud["returns"].columns:
        rows.append({"Ticker":t,"Company":u[t]["name"],"Sector":u[t].get("sector","N/A"),"Theme":u[t].get("theme","N/A"),"Country":u[t].get("country","United States"),**compute_return_metrics(ud["returns"][t],ud["primary_return"],ud["rf"])})
    return pd.DataFrame(rows)
def risk_contrib(returns,weights,u):
    weights=weights.reindex(returns.columns).fillna(0); cov=returns.cov()*TRADING_DAYS; pv=float(weights.T@cov@weights); vol=np.sqrt(pv) if pv>=0 else np.nan
    if pd.notna(vol) and vol>0: mrc=cov@weights/vol; rc=weights*mrc; rcp=rc/vol
    else: mrc=rc=rcp=pd.Series(np.nan,index=weights.index)
    return pd.DataFrame({"Ticker":weights.index,"Company":[u[t]["name"] for t in weights.index],"Sector":[u[t].get("sector","N/A") for t in weights.index],"Theme":[u[t].get("theme","N/A") for t in weights.index],"Current Weight":weights.values,"Marginal Risk Contribution":mrc.values,"Total Risk Contribution":rc.values,"Risk Contribution %":rcp.values}).sort_values("Risk Contribution %",ascending=False)
def rolling_beta(p,b):
    df=pd.concat([p,b],axis=1).dropna(); df.columns=["p","b"]
    if len(df)<60: return pd.Series(dtype=float)
    w=min(ROLLING_BETA_WINDOW,len(df)); return (df.p.rolling(w,min_periods=max(60,w//2)).cov(df.b)/df.b.rolling(w,min_periods=max(60,w//2)).var()).dropna()
def bench_table(p,brs,rf):
    rows=[]
    for b,br in brs.items():
        df=pd.concat([p,br,rf],axis=1).dropna(); df.columns=["p","b","rf"]
        if len(df)<30: continue
        active=df.p-df.b; alpha,beta,r2=regression_alpha_beta(df.p,df.b,df.rf)
        rows.append({"Benchmark":b,"Benchmark Name":INDEX_BENCHMARKS.get(b,{}).get("name",b),"Region":INDEX_BENCHMARKS.get(b,{}).get("region","N/A"),"Benchmark Type":"ETF proxy exception only for TOPIX" if b=="1306.T" else "Market index / futures benchmark","Observations":len(df),"Portfolio Total Return":(1+df.p).prod()-1,"Benchmark Total Return":(1+df.b).prod()-1,"Active Total Return":(1+df.p).prod()-(1+df.b).prod(),"Correlation":df.p.corr(df.b),"Beta":beta,"Alpha Annualized":alpha,"R-squared":r2,"Tracking Error":annualized_vol(active),"Information Ratio":safe_div(active.mean()*TRADING_DAYS,annualized_vol(active))})
    return pd.DataFrame(rows)
def stress_tests(p,primary_br,primary):
    mx=p.index.max(); windows=[("COVID-19 Crash","2020-02-19","2020-03-23"),("2022 Inflation / Rate Selloff","2022-01-03","2022-10-12"),("Regional Bank Stress","2023-03-08","2023-03-17"),("2024 AI Momentum Check","2024-03-01","2024-04-19"),("2025 Rate / Tech Rotation Check","2025-01-01","2025-04-30"),("Latest 3 Months",(mx-pd.DateOffset(months=3)).strftime("%Y-%m-%d"),mx.strftime("%Y-%m-%d"))]
    rows=[]
    for name,s,e in windows:
        df=pd.concat([p.loc[p.index.to_series().between(pd.Timestamp(s),pd.Timestamp(e))],primary_br.loc[primary_br.index.to_series().between(pd.Timestamp(s),pd.Timestamp(e))]],axis=1).dropna(); df.columns=["p","b"] if len(df.columns)==2 else []
        if len(df)<3: rows.append({"Stress Window":name,"Start":s,"End":e,"Benchmark":primary,"Portfolio Return":np.nan,"Benchmark Return":np.nan,"Active Return":np.nan,"Portfolio Max Drawdown":np.nan,"Observations":len(df),"Comment":"Not enough overlapping data"}); continue
        pret=(1+df.p).prod()-1; bret=(1+df.b).prod()-1; mdd,_=max_drawdown(df.p)
        rows.append({"Stress Window":name,"Start":df.index.min().date(),"End":df.index.max().date(),"Benchmark":primary,"Portfolio Return":pret,"Benchmark Return":bret,"Active Return":pret-bret,"Portfolio Max Drawdown":mdd,"Observations":len(df),"Comment":"Actual overlapping daily returns"})
    return pd.DataFrame(rows)
def optimize(returns,rf):
    tickers=list(returns.columns); n=len(tickers); mu=returns.mean()*TRADING_DAYS; cov=returns.cov()*TRADING_DAYS; rfa=rf.mean()*TRADING_DAYS; x0=np.repeat(1/n,n); bounds=tuple((0,MAX_SINGLE_NAME_WEIGHT) for _ in range(n)); cons=({"type":"eq","fun":lambda w:np.sum(w)-1},)
    def perf(w):
        ret=float(w@mu.values); vol=float(np.sqrt(w.T@cov.values@w)); return ret,vol,safe_div(ret-rfa,vol)
    def volobj(w): return np.sqrt(w.T@cov.values@w)
    def negsr(w): return -perf(w)[2] if pd.notna(perf(w)[2]) else 1e6
    def rp(w):
        v=np.sqrt(w.T@cov.values@w)
        if v<=0: return 1e6
        rc=w*(cov.values@w/v); return np.sum((rc-np.repeat(v/n,n))**2)
    scenarios={"Equal Weight":x0}
    for name,obj in [("Min Volatility",volobj),("Max Sharpe",negsr),("Risk Parity",rp)]:
        try:
            res=minimize(obj,x0,method="SLSQP",bounds=bounds,constraints=cons,options={"maxiter":1000,"ftol":1e-10}); scenarios[name]=res.x if res.success else np.full(n,np.nan)
        except Exception: scenarios[name]=np.full(n,np.nan)
    tw=min(TRADING_DAYS,len(returns)); score=(((1+returns.tail(tw)).prod()-1)/(returns.tail(tw).std()*np.sqrt(TRADING_DAYS)).replace(0,np.nan)).rank(pct=True).fillna(.5); raw=score/score.sum(); cap=raw.clip(upper=MAX_SINGLE_NAME_WEIGHT); scenarios["Momentum Risk-Adjusted"]=(cap/cap.sum()).values
    wt=pd.DataFrame({"Ticker":tickers}); rows=[]
    for name,w in scenarios.items():
        wt[name]=w
        if np.isfinite(w).all():
            ret,vol,sr=perf(w); rows.append({"Scenario":name,"Expected Return Ann.":ret,"Expected Volatility Ann.":vol,"Expected Sharpe":sr,"Max Single Name Weight":np.max(w),"Effective Number of Names":1/np.sum(w**2)})
        else: rows.append({"Scenario":name,"Expected Return Ann.":np.nan,"Expected Volatility Ann.":np.nan,"Expected Sharpe":np.nan,"Max Single Name Weight":np.nan,"Effective Number of Names":np.nan})
    return wt,pd.DataFrame(rows)
def analyze(uname,cfg,close):
    print(f"[UNIVERSE] {uname}"); ud=prepare_universe(uname,cfg,close); pf=construct_portfolio(ud); pr=pf["portfolio_return"]; primary=ud["primary"]; br=ud["primary_return"].reindex(pr.index); rf=ud["rf"].reindex(pr.index)
    am=asset_metrics(ud); rc=risk_contrib(ud["returns"].reindex(pr.index).dropna(),pf["current_weights"],cfg["universe"]); bt=bench_table(pr,ud["benchmark_returns"],rf); st=stress_tests(pr,br,primary); ow,os=optimize(ud["returns"],ud["rf"])
    if not ow.empty:
        ow.insert(1,"Company",[cfg["universe"][t]["name"] for t in ow.Ticker]); ow.insert(2,"Sector",[cfg["universe"][t].get("sector","N/A") for t in ow.Ticker]); ow.insert(3,"Theme",[cfg["universe"][t].get("theme","N/A") for t in ow.Ticker])
    print(f"  valid={len(ud['valid'])}, sample={ud['start'].date()} to {ud['end'].date()}, obs={len(ud['returns'])}")
    return {"name":uname,"ud":ud,"pf":pf,"pm":compute_return_metrics(pr,br,rf),"am":am,"rc":rc,"bt":bt,"st":st,"ow":ow,"os":os}


# ============================================================
# 5B. SUPERTRENDPRO INSTITUTIONAL INTEGRATION
# ============================================================
def stp_ema(s, span):
    return pd.Series(s, dtype=float).ewm(span=span, adjust=False, min_periods=span).mean()

def stp_rsi(s, period=14):
    s = pd.Series(s, dtype=float)
    delta = s.diff(); gain = delta.clip(lower=0); loss = -delta.clip(upper=0)
    avg_gain = gain.ewm(alpha=1/period, adjust=False, min_periods=period).mean()
    avg_loss = loss.ewm(alpha=1/period, adjust=False, min_periods=period).mean()
    rs = avg_gain / avg_loss.replace(0, np.nan)
    return 100 - 100/(1+rs)

def stp_atr(high, low, close, period=14):
    high = pd.Series(high, dtype=float); low = pd.Series(low, dtype=float); close = pd.Series(close, dtype=float)
    prev = close.shift(1)
    tr = pd.concat([high-low, (high-prev).abs(), (low-prev).abs()], axis=1).max(axis=1)
    return tr.ewm(alpha=1/period, adjust=False, min_periods=period).mean()

def stp_cci(high, low, close, period=20):
    tp = (pd.Series(high, dtype=float)+pd.Series(low, dtype=float)+pd.Series(close, dtype=float))/3
    sma = tp.rolling(period).mean()
    mad = tp.rolling(period).apply(lambda x: np.mean(np.abs(x-np.mean(x))), raw=True)
    return (tp-sma)/(0.015*mad.replace(0, np.nan))

def stp_adx(high, low, close, period=14):
    high = pd.Series(high, dtype=float); low = pd.Series(low, dtype=float); close = pd.Series(close, dtype=float)
    up = high.diff(); down = -low.diff()
    plus_dm = pd.Series(np.where((up>down)&(up>0), up, 0.0), index=high.index)
    minus_dm = pd.Series(np.where((down>up)&(down>0), down, 0.0), index=high.index)
    atrv = stp_atr(high, low, close, period)
    plus_di = 100*plus_dm.ewm(alpha=1/period, adjust=False, min_periods=period).mean()/atrv.replace(0,np.nan)
    minus_di = 100*minus_dm.ewm(alpha=1/period, adjust=False, min_periods=period).mean()/atrv.replace(0,np.nan)
    dx = 100*(plus_di-minus_di).abs()/(plus_di+minus_di).replace(0,np.nan)
    return dx.ewm(alpha=1/period, adjust=False, min_periods=period).mean()

def stp_macd(close, fast=12, slow=26, signal=9):
    line = stp_ema(close, fast)-stp_ema(close, slow)
    sig = stp_ema(line, signal)
    return line, sig, line-sig

def stp_bbands(close, period=20, ndev=2.0):
    close = pd.Series(close, dtype=float)
    mid = close.rolling(period).mean(); sd = close.rolling(period).std(ddof=1)
    return mid+ndev*sd, mid, mid-ndev*sd

def stp_compute_indicators(df):
    x = df.copy().sort_index()
    h,l,c,v = x["High"].astype(float),x["Low"].astype(float),x["Close"].astype(float),x["Volume"].astype(float)
    x["RSI"] = stp_rsi(c,14); x["EMA_20"] = stp_ema(c,20); x["EMA_50"] = stp_ema(c,50)
    x["EMA_100"] = stp_ema(c,100); x["EMA_200"] = stp_ema(c,200)
    x["CCI"] = stp_cci(h,l,c,20); x["ATR"] = stp_atr(h,l,c,14); x["ADX"] = stp_adx(h,l,c,14)
    m,s,hist = stp_macd(c,12,26,9); x["MACD"],x["MACD_SIGNAL"],x["MACD_HIST"] = m,s,hist
    up,mid,lo = stp_bbands(c,20,2); x["BB_UPPER"],x["BB_MID"],x["BB_LOWER"] = up,mid,lo
    x["Return"] = c.pct_change(); x["Log_Return"] = np.log(c/c.shift(1)); x["Dollar_Volume"] = c*v
    x["Vol_20D_Ann"] = x["Return"].rolling(20).std(ddof=1)*np.sqrt(TRADING_DAYS)
    x["Vol_63D_Ann"] = x["Return"].rolling(63).std(ddof=1)*np.sqrt(TRADING_DAYS)
    x["Momentum_20D"] = c.pct_change(20); x["Momentum_63D"] = c.pct_change(63)
    x["Momentum_126D"] = c.pct_change(126); x["Momentum_252D"] = c.pct_change(252)
    x["High_252D"] = c.rolling(252).max(); x["Low_252D"] = c.rolling(252).min()
    x["Pct_From_52W_High"] = c/x["High_252D"]-1; x["Pct_From_52W_Low"] = c/x["Low_252D"]-1
    x["Drawdown"] = c/c.cummax()-1; x["ATR_Pct"] = x["ATR"]/c.replace(0,np.nan)
    return x.replace([np.inf,-np.inf],np.nan)

def stp_compute_supertrend(df, period=10, multiplier=2.5):
    high,low,close = df["High"].astype(float),df["Low"].astype(float),df["Close"].astype(float)
    atrv = stp_atr(high,low,close,period); hl2=(high+low)/2
    bub=hl2+multiplier*atrv; blb=hl2-multiplier*atrv
    fub=pd.Series(np.nan,index=df.index,dtype=float); flb=fub.copy(); direction=pd.Series(0,index=df.index,dtype=int); line=fub.copy()
    first=atrv.first_valid_index()
    if first is None: return line,direction
    start=df.index.get_loc(first)
    for i in range(start,len(df)):
        if pd.isna(bub.iloc[i]) or pd.isna(blb.iloc[i]): continue
        if i==start or pd.isna(fub.iloc[i-1]) or pd.isna(flb.iloc[i-1]):
            fub.iloc[i]=bub.iloc[i]; flb.iloc[i]=blb.iloc[i]; direction.iloc[i]=1; line.iloc[i]=flb.iloc[i]; continue
        fub.iloc[i]=bub.iloc[i] if (bub.iloc[i]<fub.iloc[i-1] or close.iloc[i-1]>fub.iloc[i-1]) else fub.iloc[i-1]
        flb.iloc[i]=blb.iloc[i] if (blb.iloc[i]>flb.iloc[i-1] or close.iloc[i-1]<flb.iloc[i-1]) else flb.iloc[i-1]
        prev=direction.iloc[i-1] if direction.iloc[i-1] in (1,-1) else 1
        if prev==1 and close.iloc[i]<flb.iloc[i]: direction.iloc[i]=-1
        elif prev==-1 and close.iloc[i]>fub.iloc[i]: direction.iloc[i]=1
        else: direction.iloc[i]=prev
        line.iloc[i]=flb.iloc[i] if direction.iloc[i]==1 else fub.iloc[i]
    return line,direction

def stp_performance_metrics(ret, benchmark=None):
    r=pd.Series(ret,dtype=float).replace([np.inf,-np.inf],np.nan).dropna()
    if r.empty: return {"Total Return":np.nan,"CAGR":np.nan,"Ann Vol":np.nan,"Sharpe":np.nan,"Sortino":np.nan,"Max Drawdown":np.nan,"Win Rate":np.nan,"Beta":np.nan,"Information Ratio":np.nan}
    eq=(1+r).cumprod(); total=eq.iloc[-1]-1; years=max(len(r)/TRADING_DAYS,1/TRADING_DAYS)
    cagr=(1+total)**(1/years)-1 if total>-1 else np.nan; vol=r.std(ddof=1)*np.sqrt(TRADING_DAYS)
    downside=r[r<0].std(ddof=1)*np.sqrt(TRADING_DAYS) if (r<0).sum()>2 else np.nan
    dd=eq/eq.cummax()-1; beta=ir=np.nan
    if benchmark is not None:
        p=pd.concat([r.rename("s"),pd.Series(benchmark,dtype=float).rename("b")],axis=1).dropna()
        if len(p)>20 and p["b"].var(ddof=1)>0:
            beta=p["s"].cov(p["b"])/p["b"].var(ddof=1); active=p["s"]-p["b"]
            te=active.std(ddof=1)*np.sqrt(TRADING_DAYS); ir=active.mean()*TRADING_DAYS/te if te>0 else np.nan
    active_days=r[r!=0]
    return {"Total Return":total,"CAGR":cagr,"Ann Vol":vol,"Sharpe":cagr/vol if vol>0 else np.nan,"Sortino":cagr/downside if pd.notna(downside) and downside>0 else np.nan,"Max Drawdown":dd.min(),"Win Rate":(active_days>0).mean() if len(active_days) else np.nan,"Beta":beta,"Information Ratio":ir}

def stp_run_trailing_backtest(df, entry_state, exit_state, atr_mult=2.0, benchmark=None):
    x=df.copy(); entry_state=pd.Series(entry_state,index=x.index).fillna(False); exit_state=pd.Series(exit_state,index=x.index).fillna(False)
    position=0; peak=np.nan; stop=np.nan; entry_price=np.nan; positions=[]; signals=[]; stops=[]; trades=[]; entry_date=None
    for i,(dt,row) in enumerate(x.iterrows()):
        price=float(row["Close"]); atrv=float(row["ATR"]) if pd.notna(row["ATR"]) else np.nan; signal=0
        if position==1 and pd.notna(atrv):
            peak=max(peak,price); new_stop=peak-atr_mult*atrv; stop=new_stop if pd.isna(stop) else max(stop,new_stop)
        hit_stop=position==1 and pd.notna(stop) and price<=stop
        if position==0 and bool(entry_state.iloc[i]) and pd.notna(atrv):
            position=1; peak=price; stop=price-atr_mult*atrv; entry_price=price; entry_date=dt; signal=1
        elif position==1 and (hit_stop or bool(exit_state.iloc[i])):
            ret=price/entry_price-1 if entry_price>0 else np.nan
            trades.append({"Entry Date":entry_date,"Exit Date":dt,"Entry Price":entry_price,"Exit Price":price,"Trade Return":ret,"Holding Days":(dt-entry_date).days if entry_date is not None else np.nan,"Exit Reason":"ATR Stop" if hit_stop else "Rule Exit"})
            position=0; peak=stop=entry_price=np.nan; entry_date=None; signal=-1
        positions.append(position); signals.append(signal); stops.append(stop if position==1 else np.nan)
    x["Position"]=positions; x["Signal"]=signals; x["ATR_Stop"]=stops; x["Return"]=x["Close"].pct_change().fillna(0)
    x["Gross Strategy Return"]=x["Position"].shift(1).fillna(0)*x["Return"]
    turnover=x["Position"].diff().abs().fillna(x["Position"].abs()); one_way=(INSTITUTIONAL_TRANSACTION_COST_BPS+INSTITUTIONAL_SLIPPAGE_BPS)/10000
    x["Trading Cost"]=turnover*one_way; x["Strategy Return"]=x["Gross Strategy Return"]-x["Trading Cost"]
    x["Strategy Equity"]=(1+x["Strategy Return"]).cumprod(); x["Buy Hold Equity"]=(1+x["Return"]).cumprod()
    return x,pd.DataFrame(trades),stp_performance_metrics(x["Strategy Return"],benchmark)

def stp_backtest_supertrend(df, benchmark=None):
    x=df.copy(); line,direction=stp_compute_supertrend(x,10,2.5); x["ST_Line"]=line; x["ST_Dir"]=direction
    entry=(x["ST_Dir"]==1)&(x["Close"]>x["EMA_200"]); exit_state=(x["ST_Dir"]==-1)&(x["ST_Dir"].shift(1)==1)
    return stp_run_trailing_backtest(x,entry,exit_state,2.0,benchmark)

def stp_backtest_macd(df, benchmark=None):
    x=df.copy(); entry=(x["MACD"]>x["MACD_SIGNAL"])&(x["Close"]>x["EMA_200"]); exit_state=(x["MACD"]<x["MACD_SIGNAL"])&(x["MACD"].shift(1)>=x["MACD_SIGNAL"].shift(1))
    return stp_run_trailing_backtest(x,entry,exit_state,2.0,benchmark)

def stp_run_leading_signal_lab(df, benchmark=None):
    x=df.copy().sort_index(); close=x["Close"].astype(float); volume=x["Volume"].astype(float)
    x["Breakout_20"] = close > close.shift(1).rolling(20,min_periods=10).max()
    x["Volume_Pass"] = volume > volume.rolling(20,min_periods=10).median()
    conditions=pd.DataFrame({
        "Price>EMA50":close>x["EMA_50"],"EMA50>EMA200":x["EMA_50"]>x["EMA_200"],"MACD+":x["MACD"]>x["MACD_SIGNAL"],
        "Healthy RSI":x["RSI"].between(45,72),"ADX Trend":x["ADX"]>18,"20D Breakout":x["Breakout_20"],"Volume":x["Volume_Pass"]
    },index=x.index).fillna(False)
    x["Signal Score"]=conditions.sum(axis=1); desired=(x["Signal Score"]>=4).astype(int)
    desired[x["Signal Score"]<=2]=0; x["Signal Position"]=desired.shift(1).fillna(0)
    x["Signal Event"]=np.where((desired==1)&(desired.shift(1).fillna(0)==0),"BUY",np.where((desired==0)&(desired.shift(1).fillna(0)==1),"SELL",""))
    ret=close.pct_change().fillna(0); turnover=x["Signal Position"].diff().abs().fillna(x["Signal Position"].abs())
    cost=turnover*(INSTITUTIONAL_TRANSACTION_COST_BPS+INSTITUTIONAL_SLIPPAGE_BPS)/10000
    x["Signal Strategy Return"]=x["Signal Position"]*ret-cost; x["Signal Strategy Equity"]=(1+x["Signal Strategy Return"]).cumprod(); x["Signal Buy Hold Equity"]=(1+ret).cumprod()
    return x,stp_performance_metrics(x["Signal Strategy Return"],benchmark)

def stp_safe_percentile_rank(series,window=252):
    return pd.Series(series,dtype=float).rolling(window,min_periods=max(40,window//4)).apply(lambda a: pd.Series(a).rank(pct=True).iloc[-1],raw=False)

def stp_build_institutional_signal_engine(df, benchmark_close=None, benchmark_returns=None, forward_horizon=60):
    x=df.copy().sort_index(); close=x["Close"].astype(float); ret=close.pct_change(); volume=x["Volume"].astype(float)
    ema50=close.ewm(span=50,adjust=False,min_periods=50).mean(); ema200=close.ewm(span=200,adjust=False,min_periods=200).mean()
    roc20=close.pct_change(20); roc60=close.pct_change(60); vol20=ret.rolling(20,min_periods=20).std()*np.sqrt(TRADING_DAYS); vol60=ret.rolling(60,min_periods=40).std()*np.sqrt(TRADING_DAYS)
    drawdown=close/close.cummax()-1; atr_pct=x["ATR"]/close.replace(0,np.nan); vol_med20=volume.rolling(20,min_periods=20).median(); obv=(np.sign(ret.fillna(0))*volume).cumsum(); obv_ma20=obv.rolling(20,min_periods=20).mean()
    if benchmark_close is not None:
        bclose=pd.Series(benchmark_close,dtype=float).reindex(x.index).ffill(); rs=close/bclose.replace(0,np.nan); rs20=rs.pct_change(20); rs60=rs.pct_change(60); market_pass=(bclose>bclose.ewm(span=200,adjust=False,min_periods=200).mean()).astype(float)
    else:
        bclose=None; rs20=rs60=pd.Series(0.0,index=x.index); market_pass=pd.Series(0.5,index=x.index)
    if benchmark_returns is not None:
        bret=pd.Series(benchmark_returns,dtype=float).reindex(x.index); pair=pd.concat([ret.rename("a"),bret.rename("b")],axis=1); cov=pair["a"].rolling(60,min_periods=40).cov(pair["b"]); var=pair["b"].rolling(60,min_periods=40).var(); beta60=cov/var.replace(0,np.nan); alpha60=(pair["a"].rolling(60,min_periods=40).mean()-beta60*pair["b"].rolling(60,min_periods=40).mean())*TRADING_DAYS
    else:
        beta60=alpha60=pd.Series(np.nan,index=x.index)
    factors={
        "Trend Score":7*(close>ema50).astype(float)+7*(ema50>ema200).astype(float)+6*((x["ADX"]>18)&(x["ST_Dir"]>=0)).astype(float),
        "Momentum Score":6*(roc20>0).astype(float)+5*(roc60>0).astype(float)+5*x["RSI"].between(50,72).astype(float)+4*((x["MACD_HIST"]>0)&(x["MACD_HIST"]>x["MACD_HIST"].shift(1))).astype(float),
        "Relative Strength Score":8*(rs20>0).astype(float)+7*(rs60>0).astype(float),
        "Volume Score":7*(volume>vol_med20).astype(float)+5*(obv>obv_ma20).astype(float)+3*(volume.pct_change(5)>0).astype(float),
        "Volatility Score":5*(vol20<=vol60).astype(float)+3*(stp_safe_percentile_rank(vol20,252)<=0.75).astype(float)+2*(atr_pct<=atr_pct.rolling(60,min_periods=30).median()).astype(float),
        "Risk Score":4*(drawdown>-0.15).astype(float)+3*((beta60.isna())|(beta60<=1.25)).astype(float)+3*((alpha60.isna())|(alpha60>0)).astype(float),
        "Market Regime Score":10*market_pass.clip(0,1),
    }
    maxima={"Trend Score":20.0,"Momentum Score":20.0,"Relative Strength Score":15.0,"Volume Score":15.0,"Volatility Score":10.0,"Risk Score":10.0,"Market Regime Score":10.0}
    for k,v in factors.items(): x[k]=pd.Series(v,index=x.index).fillna(0)
    x["Institutional Score"]=sum(x[k] for k in maxima).clip(0,100)
    normalized=pd.DataFrame({k:pd.to_numeric(x[k],errors="coerce").fillna(0)/m for k,m in maxima.items()},index=x.index)
    agreement=1-normalized.std(axis=1).clip(0,0.5)/0.5; stability=1-(x["Institutional Score"].rolling(20,min_periods=5).std()/25).clip(0,1)
    x["Confidence Score"]=(100*(0.6*agreement+0.4*stability)).clip(0,100)
    x["Recommendation"]=pd.cut(x["Institutional Score"],[-np.inf,25,40,60,75,np.inf],labels=["STRONG SELL","SELL","HOLD","BUY","STRONG BUY"]).astype(str)
    fwd=f"Forward {forward_horizon}D Return"; x[fwd]=close.shift(-forward_horizon)/close-1
    if bclose is not None: x[f"Forward {forward_horizon}D Active Return"]=x[fwd]-(bclose.shift(-forward_horizon)/bclose-1)
    else: x[f"Forward {forward_horizon}D Active Return"]=np.nan
    current=float(x["Institutional Score"].iloc[-1]); resolved=x.iloc[:-forward_horizon].dropna(subset=[fwd]) if len(x)>forward_horizon else x.iloc[0:0]
    peers=resolved[(resolved["Institutional Score"]>=current-7.5)&(resolved["Institutional Score"]<=current+7.5)]
    if len(peers)<20 and len(resolved): peers=resolved.assign(_d=(resolved["Institutional Score"]-current).abs()).nsmallest(min(60,len(resolved)),"_d")
    active_col=f"Forward {forward_horizon}D Active Return"; latest=x.iloc[-1]
    summary={"Institutional Score":float(latest["Institutional Score"]),"Confidence Score":float(latest["Confidence Score"]),"Recommendation":str(latest["Recommendation"]),f"Positive Return Probability {forward_horizon}D %":float((peers[fwd]>0).mean()*100) if len(peers) else np.nan,f"+10% Probability {forward_horizon}D %":float((peers[fwd]>=0.10).mean()*100) if len(peers) else np.nan,f"Outperform Benchmark Probability {forward_horizon}D %":float((peers[active_col]>0).mean()*100) if len(peers) and peers[active_col].notna().any() else np.nan,"Historical Analog Count":int(len(peers))}
    contribution=pd.DataFrame({"Factor":list(maxima),"Score":[float(latest[k]) for k in maxima],"Maximum":list(maxima.values())}); contribution["Contribution %"]=contribution["Score"]/contribution["Maximum"]*100
    return x,contribution,summary

def stp_technical_grade(last):
    score=0; reasons=[]
    tests=[(last["Close"]>last["EMA_200"],20,"Price>EMA200"),(last["EMA_50"]>last["EMA_200"],15,"EMA50>EMA200"),(last["MACD"]>last["MACD_SIGNAL"],12,"MACD+"),(45<=last["RSI"]<=70,15,"Healthy RSI"),(last["ADX"]>=20,12,"ADX trend"),(last["Momentum_63D"]>0,10,"3M momentum+"),(last["Momentum_126D"]>0,8,"6M momentum+"),(last["Pct_From_52W_High"]>-0.15,8,"Near 52W high")]
    for passed,pts,label in tests:
        if bool(passed): score+=pts; reasons.append(label)
    return min(score,100),", ".join(reasons)

def analyze_supertrend_institutional(results, ohlcv_map, close):
    all_results={}
    for res in results:
        uname=res["name"]; cfg=res["ud"]["cfg"]; benchmark=res["ud"]["primary"]
        bclose=close[benchmark].dropna() if benchmark in close.columns else None; bret=bclose.pct_change().dropna() if bclose is not None else None
        rows=[]; strategy_rows=[]; factor_rows=[]; exclusions=[]; details={}
        print(f"[INSTITUTIONAL] {uname} — analyzing {len(res['ud']['valid'])} valid names")
        for ticker in res["ud"]["valid"]:
            meta=cfg["universe"][ticker]; raw=ohlcv_map.get(ticker)
            if raw is None or len(raw)<INSTITUTIONAL_MIN_OBS:
                exclusions.append({"Ticker":ticker,"Company":meta["name"],"Reason":f"Insufficient adjusted OHLCV for institutional engine: {0 if raw is None else len(raw)} < {INSTITUTIONAL_MIN_OBS}"}); continue
            try:
                ind=stp_compute_indicators(raw); ind=ind.dropna(subset=["Close","EMA_50","EMA_200","ATR","ADX","MACD","MACD_SIGNAL"])
                if len(ind)<INSTITUTIONAL_MIN_OBS: raise ValueError(f"Indicator-ready observations {len(ind)}")
                st_line,st_dir=stp_compute_supertrend(ind,10,2.5); ind["ST_Line"]=st_line; ind["ST_Dir"]=st_dir
                aligned_bret=bret.reindex(ind.index) if bret is not None else None; aligned_bclose=bclose.reindex(ind.index).ffill() if bclose is not None else None
                st_bt,st_trades,st_stats=stp_backtest_supertrend(ind,aligned_bret); macd_bt,macd_trades,macd_stats=stp_backtest_macd(ind,aligned_bret); lab_df,lab_stats=stp_run_leading_signal_lab(ind,aligned_bret)
                score_df,factors,decision=stp_build_institutional_signal_engine(ind,aligned_bclose,aligned_bret,INSTITUTIONAL_FORWARD_HORIZON)
                last=score_df.iloc[-1]; grade,reasons=stp_technical_grade(last)
                strategy_candidates={"Smart Supertrend":st_stats,"MACD + ATR":macd_stats,"Leading Signal Lab":lab_stats}
                best_name=max(strategy_candidates,key=lambda k: -np.inf if pd.isna(strategy_candidates[k].get("Sharpe")) else strategy_candidates[k].get("Sharpe"))
                best=strategy_candidates[best_name]
                row={"Universe":uname,"Ticker":ticker,"Company":meta["name"],"Country":meta.get("country","United States"),"Sector":meta.get("sector","N/A"),"Theme":meta.get("theme","N/A"),"Last Price":float(last["Close"]),"Trend State":"BULLISH" if last["Close"]>last["EMA_200"] else "BEARISH","Supertrend Direction":"UP" if int(last["ST_Dir"])==1 else "DOWN","Technical Grade":grade,"Technical Reasons":reasons,"Institutional Score":decision["Institutional Score"],"Confidence Score":decision["Confidence Score"],"Recommendation":decision["Recommendation"],"Positive 60D Probability %":decision.get("Positive Return Probability 60D %"),"+10% 60D Probability %":decision.get("+10% Probability 60D %"),"Outperform Benchmark 60D Probability %":decision.get("Outperform Benchmark Probability 60D %"),"Historical Analog Count":decision["Historical Analog Count"],"Best Strategy":best_name,"Best Strategy CAGR":best.get("CAGR"),"Best Strategy Sharpe":best.get("Sharpe"),"Best Strategy Max Drawdown":best.get("Max Drawdown"),"Best Strategy Win Rate":best.get("Win Rate"),"Benchmark":benchmark}
                rows.append(row)
                for sname,sstats in strategy_candidates.items(): strategy_rows.append({"Universe":uname,"Ticker":ticker,"Company":meta["name"],"Strategy":sname,**sstats,"Trade Count":len(st_trades) if sname=="Smart Supertrend" else (len(macd_trades) if sname=="MACD + ATR" else np.nan)})
                f=factors.copy(); f.insert(0,"Ticker",ticker); f.insert(1,"Company",meta["name"]); f.insert(2,"Universe",uname); factor_rows.append(f)
                details[ticker]={"meta":meta,"indicator":ind,"supertrend_backtest":st_bt,"macd_backtest":macd_bt,"leading_lab":lab_df,"score":score_df,"factors":factors,"decision":decision}
            except Exception as exc:
                exclusions.append({"Ticker":ticker,"Company":meta["name"],"Reason":f"Institutional engine calculation failed: {exc}"})
        all_results[uname]={"ranking":pd.DataFrame(rows).sort_values(["Institutional Score","Confidence Score"],ascending=False) if rows else pd.DataFrame(),"strategies":pd.DataFrame(strategy_rows),"factors":pd.concat(factor_rows,ignore_index=True) if factor_rows else pd.DataFrame(),"exclusions":pd.DataFrame(exclusions),"details":details,"benchmark":benchmark}
        gc.collect()
    return all_results

def compute_cross_listing_analysis(close):
    summaries=[]; histories={}; exclusions=[]
    for name,cfg in CROSS_LISTING_PAIRS.items():
        required=[cfg["local"],cfg["adr"],cfg["fx"]]
        if not all(s in close.columns for s in required):
            exclusions.append({"Pair":name,"Reason":"One or more Yahoo Finance series unavailable","Required":", ".join(required)}); continue
        d=pd.concat([close[cfg["local"]].rename("Local"),close[cfg["adr"]].rename("ADR"),close[cfg["fx"]].rename("FX")],axis=1).dropna()
        if len(d)<2:
            exclusions.append({"Pair":name,"Reason":f"Insufficient overlapping observations: {len(d)}","Required":", ".join(required)}); continue
        if cfg["fx_mode"]=="LOCAL_PER_USD": d["Local Equivalent USD per ADR"]=d["Local"]*cfg["ordinary_per_adr"]/d["FX"]
        else: d["Local Equivalent USD per ADR"]=d["Local"]*cfg["ordinary_per_adr"]*d["FX"]
        d["Premium Discount"]=d["ADR"]/d["Local Equivalent USD per ADR"]-1
        d["Local Return"]=d["Local Equivalent USD per ADR"].pct_change(); d["ADR Return"]=d["ADR"].pct_change(); d["Return Difference"]=d["ADR Return"]-d["Local Return"]
        d["Rolling Correlation 20D"]=d["ADR Return"].rolling(20,min_periods=5).corr(d["Local Return"]); d["Premium Z 20D"]=(d["Premium Discount"]-d["Premium Discount"].rolling(20,min_periods=5).mean())/d["Premium Discount"].rolling(20,min_periods=5).std(ddof=1)
        d["Local Normalized"]=d["Local Equivalent USD per ADR"]/d["Local Equivalent USD per ADR"].iloc[0]*100; d["ADR Normalized"]=d["ADR"]/d["ADR"].iloc[0]*100
        latest=d.iloc[-1]; corr=d[["ADR Return","Local Return"]].dropna().corr().iloc[0,1] if d[["ADR Return","Local Return"]].dropna().shape[0]>1 else np.nan
        summaries.append({"Pair":name,"Local Ticker":cfg["local"],"ADR Ticker":cfg["adr"],"FX Ticker":cfg["fx"],"Ordinary Shares per ADR":cfg["ordinary_per_adr"],"Observations":len(d),"First Date":d.index.min(),"Last Date":d.index.max(),"Latest Local Equivalent USD":latest["Local Equivalent USD per ADR"],"Latest ADR Price USD":latest["ADR"],"Latest Premium / Discount":latest["Premium Discount"],"Latest Premium Z 20D":latest["Premium Z 20D"],"Return Correlation":corr,"Note":cfg["note"]+" Closing-time asynchrony and market microstructure can affect the measured premium."})
        histories[name]=d
    return {"summary":pd.DataFrame(summaries),"histories":histories,"exclusions":pd.DataFrame(exclusions)}

# ============================================================
# 6. CHARTS
# ============================================================
def layout(fig, title, h=None):
    """
    Full-width institutional Plotly layout.
    Width is deliberately not fixed. CSS gives the chart full page width;
    autosize=True and responsive=True make Plotly fill that available width.
    """
    if h is None:
        h = CHART_FULL_HEIGHT
    fig.update_layout(
        template=PLOT_TEMPLATE,
        title=dict(text=title, x=.01, xanchor="left", font=dict(size=24)),
        autosize=True,
        height=h,
        margin=dict(l=72, r=48, t=96, b=72),
        font=dict(family="Arial, Helvetica, sans-serif", size=15),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        hovermode="x unified"
    )
    return fig

def div(fig, js=False):
    return pio.to_html(
        fig,
        full_html=False,
        include_plotlyjs=js,
        config=PLOT_CONFIG,
        default_width="100%",
        default_height="100%"
    )


def chart_sox_log_return_bands(sox):
    d = sox["diag"]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=d.index, y=d["Daily Log Return"], mode="lines", name="SOX daily log return"))
    fig.add_trace(go.Scatter(x=d.index, y=d["Rolling Mean 20D"], mode="lines", name="20D rolling mean"))
    fig.add_trace(go.Scatter(x=d.index, y=d["Upper Band Mean+2Sigma"], mode="lines", name="Upper band: mean + 2σ"))
    fig.add_trace(go.Scatter(x=d.index, y=d["Lower Band Mean-2Sigma"], mode="lines", name="Lower band: mean - 2σ"))

    up = d[d["Upper Breach"]]
    low = d[d["Lower Breach"]]
    if not up.empty:
        fig.add_trace(go.Scatter(x=up.index, y=up["Daily Log Return"], mode="markers", name="Upper breaches", marker=dict(size=7, symbol="triangle-up")))
    if not low.empty:
        fig.add_trace(go.Scatter(x=low.index, y=low["Daily Log Return"], mode="markers", name="Lower breaches", marker=dict(size=7, symbol="triangle-down")))

    fig.update_yaxes(title="Daily log return", tickformat=".2%")
    fig.update_xaxes(title="Date")
    return layout(fig, "Philadelphia Semiconductor Index (^SOX) — Daily Log Returns with 20D Mean ± 2σ Bands", CHART_EXTRA_LARGE_HEIGHT)


def chart_sox_close_index(sox):
    close = sox["close"]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=close.index, y=close, mode="lines", name="^SOX close"))
    fig.update_yaxes(title="Index level")
    fig.update_xaxes(title="Date")
    return layout(fig, "Philadelphia Semiconductor Index (^SOX) — Historical Close Level Since 2018", CHART_FULL_HEIGHT)
def chart_growth(res):
    pv=res["pf"]["portfolio_value"]; fig=go.Figure(); fig.add_trace(go.Scatter(x=pv.index,y=pv/pv.iloc[0]*100,mode="lines",name="Portfolio / Basket"))
    for b,br in res["ud"]["benchmark_returns"].items():
        a=br.reindex(pv.index).dropna()
        if len(a)>20: fig.add_trace(go.Scatter(x=a.index,y=(1+a).cumprod()*100,mode="lines",name=f"{b} {INDEX_BENCHMARKS.get(b,{}).get('name',b)}"))
    fig.update_yaxes(title="Growth index, base 100"); return layout(fig,res["name"]+" — Growth vs Benchmarks",CHART_EXTRA_LARGE_HEIGHT)
def chart_nav(res):
    pv=res["pf"]["portfolio_value"]; fig=go.Figure(go.Scatter(x=pv.index,y=pv,mode="lines",name="Value")); fig.update_yaxes(title="Normalized USD value / return-index value"); return layout(fig,res["name"]+" — Daily Value")
def chart_dd(res):
    mdd,dd=max_drawdown(res["pf"]["portfolio_return"]); fig=go.Figure(go.Scatter(x=dd.index,y=dd,mode="lines",name="Drawdown",fill="tozeroy")); fig.update_yaxes(title="Drawdown",tickformat=".0%"); return layout(fig,res["name"]+f" — Drawdown | Max DD {pct(mdd)}")
def chart_vol(res):
    rv=res["pf"]["portfolio_return"].rolling(ROLLING_VOL_WINDOW,min_periods=20).std()*np.sqrt(TRADING_DAYS); fig=go.Figure(go.Scatter(x=rv.index,y=rv,mode="lines",name="Rolling Vol")); fig.update_yaxes(title="Annualized volatility",tickformat=".0%"); return layout(fig,res["name"]+" — Rolling Volatility")
def chart_beta(res):
    rb=rolling_beta(res["pf"]["portfolio_return"],res["ud"]["primary_return"]); fig=go.Figure();
    if not rb.empty: fig.add_trace(go.Scatter(x=rb.index,y=rb,mode="lines",name="Rolling Beta")); fig.add_hline(y=1,line_dash="dash")
    label=INDEX_BENCHMARKS.get(res["ud"]["primary"],{}).get("name",res["ud"]["primary"]); fig.update_yaxes(title=f"Beta vs {label}"); return layout(fig,res["name"]+" — Rolling Beta")
def chart_bar(df,x,y,title,h=None):
    d=df.sort_values(x,ascending=True); fig=go.Figure(go.Bar(x=d[x],y=d[y],orientation="h",text=d[x].map(lambda z:pct(z,1)),textposition="outside")); fig.update_xaxes(tickformat=".0%"); return layout(fig,title,h or max(CHART_BAR_MIN_HEIGHT,42*len(d)))
def chart_sector(res): return chart_bar(res["pf"]["holdings"].groupby("Sector",as_index=False)["Current Weight"].sum(),"Current Weight","Sector",res["name"]+" — Sector Exposure",CHART_FULL_HEIGHT)
def chart_weights(res): return chart_bar(res["pf"]["holdings"],"Current Weight","Ticker",res["name"]+" — Current Weights")
def chart_rc(res): return chart_bar(res["rc"],"Risk Contribution %","Ticker",res["name"]+" — Risk Contribution")
def chart_rr(res):
    fig=px.scatter(res["am"],x="Annualized Volatility",y="Annualized Return",text="Ticker",hover_data=["Company","Sector","Theme","Sharpe Ratio","Beta","Max Drawdown"],template=PLOT_TEMPLATE); fig.update_traces(textposition="top center"); fig.update_xaxes(tickformat=".0%"); fig.update_yaxes(tickformat=".0%"); return layout(fig,res["name"]+" — Risk Return Map",CHART_EXTRA_LARGE_HEIGHT)
def chart_corr(res):
    c=res["ud"]["returns"].corr(); fig=go.Figure(go.Heatmap(z=c.values,x=c.columns,y=c.index,zmin=-1,zmax=1,colorbar=dict(title="Corr."))); fig.update_layout(xaxis=dict(tickangle=45)); return layout(fig,res["name"]+" — Correlation Matrix",max(CHART_MATRIX_HEIGHT,42*len(c)))
def chart_var(res):
    r=res["pf"]["portfolio_return"].dropna(); v95,_=historical_var_cvar(r,.95); v99,_=historical_var_cvar(r,.99); fig=go.Figure(go.Histogram(x=r,nbinsx=80,histnorm="probability",name="Daily returns"));
    if pd.notna(v95): fig.add_vline(x=-v95,line_dash="dash",annotation_text=f"VaR95 {pct(v95)}")
    if pd.notna(v99): fig.add_vline(x=-v99,line_dash="dot",annotation_text=f"VaR99 {pct(v99)}")
    fig.update_xaxes(tickformat=".1%"); return layout(fig,res["name"]+" — Return Distribution with VaR")
def chart_opt(res):
    fig=px.scatter(res["os"],x="Expected Volatility Ann.",y="Expected Return Ann.",text="Scenario",size="Effective Number of Names",hover_data=["Expected Sharpe","Max Single Name Weight"],template=PLOT_TEMPLATE); fig.update_traces(textposition="top center"); fig.update_xaxes(tickformat=".0%"); fig.update_yaxes(tickformat=".0%"); return layout(fig,res["name"]+" — Optimization Scenario Map",CHART_EXTRA_LARGE_HEIGHT)
def chart_monthly(res):
    m=((1+res["pf"]["portfolio_return"]).resample("M").prod()-1).to_frame("r"); m["Year"]=m.index.year; m["Month"]=m.index.month; p=m.pivot(index="Year",columns="Month",values="r").reindex(columns=range(1,13)); fig=go.Figure(go.Heatmap(z=p.values,x=["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"],y=p.index.astype(str),colorbar=dict(title="Return"),hovertemplate="Year=%{y}<br>Month=%{x}<br>Return=%{z:.2%}<extra></extra>")); return layout(fig,res["name"]+" — Monthly Return Heatmap")



def chart_institutional_ranking(df, title):
    if df is None or df.empty: return layout(go.Figure(),title,CHART_FULL_HEIGHT)
    d=df.sort_values("Institutional Score",ascending=True)
    fig=go.Figure(go.Bar(x=d["Institutional Score"],y=d["Ticker"],orientation="h",customdata=np.stack([d["Company"],d["Recommendation"],d["Confidence Score"]],axis=-1),hovertemplate="%{y}<br>%{customdata[0]}<br>Score=%{x:.1f}<br>Recommendation=%{customdata[1]}<br>Confidence=%{customdata[2]:.1f}<extra></extra>"))
    fig.add_vline(x=40,line_dash="dot"); fig.add_vline(x=60,line_dash="dot"); fig.add_vline(x=75,line_dash="dot"); fig.update_xaxes(range=[0,100],title="Institutional Decision Score")
    return layout(fig,title,max(CHART_BAR_MIN_HEIGHT,34*len(d)))

def chart_strategy_comparison(df,title):
    if df is None or df.empty: return layout(go.Figure(),title,CHART_FULL_HEIGHT)
    d=df.dropna(subset=["Sharpe"]).copy(); fig=px.scatter(d,x="Ann Vol",y="CAGR",size=d["Trade Count"].fillna(1).clip(lower=1),color="Strategy",text="Ticker",hover_data=["Company","Sharpe","Max Drawdown","Win Rate"],template=PLOT_TEMPLATE)
    fig.update_traces(textposition="top center"); fig.update_xaxes(tickformat=".0%"); fig.update_yaxes(tickformat=".0%")
    return layout(fig,title,CHART_EXTRA_LARGE_HEIGHT)

def chart_institutional_asset(detail,ticker):
    score=detail["score"].copy().sort_index(); bt=detail["supertrend_backtest"].reindex(score.index); meta=detail["meta"]
    fig=make_subplots(rows=3,cols=1,shared_xaxes=True,vertical_spacing=.045,row_heights=[.52,.24,.24],specs=[[{"secondary_y":True}],[{"secondary_y":False}],[{"secondary_y":False}]],subplot_titles=("Adjusted Price Structure — Dynamic Trend Channel, Anchored VWAP, Swing Levels and Targets","Institutional Score and Confidence","Net Strategy Equity Comparison"))
    close=score["Close"].astype(float); high=score["High"].astype(float); low=score["Low"].astype(float); volume=score["Volume"].astype(float)
    volume_colors=np.where(close>=score["Open"],"rgba(22,163,74,.30)","rgba(220,38,38,.30)")

    # Dynamic 90-observation regression channel. It uses only observed adjusted closes.
    lookback=min(90,len(score)); channel_index=score.index[-lookback:]; xi=np.arange(lookback,dtype=float)
    mid=pd.Series(np.nan,index=score.index,dtype=float); upper=mid.copy(); lower=mid.copy()
    if lookback>=40:
        slope,intercept=np.polyfit(xi,close.loc[channel_index].values,1); fitted=intercept+slope*xi
        resid=close.loc[channel_index].values-fitted; width=max(float(np.nanstd(resid,ddof=1))*1.40,float(score.loc[channel_index,"ATR"].tail(20).median())*1.20,1e-9)
        mid.loc[channel_index]=fitted; upper.loc[channel_index]=fitted+width; lower.loc[channel_index]=fitted-width

    # Five-bar swing structure and anchored VWAP from the most recent swing low.
    swing_low=(low.shift(2)>low.shift(1))&(low.shift(1)>low)&(low.shift(-1)>low)&(low.shift(-2)>low)
    swing_high=(high.shift(2)<high.shift(1))&(high.shift(1)<high)&(high.shift(-1)<high)&(high.shift(-2)<high)
    recent_lows=score.index[swing_low.fillna(False)&score.index.isin(score.index[-min(150,len(score)):])]
    anchor_date=recent_lows[-1] if len(recent_lows) else score.index[max(0,len(score)-60)]
    anchor=score.index>=anchor_date; typical=(high+low+close)/3
    avwap=pd.Series(np.nan,index=score.index,dtype=float); avwap.loc[anchor]=(typical[anchor]*volume[anchor]).cumsum()/volume[anchor].cumsum().replace(0,np.nan)
    resistance20=high.rolling(20,min_periods=10).max(); support20=low.rolling(20,min_periods=10).min(); resistance60=high.rolling(60,min_periods=30).max(); support60=low.rolling(60,min_periods=30).min()

    fig.add_trace(go.Candlestick(x=score.index,open=score["Open"],high=high,low=low,close=close,name="Adjusted OHLC",increasing_line_color="#16a34a",decreasing_line_color="#dc2626"),row=1,col=1,secondary_y=False)
    for col,name0,color,width0,dash in [("EMA_20","EMA 20","#2563eb",1.2,"solid"),("EMA_50","EMA 50","#f59e0b",1.4,"solid"),("EMA_200","EMA 200","#111827",1.7,"dash"),("ST_Line","Smart Supertrend","#7c3aed",1.5,"dot")]:
        if col in score.columns: fig.add_trace(go.Scatter(x=score.index,y=score[col],mode="lines",name=name0,line=dict(width=width0,color=color,dash=dash)),row=1,col=1,secondary_y=False)
    if upper.notna().any():
        fig.add_trace(go.Scatter(x=score.index,y=upper,mode="lines",name="Dynamic Channel Upper",line=dict(width=1.0,color="#0891b2",dash="dash")),row=1,col=1,secondary_y=False)
        fig.add_trace(go.Scatter(x=score.index,y=lower,mode="lines",name="Dynamic Channel Lower",line=dict(width=1.0,color="#0891b2",dash="dash"),fill="tonexty",fillcolor="rgba(8,145,178,.07)"),row=1,col=1,secondary_y=False)
        fig.add_trace(go.Scatter(x=score.index,y=mid,mode="lines",name="Dynamic Channel Mid",line=dict(width=1.2,color="#0f766e",dash="dot")),row=1,col=1,secondary_y=False)
    fig.add_trace(go.Scatter(x=score.index,y=avwap,mode="lines",name=f"Anchored VWAP ({pd.Timestamp(anchor_date).date()})",line=dict(width=2.0,color="#9333ea")),row=1,col=1,secondary_y=False)
    for series0,name0,color,dash in [(resistance20,"20D Resistance","#a855f7","dash"),(support20,"20D Support","#0f766e","dash"),(resistance60,"60D Resistance","#c026d3","dot"),(support60,"60D Support","#14b8a6","dot")]:
        fig.add_trace(go.Scatter(x=score.index,y=series0,mode="lines",name=name0,line=dict(width=.9,color=color,dash=dash)),row=1,col=1,secondary_y=False)

    if "Signal" in bt.columns:
        buys=bt[bt["Signal"]==1]; sells=bt[bt["Signal"]==-1]
        fig.add_trace(go.Scatter(x=buys.index,y=buys["Low"]*.985,mode="markers",name="Strategy BUY",marker=dict(symbol="triangle-up",size=11,color="#16a34a",line=dict(width=1,color="white"))),row=1,col=1,secondary_y=False)
        fig.add_trace(go.Scatter(x=sells.index,y=sells["High"]*1.015,mode="markers",name="Strategy SELL",marker=dict(symbol="triangle-down",size=11,color="#dc2626",line=dict(width=1,color="white"))),row=1,col=1,secondary_y=False)
    shp=score.loc[swing_high.fillna(False),["High"]].tail(5); slp=score.loc[swing_low.fillna(False),["Low"]].tail(5)
    if not shp.empty: fig.add_trace(go.Scatter(x=shp.index,y=shp["High"]*1.01,mode="markers+text",text=["SH"]*len(shp),textposition="top center",name="Swing High",marker=dict(symbol="diamond",size=8,color="#9333ea")),row=1,col=1,secondary_y=False)
    if not slp.empty: fig.add_trace(go.Scatter(x=slp.index,y=slp["Low"]*.99,mode="markers+text",text=["SL"]*len(slp),textposition="bottom center",name="Swing Low",marker=dict(symbol="diamond",size=8,color="#0f766e")),row=1,col=1,secondary_y=False)

    latest=score.iloc[-1]; latest_close=float(latest["Close"])
    target_floor=float(np.nanmax([latest_close,resistance20.iloc[-1] if pd.notna(resistance20.iloc[-1]) else np.nan,avwap.dropna().iloc[-1] if avwap.notna().any() else np.nan]))
    target_ceiling=float(np.nanmax([target_floor,resistance60.iloc[-1] if pd.notna(resistance60.iloc[-1]) else np.nan,upper.dropna().iloc[-1] if upper.notna().any() else np.nan]))
    risk_pivot=float(np.nanmin([support20.iloc[-1] if pd.notna(support20.iloc[-1]) else latest_close,support60.iloc[-1] if pd.notna(support60.iloc[-1]) else latest_close,lower.dropna().iloc[-1] if lower.notna().any() else latest_close]))
    if np.isfinite(target_floor) and np.isfinite(target_ceiling) and target_ceiling>=target_floor:
        fig.add_hrect(y0=target_floor,y1=target_ceiling,fillcolor="rgba(22,163,74,.09)",line_color="rgba(22,163,74,.50)",line_width=1,row=1,col=1)
        fig.add_annotation(x=score.index[-1],y=target_ceiling,text=f"Target Zone<br>{target_floor:,.2f} – {target_ceiling:,.2f}",showarrow=True,ax=45,ay=-25,bgcolor="rgba(236,253,245,.95)",bordercolor="#16a34a",row=1,col=1)
    fig.add_annotation(x=score.index[-1],y=risk_pivot,text=f"Risk Pivot<br>{risk_pivot:,.2f}",showarrow=True,ax=40,ay=25,bgcolor="rgba(255,247,237,.95)",bordercolor="#f97316",row=1,col=1)
    fig.add_trace(go.Bar(x=score.index,y=volume,name="Volume",marker_color=volume_colors,opacity=.28),row=1,col=1,secondary_y=True)

    fig.add_trace(go.Scatter(x=score.index,y=score["Institutional Score"],mode="lines",name="Institutional Score",line=dict(width=2.2,color="#111827"),fill="tozeroy",fillcolor="rgba(17,24,39,.06)"),row=2,col=1)
    fig.add_trace(go.Scatter(x=score.index,y=score["Confidence Score"],mode="lines",name="Confidence",line=dict(width=1.7,color="#7c3aed",dash="dot")),row=2,col=1)
    for y in (25,40,60,75): fig.add_hline(y=y,line_dash="dot",line_width=1,row=2,col=1)
    if "Strategy Equity" in bt.columns: fig.add_trace(go.Scatter(x=bt.index,y=bt["Strategy Equity"],mode="lines",name="Smart Supertrend Net",line=dict(width=2.0,color="#0f766e")),row=3,col=1)
    if "Buy Hold Equity" in bt.columns: fig.add_trace(go.Scatter(x=bt.index,y=bt["Buy Hold Equity"],mode="lines",name="Buy & Hold",line=dict(width=1.5,color="#64748b",dash="dot")),row=3,col=1)
    header=(f"<b>Close:</b> {latest_close:,.2f} &nbsp;|&nbsp; <b>Score:</b> {float(latest['Institutional Score']):.1f}/100 &nbsp;|&nbsp; <b>Confidence:</b> {float(latest['Confidence Score']):.1f}% &nbsp;|&nbsp; <b>Decision:</b> {latest['Recommendation']} &nbsp;|&nbsp; <b>Target:</b> {target_floor:,.2f}–{target_ceiling:,.2f} &nbsp;|&nbsp; <b>Risk Pivot:</b> {risk_pivot:,.2f}")
    fig.add_annotation(xref="paper",yref="paper",x=0,y=1.10,text=header,showarrow=False,align="left",font=dict(size=12,color="#111827"),bgcolor="rgba(255,255,255,.94)",bordercolor="#cbd5e1",borderwidth=1,borderpad=6)
    fig.update_yaxes(range=[0,100],row=2,col=1); fig.update_layout(xaxis_rangeslider_visible=False,margin=dict(l=72,r=62,t=120,b=72))
    return layout(fig,f"{ticker} — {meta['name']} | SupertrendPro Institutional Decision Engine",1120)

def chart_cross_listing(name,d):
    fig=make_subplots(rows=2,cols=1,shared_xaxes=True,vertical_spacing=.06,row_heights=[.58,.42],subplot_titles=("USD-Equivalent Normalized Performance","ADR Premium / Discount and 20D Z-Score"),specs=[[{"secondary_y":False}],[{"secondary_y":True}]])
    fig.add_trace(go.Scatter(x=d.index,y=d["Local Normalized"],mode="lines",name="Local USD-equivalent, Base 100"),row=1,col=1)
    fig.add_trace(go.Scatter(x=d.index,y=d["ADR Normalized"],mode="lines",name="ADR, Base 100"),row=1,col=1)
    fig.add_trace(go.Scatter(x=d.index,y=d["Premium Discount"],mode="lines",name="Premium / Discount",fill="tozeroy"),row=2,col=1,secondary_y=False)
    fig.add_trace(go.Scatter(x=d.index,y=d["Premium Z 20D"],mode="lines",name="Premium Z 20D",line=dict(dash="dot")),row=2,col=1,secondary_y=True)
    fig.add_hline(y=0,line_dash="dash",row=2,col=1); fig.update_yaxes(tickformat=".1%",row=2,col=1,secondary_y=False)
    return layout(fig,name+" — Cross-Listing Dislocation Monitor",CHART_EXTRA_LARGE_HEIGHT)

def institutional_engine_tab_html(inst_results):
    blocks=[]
    for uname,data in inst_results.items():
        ranking=data["ranking"]; strategies=data["strategies"]; exclusions=data["exclusions"] if not data["exclusions"].empty else pd.DataFrame([{"Ticker":"—","Company":"—","Reason":"No institutional-engine exclusions"}])
        charts=[]
        if not ranking.empty:
            charts.append(div(chart_institutional_ranking(ranking,uname+" — Institutional Decision Ranking"),False))
            charts.append(div(chart_strategy_comparison(strategies,uname+" — Net Strategy Risk / Return Comparison"),False))
            detail_tickers=list(ranking.head(INSTITUTIONAL_DETAIL_CHART_LIMIT)["Ticker"])
            if "Article Shock" in uname: detail_tickers=list(ranking["Ticker"])
            for ticker in detail_tickers:
                if ticker in data["details"]: charts.append(div(chart_institutional_asset(data["details"][ticker],ticker),False))
        blocks.append(f'<div class="section"><h2>{uname} — SupertrendPro Institutional Integration</h2><div class="note"><b>Benchmark:</b> {data["benchmark"]}<br><b>Engine:</b> Smart Supertrend + MACD/ATR + Leading Signal Lab + Explainable 100-Point Institutional Score.<br><b>Execution:</b> signals are applied on the next bar and net returns deduct {INSTITUTIONAL_TRANSACTION_COST_BPS:.0f} bps transaction cost plus {INSTITUTIONAL_SLIPPAGE_BPS:.0f} bps slippage per side. No synthetic price or proxy security is used.</div><h3>Institutional Ranking</h3>{table(ranking,"inst_rank_"+str(abs(hash(uname))%100000))}<h3>Strategy Comparison</h3>{table(strategies,"inst_strat_"+str(abs(hash(uname))%100000))}<h3>Latest Factor Contributions</h3>{table(data["factors"],"inst_fac_"+str(abs(hash(uname))%100000))}<h3>Institutional Engine Exclusion Log</h3>{table(exclusions,"inst_exc_"+str(abs(hash(uname))%100000))}<h3>Interactive Institutional Charts</h3>{"".join([f"<div class=\"chart-block\">{c}</div>" for c in charts])}</div>')
    return "".join(blocks)

def cross_listing_tab_html(cross):
    summary=cross["summary"]; exc=cross["exclusions"] if not cross["exclusions"].empty else pd.DataFrame([{"Pair":"—","Reason":"No cross-listing exclusions","Required":"—"}]); chart_blocks=[]
    for name,d in cross["histories"].items(): chart_blocks.append(f'<div class="chart-block">{div(chart_cross_listing(name,d),False)}</div>')
    return f'<div class="section"><h2>ADR / Local Cross-Listing Dislocation Monitor</h2><div class="note">The monitor converts local ordinary-share values to USD using observed Yahoo Finance FX data and documented ADR ratios. It does not create synthetic prices. Same-day closes are asynchronous across Asia, Europe and the United States; measured premium/discount therefore includes closing-time and microstructure effects. SKHY is retained even with a short history and is treated as a new-listing event monitor rather than forced into a five-year backtest.</div><h3>Cross-Listing Summary</h3>{table(summary,"cross_summary")}<h3>Cross-Listing Exclusion Log</h3>{table(exc,"cross_exc")}<h3>Interactive Pair Monitors</h3>{"".join(chart_blocks)}</div>'

# ============================================================
# 7. HTML AND EXCEL OUTPUT
# ============================================================
PCT_COLS={"Target Weight","Current Weight","Missing % Raw","Annualized Return","Annualized Volatility","Max Drawdown","Downside Deviation","VaR 95% 1D Hist","CVaR 95% 1D Hist","VaR 99% 1D Hist","CVaR 99% 1D Hist","VaR 95% 1D Normal","CVaR 95% 1D Normal","VaR 99% 1D Normal","CVaR 99% 1D Normal","Tracking Error","Alpha Annualized","Win Rate","Up Capture","Down Capture","Risk Contribution %","Portfolio Return","Benchmark Return","Active Return","Portfolio Max Drawdown","Portfolio Total Return","Benchmark Total Return","Active Total Return","Expected Return Ann.","Expected Volatility Ann.","Max Single Name Weight","Equal Weight","Min Volatility","Max Sharpe","Risk Parity","Momentum Risk-Adjusted","Daily Log Return","Rolling Mean 20D","Rolling Sigma 20D","Upper Band Mean+2Sigma","Lower Band Mean-2Sigma","Breach Magnitude","Upper Breach Magnitude","Lower Breach Magnitude","Best Strategy CAGR","Best Strategy Max Drawdown","Best Strategy Win Rate","Latest Premium / Discount","Return Difference","Local Return","ADR Return"}
MONEY_COLS={"Target Dollars","Invested Dollars","Residual Cash Allocation","Latest Market Value"}
FLOAT_COLS={"Initial Price","Latest Price","Whole Shares","Observations","Observations Raw","Sharpe Ratio","Sortino Ratio","Calmar Ratio","Payoff Ratio","Profit Factor","Skewness","Excess Kurtosis","Tail Ratio 95/5","Jarque-Bera p-value","Information Ratio","Beta","R-squared","Correlation","Expected Sharpe","Effective Number of Names","Marginal Risk Contribution","Total Risk Contribution","Institutional Score","Confidence Score","Technical Grade","Positive 60D Probability %","+10% 60D Probability %","Outperform Benchmark 60D Probability %","Historical Analog Count","Best Strategy Sharpe","Latest Premium Z 20D","Return Correlation","Ordinary Shares per ADR"}
DATE_COLS={"First Date","Last Date","Start","End","Date"}
def fmt(df):
    if df is None or df.empty: return pd.DataFrame({"Info":["No data available"]})
    out=df.copy()
    for c in out.columns:
        if c in PCT_COLS: out[c]=out[c].map(lambda x:pct(x,2))
        elif c in MONEY_COLS: out[c]=out[c].map(lambda x:money(x,0))
        elif c in FLOAT_COLS: out[c]=out[c].map(lambda x:num(x,3))
        elif c in DATE_COLS: out[c]=pd.to_datetime(out[c],errors="coerce").dt.strftime("%Y-%m-%d")
    return out
def table(df,tid): return fmt(df).to_html(index=False,table_id=tid,classes="display compact smart-table",border=0,escape=False)
def metrics_df(m): return pd.DataFrame([{"Metric":k,"Value":v} for k,v in m.items()])
def article_tables():
    ac=pd.DataFrame([{"Ticker":t,"Company":m["name"],"Country":m.get("country","N/A"),"Sector":m.get("sector","N/A"),"Theme":m.get("theme","N/A"),"Article Role":m.get("article_role","N/A"),"Source Article":m.get("source_article","Article 1 / Existing")} for t,m in ARTICLE_SHOCK_UNIVERSE.items()])
    ai=pd.DataFrame([{"Ticker":t,"Index Name":INDEX_BENCHMARKS.get(t,{}).get("name",t),"Region":INDEX_BENCHMARKS.get(t,{}).get("region","N/A"),"Benchmark Type":"ETF proxy exception only for TOPIX" if t=="1306.T" else "Market index / futures benchmark"} for t in UNIVERSE_CONFIGS["Article Shock Universe — AI Chip Selloff"]["benchmarks"]])
    return ac,ai
def download_index_close_for_qs_engine(ticker, label):
    """Downloads a real index/proxy series for QS Engine. No synthetic fallback is used."""
    today = pd.Timestamp.today().normalize()
    end = today + pd.DateOffset(days=1)
    print(f"[QS ENGINE] Downloading {label} ({ticker}) from {QS_HISTORY_START}...")
    raw = yf.download(ticker, start=QS_HISTORY_START, end=end, interval="1d", auto_adjust=True, actions=False, group_by="ticker", threads=True, progress=False)
    if raw is None or raw.empty:
        raise RuntimeError(f"QS Engine failed: Yahoo Finance returned no data for {ticker}. No synthetic fallback is used.")
    if isinstance(raw.columns, pd.MultiIndex):
        close = extract_close(raw, [ticker])
        if ticker not in close.columns:
            raise RuntimeError(f"QS Engine failed: close column missing for {ticker}.")
        s = close[ticker].dropna()
    else:
        if "Close" not in raw.columns:
            raise RuntimeError(f"QS Engine failed: close column missing for {ticker}.")
        s = raw["Close"].dropna()
        s.index = pd.to_datetime(s.index)
    s = s.sort_index()
    if len(s) < 252:
        raise RuntimeError(f"QS Engine failed: insufficient observations for {ticker}. No synthetic fallback is used.")
    return s

def compute_qs_engine_for_index(ticker, label, html_path, proxy_note=""):
    """Creates QS Engine standalone HTML and compact smart-table summary."""
    close = download_index_close_for_qs_engine(ticker, label)
    returns = close.pct_change().dropna()
    returns.name = label
    returns.index = pd.to_datetime(returns.index).tz_localize(None)
    qs.reports.html(returns, output=html_path, title=f"{label} - QS Engine Risk & Performance Report", compounded=True)
    summary = pd.DataFrame([
        {"Metric": "Ticker", "Value": ticker},
        {"Metric": "Label", "Value": label},
        {"Metric": "History Start Requested", "Value": QS_HISTORY_START},
        {"Metric": "Actual First Return Date", "Value": returns.index.min().strftime("%Y-%m-%d")},
        {"Metric": "Actual Last Return Date", "Value": returns.index.max().strftime("%Y-%m-%d")},
        {"Metric": "Observations", "Value": int(len(returns))},
        {"Metric": "CAGR", "Value": qs.stats.cagr(returns)},
        {"Metric": "Annualized Volatility", "Value": qs.stats.volatility(returns)},
        {"Metric": "Sharpe", "Value": qs.stats.sharpe(returns)},
        {"Metric": "Sortino", "Value": qs.stats.sortino(returns)},
        {"Metric": "Max Drawdown", "Value": qs.stats.max_drawdown(returns)},
        {"Metric": "Calmar", "Value": qs.stats.calmar(returns)},
        {"Metric": "Skew", "Value": returns.skew()},
        {"Metric": "Kurtosis", "Value": returns.kurtosis()},
        {"Metric": "QS Engine HTML", "Value": Path(html_path).name},
        {"Metric": "Proxy / Data Note", "Value": proxy_note if proxy_note else "Direct Yahoo Finance index series; no synthetic fallback."},
    ])
    return {"ticker": ticker, "label": label, "close": close, "returns": returns, "summary": summary, "html_path": html_path, "proxy_note": proxy_note}

def compute_qs_engine_reports():
    """Separate QS Engine reports for Nikkei 225 and TOPIX proxy."""
    nikkei = compute_qs_engine_for_index(NIKKEI_TICKER, "Nikkei 225 Index", NIKKEI_QS_HTML, "Direct Yahoo Finance index series; no synthetic fallback.")
    topix = compute_qs_engine_for_index(TOPIX_QS_TICKER, "TOPIX Benchmark Proxy - NEXT FUNDS TOPIX ETF 1306.T", TOPIX_QS_HTML, "TOPIX exception: 1306.T ETF is used only as TOPIX benchmark proxy because ^TOPX was unavailable; never used as portfolio constituent.")
    return {"Nikkei 225": nikkei, "TOPIX Proxy": topix}

def qs_engine_tab_html(qs_reports):
    blocks = []
    for key, report in qs_reports.items():
        safe_id = "qs_" + re.sub(r"[^A-Za-z0-9]+", "_", key).strip("_").lower()
        summary_table = table(report["summary"], safe_id + "_summary")
        iframe_src = Path(report["html_path"]).name
        note = report["proxy_note"]
        block = f'<div class="section"><h2>{report["label"]} - QS Engine Analysis</h2><div class="note"><b>QS Engine source:</b> {report["ticker"]}<br><b>Output file:</b> <code>{iframe_src}</code><br><b>Data rule:</b> {note}</div><h3>QS Engine Summary Smart Table</h3>{summary_table}<h3>Embedded QS Engine HTML Report</h3><iframe src="{iframe_src}" style="width:100%;height:1200px;border:1px solid #e4e7ec;border-radius:12px;background:white;"></iframe></div>'
        blocks.append(block)
    return "".join(blocks)

def kpis(res):
    pv=res["pf"]["portfolio_value"]; pm=res["pm"]; vals=[("Latest Value / Index",money(pv.iloc[-1],0)),("Total Return",pct(pv.iloc[-1]/pv.iloc[0]-1)),("Ann. Return",pct(pm.get("Annualized Return"))),("Ann. Volatility",pct(pm.get("Annualized Volatility"))),("Sharpe",num(pm.get("Sharpe Ratio"))),("Max Drawdown",pct(pm.get("Max Drawdown"))),("Beta",num(pm.get("Beta"))),("Tracking Error",pct(pm.get("Tracking Error"))),("VaR 99%",pct(pm.get("VaR 99% 1D Hist"))),("CVaR 99%",pct(pm.get("CVaR 99% 1D Hist"))),("Valid Names",str(len(res["ud"]["valid"]))),("Observations",f"{int(pm.get('Observations',0)):,}")]
    return "".join([f'<div class="kpi-card"><div class="kpi-label">{a}</div><div class="kpi-value">{b}</div></div>' for a,b in vals])
def section(res,js=False):
    name=res["name"]; uid=abs(hash(name))%10000000; figs=[chart_growth(res),chart_nav(res),chart_dd(res),chart_vol(res),chart_beta(res),chart_weights(res),chart_sector(res),chart_rc(res),chart_rr(res),chart_corr(res),chart_var(res),chart_opt(res),chart_monthly(res)]; ds=[div(f,js and i==0) for i,f in enumerate(figs)]
    ex=res["ud"]["exclusions"] if not res["ud"]["exclusions"].empty else pd.DataFrame([{"Ticker":"—","Name":"—","Reason":"No exclusions"}])
    bex=res["ud"]["benchmark_exclusions"] if not res["ud"]["benchmark_exclusions"].empty else pd.DataFrame([{"Benchmark":"—","Name":"—","Reason":"No benchmark exclusions"}])
    return f"""<div class="section"><h2>{name}</h2><div class="note"><b>Description:</b> {res["ud"]["cfg"]["description"]}<br><b>Implementation:</b> {res["pf"]["mode_note"]}<br><b>Primary benchmark:</b> {res["ud"]["primary"]} — {INDEX_BENCHMARKS.get(res["ud"]["primary"],{}).get("name",res["ud"]["primary"])}<br><b>Sample:</b> {res["ud"]["start"].date()} to {res["ud"]["end"].date()}</div><br><div class="kpi-grid">{kpis(res)}</div><h3>Interactive Charts</h3>{''.join([f'<div class="chart-block">{x}</div>' for x in ds])}<h3>Portfolio Metrics</h3>{table(metrics_df(res["pm"]),"m"+str(uid))}<h3>Holdings / Constituents</h3>{table(res["pf"]["holdings"],"h"+str(uid))}<h3>Asset Metrics</h3>{table(res["am"].sort_values("Sharpe Ratio",ascending=False),"a"+str(uid))}<h3>Risk Contribution</h3>{table(res["rc"],"r"+str(uid))}<h3>Multi-Benchmark Comparison</h3>{table(res["bt"],"b"+str(uid))}<h3>Stress Tests</h3>{table(res["st"],"s"+str(uid))}<h3>Optimization Summary</h3>{table(res["os"],"os"+str(uid))}<h3>Optimization Weights</h3>{table(res["ow"],"ow"+str(uid))}<h3>Data Quality</h3>{table(res["ud"]["data_quality"],"dq"+str(uid))}<h3>Security Exclusion Log</h3>{table(ex,"ex"+str(uid))}<h3>Benchmark Exclusion Log</h3>{table(bex,"bex"+str(uid))}</div>"""
def create_report(results, sox, qs_reports, institutional_results, cross_listing):
    ac,ai=article_tables(); all_rows=[]
    for uname,cfg in UNIVERSE_CONFIGS.items():
        for t,m in cfg["universe"].items(): all_rows.append({"Universe":uname,"Ticker":t,"Company":m["name"],"Sector":m.get("sector","N/A"),"Theme":m.get("theme","N/A"),"Country":m.get("country","United States")})
    tabs=['<button class="tablink active" onclick="openTab(event, \'source\')">News Source & Universes</button>']; contents=[f'<div id="source" class="tabcontent active-content"><div class="section"><h2>News Source & Project Scope</h2><div class="note"><b>News 1:</b> {NEWS_SOURCE_TITLE}<br><b>URL 1:</b> {NEWS_SOURCE_URL}<br><b>News 2:</b> {NEWS_SOURCE_TITLE_2}<br><b>URL 2:</b> {NEWS_SOURCE_URL_2}<br><b>News 3:</b> {NEWS_SOURCE_TITLE_3}<br><b>URL 3:</b> {NEWS_SOURCE_URL_3}<br><b>Rule:</b> Existing features preserved. Added Article Shock Universe from all three Investing.com articles and US Technology + AI + Chip Universe. The third article adds SKHY, TSM and ASML.AS, while ASML and the new US ADR listings are included in the integrated technical engine where history permits. No ETF constituents in investment universes. Interactive charts are rendered in full horizontal page width. <b>TOPIX exception:</b> because Yahoo Finance did not return ^TOPX index data, TOPIX benchmark exposure is represented only by 1306.T, NEXT FUNDS TOPIX ETF. This ETF is used solely as a benchmark proxy, never as a portfolio constituent. No synthetic fallback.<br><b>SOX diagnostics:</b> Philadelphia Semiconductor Index <code>^SOX</code> is separately downloaded from 2018-01-01. The report includes daily log returns, 20D rolling mean, 20D ±2σ bands, breach counts and largest breach dates.</div><h3>Article Companies</h3>{table(ac,"articlec")}<h3>Article Indices / Benchmarks</h3>{table(ai,"articlei")}<h3>All Configured Universes</h3>{table(pd.DataFrame(all_rows),"allu")}</div></div>']
    sox_summary_table = table(sox["summary"], "soxsummary")
    sox_breach_top = sox["breaches"].head(SOX_TOP_BREACH_ROWS).copy()
    sox_breach_table = table(sox_breach_top, "soxbreaches")
    sox_diag_tail = sox["diag"].reset_index().rename(columns={"index":"Date"}).tail(250).copy()
    sox_diag_table = table(sox_diag_tail, "soxdiagtail")
    # IMPORTANT RENDERING FIX:
    # The SOX tab is created before the universe tabs. Therefore the first SOX Plotly chart
    # must include Plotly.js; otherwise the inline Plotly.newPlot scripts run before Plotly is loaded,
    # leaving the "Interactive SOX Charts" section blank.
    sox_figs = [div(chart_sox_close_index(sox), True), div(chart_sox_log_return_bands(sox), False)]
    tabs.append('<button class="tablink" onclick="openTab(event, \'soxdiag\')">Philadelphia SOX Diagnostics</button>')
    contents.append(f'<div id="soxdiag" class="tabcontent"><div class="section"><h2>Philadelphia Semiconductor Index (^SOX) Diagnostics</h2><div class="note"><b>Purpose:</b> Standalone semiconductor-index diagnostics from 2018 onward. No synthetic fallback is used. Daily log returns are compared against 20 trading-day rolling mean ± 2σ bands. Upper and lower band breaches are counted separately and the largest breach dates are ranked below.<br><b>Rendering note:</b> Plotly.js is intentionally loaded in the first SOX chart so this diagnostics tab renders correctly even though it appears before the universe chart tabs.</div><h3>Interactive SOX Charts</h3><div class="chart-block">{sox_figs[0]}</div><div class="chart-block">{sox_figs[1]}</div><h3>SOX Band Breach Summary</h3>{sox_summary_table}<h3>Largest SOX Band Breaches — Ranked by Breach Magnitude</h3>{sox_breach_table}<h3>Latest 250 SOX Diagnostic Observations</h3>{sox_diag_table}</div></div>')
    tabs.append('<button class="tablink" onclick="openTab(event, \'qsnikketopix\')">Nikkei 225 + TOPIX QS Engine</button>')
    contents.append(f'<div id="qsnikketopix" class="tabcontent">{qs_engine_tab_html(qs_reports)}</div>')
    tabs.append('<button class="tablink" onclick="openTab(event, \'institutionalengine\')">SupertrendPro Institutional Engine</button>')
    contents.append(f'<div id="institutionalengine" class="tabcontent">{institutional_engine_tab_html(institutional_results)}</div>')
    tabs.append('<button class="tablink" onclick="openTab(event, \'crosslisting\')">ADR / Local Cross-Listing</button>')
    contents.append(f'<div id="crosslisting" class="tabcontent">{cross_listing_tab_html(cross_listing)}</div>')
    first_js=False
    for i,res in enumerate(results):
        tid=f"tab{i}"; tabs.append(f'<button class="tablink" onclick="openTab(event, \'{tid}\')">{res["name"]}</button>'); contents.append(f'<div id="{tid}" class="tabcontent">{section(res,first_js)}</div>'); first_js=False
    html=f"""<!DOCTYPE html><html><head><meta charset="utf-8"><title>{REPORT_TITLE}</title><meta name="viewport" content="width=device-width, initial-scale=1"><link rel="stylesheet" href="https://cdn.datatables.net/1.13.8/css/jquery.dataTables.min.css"><style>:root{{--bg:#f7f8fa;--card:#fff;--ink:#182230;--muted:#667085;--line:#e4e7ec;--navy:#102a43;--blue:#315f86}}body{{margin:0;background:var(--bg);color:var(--ink);font-family:Inter,Aptos,"Segoe UI",Arial,Helvetica,sans-serif;font-size:14px;font-weight:300;letter-spacing:.005em;width:100%;overflow-x:hidden}}.header{{padding:34px 42px 26px;background:linear-gradient(90deg,#0f2437,#183b56);color:white}}.header h1{{margin:0 0 8px;font-size:28px;font-weight:400}}.header p{{margin:4px 0;color:#d8e3ec;font-weight:300}}.container{{padding:24px 14px 60px;width:calc(100vw - 28px);max-width:none;margin:0 auto;box-sizing:border-box}}.tabbar{{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:18px}}.tablink{{border:1px solid var(--line);background:#fff;color:#182230;padding:10px 14px;border-radius:10px;cursor:pointer;font-size:13px}}.tablink.active{{background:#102a43;color:white}}.tabcontent{{display:none}}.active-content{{display:block}}.section{{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:22px;margin-bottom:22px;width:100%;box-sizing:border-box;box-shadow:0 1px 2px rgba(16,24,40,.04)}}.section h2{{margin:0 0 14px;font-size:20px;font-weight:500;color:var(--navy)}}.section h3{{margin-top:24px;font-size:16px;font-weight:500;color:var(--blue)}}.kpi-grid{{display:grid;grid-template-columns:repeat(4,minmax(180px,1fr));gap:14px}}.kpi-card{{background:#fbfcfd;border:1px solid var(--line);border-radius:12px;padding:15px 16px}}.kpi-label{{color:var(--muted);font-size:12px;margin-bottom:6px}}.kpi-value{{color:var(--ink);font-size:21px;font-weight:500}}.note{{background:#f2f4f7;border-left:4px solid #315f86;padding:12px 14px;border-radius:8px;color:#344054;line-height:1.55}}.warning{{background:#fff8e6;border-left:4px solid #b7791f;padding:12px 14px;border-radius:8px;color:#3f2f0b;line-height:1.55}}.chart-block{{margin-top:26px;border-top:1px solid var(--line);padding-top:20px;width:100%;min-height:940px;box-sizing:border-box;overflow-x:visible}}.chart-block .plotly-graph-div{{width:100%!important;min-width:100%!important}}.chart-block .js-plotly-plot,.chart-block .plot-container,.chart-block .svg-container{{width:100%!important;min-width:100%!important}}table.dataTable{{width:100%!important;font-size:12px}}.footer{{text-align:center;color:var(--muted);font-size:12px;padding:26px}}@media(max-width:1000px){{.kpi-grid{{grid-template-columns:repeat(2,1fr)}}.container{{padding:18px;width:calc(100vw - 36px)}}}}</style></head><body><div class="header"><h1>{REPORT_TITLE}</h1><p>Daily frequency | Real Yahoo Finance data | No synthetic prices | No ETF constituents except TOPIX benchmark proxy</p><p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')} | {AUTHOR_LINE}</p></div><div class="container"><div class="tabbar">{''.join(tabs)}</div>{''.join(contents)}<div class="section"><h2>Important Note</h2><div class="warning">This report is Simulation Pivotal analytical. It is not investment advice. Missing prices are not synthetically filled. <b>TOPIX exception:</b> 1306.T is used only as a TOPIX benchmark proxy because ^TOPX was unavailable from Yahoo Finance in the previous run; it is not included in any investment universe or portfolio holdings.</div></div></div><div class="footer">{AUTHOR_LINE}</div><script src="https://code.jquery.com/jquery-3.7.1.min.js"></script><script src="https://cdn.datatables.net/1.13.8/js/jquery.dataTables.min.js"></script><script>function resizeVisiblePlots(scope){{try{{var root=scope||document;var plots=root.getElementsByClassName('js-plotly-plot');for(var j=0;j<plots.length;j++){{Plotly.Plots.resize(plots[j]);}}}}catch(e){{}}}}
function openTab(evt,tabName){{var i,tc,tl;tc=document.getElementsByClassName('tabcontent');for(i=0;i<tc.length;i++){{tc[i].style.display='none';tc[i].classList.remove('active-content')}}tl=document.getElementsByClassName('tablink');for(i=0;i<tl.length;i++){{tl[i].className=tl[i].className.replace(' active','')}}var active=document.getElementById(tabName);active.style.display='block';active.classList.add('active-content');evt.currentTarget.className+=' active';setTimeout(function(){{resizeVisiblePlots(active)}},250);setTimeout(function(){{resizeVisiblePlots(active)}},900)}}
$(document).ready(function(){{$('.smart-table').DataTable({{pageLength:15,lengthMenu:[[10,15,25,50,-1],[10,15,25,50,'All']],scrollX:true,order:[]}});setTimeout(function(){{resizeVisiblePlots(document)}},600);setTimeout(function(){{resizeVisiblePlots(document)}},1500);setTimeout(function(){{var active=document.getElementsByClassName('active-content')[0];if(active){{resizeVisiblePlots(active);}}}},2200);}});
window.addEventListener('resize',function(){{resizeVisiblePlots(document)}});</script></body></html>"""
    Path(REPORT_OUTPUT).write_text(html,encoding="utf-8"); print(f"[OUTPUT] HTML: {REPORT_OUTPUT}")
def sheet(s):
    for ch in r'\/*?:[]': s=s.replace(ch,'_')
    return s[:31]
def export_excel(results, sox, qs_reports, institutional_results, cross_listing):
    with pd.ExcelWriter(EXCEL_OUTPUT,engine="xlsxwriter") as writer:
        ac,ai=article_tables(); ac.to_excel(writer,"Article_Companies",index=False); ai.to_excel(writer,"Article_Indices",index=False)
        sox["summary"].to_excel(writer, "SOX_Summary", index=False)
        sox["diag"].to_excel(writer, "SOX_LogRet_Bands")
        sox["breaches"].to_excel(writer, "SOX_Breach_Ranking", index=False)
        for qs_name, qs_report in qs_reports.items():
            qs_report["summary"].to_excel(writer, sheet("QS_" + qs_name + "_Summary"), index=False)
            qs_report["returns"].to_frame("Daily Return").to_excel(writer, sheet("QS_" + qs_name + "_Returns"))
        for uname, inst in institutional_results.items():
            p=sheet("INST_"+re.sub(r"[^A-Za-z0-9]+","_",uname)[:14])
            inst["ranking"].to_excel(writer,sheet(p+"_Ranking"),index=False)
            inst["strategies"].to_excel(writer,sheet(p+"_Strategies"),index=False)
            inst["factors"].to_excel(writer,sheet(p+"_Factors"),index=False)
            inst["exclusions"].to_excel(writer,sheet(p+"_Exclusions"),index=False)
            for ticker,detail in inst["details"].items():
                compact=detail["score"][[c for c in ["Close","EMA_20","EMA_50","EMA_200","ST_Line","ST_Dir","RSI","ADX","MACD","MACD_SIGNAL","Institutional Score","Confidence Score","Recommendation"] if c in detail["score"].columns]].tail(750)
                compact.to_excel(writer,sheet("STP_"+ticker.replace(".","_")[:20]))
        cross_listing["summary"].to_excel(writer,"Cross_Listing_Summary",index=False)
        cross_listing["exclusions"].to_excel(writer,"Cross_Listing_Excl",index=False)
        for pair_name,hist in cross_listing["histories"].items():
            hist.to_excel(writer,sheet("XL_"+re.sub(r"[^A-Za-z0-9]+","_",pair_name)[:25]))
        for res in results:
            p=sheet(res["name"].replace(" ","_")[:16])
            metrics_df(res["pm"]).to_excel(writer,sheet(p+"_Metrics"),index=False); res["pf"]["holdings"].to_excel(writer,sheet(p+"_Holdings"),index=False); res["am"].to_excel(writer,sheet(p+"_AssetMetrics"),index=False); res["rc"].to_excel(writer,sheet(p+"_RiskContrib"),index=False); res["bt"].to_excel(writer,sheet(p+"_Benchmarks"),index=False); res["st"].to_excel(writer,sheet(p+"_Stress"),index=False); res["os"].to_excel(writer,sheet(p+"_OptSummary"),index=False); res["ow"].to_excel(writer,sheet(p+"_OptWeights"),index=False); res["ud"]["data_quality"].to_excel(writer,sheet(p+"_DataQuality"),index=False); res["ud"]["exclusions"].to_excel(writer,sheet(p+"_Exclusions"),index=False); res["ud"]["prices"].to_excel(writer,sheet(p+"_Prices")); res["ud"]["returns"].to_excel(writer,sheet(p+"_Returns")); res["pf"]["portfolio_value"].to_frame("Portfolio_or_Basket_Value").to_excel(writer,sheet(p+"_NAV"))
        fmt=writer.book.add_format({"bold":True,"bg_color":"#D9EAF7","border":1})
        for ws in writer.sheets.values(): ws.freeze_panes(1,0); ws.set_row(0,None,fmt); ws.set_column(0,20,18)
    print(f"[OUTPUT] Excel: {EXCEL_OUTPUT}")

# ============================================================
# 8. STREAMLIT APPLICATION LAYER
# ============================================================
STREAMLIT_APP_VERSION = "2.1.0"

st.set_page_config(
    page_title="AI / Chip Institutional Platform",
    page_icon="◼",
    layout="wide",
    initial_sidebar_state="expanded",
)

STREAMLIT_CSS = """
<style>
:root {
  --navy:#0b1f33; --navy2:#132f4c; --ink:#17212b; --muted:#667085;
  --line:#dfe5ec; --card:#ffffff; --bg:#f5f7fa; --accent:#315f86;
}
html, body, [class*="css"] {font-family: Inter, Aptos, "Segoe UI", Arial, sans-serif;}
.stApp {background:var(--bg); color:var(--ink);}
.block-container {max-width:none; padding-top:1.2rem; padding-left:1.5rem; padding-right:1.5rem;}
.mk-masthead {background:linear-gradient(100deg,var(--navy),var(--navy2)); color:#fff; border-radius:14px; padding:24px 28px; margin-bottom:14px; border:1px solid rgba(255,255,255,.08);}
.mk-kicker {font-size:.72rem; letter-spacing:.18em; text-transform:uppercase; color:#b8c8d8; font-weight:500;}
.mk-title {font-size:2rem; letter-spacing:-.025em; font-weight:350; margin:.25rem 0;}
.mk-subtitle {font-size:.88rem; color:#d7e1ea; font-weight:300;}
.mk-section {font-size:.74rem; letter-spacing:.13em; text-transform:uppercase; color:#315f86; font-weight:600; margin:1.2rem 0 .5rem;}
div[data-testid="stMetric"] {background:#fff; border:1px solid var(--line); border-radius:10px; padding:12px 14px; box-shadow:0 1px 2px rgba(16,24,40,.03);}
div[data-testid="stMetricLabel"] {font-size:.72rem; letter-spacing:.04em; text-transform:uppercase; color:var(--muted);}
div[data-testid="stMetricValue"] {font-weight:400; color:var(--navy);}
.stTabs [data-baseweb="tab-list"] {gap:.35rem; border-bottom:1px solid var(--line);}
.stTabs [data-baseweb="tab"] {height:2.8rem; padding:0 .9rem; font-size:.77rem; letter-spacing:.035em; text-transform:uppercase; font-weight:450; color:#475467;}
.stTabs [aria-selected="true"] {color:var(--navy)!important; border-bottom:2px solid var(--navy)!important;}
section[data-testid="stSidebar"] {background:#eef2f6; border-right:1px solid var(--line);}
.stButton>button, .stDownloadButton>button {border-radius:8px; border:1px solid #b8c4d0; font-weight:450;}
[data-testid="stDataFrame"] {border:1px solid var(--line); border-radius:8px; overflow:hidden;}
.mk-note {background:#fff; border:1px solid var(--line); border-left:3px solid var(--accent); border-radius:8px; padding:11px 13px; color:#475467; font-size:.84rem; line-height:1.55;}
</style>
"""
st.markdown(STREAMLIT_CSS, unsafe_allow_html=True)


def _safe_metric_value(value, kind="number"):
    if value is None or (isinstance(value, (float, np.floating)) and (pd.isna(value) or np.isinf(value))):
        return "—"
    if kind == "percent": return f"{float(value)*100:,.2f}%"
    if kind == "money": return f"${float(value):,.0f}"
    if kind == "score": return f"{float(value):,.1f}"
    if kind == "int": return f"{int(value):,}"
    return f"{float(value):,.3f}" if isinstance(value, (float, np.floating)) else str(value)


def _show_df(df, height=420, key=None):
    if df is None or len(df) == 0:
        st.info("No data available for this section.")
        return
    st.dataframe(df, width="stretch", height=height, hide_index=True, key=key)


def _plot(fig, key=None):
    # Streamlit controls width; legacy fixed chart heights remain as institutional defaults.
    st.plotly_chart(fig, width="stretch", theme=None, config=PLOT_CONFIG, key=key)


@st.cache_data(ttl=3600, show_spinner=False)
def load_institutional_platform():
    close, ohlcv_map = download_all()
    sox = compute_sox_diagnostics()
    results = [analyze(uname, cfg, close) for uname, cfg in UNIVERSE_CONFIGS.items()]
    institutional_results = analyze_supertrend_institutional(results, ohlcv_map, close)
    cross_listing = compute_cross_listing_analysis(close)
    return close, ohlcv_map, sox, results, institutional_results, cross_listing


@st.cache_data(ttl=3600, show_spinner=False)
def generate_qs_reports_cached():
    return compute_qs_engine_reports()


def _render_masthead():
    st.markdown(
        f"""
        <div class="mk-masthead">
          <div class="mk-kicker">MK FinTECH LabGEN · Institutional Analytics</div>
          <div class="mk-title">Multi-Universe AI / Chip Institutional Platform</div>
          <div class="mk-subtitle">SupertrendPro Institutional Integrated · Version {STREAMLIT_APP_VERSION} · Daily Yahoo Finance data · No synthetic prices</div>
        </div>
        """, unsafe_allow_html=True,
    )


def _render_executive(res, inst):
    pm=res["pm"]; pv=res["pf"]["portfolio_value"]
    cols=st.columns(6)
    vals=[
        ("Latest Value", _safe_metric_value(pv.iloc[-1], "money")),
        ("Annual Return", _safe_metric_value(pm.get("Annualized Return"), "percent")),
        ("Annual Volatility", _safe_metric_value(pm.get("Annualized Volatility"), "percent")),
        ("Sharpe", _safe_metric_value(pm.get("Sharpe Ratio"))),
        ("Max Drawdown", _safe_metric_value(pm.get("Max Drawdown"), "percent")),
        ("Valid Names", _safe_metric_value(len(res["ud"]["valid"]), "int")),
    ]
    for c,(label,value) in zip(cols,vals): c.metric(label,value)
    _plot(chart_growth(res), key="exec_growth")
    left,right=st.columns(2)
    with left: _plot(chart_rr(res), key="exec_rr")
    with right:
        rank=inst.get("ranking",pd.DataFrame())
        _plot(chart_institutional_ranking(rank, res["name"]+" — Institutional Ranking"), key="exec_rank")
    st.markdown('<div class="mk-section">Top institutional decisions</div>',unsafe_allow_html=True)
    ranking=inst.get("ranking",pd.DataFrame()).copy()
    if not ranking.empty:
        cols_keep=[c for c in ["Ticker","Company","Country","Institutional Score","Confidence Score","Recommendation","Technical Grade","Best Strategy","Best Strategy Sharpe","Positive 60D Probability %"] if c in ranking.columns]
        _show_df(ranking.sort_values("Institutional Score",ascending=False)[cols_keep],height=430,key="exec_table")


def _render_universe(res):
    tab_names=["Portfolio & Benchmark","Risk","Constituents","Optimization","Stress & Governance"]
    a,b,c,d,e=st.tabs(tab_names)
    with a:
        _plot(chart_growth(res),key="uni_growth"); _plot(chart_nav(res),key="uni_nav"); _plot(chart_monthly(res),key="uni_month")
        _show_df(metrics_df(res["pm"]),height=480,key="uni_pm")
    with b:
        x,y=st.columns(2)
        with x: _plot(chart_dd(res),key="uni_dd"); _plot(chart_var(res),key="uni_var")
        with y: _plot(chart_vol(res),key="uni_vol"); _plot(chart_beta(res),key="uni_beta")
        _plot(chart_corr(res),key="uni_corr"); _show_df(res["rc"],height=500,key="uni_rc_table")
    with c:
        x,y=st.columns(2)
        with x: _plot(chart_weights(res),key="uni_weights")
        with y: _plot(chart_sector(res),key="uni_sector")
        _show_df(res["pf"]["holdings"],height=520,key="uni_hold"); _show_df(res["am"].sort_values("Sharpe Ratio",ascending=False),height=560,key="uni_am")
    with d:
        _plot(chart_opt(res),key="uni_opt"); _show_df(res["os"],height=360,key="uni_os"); _show_df(res["ow"],height=520,key="uni_ow")
    with e:
        _show_df(res["st"],height=400,key="uni_stress"); _show_df(res["bt"],height=430,key="uni_bt"); _show_df(res["ud"]["data_quality"],height=480,key="uni_dq")
        _show_df(res["ud"]["exclusions"],height=280,key="uni_ex")


def _render_institutional(inst):
    ranking=inst.get("ranking",pd.DataFrame()); strategies=inst.get("strategies",pd.DataFrame()); factors=inst.get("factors",pd.DataFrame())
    _plot(chart_institutional_ranking(ranking,"SupertrendPro Institutional — Decision Score Ranking"),key="inst_rank")
    _plot(chart_strategy_comparison(strategies,"Net Strategy Risk / Return Comparison"),key="inst_strat")
    a,b,c=st.tabs(["Decision Ranking","Strategy Results","Factor Contribution"])
    with a: _show_df(ranking.sort_values("Institutional Score",ascending=False) if not ranking.empty else ranking,height=600,key="inst_rank_table")
    with b: _show_df(strategies,height=600,key="inst_strat_table")
    with c: _show_df(factors,height=600,key="inst_factor_table")


def _render_asset_detail(inst, selected_ticker):
    details=inst.get("details",{})
    if selected_ticker not in details:
        st.warning("The selected security does not have sufficient adjusted OHLCV history for the institutional engine.")
        return
    detail=details[selected_ticker]
    score=detail["score"]; last=score.iloc[-1]; decision=detail["decision"]
    cols=st.columns(6)
    metrics=[
        ("Last Price",_safe_metric_value(last.get("Close"))),
        ("Institutional Score",_safe_metric_value(decision.get("Institutional Score"),"score")),
        ("Confidence",_safe_metric_value(decision.get("Confidence Score"),"score")),
        ("Recommendation",str(decision.get("Recommendation","—"))),
        ("Positive 60D",f"{decision.get('Positive Return Probability 60D %',np.nan):,.1f}%" if pd.notna(decision.get('Positive Return Probability 60D %')) else "—"),
        ("Historical Analogs",_safe_metric_value(decision.get("Historical Analog Count",0),"int")),
    ]
    for c,(l,v) in zip(cols,metrics): c.metric(l,v)
    _plot(chart_institutional_asset(detail,selected_ticker),key="asset_chart")
    a,b,c,d=st.tabs(["Factor Scorecard","Supertrend Backtest","MACD + ATR","Decision History"])
    with a: _show_df(detail["factors"],height=420,key="asset_factors")
    strategy_rows=inst.get("strategies",pd.DataFrame())
    selected_strategy_rows=strategy_rows[strategy_rows["Ticker"].eq(selected_ticker)] if (not strategy_rows.empty and "Ticker" in strategy_rows.columns) else pd.DataFrame()
    with b:
        _show_df(selected_strategy_rows[selected_strategy_rows["Strategy"].eq("Smart Supertrend")] if "Strategy" in selected_strategy_rows.columns else selected_strategy_rows,height=240,key="asset_st_stats")
        st_bt=detail["supertrend_backtest"].copy().tail(750).reset_index()
        _show_df(st_bt[[c for c in ["Date","Close","ST_Line","ST_Dir","Position","Signal","ATR_Stop","Strategy Return","Strategy Equity","Buy Hold Equity"] if c in st_bt.columns]],height=500,key="asset_st_history")
    with c:
        _show_df(selected_strategy_rows[selected_strategy_rows["Strategy"].eq("MACD + ATR")] if "Strategy" in selected_strategy_rows.columns else selected_strategy_rows,height=240,key="asset_macd_stats")
        macd_bt=detail["macd_backtest"].copy().tail(750).reset_index()
        _show_df(macd_bt[[c for c in ["Date","Close","MACD","MACD_SIGNAL","Position","Signal","ATR_Stop","Strategy Return","Strategy Equity","Buy Hold Equity"] if c in macd_bt.columns]],height=500,key="asset_macd_history")
    with d:
        keep=[c for c in ["Close","EMA_20","EMA_50","EMA_200","RSI","ADX","MACD","MACD_SIGNAL","Institutional Score","Confidence Score","Recommendation"] if c in score.columns]
        hist=score[keep].tail(750).reset_index().rename(columns={score.index.name or "index":"Date"})
        _show_df(hist,height=600,key="asset_hist")
        st.download_button("Download selected security decision history",hist.to_csv(index=False).encode("utf-8"),file_name=f"{selected_ticker}_institutional_history.csv",mime="text/csv")


def _render_sox(sox):
    x,y=st.columns(2)
    with x: _plot(chart_sox_close_index(sox),key="sox_close")
    with y: _plot(chart_sox_log_return_bands(sox),key="sox_bands")
    a,b,c=st.tabs(["Summary","Largest Breaches","Latest Diagnostics"])
    with a: _show_df(sox["summary"],height=420,key="sox_sum")
    with b: _show_df(sox["breaches"].head(SOX_TOP_BREACH_ROWS),height=560,key="sox_br")
    with c: _show_df(sox["diag"].tail(500).reset_index(),height=600,key="sox_diag")


def _render_cross_listing(cross):
    _show_df(cross.get("summary",pd.DataFrame()),height=440,key="xl_sum")
    histories=cross.get("histories",{})
    if histories:
        selected=st.selectbox("Cross-listing pair",list(histories.keys()),key="xl_pair")
        hist=histories[selected]
        # Generic cross-listing chart from the observed columns.
        fig=go.Figure()
        for col in [c for c in hist.columns if any(k in c.lower() for k in ["premium","discount","z-score","zscore"] )]:
            fig.add_trace(go.Scatter(x=hist.index,y=hist[col],mode="lines",name=col))
        if not fig.data:
            numeric=hist.select_dtypes(include=[np.number]).columns[:4]
            for col in numeric: fig.add_trace(go.Scatter(x=hist.index,y=hist[col],mode="lines",name=col))
        _plot(layout(fig,selected+" — Cross-Listing Dislocation",CHART_FULL_HEIGHT),key="xl_chart")
        _show_df(hist.tail(750).reset_index(),height=580,key="xl_hist")
    _show_df(cross.get("exclusions",pd.DataFrame()),height=300,key="xl_ex")


def _render_news_and_governance(res):
    st.markdown(f'<div class="mk-note"><b>News 1:</b> {NEWS_SOURCE_TITLE}<br>{NEWS_SOURCE_URL}<br><br><b>News 2:</b> {NEWS_SOURCE_TITLE_2}<br>{NEWS_SOURCE_URL_2}<br><br><b>News 3:</b> {NEWS_SOURCE_TITLE_3}<br>{NEWS_SOURCE_URL_3}</div>',unsafe_allow_html=True)
    ac,ai=article_tables()
    a,b,c=st.tabs(["Article Companies","Benchmarks","Data Governance"])
    with a: _show_df(ac,height=620,key="news_companies")
    with b: _show_df(ai,height=520,key="news_bench")
    with c:
        _show_df(res["ud"]["data_quality"],height=540,key="gov_dq")
        st.markdown(f'<div class="mk-note"><b>TOPIX benchmark rule:</b> {TOPIX_BENCHMARK_PROXY_NOTE}<br><b>Data rule:</b> Yahoo Finance daily observations only; no synthetic security prices and no portfolio ETF constituents.</div>',unsafe_allow_html=True)


def _render_exports(results,sox,institutional_results,cross_listing):
    st.markdown('<div class="mk-note">HTML, Excel and standalone QS Engine reports are generated only when requested. This prevents expensive report generation on every Streamlit rerun.</div>',unsafe_allow_html=True)
    if st.button("Generate full institutional report package",type="primary",width="stretch"):
        with st.spinner("Generating QS Engine, HTML and Excel outputs..."):
            qs_reports=generate_qs_reports_cached()
            create_report(results,sox,qs_reports,institutional_results,cross_listing)
            export_excel(results,sox,qs_reports,institutional_results,cross_listing)
        st.success("Report package generated.")
    files=[
        (REPORT_OUTPUT,"Full Institutional HTML","text/html"),
        (EXCEL_OUTPUT,"Institutional Analytics Excel","application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"),
        (NIKKEI_QS_HTML,"Nikkei 225 QS Engine HTML","text/html"),
        (TOPIX_QS_HTML,"TOPIX Proxy QS Engine HTML","text/html"),
    ]
    for path,label,mime in files:
        p=Path(path)
        if p.exists(): st.download_button(label,p.read_bytes(),file_name=p.name,mime=mime,width="stretch")


def streamlit_main():
    _render_masthead()
    with st.sidebar:
        st.markdown("### Institutional Controls")
        universe_name=st.selectbox("Investment Universe",list(UNIVERSE_CONFIGS.keys()))
        st.caption("Changing a selector does not redownload data while the one-hour cache remains valid.")
        if st.button("Refresh Yahoo Finance cache",width="stretch"):
            st.cache_data.clear(); st.rerun()
        st.divider()
        st.caption("Real Yahoo Finance daily data · No synthetic security prices · TOPIX proxy exception only.")

    try:
        with st.spinner("Loading Yahoo Finance data and institutional analytics..."):
            close,ohlcv_map,sox,results,institutional_results,cross_listing=load_institutional_platform()
    except Exception as exc:
        st.error("Institutional platform could not complete the Yahoo Finance data pipeline.")
        st.exception(exc)
        st.stop()

    result_map={r["name"]:r for r in results}; res=result_map[universe_name]; inst=institutional_results.get(universe_name,{})
    details=inst.get("details",{})
    with st.sidebar:
        asset_options=list(details.keys())
        selected_asset=st.selectbox("Institutional Asset Deep Dive",asset_options) if asset_options else None
        st.markdown(f"**Sample:** {res['ud']['start'].date()} → {res['ud']['end'].date()}")
        st.markdown(f"**Primary benchmark:** {res['ud']['primary']}")

    tabs=st.tabs(["Executive Dashboard","Universe Analytics","Institutional Engine","Asset Deep Dive","SOX Diagnostics","ADR / Local","News & Governance","Export Center"])
    with tabs[0]: _render_executive(res,inst)
    with tabs[1]: _render_universe(res)
    with tabs[2]: _render_institutional(inst)
    with tabs[3]:
        if selected_asset: _render_asset_detail(inst,selected_asset)
        else: st.info("No security has sufficient history for the institutional deep-dive engine.")
    with tabs[4]: _render_sox(sox)
    with tabs[5]: _render_cross_listing(cross_listing)
    with tabs[6]: _render_news_and_governance(res)
    with tabs[7]: _render_exports(results,sox,institutional_results,cross_listing)

    st.caption(AUTHOR_LINE+" · Analytical simulation; not investment advice.")


def main():
    """Streamlit entry point; original analytical functions remain available for batch exports."""
    streamlit_main()


if __name__ == "__main__":
    main()
