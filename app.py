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
REPORT_TITLE = "Global AI / Semiconductor Institutional Hedge Fund Management Report — Asia YTD & Contagion Integrated"
AUTHOR_LINE = "MK FinTECH LabGEN @2026 Istanbul, Murat KONUKLAR"
NEWS_SOURCE_URL = "https://www.investing.com/news/stock-market-news/korea-sinks-as-ai-chip-selloff-deepens-japan-suppliers-tumble-4772256"
NEWS_SOURCE_TITLE = "Korea sinks as AI-chip selloff deepens; Japan suppliers tumble"
NEWS_SOURCE_URL_2 = "https://www.investing.com/news/stock-market-news/asia-stocks-fall-as-ai-valuation-fears-overshadow-samsungs-blockbuster-earnings-4778205"
NEWS_SOURCE_TITLE_2 = "Asia stocks fall as AI valuation fears overshadow Samsung's blockbuster earnings"
NEWS_SOURCE_URL_3 = "https://www.investing.com/news/stock-market-news/sk-hynix-shares-slide-nearly-11-in-seoul-after-bumper-nasdaq-debut-4787404"
NEWS_SOURCE_TITLE_3 = "SK Hynix shares slide nearly 14% in Seoul after bumper Nasdaq debut"
NEWS_SOURCE_URL_4 = "https://www.investing.com/news/stock-market-news/asia-stocks-slide-as-s-korea-chip-stocks-tumble-tsmc-earnings-in-focus-4794618"
NEWS_SOURCE_TITLE_4 = "Asia stocks slide as S. Korea chip stocks tumble; TSMC earnings in focus"
NEWS_SOURCE_DATE_4 = "2026-07-16"
NEWS_SOURCE_URL_5 = "https://www.investing.com/news/stock-market-news/european-chip-stocks-fall-after-sharp-us-peers-selloff-4797767"
NEWS_SOURCE_TITLE_5 = "European chip stocks fall after sharp U.S. peers' selloff"
NEWS_SOURCE_DATE_5 = "2026-07-17"

# Article-five European semiconductor contagion universe. Yahoo tickers are direct local listings;
# unavailable names remain visible in exclusion/data-quality logs and are never replaced synthetically.
NEWS_EVENT_5_TICKERS = [
    "ASML.AS", "ASM.AS", "BESI.AS", "SOI.PA", "IFX.DE", "AIXA.DE",
    "STMPA.PA", "WAF.DE", "AMS.SW", "INTC", "WDC", "STX", "SNDK", "TSM", "^SOX"
]
EUROPE_SEMICONDUCTOR_SUBSECTORS = {
    "ASML.AS":"Lithography / WFE", "ASM.AS":"Deposition / WFE", "BESI.AS":"Assembly / Advanced Packaging",
    "SOI.PA":"Engineered Substrates", "IFX.DE":"Power / Automotive Semiconductors", "AIXA.DE":"Deposition Equipment",
    "STMPA.PA":"Diversified Semiconductors", "WAF.DE":"Silicon Wafers / Materials", "AMS.SW":"Optical Sensors / Photonics",
}

SEMICONDUCTOR_REGION_BASKETS = {
    "United States": ["NVDA","AMD","MU","INTC","WDC","STX","SNDK","AMAT","LRCX","KLAC","AVGO"],
    "Europe": list(EUROPE_SEMICONDUCTOR_SUBSECTORS.keys()),
    "Asia": ["005930.KS","000660.KS","2330.TW","2454.TW","285A.T","4062.T"],
}

# Asia-origin company registry used by the YTD performance cockpit. Local listings and ADRs are
# shown separately, while country aggregates prefer primary local listings to avoid double counting.
ASIA_ORIGIN_SECURITIES = {
    "005930.KS":{"issuer":"Samsung Electronics Co., Ltd.","country":"South Korea","subsector":"Memory / Foundry / Consumer Electronics","listing_market":"Seoul","listing_type":"Primary Local","currency":"KRW"},
    "000660.KS":{"issuer":"SK hynix Inc.","country":"South Korea","subsector":"HBM / DRAM / NAND Memory","listing_market":"Seoul","listing_type":"Primary Local","currency":"KRW"},
    "011070.KS":{"issuer":"LG Innotek Co., Ltd.","country":"South Korea","subsector":"Electronic Components / Camera Modules","listing_market":"Seoul","listing_type":"Primary Local","currency":"KRW"},
    "SKHY":{"issuer":"SK hynix Inc.","country":"South Korea","subsector":"HBM / DRAM / NAND Memory","listing_market":"Nasdaq","listing_type":"ADR / Cross-Listing","currency":"USD"},
    "2330.TW":{"issuer":"Taiwan Semiconductor Manufacturing Co.","country":"Taiwan","subsector":"Leading-Edge Foundry","listing_market":"Taiwan","listing_type":"Primary Local","currency":"TWD"},
    "2317.TW":{"issuer":"Hon Hai Precision Industry / Foxconn","country":"Taiwan","subsector":"AI Servers / Electronics Manufacturing","listing_market":"Taiwan","listing_type":"Primary Local","currency":"TWD"},
    "2454.TW":{"issuer":"MediaTek Inc.","country":"Taiwan","subsector":"Mobile / Edge AI Semiconductors","listing_market":"Taiwan","listing_type":"Primary Local","currency":"TWD"},
    "TSM":{"issuer":"Taiwan Semiconductor Manufacturing Co.","country":"Taiwan","subsector":"Leading-Edge Foundry","listing_market":"NYSE","listing_type":"ADR / Cross-Listing","currency":"USD"},
    "285A.T":{"issuer":"Kioxia Holdings Corporation","country":"Japan","subsector":"NAND Flash Memory","listing_market":"Tokyo","listing_type":"Primary Local","currency":"JPY"},
    "4062.T":{"issuer":"Ibiden Co., Ltd.","country":"Japan","subsector":"Advanced IC Substrates","listing_market":"Tokyo","listing_type":"Primary Local","currency":"JPY"},
    "6981.T":{"issuer":"Murata Manufacturing Co., Ltd.","country":"Japan","subsector":"Electronic Components","listing_market":"Tokyo","listing_type":"Primary Local","currency":"JPY"},
    "5801.T":{"issuer":"Furukawa Electric Co., Ltd.","country":"Japan","subsector":"Fiber / Cables / AI Connectivity","listing_market":"Tokyo","listing_type":"Primary Local","currency":"JPY"},
    "5706.T":{"issuer":"Mitsui Mining and Smelting Co., Ltd.","country":"Japan","subsector":"Electronic Materials / Copper Foil","listing_market":"Tokyo","listing_type":"Primary Local","currency":"JPY"},
    "9984.T":{"issuer":"SoftBank Group Corp.","country":"Japan","subsector":"Technology Investment / AI Exposure","listing_market":"Tokyo","listing_type":"Primary Local","currency":"JPY"},
    "2371.T":{"issuer":"Kakaku.com, Inc.","country":"Japan","subsector":"Internet Services / Technology","listing_market":"Tokyo","listing_type":"Primary Local","currency":"JPY"},
}
ASIA_ORIGIN_COUNTRY_ORDER = ["South Korea", "Taiwan", "Japan"]

# Event-four securities and macro/regional risk factors. These are monitoring inputs,
# not synthetic prices and not automatic portfolio constituents.
NEWS_EVENT_4_TICKERS = ["005930.KS", "000660.KS", "2330.TW", "TSM", "NVDA", "AAPL", "ASML.AS", "ASML", "SKHY"]
NEWS_EVENT_MONITOR_TICKERS = list(dict.fromkeys(NEWS_EVENT_4_TICKERS + NEWS_EVENT_5_TICKERS))
MANAGEMENT_RISK_FACTORS = {
    "^KS11": {"name": "KOSPI Composite", "type": "equity_return", "risk_sign": -1, "channel": "Korea chip concentration"},
    "^SOX": {"name": "Philadelphia Semiconductor Index", "type": "equity_return", "risk_sign": -1, "channel": "Global semiconductor beta"},
    "^TWII": {"name": "Taiwan Weighted Index", "type": "equity_return", "risk_sign": -1, "channel": "TSMC / Taiwan technology beta"},
    "^N225": {"name": "Nikkei 225", "type": "equity_return", "risk_sign": -1, "channel": "Japan memory and equipment beta"},
    "^HSI": {"name": "Hang Seng Index", "type": "equity_return", "risk_sign": -1, "channel": "China / Hong Kong offset"},
    "^STI": {"name": "Straits Times Index", "type": "equity_return", "risk_sign": -1, "channel": "Singapore regional beta"},
    "CL=F": {"name": "WTI Crude Oil", "type": "market_return", "risk_sign": 1, "channel": "Energy inflation / Hormuz risk"},
    "DX-Y.NYB": {"name": "US Dollar Index", "type": "market_return", "risk_sign": 1, "channel": "USD financial conditions"},
    "^TNX": {"name": "US Treasury 10Y Yield", "type": "yield_level", "risk_sign": 1, "channel": "Discount-rate pressure"},
}

# SupertrendPro Institutional integration controls
INSTITUTIONAL_ENGINE_VERSION = "2.2.0"
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
REPORT_OUTPUT = str(OUTPUT_DIR / "Global_Semiconductor_SupertrendPro_Institutional_QS_ENGINE.html")
EXCEL_OUTPUT = str(OUTPUT_DIR / "Global_Semiconductor_SupertrendPro_Institutional_QS_ENGINE_Analytics.xlsx")

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
"005930.KS":{"name":"Samsung Electronics Co., Ltd.","sector":"Semiconductors","theme":"Memory / AI Supply Chain","country":"South Korea","article_role":"KOSPI heavyweight; renewed 8%+ selloff and trading-halt event exposure","source_article":"Articles 1, 2 & 4"},
"000660.KS":{"name":"SK Hynix Inc.","sector":"Semiconductors","theme":"HBM / Memory / AI Supply Chain","country":"South Korea","article_role":"KOSPI heavyweight; renewed 11% selloff and memory-risk transmission channel","source_article":"Articles 1, 3 & 4"},
"META":{"name":"Meta Platforms, Inc.","sector":"Communication Services","theme":"AI Infrastructure / Hyperscaler","country":"United States","article_role":"Cloud infrastructure reports cited as AI spending concern"},
"AAPL":{"name":"Apple Inc.","sector":"Information Technology","theme":"Technology / Memory Demand","country":"United States","article_role":"End-demand and TSMC customer exposure highlighted in the event chain","source_article":"Articles 1 & 4"},
"NVDA":{"name":"NVIDIA Corporation","sector":"Semiconductors","theme":"AI GPU / TSMC Demand Anchor","country":"United States","article_role":"Primary advanced-AI-chip customer and demand read-through named in the TSMC event chain","source_article":"Article 4"},
"MU":{"name":"Micron Technology, Inc.","sector":"Semiconductors","theme":"Memory","country":"United States","article_role":"US memory maker mentioned as falling more than 10%"},
"SNDK":{"name":"SanDisk Corporation","sector":"Technology Hardware / Storage","theme":"Storage / Memory","country":"United States","article_role":"Storage company mentioned as falling more than 10%"},
"285A.T":{"name":"Kioxia Holdings Corporation","sector":"Semiconductors","theme":"NAND Memory","country":"Japan","article_role":"Japan chip-related name mentioned as tumbling"},
"4062.T":{"name":"Ibiden Co., Ltd.","sector":"Semiconductor Components","theme":"Substrate / AI Supply Chain","country":"Japan","article_role":"Japan chip supplier mentioned as falling"},
"6981.T":{"name":"Murata Manufacturing Co., Ltd.","sector":"Electronic Components","theme":"Components / AI Supply Chain","country":"Japan","article_role":"Japan supplier mentioned as falling"},
"5801.T":{"name":"Furukawa Electric Co., Ltd.","sector":"Electronic Components / Materials","theme":"Cables / Components","country":"Japan","article_role":"Japan supplier mentioned as falling"},
"5706.T":{"name":"Mitsui Mining and Smelting Co., Ltd.","sector":"Materials / Electronics Supply Chain","theme":"Materials / AI Supply Chain","country":"Japan","article_role":"Japan supplier mentioned as falling"},
"2330.TW":{"name":"Taiwan Semiconductor Manufacturing Company","sector":"Semiconductors","theme":"Foundry / AI Supply Chain","country":"Taiwan","article_role":"TSMC earnings bellwether for AI demand, capex and sector guidance","source_article":"Articles 1, 3 & 4"},
"9984.T":{"name":"SoftBank Group Corp.","sector":"Technology Investment","theme":"AI Investment / OpenAI Exposure","country":"Japan","article_role":"AI investment financing report mentioned"},
"2371.T":{"name":"Kakaku.com, Inc.","sector":"Internet Services","theme":"Online price-comparison technology","country":"Japan","article_role":"Online price-comparison operator mentioned","source_article":"Article 1"},
"2317.TW":{"name":"Hon Hai Precision Industry Co., Ltd. / Foxconn","sector":"Electronics Manufacturing / AI Servers","theme":"NVIDIA AI server assembly partner / AI hardware supply chain","country":"Taiwan","article_role":"Nvidia largest AI server assembly partner mentioned in second article","source_article":"Article 2"},
"2454.TW":{"name":"MediaTek Inc.","sector":"Semiconductors","theme":"Mobile / edge AI semiconductors","country":"Taiwan","article_role":"Taiwan semiconductor name mentioned as falling in second article","source_article":"Article 2"},
"011070.KS":{"name":"LG Innotek Co., Ltd.","sector":"Electronic Components","theme":"Camera modules / electronic components / AI hardware supply chain","country":"South Korea","article_role":"Korean technology component supplier mentioned as falling in related chip-share article","source_article":"Article 2"},
"SKHY":{"name":"SK hynix Inc. American Depositary Shares","sector":"Semiconductors","theme":"HBM / Memory / Nasdaq ADR","country":"United States / South Korea","article_role":"Nasdaq ADR and cross-listing transmission channel during renewed Seoul selloff","source_article":"Articles 3 & 4"},
"TSM":{"name":"Taiwan Semiconductor Manufacturing Company Limited ADR","sector":"Semiconductors","theme":"Foundry / AI Supply Chain / US ADR","country":"United States / Taiwan","article_role":"US-listed TSMC earnings and guidance transmission instrument","source_article":"Articles 3 & 4"},
"ASML.AS":{"name":"ASML Holding N.V. — Euronext Amsterdam","sector":"Semiconductor Equipment","theme":"Advanced Lithography / EUV","country":"Netherlands","article_role":"Equipment-cycle read-through and European contagion bellwether","source_article":"Articles 3, 4 & 5"},
"ASM.AS":{"name":"ASM International N.V.","sector":"Semiconductor Equipment","theme":"Atomic Layer Deposition / WFE","country":"Netherlands","article_role":"European chip-equipment selloff transmission","source_article":"Article 5"},
"BESI.AS":{"name":"BE Semiconductor Industries N.V.","sector":"Semiconductor Equipment","theme":"Advanced Packaging / Assembly","country":"Netherlands","article_role":"Advanced packaging selloff transmission","source_article":"Article 5"},
"SOI.PA":{"name":"Soitec S.A.","sector":"Semiconductor Materials","theme":"Engineered Substrates","country":"France","article_role":"European materials selloff transmission","source_article":"Article 5"},
"IFX.DE":{"name":"Infineon Technologies AG","sector":"Semiconductors","theme":"Power / Automotive Semiconductors","country":"Germany","article_role":"European diversified chip selloff transmission","source_article":"Article 5"},
"AIXA.DE":{"name":"AIXTRON SE","sector":"Semiconductor Equipment","theme":"Compound Semiconductor Deposition","country":"Germany","article_role":"European WFE selloff transmission","source_article":"Article 5"},
"STMPA.PA":{"name":"STMicroelectronics N.V.","sector":"Semiconductors","theme":"MCU / Analog / Power","country":"France / Switzerland","article_role":"European diversified chip selloff transmission","source_article":"Article 5"},
"WAF.DE":{"name":"Siltronic AG","sector":"Semiconductor Materials","theme":"Silicon Wafers","country":"Germany","article_role":"Upstream wafer-materials selloff transmission","source_article":"Article 5"},
"AMS.SW":{"name":"ams-OSRAM AG","sector":"Electronic Components / Semiconductors","theme":"Optical Sensors / Photonics","country":"Switzerland / Austria","article_role":"European optical-sensor selloff transmission","source_article":"Article 5"},
"WDC":{"name":"Western Digital Corporation","sector":"Technology Hardware / Storage","theme":"Data Storage / Memory","country":"United States","article_role":"U.S. memory/storage shock source named in Article 5","source_article":"Article 5"},
"STX":{"name":"Seagate Technology Holdings plc","sector":"Technology Hardware / Storage","theme":"Data Storage / Memory","country":"United States / Ireland","article_role":"U.S. memory/storage shock source named in Article 5","source_article":"Article 5"},
"INTC":{"name":"Intel Corporation","sector":"Semiconductors","theme":"CPU / Foundry","country":"United States","article_role":"U.S. chip selloff source named in Article 5","source_article":"Article 5"}}

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


EUROPEAN_SEMICONDUCTOR_UNIVERSE = {
"ASML.AS":{"name":"ASML Holding N.V.","sector":"Semiconductor Equipment","theme":"EUV Lithography / WFE","country":"Netherlands","article_role":"European bellwether; sharp selloff after U.S. peer weakness","source_article":"Article 5"},
"ASM.AS":{"name":"ASM International N.V.","sector":"Semiconductor Equipment","theme":"Atomic Layer Deposition / WFE","country":"Netherlands","article_role":"European deposition-equipment contagion channel","source_article":"Article 5"},
"BESI.AS":{"name":"BE Semiconductor Industries N.V.","sector":"Semiconductor Equipment","theme":"Advanced Packaging / Assembly","country":"Netherlands","article_role":"Advanced-packaging beta and high-expectation risk channel","source_article":"Article 5"},
"SOI.PA":{"name":"Soitec S.A.","sector":"Semiconductor Materials","theme":"Engineered Substrates / SOI Wafers","country":"France","article_role":"European substrate and materials shock channel","source_article":"Article 5"},
"IFX.DE":{"name":"Infineon Technologies AG","sector":"Semiconductors","theme":"Power / Automotive / Industrial Chips","country":"Germany","article_role":"European diversified semiconductor beta","source_article":"Article 5"},
"AIXA.DE":{"name":"AIXTRON SE","sector":"Semiconductor Equipment","theme":"Compound Semiconductor Deposition","country":"Germany","article_role":"High-beta deposition-equipment contagion channel","source_article":"Article 5"},
"STMPA.PA":{"name":"STMicroelectronics N.V.","sector":"Semiconductors","theme":"MCU / Analog / Power / Automotive","country":"France / Switzerland","article_role":"European diversified chip de-rating channel","source_article":"Article 5"},
"WAF.DE":{"name":"Siltronic AG","sector":"Semiconductor Materials","theme":"Silicon Wafers / Materials","country":"Germany","article_role":"Upstream wafer-materials stress channel","source_article":"Article 5"},
"AMS.SW":{"name":"ams-OSRAM AG","sector":"Electronic Components / Semiconductors","theme":"Optical Sensors / Photonics / LEDs","country":"Switzerland / Austria","article_role":"Optical and sensor high-volatility contagion channel","source_article":"Article 5"},
}

INDEX_BENCHMARKS = {
"^GSPC":{"name":"S&P 500 Index","region":"United States"}, "^IXIC":{"name":"Nasdaq Composite Index","region":"United States"},
"^NDX":{"name":"Nasdaq 100 Index","region":"United States"}, "^SOX":{"name":"Philadelphia Semiconductor Index","region":"United States"},
"^KS11":{"name":"KOSPI Composite Index","region":"South Korea"}, "^N225":{"name":"Nikkei 225 Index","region":"Japan"},
"1306.T":{"name":"NEXT FUNDS TOPIX ETF — TOPIX Benchmark Proxy (ETF Exception Only for TOPIX)","region":"Japan","benchmark_type":"ETF proxy exception"}, "^AXJO":{"name":"S&P/ASX 200 Index","region":"Australia"},
"^NSEI":{"name":"Nifty 50 Index","region":"India"}, "^JKSE":{"name":"Jakarta Composite Index","region":"Indonesia"},
"000001.SS":{"name":"Shanghai Composite Index","region":"China"}, "000300.SS":{"name":"CSI 300 Index","region":"China"},
"^TWII":{"name":"TWSE Capitalization Weighted Index","region":"Taiwan"}, "^HSI":{"name":"Hang Seng Index","region":"Hong Kong"},
"^STI":{"name":"Straits Times Index","region":"Singapore"},
"^STOXX50E":{"name":"EURO STOXX 50 Index","region":"Euro Area"}, "^GDAXI":{"name":"DAX Index","region":"Germany"},
"^FCHI":{"name":"CAC 40 Index","region":"France"}, "^AEX":{"name":"AEX Index","region":"Netherlands"},
"^SSMI":{"name":"Swiss Market Index","region":"Switzerland"},
"NQ=F":{"name":"Nasdaq 100 Futures","region":"US Futures"}, "ES=F":{"name":"S&P 500 Futures","region":"US Futures"}}

UNIVERSE_CONFIGS = {
"US Major Stocks 10M Portfolio":{"universe":US_MAJOR_UNIVERSE,"primary_benchmark":"^GSPC","benchmarks":["^GSPC","^IXIC"],"min_observations":756,"capital_mode":"whole_share_usd","description":"Original US major single-stock 10M USD portfolio. Existing feature set preserved."},
"Article Shock Universe — AI Chip Selloff":{"universe":ARTICLE_SHOCK_UNIVERSE,"primary_benchmark":"^KS11","benchmarks":["^KS11","^N225","1306.T","^TWII","^HSI","^STI","^IXIC","^NDX","^SOX","^GSPC","^AXJO","^NSEI","^JKSE","000001.SS","000300.SS","NQ=F","ES=F"],"min_observations":60,"capital_mode":"equal_weight_return_index","description":"Companies and transmission channels identified across five Investing.com AI-chip articles. The fourth event adds renewed Korea selloff, TSMC earnings-risk, BOK tightening, regional-index dispersion and energy-inflation channels. Mixed currencies; analyzed as an actual-return equal-weight basket. New listings remain in the event monitor when long-history requirements are not met."},
"US Technology + AI + Chip 20+ Universe":{"universe":US_TECH_AI_CHIP_UNIVERSE,"primary_benchmark":"^IXIC","benchmarks":["^IXIC","^SOX","^NDX","^GSPC"],"min_observations":504,"capital_mode":"whole_share_usd","description":"US-listed technology, AI infrastructure, semiconductor and chip ecosystem single stocks, including TSM, ASML and new SKHY ADR. No ETFs."},
"European Semiconductor Contagion Universe":{"universe":EUROPEAN_SEMICONDUCTOR_UNIVERSE,"primary_benchmark":"^STOXX50E","benchmarks":["^STOXX50E","^AEX","^GDAXI","^FCHI","^SSMI","^SOX","^NDX"],"min_observations":504,"capital_mode":"equal_weight_return_index","description":"European semiconductor, equipment and materials companies identified in Article 5. Mixed European currencies are analyzed as local-currency actual-return series; no synthetic FX conversion and no ETF constituents."}}

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
    symbols += list(MANAGEMENT_RISK_FACTORS.keys())
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
                details[ticker]={"meta":meta,"indicator":ind,"supertrend_backtest":st_bt,"supertrend_trades":st_trades,"supertrend_stats":st_stats,"macd_backtest":macd_bt,"macd_trades":macd_trades,"macd_stats":macd_stats,"leading_lab":lab_df,"leading_stats":lab_stats,"score":score_df,"factors":factors,"decision":decision}
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
        uid = str(abs(hash(uname)) % 100000)
        chart_html = "".join(f'<div class="chart-block">{c}</div>' for c in charts)
        blocks.append(
            f'<div class="section"><h2>{uname} — SupertrendPro Institutional Integration</h2>'
            f'<div class="note"><b>Benchmark:</b> {data["benchmark"]}<br>'
            f'<b>Engine:</b> Smart Supertrend + MACD/ATR + Leading Signal Lab + Explainable 100-Point Institutional Score.<br>'
            f'<b>Execution:</b> signals are applied on the next bar and net returns deduct '
            f'{INSTITUTIONAL_TRANSACTION_COST_BPS:.0f} bps transaction cost plus '
            f'{INSTITUTIONAL_SLIPPAGE_BPS:.0f} bps slippage per side. No synthetic price or proxy security is used.</div>'
            f'<h3>Institutional Ranking</h3>{table(ranking, "inst_rank_" + uid)}'
            f'<h3>Strategy Comparison</h3>{table(strategies, "inst_strat_" + uid)}'
            f'<h3>Latest Factor Contributions</h3>{table(data["factors"], "inst_fac_" + uid)}'
            f'<h3>Institutional Engine Exclusion Log</h3>{table(exclusions, "inst_exc_" + uid)}'
            f'<h3>Interactive Institutional Charts</h3>{chart_html}</div>'
        )
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
PCT_COLS.update({"1D Return","5D Return","20D Return","Current Drawdown","Current Weight","Risk Contribution %","Risk Budget Gap","EWMA Ann Vol","Vol Percentile","Momentum 20D","Momentum 63D","News Event Exposure","Buy Breadth","Sell Breadth","Portfolio EWMA Vol","Portfolio Vol Percentile","Portfolio 1D","Portfolio 5D","Portfolio 20D","Weight HHI","Negative Breadth","EWMA Volatility","Volatility Percentile","1D Basket Return","5D Basket Return","20D Basket Return","252D Return","Distance From 52W High","YTD Return","60D Return","Distance to YTD High","YTD Max Drawdown","Average YTD Return","Median YTD Return","Positive Breadth","Best YTD Return","Worst YTD Return","Average EWMA Volatility"})
FLOAT_COLS.update({"Shock Z","Risk Pressure Z","Event Stress Score","Conviction Score","Risk Score","Average Institutional Score","Average Confidence","Contagion Score","Expectation Risk Score","SOX Same-Day Beta","SOX Lag-1 Beta","SOX Same-Day Correlation","SOX Lag-1 Correlation","Downside Shock Z","Reference Price","YTD High","YTD Low"})
DATE_COLS.update({"Reference Date","Latest Date"})
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

def news_event_register():
    """Structured event register used by Streamlit, HTML and Excel governance outputs."""
    return pd.DataFrame([
        {"Event ID":"AI_CHIP_01","Event Date":"2026-06-22","News Source":NEWS_SOURCE_TITLE,"Primary Shock":"Asia semiconductor de-rating","Affected Securities":"Samsung, SK Hynix, Japan suppliers, TSMC","Risk Channels":"AI valuation, memory cycle, supplier beta","Management Horizon":"1D / 20D / 60D"},
        {"Event ID":"AI_CHIP_02","Event Date":"2026-07-08","News Source":NEWS_SOURCE_TITLE_2,"Primary Shock":"AI valuation concerns despite strong earnings","Affected Securities":"Samsung, Asian AI hardware chain","Risk Channels":"Earnings hurdle, capex sustainability, factor rotation","Management Horizon":"1D / earnings window / 60D"},
        {"Event ID":"AI_CHIP_03","Event Date":"2026-07-13","News Source":NEWS_SOURCE_TITLE_3,"Primary Shock":"SK Hynix ADR/local cross-listing dislocation","Affected Securities":"000660.KS, SKHY, MU, SNDK, SOX","Risk Channels":"ADR liquidity, price discovery, memory volatility","Management Horizon":"Intraday / 5D / 20D"},
        {"Event ID":"AI_CHIP_04","Event Date":NEWS_SOURCE_DATE_4,"News Source":NEWS_SOURCE_TITLE_4,"Primary Shock":"KOSPI trading halt and renewed chip selloff ahead of TSMC earnings","Affected Securities":"005930.KS, 000660.KS, 2330.TW, TSM, NVDA, AAPL, ASML.AS","Risk Channels":"Korea concentration, TSMC earnings hurdle, BOK +25bp, oil inflation, Hormuz risk","Management Horizon":"1D shock / 20D tactical / 60D allocation"},
        {"Event ID":"AI_CHIP_05","Event Date":NEWS_SOURCE_DATE_5,"News Source":NEWS_SOURCE_TITLE_5,"Primary Shock":"U.S. semiconductor selloff transmitted into European chip, equipment and materials names","Affected Securities":"ASML.AS, ASM.AS, BESI.AS, SOI.PA, IFX.DE, AIXA.DE, STMPA.PA, WAF.DE, AMS.SW, INTC, WDC, STX, TSM, SOX","Risk Channels":"SOX beta, overnight contagion, memory/storage shock, expectations de-rating, WFE and materials breadth","Management Horizon":"1D event / 5D contagion / 20D tactical / 60D allocation"},
    ])
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
def create_report(results, sox, qs_reports, institutional_results, cross_listing, management_packs=None, contagion_pack=None, asia_ytd_pack=None):
    ac,ai=article_tables(); all_rows=[]
    for uname,cfg in UNIVERSE_CONFIGS.items():
        for t,m in cfg["universe"].items(): all_rows.append({"Universe":uname,"Ticker":t,"Company":m["name"],"Sector":m.get("sector","N/A"),"Theme":m.get("theme","N/A"),"Country":m.get("country","United States")})
    tabs=['<button class="tablink active" onclick="openTab(event, \'source\')">News Source & Universes</button>']; contents=[f'<div id="source" class="tabcontent active-content"><div class="section"><h2>News Source & Project Scope</h2><div class="note"><b>News 1:</b> {NEWS_SOURCE_TITLE}<br><b>URL 1:</b> {NEWS_SOURCE_URL}<br><b>News 2:</b> {NEWS_SOURCE_TITLE_2}<br><b>URL 2:</b> {NEWS_SOURCE_URL_2}<br><b>News 3:</b> {NEWS_SOURCE_TITLE_3}<br><b>URL 3:</b> {NEWS_SOURCE_URL_3}<br><b>News 4:</b> {NEWS_SOURCE_TITLE_4}<br><b>URL 4:</b> {NEWS_SOURCE_URL_4}<br><b>News 5:</b> {NEWS_SOURCE_TITLE_5}<br><b>URL 5:</b> {NEWS_SOURCE_URL_5}<br><b>Rule:</b> Existing features preserved. Added Article Shock Universe from all five Investing.com articles and US Technology + AI + Chip Universe. The third article adds the SKHY cross-listing channel; the fourth adds renewed Korea selloff and macro-risk monitoring; the fifth adds U.S.-to-Europe semiconductor contagion, WFE/materials breadth and expectations de-rating analysis. The Asia YTD cockpit groups all configured South Korean, Taiwanese and Japanese-origin issuers by country, listing type and subsector with strict YTD governance. SKHY, TSM, ASML.AS, ASML and related listings are analyzed where real Yahoo history permits. No ETF constituents in investment universes. Interactive charts are rendered in full horizontal page width. <b>TOPIX exception:</b> because Yahoo Finance did not return ^TOPX index data, TOPIX benchmark exposure is represented only by 1306.T, NEXT FUNDS TOPIX ETF. This ETF is used solely as a benchmark proxy, never as a portfolio constituent. No synthetic fallback.<br><b>SOX diagnostics:</b> Philadelphia Semiconductor Index <code>^SOX</code> is separately downloaded from 2018-01-01. The report includes daily log returns, 20D rolling mean, 20D ±2σ bands, breach counts and largest breach dates.</div><h3>Structured News Event Register</h3>{table(news_event_register(),"news_events")}<h3>Article Companies</h3>{table(ac,"articlec")}<h3>Article Indices / Benchmarks</h3>{table(ai,"articlei")}<h3>All Configured Universes</h3>{table(pd.DataFrame(all_rows),"allu")}</div></div>']
    if management_packs:
        tabs.append("<button class='tablink' onclick=\"openTab(event, 'managementbrief')\">Hedge Fund Management Brief</button>")
        contents.append(f'<div id="managementbrief" class="tabcontent">{management_pack_html(management_packs)}</div>')
    if contagion_pack:
        tabs.append("<button class='tablink' onclick=\"openTab(event, 'globalcontagion')\">Global Semiconductor Contagion</button>")
        contents.append(f'<div id="globalcontagion" class="tabcontent">{global_contagion_tab_html(contagion_pack)}</div>')
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
    if asia_ytd_pack:
        tabs.append('<button class="tablink" onclick="openTab(event, \'asiaytd\')">Asia YTD Performance</button>')
        contents.append(f'<div id="asiaytd" class="tabcontent">{asia_ytd_tab_html(asia_ytd_pack)}</div>')
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
def export_excel(results, sox, qs_reports, institutional_results, cross_listing, management_packs=None, contagion_pack=None, asia_ytd_pack=None):
    with pd.ExcelWriter(EXCEL_OUTPUT,engine="xlsxwriter") as writer:
        ac,ai=article_tables(); ac.to_excel(writer,"Article_Companies",index=False); ai.to_excel(writer,"Article_Indices",index=False); news_event_register().to_excel(writer,"News_Event_Register",index=False)
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
        if management_packs:
            for uname, pack in management_packs.items():
                p=sheet("MGMT_"+re.sub(r"[^A-Za-z0-9]+","_",uname)[:14])
                metrics_df(pack["summary"]).to_excel(writer,sheet(p+"_Summary"),index=False)
                pack["macro"].to_excel(writer,sheet(p+"_Macro"),index=False)
                pack["event"].to_excel(writer,sheet(p+"_Event"),index=False)
                pack["actions"].to_excel(writer,sheet(p+"_Actions"),index=False)
        if contagion_pack:
            metrics_df(contagion_pack["summary"]).to_excel(writer,"Global_Contagion_Summary",index=False)
            contagion_pack["regional"].to_excel(writer,"Regional_Chip_Baskets",index=False)
            contagion_pack["europe"].to_excel(writer,"Europe_Contagion",index=False)
            contagion_pack["segments"].to_excel(writer,"Europe_Subsector_Stress",index=False)
            for region,hist in contagion_pack.get("regional_history",{}).items():
                hist.to_excel(writer,sheet("Region_"+region))
        if asia_ytd_pack:
            metrics_df(asia_ytd_pack.get("summary", {})).to_excel(writer,"Asia_YTD_Summary",index=False)
            asia_ytd_pack.get("securities", pd.DataFrame()).drop(columns=["Country Order"], errors="ignore").to_excel(writer,"Asia_YTD_Securities",index=False)
            asia_ytd_pack.get("countries", pd.DataFrame()).to_excel(writer,"Asia_YTD_Countries",index=False)
            asia_ytd_pack.get("subsectors", pd.DataFrame()).to_excel(writer,"Asia_YTD_Subsectors",index=False)
            asia_ytd_pack.get("exclusions", pd.DataFrame()).to_excel(writer,"Asia_YTD_Exclusions",index=False)
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


# -------------------------------------------------------------------------
# ASIA-ORIGIN YTD PERFORMANCE & BREADTH ENGINE
# -------------------------------------------------------------------------
def _strict_ytd_snapshot(series):
    """Return strict YTD metrics using the last observed close before Jan 1.

    New listings without a prior-year close use the first available current-year observation and
    are explicitly labelled as a since-listing/YTD proxy rather than being silently overstated.
    """
    s = pd.Series(series, dtype=float).replace([np.inf, -np.inf], np.nan).dropna().sort_index()
    if s.empty:
        return None
    normalized_index = pd.to_datetime(s.index)
    if getattr(normalized_index, "tz", None) is not None:
        normalized_index = normalized_index.tz_localize(None)
    s.index = normalized_index
    latest_date = pd.Timestamp(s.index[-1])
    latest_price = float(s.iloc[-1])
    year_start = pd.Timestamp(year=latest_date.year, month=1, day=1)
    prior = s[s.index < year_start]
    current = s[s.index >= year_start]
    if current.empty:
        return None
    if not prior.empty:
        reference_date = pd.Timestamp(prior.index[-1])
        reference_price = float(prior.iloc[-1])
        basis = "Prior-year closing observation"
        strict_ytd = True
    else:
        reference_date = pd.Timestamp(current.index[0])
        reference_price = float(current.iloc[0])
        basis = "First available current-year observation (since-listing proxy)"
        strict_ytd = False
    ytd_return = latest_price / reference_price - 1 if reference_price > 0 else np.nan
    ytd_path = current / reference_price - 1 if reference_price > 0 else pd.Series(dtype=float)
    ytd_high = float(current.max()) if not current.empty else np.nan
    ytd_low = float(current.min()) if not current.empty else np.nan
    ytd_dd = current / current.cummax() - 1 if not current.empty else pd.Series(dtype=float)
    return {
        "Reference Date": reference_date,
        "Reference Price": reference_price,
        "Latest Date": latest_date,
        "Latest Price": latest_price,
        "YTD Return": ytd_return,
        "YTD High": ytd_high,
        "YTD Low": ytd_low,
        "Distance to YTD High": latest_price / ytd_high - 1 if ytd_high > 0 else np.nan,
        "YTD Max Drawdown": float(ytd_dd.min()) if not ytd_dd.empty else np.nan,
        "YTD Positive Days": int((ytd_path.diff() > 0).sum()) if len(ytd_path) > 1 else 0,
        "YTD Negative Days": int((ytd_path.diff() < 0).sum()) if len(ytd_path) > 1 else 0,
        "Performance Basis": basis,
        "Strict YTD": strict_ytd,
    }


def build_asia_origin_ytd_pack(close, institutional_results):
    """Create security-, country- and subsector-level Asia-origin YTD analytics."""
    details = _all_institutional_details(institutional_results)
    rows, exclusions = [], []
    for ticker, meta in ASIA_ORIGIN_SECURITIES.items():
        if ticker not in close.columns:
            exclusions.append({"Ticker":ticker,"Issuer":meta["issuer"],"Origin Country":meta["country"],"Reason":"No Yahoo Finance close series returned"})
            continue
        s = pd.Series(close[ticker], dtype=float).replace([np.inf, -np.inf], np.nan).dropna().sort_index()
        snap = _strict_ytd_snapshot(s)
        if snap is None:
            exclusions.append({"Ticker":ticker,"Issuer":meta["issuer"],"Origin Country":meta["country"],"Reason":"No current-year observations available"})
            continue
        ewma_vol, vol_pct, _ = _ewma_latest_from_returns(s.pct_change())
        detail = details.get(ticker, {})
        decision = detail.get("decision", {}) if isinstance(detail, dict) else {}
        row = {
            "Ticker":ticker,
            "Issuer":meta["issuer"],
            "Origin Country":meta["country"],
            "Subsector":meta["subsector"],
            "Listing Market":meta["listing_market"],
            "Listing Type":meta["listing_type"],
            "Currency":meta["currency"],
            **snap,
            "1D Return":_window_total_return(s, 1),
            "5D Return":_window_total_return(s, 5),
            "20D Return":_window_total_return(s, 20),
            "60D Return":_window_total_return(s, 60),
            "EWMA Volatility":ewma_vol,
            "Volatility Percentile":vol_pct,
            "Institutional Score":decision.get("Institutional Score", np.nan),
            "Confidence Score":decision.get("Confidence Score", np.nan),
            "Recommendation":decision.get("Recommendation", "INSUFFICIENT HISTORY"),
            "Available Observations":int(len(s)),
        }
        row["YTD Direction"] = "GAIN" if row["YTD Return"] > 0.001 else ("LOSS" if row["YTD Return"] < -0.001 else "FLAT")
        rows.append(row)
    securities = pd.DataFrame(rows)
    exclusions_df = pd.DataFrame(exclusions)
    if securities.empty:
        return {"summary":{},"securities":securities,"countries":pd.DataFrame(),"subsectors":pd.DataFrame(),"exclusions":exclusions_df}
    country_order = {c:i for i,c in enumerate(ASIA_ORIGIN_COUNTRY_ORDER)}
    securities["Country Order"] = securities["Origin Country"].map(country_order).fillna(99).astype(int)
    securities["Global YTD Rank"] = securities["YTD Return"].rank(ascending=False, method="min").astype("Int64")
    securities["Country YTD Rank"] = securities.groupby("Origin Country")["YTD Return"].rank(ascending=False, method="min").astype("Int64")
    securities = securities.sort_values(["Country Order","YTD Return"], ascending=[True,False]).reset_index(drop=True)

    country_rows = []
    for country, group_all in securities.groupby("Origin Country", sort=False):
        primary = group_all[group_all["Listing Type"].eq("Primary Local")]
        group = primary if not primary.empty else group_all
        best = group.loc[group["YTD Return"].idxmax()]
        worst = group.loc[group["YTD Return"].idxmin()]
        country_rows.append({
            "Origin Country":country,
            "Aggregation Basis":"Primary local listings" if not primary.empty else "All available listings",
            "Unique Issuers":int(group["Issuer"].nunique()),
            "Listed Instruments":int(len(group_all)),
            "Average YTD Return":float(group["YTD Return"].mean()),
            "Median YTD Return":float(group["YTD Return"].median()),
            "Positive Breadth":float((group["YTD Return"] > 0).mean()),
            "Gainers":int((group["YTD Return"] > 0).sum()),
            "Decliners":int((group["YTD Return"] < 0).sum()),
            "Best Ticker":best["Ticker"],
            "Best YTD Return":float(best["YTD Return"]),
            "Worst Ticker":worst["Ticker"],
            "Worst YTD Return":float(worst["YTD Return"]),
            "Average EWMA Volatility":float(group["EWMA Volatility"].mean()) if group["EWMA Volatility"].notna().any() else np.nan,
            "Average Institutional Score":float(group["Institutional Score"].mean()) if group["Institutional Score"].notna().any() else np.nan,
        })
    countries = pd.DataFrame(country_rows)
    countries["Country Order"] = countries["Origin Country"].map(country_order).fillna(99).astype(int)
    countries = countries.sort_values("Country Order").drop(columns=["Country Order"]).reset_index(drop=True)

    subsectors = securities[securities["Listing Type"].eq("Primary Local")].groupby(["Origin Country","Subsector"], as_index=False).agg(
        Securities=("Ticker","count"),
        Average_YTD_Return=("YTD Return","mean"),
        Median_YTD_Return=("YTD Return","median"),
        Positive_Breadth=("YTD Return",lambda x: float((x>0).mean())),
        Average_EWMA_Volatility=("EWMA Volatility","mean"),
    ).rename(columns={
        "Average_YTD_Return":"Average YTD Return","Median_YTD_Return":"Median YTD Return",
        "Positive_Breadth":"Positive Breadth","Average_EWMA_Volatility":"Average EWMA Volatility"
    })
    best_all = securities.loc[securities["YTD Return"].idxmax()]
    worst_all = securities.loc[securities["YTD Return"].idxmin()]
    latest_date = pd.to_datetime(securities["Latest Date"]).max()
    strict_count = int(securities["Strict YTD"].sum())
    summary = {
        "As of Date":latest_date.strftime("%Y-%m-%d") if pd.notna(latest_date) else "N/A",
        "Asian-Origin Listed Instruments":int(len(securities)),
        "Unique Asian Issuers":int(securities["Issuer"].nunique()),
        "Origin Countries":int(securities["Origin Country"].nunique()),
        "Strict YTD Observations":strict_count,
        "Since-Listing Proxies":int(len(securities)-strict_count),
        "Gainers":int((securities["YTD Return"]>0).sum()),
        "Decliners":int((securities["YTD Return"]<0).sum()),
        "Median Security YTD Return":float(securities["YTD Return"].median()),
        "Best YTD Security":f'{best_all["Ticker"]} ({best_all["YTD Return"]:.2%})',
        "Worst YTD Security":f'{worst_all["Ticker"]} ({worst_all["YTD Return"]:.2%})',
    }
    return {"summary":summary,"securities":securities,"countries":countries,"subsectors":subsectors,"exclusions":exclusions_df}


def chart_asia_ytd_grouped(securities):
    """One full-width smart chart, vertically grouped by origin country."""
    d = securities.copy()
    if d.empty:
        return layout(go.Figure(), "Asia-Origin Companies — YTD Performance", CHART_FULL_HEIGHT)
    countries = [c for c in ASIA_ORIGIN_COUNTRY_ORDER if c in d["Origin Country"].unique()]
    other = [c for c in d["Origin Country"].dropna().unique() if c not in countries]
    countries += sorted(other)
    fig = make_subplots(rows=len(countries), cols=1, shared_xaxes=True, vertical_spacing=max(0.025, 0.08/max(len(countries),1)), subplot_titles=countries)
    for row_no, country in enumerate(countries, 1):
        g = d[d["Origin Country"].eq(country)].sort_values("YTD Return", ascending=True)
        colors = np.where(g["YTD Return"] >= 0, "#16794a", "#b42318")
        custom = np.column_stack([
            g["Issuer"], g["Subsector"], g["Listing Type"], g["Listing Market"],
            g["1D Return"], g["20D Return"], g["EWMA Volatility"], g["Recommendation"], g["Performance Basis"]
        ])
        fig.add_trace(go.Bar(
            x=g["YTD Return"]*100, y=g["Ticker"], orientation="h", name=country, showlegend=False,
            marker=dict(color=colors), text=(g["YTD Return"]*100).map(lambda x:f"{x:+.1f}%"), textposition="outside",
            customdata=custom,
            hovertemplate=("<b>%{y}</b><br>%{customdata[0]}<br>YTD: %{x:.2f}%<br>Subsector: %{customdata[1]}"
                           "<br>Listing: %{customdata[2]} · %{customdata[3]}<br>1D: %{customdata[4]:.2%}"
                           "<br>20D: %{customdata[5]:.2%}<br>EWMA vol: %{customdata[6]:.2%}"
                           "<br>Decision: %{customdata[7]}<br>Basis: %{customdata[8]}<extra></extra>"),
        ), row=row_no, col=1)
        fig.add_vline(x=0, line_width=1, line_dash="dot", line_color="#667085", row=row_no, col=1)
        fig.update_yaxes(categoryorder="array", categoryarray=list(g["Ticker"]), row=row_no, col=1)
    fig.update_xaxes(title_text="Year-to-date return (%)", ticksuffix="%", row=len(countries), col=1)
    height = max(CHART_EXTRA_LARGE_HEIGHT, 300*len(countries) + 220)
    fig = layout(fig, "Asia-Origin Companies — Grouped YTD Performance", height)
    fig.update_layout(hovermode="closest", bargap=0.26)
    return fig


def chart_asia_country_breadth(countries):
    d = countries.copy()
    if d.empty:
        return layout(go.Figure(), "Asia Country YTD Breadth", CHART_FULL_HEIGHT)
    fig = go.Figure()
    fig.add_trace(go.Bar(x=d["Origin Country"], y=d["Median YTD Return"]*100, name="Median YTD return", text=(d["Median YTD Return"]*100).map(lambda x:f"{x:+.1f}%"), textposition="outside"))
    fig.add_trace(go.Scatter(x=d["Origin Country"], y=d["Positive Breadth"]*100, name="Positive breadth", mode="lines+markers+text", text=(d["Positive Breadth"]*100).map(lambda x:f"{x:.0f}%"), textposition="top center", yaxis="y2"))
    fig.update_layout(yaxis=dict(title="Median YTD return (%)", ticksuffix="%"), yaxis2=dict(title="Positive breadth (%)", ticksuffix="%", overlaying="y", side="right", range=[0,105]))
    return layout(fig, "Asia-Origin Country Performance & Breadth", CHART_FULL_HEIGHT)


def asia_ytd_tab_html(pack):
    if not pack or pack.get("securities", pd.DataFrame()).empty:
        return '<div class="section"><h2>Asia-Origin YTD Performance</h2><div class="warning">No current-year Asia-origin security observations were available.</div></div>'
    chart1 = div(chart_asia_ytd_grouped(pack["securities"]), False)
    chart2 = div(chart_asia_country_breadth(pack["countries"]), False)
    return (f'<div class="section"><h2>Asia-Origin YTD Performance & Breadth</h2>'
            f'<div class="note"><b>Method:</b> Strict YTD uses the final available close before 1 January as the reference. '
            f'New listings without a prior-year close are explicitly labelled as since-listing proxies. Country aggregates use primary local listings where available to avoid ADR double counting.</div>'
            f'<h3>Executive KPI Summary</h3>{table(metrics_df(pack["summary"]),"asia_ytd_summary")}'
            f'<h3>Grouped Interactive YTD Chart</h3><div class="chart-block">{chart1}</div>'
            f'<h3>Country Performance & Breadth</h3><div class="chart-block">{chart2}</div>{table(pack["countries"],"asia_ytd_countries")}'
            f'<h3>Asia-Origin Security Smart Table</h3>{table(pack["securities"].drop(columns=["Country Order"], errors="ignore"),"asia_ytd_securities")}'
            f'<h3>Subsector YTD Summary</h3>{table(pack["subsectors"],"asia_ytd_subsectors")}'
            f'<h3>Exclusion / Availability Log</h3>{table(pack["exclusions"] if not pack["exclusions"].empty else pd.DataFrame([{"Status":"No exclusions"}]),"asia_ytd_exclusions")}</div>')

# ============================================================
# 8. STREAMLIT APPLICATION LAYER
# ============================================================
STREAMLIT_APP_VERSION = "2.5.0"

st.set_page_config(
    page_title="Global Semiconductor & Asia YTD Institutional Platform",
    page_icon="◼",
    layout="wide",
    initial_sidebar_state="expanded",
)

STREAMLIT_CSS = """
<style>
:root {
  --navy:#0a1d30; --navy2:#123552; --ink:#182230; --muted:#667085;
  --line:#dde4eb; --card:#ffffff; --bg:#f4f6f8; --accent:#315f86;
  --soft:#f8fafc; --positive:#16794a; --negative:#b42318;
}
html, body, [class*="css"] {
  font-family: Inter, Aptos, "Segoe UI", Arial, sans-serif;
  font-weight:300;
  letter-spacing:.004em;
}
.stApp {background:var(--bg); color:var(--ink);}
.block-container {max-width:none; padding-top:1rem; padding-left:1.35rem; padding-right:1.35rem; padding-bottom:3rem;}
.mk-masthead {
  background:linear-gradient(102deg,var(--navy),var(--navy2)); color:#fff;
  border-radius:12px; padding:25px 30px 23px; margin-bottom:14px;
  border:1px solid rgba(255,255,255,.08); box-shadow:0 4px 18px rgba(10,29,48,.10);
}
.mk-kicker {font-size:.68rem; letter-spacing:.20em; text-transform:uppercase; color:#b8c8d8; font-weight:500;}
.mk-title {font-size:2.05rem; letter-spacing:-.030em; font-weight:300; margin:.30rem 0 .25rem;}
.mk-subtitle {font-size:.84rem; color:#d7e1ea; font-weight:300; letter-spacing:.018em;}
.mk-section {
  font-size:.70rem; letter-spacing:.16em; text-transform:uppercase; color:#315f86;
  font-weight:600; margin:1.55rem 0 .55rem; padding-bottom:.42rem; border-bottom:1px solid var(--line);
}
.mk-panel-title {font-size:1.05rem; color:var(--navy); font-weight:400; margin:1.25rem 0 .20rem; letter-spacing:-.01em;}
.mk-panel-caption {font-size:.78rem; color:var(--muted); margin-bottom:.65rem;}
div[data-testid="stMetric"] {
  background:#fff; border:1px solid var(--line); border-radius:9px; padding:12px 14px;
  box-shadow:0 1px 3px rgba(16,24,40,.035); min-height:92px;
}
div[data-testid="stMetricLabel"] {font-size:.66rem; letter-spacing:.08em; text-transform:uppercase; color:var(--muted); font-weight:500;}
div[data-testid="stMetricValue"] {font-weight:350; color:var(--navy); font-size:1.38rem; letter-spacing:-.02em;}
div[data-testid="stMetricDelta"] {font-size:.72rem;}
.stTabs [data-baseweb="tab-list"] {gap:.25rem; border-bottom:1px solid var(--line); overflow-x:auto; flex-wrap:nowrap;}
.stTabs [data-baseweb="tab"] {
  height:2.75rem; padding:0 .78rem; font-size:.70rem; letter-spacing:.055em;
  text-transform:uppercase; font-weight:450; color:#475467; white-space:nowrap;
}
.stTabs [aria-selected="true"] {color:var(--navy)!important; border-bottom:2px solid var(--navy)!important; background:rgba(49,95,134,.035);}
section[data-testid="stSidebar"] {background:#edf1f5; border-right:1px solid var(--line);}
section[data-testid="stSidebar"] * {font-weight:350;}
.stButton>button, .stDownloadButton>button {border-radius:7px; border:1px solid #b8c4d0; font-weight:450;}
[data-testid="stDataFrame"] {border:1px solid var(--line); border-radius:8px; overflow:hidden; background:#fff;}
.mk-note {background:#fff; border:1px solid var(--line); border-left:3px solid var(--accent); border-radius:8px; padding:12px 14px; color:#475467; font-size:.81rem; line-height:1.58;}
.mk-warning {background:#fffaf0; border:1px solid #f1dfb8; border-left:3px solid #b7791f; border-radius:8px; padding:12px 14px; color:#5f4715; font-size:.81rem; line-height:1.58;}
[data-testid="stPlotlyChart"] {background:#fff; border:1px solid var(--line); border-radius:10px; padding:3px; margin-bottom:1.15rem; box-shadow:0 1px 3px rgba(16,24,40,.025);}
hr {border-color:var(--line)!important;}
@media(max-width:1100px){.mk-title{font-size:1.65rem}.block-container{padding-left:.8rem;padding-right:.8rem}}
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
    if kind == "price": return f"{float(value):,.2f}"
    return f"{float(value):,.3f}" if isinstance(value, (float, np.floating)) else str(value)


def _section(title, caption=""):
    st.markdown(f'<div class="mk-section">{title}</div>', unsafe_allow_html=True)
    if caption:
        st.markdown(f'<div class="mk-panel-caption">{caption}</div>', unsafe_allow_html=True)


def _show_df(df, height=420, key=None):
    if df is None or len(df) == 0:
        st.info("No data available for this section.")
        return
    st.dataframe(df, width="stretch", height=height, hide_index=True, key=key)


def _plot(fig, key=None):
    """All charts are rendered one-by-one at full width; no chart is placed in a column."""
    st.plotly_chart(fig, width="stretch", theme=None, config=PLOT_CONFIG, key=key)


def _metric_grid(items, columns=4):
    """Institutional KPI layout with controlled width and multiple rows."""
    for start in range(0, len(items), columns):
        chunk = items[start:start+columns]
        cols = st.columns(columns)
        for i, col in enumerate(cols):
            if i < len(chunk):
                label, value = chunk[i]
                col.metric(label, value)


def _selected_detail(inst, selected_ticker):
    return inst.get("details", {}).get(selected_ticker)


# -------------------------------------------------------------------------
# EWMA VOLATILITY ENGINE
# -------------------------------------------------------------------------
def compute_ewma_volatility_frame(close_or_returns, input_is_price=True):
    s = pd.Series(close_or_returns, dtype=float).replace([np.inf, -np.inf], np.nan).dropna().sort_index()
    if input_is_price:
        r = np.log(s / s.shift(1))
    else:
        r = np.log1p(s.clip(lower=-0.999999))
    r = r.replace([np.inf, -np.inf], np.nan)
    out = pd.DataFrame(index=r.index)
    out["Log Return"] = r
    for lam in (0.94, 0.97):
        var = r.pow(2).shift(1).ewm(alpha=1.0-lam, adjust=False, min_periods=20).mean()
        out[f"EWMA {lam:.2f} Daily Sigma"] = np.sqrt(var)
        out[f"EWMA {lam:.2f} Ann Vol"] = np.sqrt(var * TRADING_DAYS)
    out["Rolling 20D Ann Vol"] = r.rolling(20, min_periods=20).std(ddof=1) * np.sqrt(TRADING_DAYS)
    out["Rolling 63D Ann Vol"] = r.rolling(63, min_periods=40).std(ddof=1) * np.sqrt(TRADING_DAYS)
    out["Rolling 252D Ann Vol"] = r.rolling(252, min_periods=126).std(ddof=1) * np.sqrt(TRADING_DAYS)
    out["EWMA 0.94 Upper 2Sigma"] = 2.0 * out["EWMA 0.94 Daily Sigma"]
    out["EWMA 0.94 Lower 2Sigma"] = -2.0 * out["EWMA 0.94 Daily Sigma"]
    out["EWMA 0.94 20D Change"] = out["EWMA 0.94 Ann Vol"].pct_change(20)
    out["EWMA 0.94 Percentile 252D"] = out["EWMA 0.94 Ann Vol"].rolling(252, min_periods=63).apply(
        lambda a: float(pd.Series(a).rank(pct=True).iloc[-1]), raw=False
    )
    return out


def chart_ewma_volatility_levels(vol_df, title):
    fig = go.Figure()
    specs = [
        ("EWMA 0.94 Ann Vol", "EWMA λ=0.94", "#0f4c81", 2.3, "solid"),
        ("EWMA 0.97 Ann Vol", "EWMA λ=0.97", "#7c3aed", 2.0, "dot"),
        ("Rolling 20D Ann Vol", "Rolling 20D", "#f59e0b", 1.4, "dash"),
        ("Rolling 63D Ann Vol", "Rolling 63D", "#475467", 1.4, "solid"),
        ("Rolling 252D Ann Vol", "Rolling 252D", "#111827", 1.5, "dot"),
    ]
    for col, name, color, width, dash in specs:
        if col in vol_df.columns:
            fig.add_trace(go.Scatter(x=vol_df.index, y=vol_df[col], mode="lines", name=name, line=dict(color=color, width=width, dash=dash)))
    fig.update_yaxes(title="Annualized volatility", tickformat=".1%")
    return layout(fig, title + " — EWMA and Rolling Volatility", CHART_EXTRA_LARGE_HEIGHT)


def chart_ewma_return_shocks(vol_df, title):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=vol_df.index, y=vol_df["Log Return"], mode="lines", name="Daily Log Return", line=dict(color="#334155", width=1.0)))
    fig.add_trace(go.Scatter(x=vol_df.index, y=vol_df["EWMA 0.94 Upper 2Sigma"], mode="lines", name="EWMA +2σ", line=dict(color="#b42318", width=1.2, dash="dash")))
    fig.add_trace(go.Scatter(x=vol_df.index, y=vol_df["EWMA 0.94 Lower 2Sigma"], mode="lines", name="EWMA -2σ", line=dict(color="#16794a", width=1.2, dash="dash"), fill="tonexty", fillcolor="rgba(49,95,134,.045)"))
    upper = vol_df[vol_df["Log Return"] > vol_df["EWMA 0.94 Upper 2Sigma"]]
    lower = vol_df[vol_df["Log Return"] < vol_df["EWMA 0.94 Lower 2Sigma"]]
    if not upper.empty:
        fig.add_trace(go.Scatter(x=upper.index, y=upper["Log Return"], mode="markers", name="Upper Shock", marker=dict(symbol="triangle-up", size=8, color="#b42318")))
    if not lower.empty:
        fig.add_trace(go.Scatter(x=lower.index, y=lower["Log Return"], mode="markers", name="Lower Shock", marker=dict(symbol="triangle-down", size=8, color="#16794a")))
    fig.update_yaxes(title="Daily log return", tickformat=".2%")
    return layout(fig, title + " — EWMA Return Shock Bands", CHART_FULL_HEIGHT)


def build_ewma_snapshot(inst):
    rows = []
    for ticker, detail in inst.get("details", {}).items():
        score = detail.get("score", pd.DataFrame())
        if score.empty or "Close" not in score:
            continue
        v = compute_ewma_volatility_frame(score["Close"], input_is_price=True).dropna(subset=["EWMA 0.94 Ann Vol"])
        if v.empty:
            continue
        last = v.iloc[-1]
        pctile = last.get("EWMA 0.94 Percentile 252D", np.nan)
        regime = "HIGH" if pd.notna(pctile) and pctile >= .75 else ("LOW" if pd.notna(pctile) and pctile <= .25 else "NORMAL")
        rows.append({
            "Ticker": ticker,
            "Company": detail["meta"].get("name", ticker),
            "EWMA 0.94 Ann Vol": last.get("EWMA 0.94 Ann Vol"),
            "EWMA 0.97 Ann Vol": last.get("EWMA 0.97 Ann Vol"),
            "Rolling 20D Ann Vol": last.get("Rolling 20D Ann Vol"),
            "Rolling 63D Ann Vol": last.get("Rolling 63D Ann Vol"),
            "20D Vol Change": last.get("EWMA 0.94 20D Change"),
            "Vol Percentile 252D": pctile,
            "Volatility Regime": regime,
            "Institutional Score": detail.get("decision", {}).get("Institutional Score"),
            "Recommendation": detail.get("decision", {}).get("Recommendation"),
        })
    return pd.DataFrame(rows).sort_values("EWMA 0.94 Ann Vol", ascending=False) if rows else pd.DataFrame()


# -------------------------------------------------------------------------
# FULL-WIDTH ASSET CHARTS
# -------------------------------------------------------------------------
def chart_strategy_signal(detail, ticker, strategy_name):
    bt = detail["supertrend_backtest"].copy() if strategy_name == "Smart Supertrend" else detail["macd_backtest"].copy()
    fig = go.Figure()
    fig.add_trace(go.Candlestick(x=bt.index, open=bt["Open"], high=bt["High"], low=bt["Low"], close=bt["Close"], name="Adjusted OHLC", increasing_line_color="#16794a", decreasing_line_color="#b42318"))
    if "ATR_Stop" in bt.columns:
        fig.add_trace(go.Scatter(x=bt.index, y=bt["ATR_Stop"], mode="lines", name="ATR Trailing Stop", line=dict(color="#f97316", width=1.2, dash="dot")))
    if "ST_Line" in bt.columns:
        fig.add_trace(go.Scatter(x=bt.index, y=bt["ST_Line"], mode="lines", name="Smart Supertrend", line=dict(color="#7c3aed", width=1.4)))
    for col, name, color in [("EMA_20", "EMA 20", "#2563eb"), ("EMA_50", "EMA 50", "#f59e0b"), ("EMA_200", "EMA 200", "#111827")]:
        if col in bt.columns:
            fig.add_trace(go.Scatter(x=bt.index, y=bt[col], mode="lines", name=name, line=dict(color=color, width=1.1, dash="dot" if col == "EMA_200" else "solid")))
    if "Signal" in bt.columns:
        buys = bt[bt["Signal"] == 1]
        sells = bt[bt["Signal"] == -1]
        if not buys.empty:
            fig.add_trace(go.Scatter(x=buys.index, y=buys["Low"] * .985, mode="markers", name="BUY", marker=dict(symbol="triangle-up", size=12, color="#16794a", line=dict(width=1, color="white"))))
        if not sells.empty:
            fig.add_trace(go.Scatter(x=sells.index, y=sells["High"] * 1.015, mode="markers", name="SELL", marker=dict(symbol="triangle-down", size=12, color="#b42318", line=dict(width=1, color="white"))))
    fig.update_layout(xaxis_rangeslider_visible=False)
    return layout(fig, f"{ticker} — {strategy_name} | Price, Signals and ATR Risk Control", CHART_EXTRA_LARGE_HEIGHT)


def chart_strategy_equity(detail, ticker, strategy_name):
    bt = detail["supertrend_backtest"].copy() if strategy_name == "Smart Supertrend" else detail["macd_backtest"].copy()
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=bt.index, y=bt.get("Strategy Equity"), mode="lines", name=f"{strategy_name} Net Equity", line=dict(color="#0f766e", width=2.2)))
    fig.add_trace(go.Scatter(x=bt.index, y=bt.get("Buy Hold Equity"), mode="lines", name="Buy & Hold", line=dict(color="#64748b", width=1.5, dash="dot")))
    return layout(fig, f"{ticker} — {strategy_name} Net Equity vs Buy & Hold", CHART_FULL_HEIGHT)


def chart_strategy_drawdown(detail, ticker, strategy_name):
    bt = detail["supertrend_backtest"].copy() if strategy_name == "Smart Supertrend" else detail["macd_backtest"].copy()
    strategy_eq = pd.Series(bt.get("Strategy Equity"), index=bt.index, dtype=float)
    buyhold_eq = pd.Series(bt.get("Buy Hold Equity"), index=bt.index, dtype=float)
    sdd = strategy_eq / strategy_eq.cummax() - 1
    bdd = buyhold_eq / buyhold_eq.cummax() - 1
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=sdd.index, y=sdd, mode="lines", name="Strategy Drawdown", fill="tozeroy", line=dict(color="#b42318", width=1.7)))
    fig.add_trace(go.Scatter(x=bdd.index, y=bdd, mode="lines", name="Buy & Hold Drawdown", line=dict(color="#64748b", width=1.3, dash="dot")))
    fig.update_yaxes(tickformat=".1%", title="Drawdown")
    return layout(fig, f"{ticker} — Drawdown Comparison", CHART_FULL_HEIGHT)


def chart_technical_price(detail, ticker):
    x = detail["score"].copy().sort_index()
    fig = go.Figure()
    fig.add_trace(go.Candlestick(x=x.index, open=x["Open"], high=x["High"], low=x["Low"], close=x["Close"], name="Adjusted OHLC", increasing_line_color="#16794a", decreasing_line_color="#b42318"))
    for col, name, color, dash in [
        ("BB_UPPER", "BB Upper", "rgba(59,130,246,.55)", "dot"), ("BB_MID", "BB Mid", "rgba(59,130,246,.75)", "dash"), ("BB_LOWER", "BB Lower", "rgba(59,130,246,.55)", "dot"),
        ("EMA_20", "EMA 20", "#2563eb", "solid"), ("EMA_50", "EMA 50", "#f59e0b", "solid"), ("EMA_200", "EMA 200", "#111827", "dash"), ("ST_Line", "Smart Supertrend", "#7c3aed", "dot")]:
        if col in x.columns:
            fig.add_trace(go.Scatter(x=x.index, y=x[col], mode="lines", name=name, line=dict(color=color, width=1.25, dash=dash)))
    fig.update_layout(xaxis_rangeslider_visible=False)
    return layout(fig, f"{ticker} — Candlestick, Bollinger, EMA and Smart Supertrend", CHART_EXTRA_LARGE_HEIGHT)


def chart_technical_macd(detail, ticker):
    x = detail["score"].copy().sort_index()
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x.index, y=x["MACD"], mode="lines", name="MACD", line=dict(color="#0f4c81", width=1.8)))
    fig.add_trace(go.Scatter(x=x.index, y=x["MACD_SIGNAL"], mode="lines", name="Signal", line=dict(color="#f59e0b", width=1.5, dash="dot")))
    fig.add_trace(go.Bar(x=x.index, y=x["MACD_HIST"], name="Histogram", marker_color=np.where(x["MACD_HIST"] >= 0, "rgba(22,121,74,.55)", "rgba(180,35,24,.55)")))
    fig.add_hline(y=0, line_dash="dash", line_width=1)
    return layout(fig, f"{ticker} — MACD Momentum Structure", CHART_FULL_HEIGHT)


def chart_technical_rsi_adx(detail, ticker):
    x = detail["score"].copy().sort_index()
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Scatter(x=x.index, y=x["RSI"], mode="lines", name="RSI", line=dict(color="#7c3aed", width=1.8)), secondary_y=False)
    fig.add_trace(go.Scatter(x=x.index, y=x["ADX"], mode="lines", name="ADX", line=dict(color="#0f766e", width=1.6, dash="dot")), secondary_y=True)
    fig.add_hrect(y0=70, y1=100, opacity=.06, line_width=0, secondary_y=False)
    fig.add_hrect(y0=0, y1=30, opacity=.06, line_width=0, secondary_y=False)
    fig.add_hline(y=20, line_dash="dot", line_width=1, secondary_y=True)
    fig.update_yaxes(title="RSI", range=[0, 100], secondary_y=False)
    fig.update_yaxes(title="ADX", range=[0, 100], secondary_y=True)
    return layout(fig, f"{ticker} — RSI and ADX Regime Diagnostics", CHART_FULL_HEIGHT)


def chart_leading_signal_events(detail, ticker):
    x = detail["leading_lab"].copy().sort_index()
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x.index, y=x["Close"], mode="lines", name="Adjusted Close", line=dict(color="#111827", width=1.7)))
    buys = x[x["Signal Event"] == "BUY"]
    sells = x[x["Signal Event"] == "SELL"]
    if not buys.empty:
        fig.add_trace(go.Scatter(x=buys.index, y=buys["Close"] * .985, mode="markers", name="Leading BUY", marker=dict(symbol="triangle-up", size=11, color="#16794a")))
    if not sells.empty:
        fig.add_trace(go.Scatter(x=sells.index, y=sells["Close"] * 1.015, mode="markers", name="Leading SELL", marker=dict(symbol="triangle-down", size=11, color="#b42318")))
    return layout(fig, f"{ticker} — Leading Signal Events", CHART_EXTRA_LARGE_HEIGHT)


def chart_leading_signal_score(detail, ticker):
    x = detail["leading_lab"].copy().sort_index()
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x.index, y=x["Signal Score"], mode="lines", name="Signal Score", fill="tozeroy", line=dict(color="#315f86", width=2.0), fillcolor="rgba(49,95,134,.08)"))
    fig.add_hline(y=4, line_dash="dash", annotation_text="BUY threshold")
    fig.add_hline(y=2, line_dash="dot", annotation_text="Exit threshold")
    fig.update_yaxes(range=[0, 7], title="Signal score")
    return layout(fig, f"{ticker} — Leading Signal Score History", CHART_FULL_HEIGHT)


def chart_leading_signal_equity(detail, ticker):
    x = detail["leading_lab"].copy().sort_index()
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x.index, y=x["Signal Strategy Equity"], mode="lines", name="Leading Signal Net Equity", line=dict(color="#0f766e", width=2.2)))
    fig.add_trace(go.Scatter(x=x.index, y=x["Signal Buy Hold Equity"], mode="lines", name="Buy & Hold", line=dict(color="#64748b", width=1.5, dash="dot")))
    return layout(fig, f"{ticker} — Leading Signal Lab Equity Comparison", CHART_FULL_HEIGHT)


def build_blue_chip_screener(res, inst):
    ranking = inst.get("ranking", pd.DataFrame()).copy()
    if ranking.empty:
        return pd.DataFrame()
    metrics = res.get("am", pd.DataFrame()).copy()
    base = ranking.merge(metrics, on=[c for c in ["Ticker", "Company", "Sector", "Theme", "Country"] if c in ranking.columns and c in metrics.columns], how="left", suffixes=("", "_Metric"))
    liquidity = []
    observations = []
    momentum = []
    for ticker in base["Ticker"]:
        detail = inst.get("details", {}).get(ticker)
        if detail is None:
            liquidity.append(np.nan); observations.append(0); momentum.append(np.nan); continue
        ind = detail["indicator"]
        liquidity.append(float(ind["Dollar_Volume"].tail(63).median()) if "Dollar_Volume" in ind else np.nan)
        observations.append(len(ind))
        momentum.append(float(ind["Momentum_252D"].iloc[-1]) if "Momentum_252D" in ind and pd.notna(ind["Momentum_252D"].iloc[-1]) else np.nan)
    base["Median Dollar Volume 63D"] = liquidity
    base["Indicator Observations"] = observations
    base["Momentum 252D"] = momentum
    liq_rank = base["Median Dollar Volume 63D"].rank(pct=True).fillna(.5)
    vol_rank = base.get("Annualized Volatility", pd.Series(np.nan, index=base.index)).rank(pct=True).fillna(.5)
    dd_quality = (1.0 - base.get("Max Drawdown", pd.Series(np.nan, index=base.index)).abs().rank(pct=True)).fillna(.5)
    obs_score = (base["Indicator Observations"] / 1000.0).clip(0, 1)
    mom_rank = base["Momentum 252D"].rank(pct=True).fillna(.5)
    inst_score = pd.to_numeric(base["Institutional Score"], errors="coerce").fillna(50) / 100.0
    base["Blue-Chip Quality Score"] = (25*liq_rank + 20*(1-vol_rank) + 15*dd_quality + 20*inst_score + 10*mom_rank + 10*obs_score).clip(0, 100)
    base["Quality Tier"] = pd.cut(base["Blue-Chip Quality Score"], [-np.inf, 40, 55, 70, 85, np.inf], labels=["SPECULATIVE", "WATCH", "CORE CANDIDATE", "INSTITUTIONAL", "PREMIUM BLUE-CHIP"]).astype(str)
    cols = [c for c in ["Ticker","Company","Country","Sector","Theme","Blue-Chip Quality Score","Quality Tier","Institutional Score","Confidence Score","Recommendation","Median Dollar Volume 63D","Annualized Volatility","Max Drawdown","Sharpe Ratio","Beta","Momentum 252D","Indicator Observations"] if c in base.columns]
    return base[cols].sort_values(["Blue-Chip Quality Score","Institutional Score"], ascending=False)


def chart_blue_chip_screener(df, title):
    if df is None or df.empty:
        return layout(go.Figure(), title, CHART_FULL_HEIGHT)
    d = df.sort_values("Blue-Chip Quality Score", ascending=True)
    fig = go.Figure(go.Bar(x=d["Blue-Chip Quality Score"], y=d["Ticker"], orientation="h", customdata=np.stack([d["Company"], d["Quality Tier"], d["Recommendation"]], axis=-1), hovertemplate="%{y}<br>%{customdata[0]}<br>Quality=%{x:.1f}<br>Tier=%{customdata[1]}<br>Decision=%{customdata[2]}<extra></extra>"))
    fig.add_vline(x=70, line_dash="dot"); fig.add_vline(x=85, line_dash="dash")
    fig.update_xaxes(range=[0, 100], title="Blue-Chip Quality Score")
    return layout(fig, title, max(CHART_BAR_MIN_HEIGHT, 34*len(d)))


def build_capital_gain_leaders(inst):
    rows = []
    for ticker, detail in inst.get("details", {}).items():
        x = detail["indicator"]
        last = x.iloc[-1]
        rows.append({
            "Ticker": ticker,
            "Company": detail["meta"].get("name", ticker),
            "Country": detail["meta"].get("country", "N/A"),
            "Sector": detail["meta"].get("sector", "N/A"),
            "Return 20D": last.get("Momentum_20D"),
            "Return 63D": last.get("Momentum_63D"),
            "Return 126D": last.get("Momentum_126D"),
            "Return 252D": last.get("Momentum_252D"),
            "From 52W High": last.get("Pct_From_52W_High"),
            "Institutional Score": detail.get("decision", {}).get("Institutional Score"),
            "Confidence Score": detail.get("decision", {}).get("Confidence Score"),
            "Recommendation": detail.get("decision", {}).get("Recommendation"),
        })
    df = pd.DataFrame(rows)
    if df.empty:
        return df
    ranks = []
    for c in ["Return 20D", "Return 63D", "Return 126D", "Return 252D"]:
        ranks.append(df[c].rank(pct=True).fillna(.5))
    df["Capital Gain Composite"] = (0.20*ranks[0] + 0.30*ranks[1] + 0.20*ranks[2] + 0.30*ranks[3]) * 100
    return df.sort_values("Capital Gain Composite", ascending=False)


def chart_capital_gain(df, column, title):
    if df is None or df.empty:
        return layout(go.Figure(), title, CHART_FULL_HEIGHT)
    d = df.dropna(subset=[column]).nlargest(min(25, len(df)), column).sort_values(column, ascending=True)
    fig = go.Figure(go.Bar(x=d[column], y=d["Ticker"], orientation="h", customdata=np.stack([d["Company"], d["Recommendation"], d["Institutional Score"]], axis=-1), hovertemplate="%{y}<br>%{customdata[0]}<br>Return=%{x:.2%}<br>Decision=%{customdata[1]}<br>Score=%{customdata[2]:.1f}<extra></extra>"))
    fig.update_xaxes(tickformat=".1%", title=column)
    return layout(fig, title, max(CHART_BAR_MIN_HEIGHT, 34*len(d)))


def build_strategy_diagnostics(detail):
    st_bt = detail["supertrend_backtest"]
    macd_bt = detail["macd_backtest"]
    lab = detail["leading_lab"]
    rows = []
    def add(name, series, description):
        s = pd.Series(series).fillna(False).astype(bool)
        rows.append({"Constraint": name, "Description": description, "Days Passed": int(s.sum()), "Pass Rate %": float(s.mean()*100), "Days Blocked": int((~s).sum())})
    add("Supertrend UP", st_bt.get("ST_Dir", pd.Series(index=st_bt.index, dtype=float)).eq(1), "Smart Supertrend directional regime")
    add("Price > EMA200", st_bt["Close"] > st_bt["EMA_200"], "Long-term trend quality")
    add("MACD > Signal", macd_bt["MACD"] > macd_bt["MACD_SIGNAL"], "Momentum confirmation")
    add("ADX > 18", detail["indicator"]["ADX"] > 18, "Trend strength confirmation")
    add("Leading Score >= 4", lab["Signal Score"] >= 4, "Multi-factor leading entry threshold")
    add("Healthy RSI 45–72", detail["indicator"]["RSI"].between(45,72), "Non-exhausted momentum regime")
    return pd.DataFrame(rows)


def chart_strategy_diagnostics(df, ticker):
    if df.empty:
        return layout(go.Figure(), ticker + " — Strategy Diagnostic Funnel", CHART_FULL_HEIGHT)
    d = df.sort_values("Days Passed", ascending=True)
    fig = go.Figure(go.Bar(x=d["Days Passed"], y=d["Constraint"], orientation="h", text=d["Pass Rate %"].map(lambda x: f"{x:.1f}%"), textposition="auto"))
    fig.update_xaxes(title="Trading days passing condition")
    return layout(fig, ticker + " — Strategy Constraint Funnel", CHART_FULL_HEIGHT)



# -------------------------------------------------------------------------
# HEDGE FUND MANAGEMENT COCKPIT
# -------------------------------------------------------------------------
def _window_total_return(series, periods):
    s = pd.Series(series, dtype=float).dropna()
    if len(s) <= periods:
        return np.nan
    return float(s.iloc[-1] / s.iloc[-periods-1] - 1.0)


def build_macro_risk_pulse(close):
    rows = []
    for ticker, meta in MANAGEMENT_RISK_FACTORS.items():
        if ticker not in close.columns:
            rows.append({"Ticker":ticker,"Factor":meta["name"],"Channel":meta["channel"],"Status":"UNAVAILABLE"})
            continue
        s = pd.Series(close[ticker], dtype=float).replace([np.inf, -np.inf], np.nan).dropna().sort_index()
        if len(s) < 25:
            rows.append({"Ticker":ticker,"Factor":meta["name"],"Channel":meta["channel"],"Status":"INSUFFICIENT"})
            continue
        if meta["type"] == "yield_level":
            d = s.diff() * 100.0
            one = float(d.iloc[-1]) if len(d.dropna()) else np.nan
            five = float((s.iloc[-1] - s.iloc[-6]) * 100.0) if len(s) > 5 else np.nan
            twenty = float((s.iloc[-1] - s.iloc[-21]) * 100.0) if len(s) > 20 else np.nan
            sigma = d.rolling(60, min_periods=20).std(ddof=1).iloc[-1]
            shock_z = one / sigma if pd.notna(sigma) and sigma > 0 else np.nan
            units = "bp"
        else:
            lr = np.log(s / s.shift(1))
            one = float(s.pct_change().iloc[-1])
            five = _window_total_return(s, 5)
            twenty = _window_total_return(s, 20)
            sigma = lr.rolling(60, min_periods=20).std(ddof=1).iloc[-1]
            shock_z = float(lr.iloc[-1] / sigma) if pd.notna(sigma) and sigma > 0 else np.nan
            units = "return"
        pressure = float(np.clip(meta["risk_sign"] * shock_z, -3.0, 3.0)) if pd.notna(shock_z) else np.nan
        rows.append({
            "Ticker":ticker,"Factor":meta["name"],"Channel":meta["channel"],"Type":meta["type"],
            "Latest Level":float(s.iloc[-1]),"1D Move":one,"5D Move":five,"20D Move":twenty,
            "Shock Z":shock_z,"Risk Pressure Z":pressure,"Units":units,"Status":"LIVE",
        })
    return pd.DataFrame(rows)


def build_event_shock_monitor(inst, close):
    rows = []
    details = inst.get("details", {})
    for ticker in NEWS_EVENT_MONITOR_TICKERS:
        meta = ARTICLE_SHOCK_UNIVERSE.get(ticker, US_TECH_AI_CHIP_UNIVERSE.get(ticker, {"name":ticker,"sector":"N/A","theme":"N/A","country":"N/A"}))
        detail = details.get(ticker)
        if detail is not None:
            x = detail["indicator"].copy().sort_index()
            s = x["Close"].dropna()
            vol = compute_ewma_volatility_frame(s, input_is_price=True).dropna(subset=["EWMA 0.94 Daily Sigma"])
            sigma = float(vol["EWMA 0.94 Daily Sigma"].iloc[-1]) if not vol.empty else np.nan
            one = float(s.pct_change().iloc[-1]) if len(s) > 1 else np.nan
            five = _window_total_return(s, 5)
            twenty = _window_total_return(s, 20)
            lr = float(np.log(s.iloc[-1] / s.iloc[-2])) if len(s) > 1 else np.nan
            shock_z = lr / sigma if pd.notna(sigma) and sigma > 0 else np.nan
            drawdown = float(x["Drawdown"].iloc[-1]) if "Drawdown" in x and pd.notna(x["Drawdown"].iloc[-1]) else np.nan
            decision = detail.get("decision", {})
            score = decision.get("Institutional Score")
            confidence = decision.get("Confidence Score")
            recommendation = decision.get("Recommendation")
        elif ticker in close.columns:
            s = pd.Series(close[ticker], dtype=float).dropna().sort_index()
            one = float(s.pct_change().iloc[-1]) if len(s) > 1 else np.nan
            five = _window_total_return(s, 5)
            twenty = _window_total_return(s, 20)
            lr_s = np.log(s / s.shift(1)); sigma = lr_s.ewm(alpha=.06, adjust=False, min_periods=20).std().iloc[-1]
            shock_z = float(lr_s.iloc[-1] / sigma) if pd.notna(sigma) and sigma > 0 else np.nan
            drawdown = float(s.iloc[-1] / s.cummax().iloc[-1] - 1.0)
            score = confidence = recommendation = np.nan
        else:
            rows.append({"Ticker":ticker,"Company":meta.get("name",ticker),"Status":"UNAVAILABLE"})
            continue
        stress = float(np.clip(50.0 + 15.0 * max(0.0, -shock_z if pd.notna(shock_z) else 0.0) + 35.0 * abs(min(0.0, drawdown if pd.notna(drawdown) else 0.0)), 0, 100))
        state = "SEVERE" if stress >= 80 else ("ELEVATED" if stress >= 65 else ("WATCH" if stress >= 50 else "STABLE"))
        rows.append({
            "Ticker":ticker,"Company":meta.get("name",ticker),"Country":meta.get("country","N/A"),
            "Sector":meta.get("sector","N/A"),"Event Role":meta.get("article_role","Multi-event transmission channel"),
            "1D Return":one,"5D Return":five,"20D Return":twenty,"Shock Z":shock_z,"Current Drawdown":drawdown,
            "Event Stress Score":stress,"Event State":state,"Institutional Score":score,"Confidence Score":confidence,
            "Recommendation":recommendation,"Status":"LIVE",
        })
    df = pd.DataFrame(rows)
    return df.sort_values(["Event Stress Score","Shock Z"], ascending=[False, True], na_position="last") if not df.empty else df


def build_management_action_matrix(res, inst):
    ranking = inst.get("ranking", pd.DataFrame()).copy()
    if ranking.empty:
        return pd.DataFrame()
    weights = res.get("pf", {}).get("current_weights", pd.Series(dtype=float))
    rc = res.get("rc", pd.DataFrame())
    rc_map = rc.set_index("Ticker")["Risk Contribution %"].to_dict() if not rc.empty and "Ticker" in rc and "Risk Contribution %" in rc else {}
    rows = []
    for _, r in ranking.iterrows():
        ticker = r.get("Ticker")
        detail = inst.get("details", {}).get(ticker)
        if detail is None:
            continue
        ind = detail["indicator"].copy().sort_index(); last = ind.iloc[-1]
        vol = compute_ewma_volatility_frame(ind["Close"], input_is_price=True).dropna(subset=["EWMA 0.94 Ann Vol"])
        vol_now = float(vol["EWMA 0.94 Ann Vol"].iloc[-1]) if not vol.empty else np.nan
        vol_pct = float(vol["EWMA 0.94 Percentile 252D"].iloc[-1]) if not vol.empty and pd.notna(vol["EWMA 0.94 Percentile 252D"].iloc[-1]) else np.nan
        score = float(r.get("Institutional Score", np.nan)); conf = float(r.get("Confidence Score", np.nan))
        mom20 = float(last.get("Momentum_20D", np.nan)); mom63 = float(last.get("Momentum_63D", np.nan)); dd = float(last.get("Drawdown", np.nan))
        event_flag = ticker in NEWS_EVENT_MONITOR_TICKERS
        if score >= 80 and conf >= 65 and (pd.isna(vol_pct) or vol_pct < .85): action = "ADD / HIGH CONVICTION"
        elif score >= 65 and conf >= 55: action = "ACCUMULATE"
        elif score <= 20: action = "EXIT WATCH"
        elif score <= 40: action = "REDUCE"
        else: action = "HOLD / MONITOR"
        if event_flag and pd.notna(vol_pct) and vol_pct >= .80 and action in ("ADD / HIGH CONVICTION", "ACCUMULATE"):
            action = "HOLD / EVENT CONFIRMATION"
        if pd.notna(dd) and dd <= -.25 and score < 60:
            action = "REDUCE / DRAWDOWN CONTROL"
        conviction = np.clip(.55*score + .20*conf + 12.5*np.nan_to_num(mom20, nan=0.0) + 7.5*np.nan_to_num(mom63, nan=0.0) - 12.5*np.nan_to_num(vol_pct, nan=.5), 0, 100)
        weight = float(weights.get(ticker, 0.0)) if hasattr(weights, "get") else 0.0
        risk_contrib = float(rc_map.get(ticker, np.nan))
        budget_gap = risk_contrib - weight if pd.notna(risk_contrib) else np.nan
        discipline = "Do not chase; wait for confirmation" if event_flag and action.startswith("HOLD") else ("Risk reduction priority" if action.startswith(("REDUCE","EXIT")) else ("Scale in, not one-shot" if action.startswith(("ADD","ACCUMULATE")) else "Maintain and reassess"))
        rows.append({
            "Ticker":ticker,"Company":r.get("Company"),"Country":r.get("Country"),"Sector":r.get("Sector"),
            "Action":action,"Conviction Score":float(conviction),"Institutional Score":score,"Confidence Score":conf,
            "Recommendation":r.get("Recommendation"),"Current Weight":weight,"Risk Contribution %":risk_contrib,
            "Risk Budget Gap":budget_gap,"EWMA Ann Vol":vol_now,"Vol Percentile":vol_pct,"Momentum 20D":mom20,
            "Momentum 63D":mom63,"Current Drawdown":dd,"News Event Flag":event_flag,"Position Discipline":discipline,
        })
    priority = {"EXIT WATCH":0,"REDUCE / DRAWDOWN CONTROL":1,"REDUCE":2,"HOLD / EVENT CONFIRMATION":3,"HOLD / MONITOR":4,"ACCUMULATE":5,"ADD / HIGH CONVICTION":6}
    out = pd.DataFrame(rows)
    if not out.empty:
        out["_priority"] = out["Action"].map(priority).fillna(4)
        out = out.sort_values(["_priority","Conviction Score"], ascending=[True,False]).drop(columns="_priority")
    return out


def build_hedge_fund_management_pack(res, inst, close):
    macro = build_macro_risk_pulse(close)
    event = build_event_shock_monitor(inst, close)
    actions = build_management_action_matrix(res, inst)
    ranking = inst.get("ranking", pd.DataFrame()).copy()
    portfolio_return = res["pf"]["portfolio_return"].dropna()
    portfolio_vol = compute_ewma_volatility_frame(portfolio_return, input_is_price=False).dropna(subset=["EWMA 0.94 Ann Vol"])
    vol_now = float(portfolio_vol["EWMA 0.94 Ann Vol"].iloc[-1]) if not portfolio_vol.empty else np.nan
    vol_pct = float(portfolio_vol["EWMA 0.94 Percentile 252D"].iloc[-1]) if not portfolio_vol.empty and pd.notna(portfolio_vol["EWMA 0.94 Percentile 252D"].iloc[-1]) else .5
    buy_mask = ranking["Recommendation"].isin(["BUY","STRONG BUY"]) if not ranking.empty and "Recommendation" in ranking else pd.Series(dtype=bool)
    sell_mask = ranking["Recommendation"].isin(["SELL","STRONG SELL"]) if not ranking.empty and "Recommendation" in ranking else pd.Series(dtype=bool)
    buy_breadth = float(buy_mask.mean()) if len(buy_mask) else np.nan
    sell_breadth = float(sell_mask.mean()) if len(sell_mask) else np.nan
    average_score = float(pd.to_numeric(ranking.get("Institutional Score"), errors="coerce").mean()) if not ranking.empty else np.nan
    average_conf = float(pd.to_numeric(ranking.get("Confidence Score"), errors="coerce").mean()) if not ranking.empty else np.nan
    weights = res["pf"]["current_weights"]
    weight_hhi = float((pd.Series(weights, dtype=float).fillna(0.0)**2).sum()) if len(weights) else np.nan
    event_exposure = float(pd.Series(weights).reindex(NEWS_EVENT_MONITOR_TICKERS).fillna(0.0).sum()) if len(weights) else 0.0
    positive_pressure = pd.to_numeric(macro.get("Risk Pressure Z"), errors="coerce").clip(lower=0).mean() if not macro.empty else 0.0
    risk_score = float(np.clip(45 + 12*np.nan_to_num(positive_pressure, nan=0.0) + 20*(np.nan_to_num(vol_pct, nan=.5)-.5) + 18*(np.nan_to_num(sell_breadth, nan=0.0)-np.nan_to_num(buy_breadth, nan=0.0)) + 8*min(event_exposure/.25,1.0), 0, 100))
    if risk_score >= 75: stance, exposure, hedge = "DEFENSIVE", "45–65%", "HIGH"
    elif risk_score >= 60: stance, exposure, hedge = "CAUTIOUS", "60–75%", "MEDIUM-HIGH"
    elif risk_score >= 40: stance, exposure, hedge = "BALANCED", "70–90%", "MEDIUM"
    elif risk_score >= 25: stance, exposure, hedge = "SELECTIVE RISK-ON", "85–100%", "LOW-MEDIUM"
    else: stance, exposure, hedge = "PRO-RISK", "95–110%", "LOW"
    severe = int((pd.to_numeric(event.get("Event Stress Score"), errors="coerce") >= 80).sum()) if not event.empty else 0
    summary = {
        "Management Stance":stance,"Risk Score":risk_score,"Model Gross Exposure Bias":exposure,"Hedge Intensity":hedge,
        "Portfolio EWMA Vol":vol_now,"Portfolio Vol Percentile":vol_pct,"Buy Breadth":buy_breadth,"Sell Breadth":sell_breadth,
        "Average Institutional Score":average_score,"Average Confidence":average_conf,"Weight HHI":weight_hhi,
        "News Event Exposure":event_exposure,"Severe Event Names":severe,
        "Portfolio 1D":float(portfolio_return.iloc[-1]) if len(portfolio_return) else np.nan,
        "Portfolio 5D":float((1+portfolio_return.tail(5)).prod()-1) if len(portfolio_return)>=5 else np.nan,
        "Portfolio 20D":float((1+portfolio_return.tail(20)).prod()-1) if len(portfolio_return)>=20 else np.nan,
    }
    summary["Executive Interpretation"] = (
        f"{stance} posture with model gross-exposure bias {exposure} and {hedge.lower()} hedge intensity. "
        f"Decision breadth is {buy_breadth:.0%} BUY versus {sell_breadth:.0%} SELL where available. "
        f"Multi-event exposure is {event_exposure:.1%}; {severe} monitored names are in severe event stress. "
        "Actions are conditional model outputs, not automatic trades."
    )
    return {"summary":summary,"macro":macro,"event":event,"actions":actions,"event_register":news_event_register()}


def chart_macro_risk_pulse(df):
    live = df.dropna(subset=["Risk Pressure Z"]).copy() if df is not None and not df.empty else pd.DataFrame()
    if live.empty:
        return layout(go.Figure(), "Cross-Market Macro and Regional Risk Pulse", CHART_FULL_HEIGHT)
    live = live.sort_values("Risk Pressure Z", ascending=True)
    colors = np.where(live["Risk Pressure Z"] >= 1.0, "#b42318", np.where(live["Risk Pressure Z"] <= -1.0, "#16794a", "#667085"))
    fig = go.Figure(go.Bar(x=live["Risk Pressure Z"], y=live["Factor"], orientation="h", marker_color=colors, customdata=np.stack([live["Ticker"],live["Channel"],live["Shock Z"]],axis=-1), hovertemplate="%{y}<br>Ticker=%{customdata[0]}<br>Risk pressure=%{x:.2f}σ<br>Raw shock=%{customdata[2]:.2f}σ<br>%{customdata[1]}<extra></extra>"))
    fig.add_vline(x=0,line_width=1); fig.add_vline(x=1,line_dash="dot"); fig.add_vline(x=2,line_dash="dash")
    fig.update_xaxes(title="Risk-pressure z-score (positive = risk-off pressure)")
    return layout(fig, "Cross-Market Macro and Regional Risk Pulse", CHART_FULL_HEIGHT)


def chart_event_shock_monitor(df):
    live = df.dropna(subset=["Shock Z"]).copy() if df is not None and not df.empty else pd.DataFrame()
    if live.empty:
        return layout(go.Figure(), "Multi-Event Semiconductor Shock Monitor", CHART_FULL_HEIGHT)
    live = live.sort_values("Shock Z", ascending=True)
    colors = np.where(live["Shock Z"] < -1, "#b42318", np.where(live["Shock Z"] > 1, "#16794a", "#667085"))
    fig = go.Figure(go.Bar(x=live["Shock Z"], y=live["Ticker"], orientation="h", marker_color=colors, customdata=np.stack([live["Company"],live["Event Stress Score"],live["Recommendation"].fillna("N/A")],axis=-1), hovertemplate="%{y}<br>%{customdata[0]}<br>Daily shock=%{x:.2f}σ<br>Event stress=%{customdata[1]:.1f}<br>Decision=%{customdata[2]}<extra></extra>"))
    fig.add_vline(x=0,line_width=1); fig.add_vline(x=-2,line_dash="dash"); fig.add_vline(x=2,line_dash="dash")
    fig.update_xaxes(title="Latest return shock / EWMA daily sigma")
    return layout(fig, "Multi-Event Semiconductor Shock Monitor", CHART_FULL_HEIGHT)


def chart_decision_breadth(ranking):
    order = ["STRONG SELL","SELL","HOLD","BUY","STRONG BUY"]
    if ranking is None or ranking.empty or "Recommendation" not in ranking:
        return layout(go.Figure(), "Institutional Decision Breadth", CHART_FULL_HEIGHT)
    count = ranking["Recommendation"].value_counts().reindex(order, fill_value=0)
    fig = go.Figure(go.Bar(x=count.index, y=count.values, marker_color=["#7f1d1d","#b42318","#667085","#16794a","#065f46"], text=count.values, textposition="outside"))
    fig.update_yaxes(title="Number of securities")
    return layout(fig, "Institutional Decision Breadth", CHART_FULL_HEIGHT)


def chart_management_action_map(actions):
    if actions is None or actions.empty:
        return layout(go.Figure(), "Position Action and Risk Map", CHART_FULL_HEIGHT)
    d = actions.copy(); d["Bubble Size"] = (pd.to_numeric(d["Current Weight"],errors="coerce").fillna(0)*100 + 1.0).clip(lower=1)
    color_map = {"ADD / HIGH CONVICTION":"#065f46","ACCUMULATE":"#16794a","HOLD / MONITOR":"#667085","HOLD / EVENT CONFIRMATION":"#b7791f","REDUCE":"#b42318","REDUCE / DRAWDOWN CONTROL":"#991b1b","EXIT WATCH":"#7f1d1d"}
    fig = px.scatter(d, x="Institutional Score", y="EWMA Ann Vol", size="Bubble Size", text="Ticker", color="Action", color_discrete_map=color_map, hover_data=["Company","Confidence Score","Momentum 20D","Current Drawdown","Current Weight","Risk Contribution %","News Event Flag"], template=PLOT_TEMPLATE)
    fig.update_traces(textposition="top center")
    fig.add_vline(x=40,line_dash="dot"); fig.add_vline(x=65,line_dash="dot"); fig.add_vline(x=80,line_dash="dash")
    fig.update_xaxes(range=[0,100]); fig.update_yaxes(tickformat=".1%",title="EWMA annualized volatility")
    return layout(fig, "Position Action and Risk Map", CHART_EXTRA_LARGE_HEIGHT)


def management_pack_html(management_packs):
    blocks = []
    for uname, pack in management_packs.items():
        safe = re.sub(r"[^A-Za-z0-9]+","_",uname).strip("_").lower()
        summary = metrics_df(pack["summary"])
        blocks.append(f'<div class="section"><h2>{uname} — Hedge Fund Management Brief</h2><div class="note">{pack["summary"].get("Executive Interpretation","")}</div><h3>Management KPI Summary</h3>{table(summary,"mgmt_sum_"+safe)}<h3>Macro / Regional Risk Pulse</h3>{table(pack["macro"],"mgmt_macro_"+safe)}<h3>Multi-Event Shock Monitor</h3>{table(pack["event"],"mgmt_event_"+safe)}<h3>Position Action Matrix</h3>{table(pack["actions"],"mgmt_actions_"+safe)}</div>')
    return "".join(blocks)


# -------------------------------------------------------------------------
# GLOBAL SEMICONDUCTOR CONTAGION & POSITIONING ENGINE — ARTICLE 5
# -------------------------------------------------------------------------
def _all_institutional_details(institutional_results):
    out = {}
    for inst in institutional_results.values():
        for ticker, detail in inst.get("details", {}).items():
            out.setdefault(ticker, detail)
    return out


def _basket_return_series(close, tickers, min_names=2):
    available = [t for t in tickers if t in close.columns and close[t].dropna().shape[0] >= 30]
    if not available:
        return pd.Series(dtype=float), pd.Series(dtype=float), []
    returns = close[available].pct_change()
    count = returns.notna().sum(axis=1)
    basket = returns.mean(axis=1, skipna=True).where(count >= min(min_names, len(available))).dropna()
    return basket, count.reindex(basket.index), available


def _ewma_latest_from_returns(r):
    r = pd.Series(r, dtype=float).replace([np.inf, -np.inf], np.nan).dropna()
    if len(r) < 20:
        return np.nan, np.nan, np.nan
    var = r.pow(2).shift(1).ewm(alpha=0.06, adjust=False, min_periods=20).mean()
    ann = np.sqrt(var * TRADING_DAYS)
    pct_rank = ann.rolling(252, min_periods=63).apply(lambda a: float(pd.Series(a).rank(pct=True).iloc[-1]), raw=False)
    sigma = np.sqrt(var)
    return float(ann.iloc[-1]) if pd.notna(ann.iloc[-1]) else np.nan, float(pct_rank.iloc[-1]) if pd.notna(pct_rank.iloc[-1]) else np.nan, float(sigma.iloc[-1]) if pd.notna(sigma.iloc[-1]) else np.nan


def build_regional_semiconductor_baskets(close):
    summary_rows, history = [], {}
    for region, tickers in SEMICONDUCTOR_REGION_BASKETS.items():
        r, count, available = _basket_return_series(close, tickers, min_names=2)
        if r.empty:
            summary_rows.append({"Region":region,"Status":"INSUFFICIENT","Available Names":len(available)})
            continue
        equity = (1+r).cumprod()
        ann_vol, vol_pct, daily_sigma = _ewma_latest_from_returns(r)
        shock_z = float(r.iloc[-1]/daily_sigma) if pd.notna(daily_sigma) and daily_sigma > 0 else np.nan
        latest_constituent_returns = close[available].pct_change().iloc[-1].dropna()
        negative_breadth = float((latest_constituent_returns < 0).mean()) if len(latest_constituent_returns) else np.nan
        history[region] = pd.DataFrame({"Basket Return":r,"Basket Equity":equity,"Constituent Count":count})
        summary_rows.append({
            "Region":region,"Status":"LIVE","Available Names":len(available),"Constituents":", ".join(available),
            "1D Basket Return":float(r.iloc[-1]),"5D Basket Return":float((1+r.tail(5)).prod()-1) if len(r)>=5 else np.nan,
            "20D Basket Return":float((1+r.tail(20)).prod()-1) if len(r)>=20 else np.nan,
            "EWMA Volatility":ann_vol,"Volatility Percentile":vol_pct,"Downside Shock Z":-shock_z if pd.notna(shock_z) else np.nan,
            "Negative Breadth":negative_breadth,
        })
    return pd.DataFrame(summary_rows), history


def _sox_transmission_metrics(asset_return, sox_return):
    pair = pd.concat([pd.Series(asset_return,name="a"),pd.Series(sox_return,name="s")],axis=1).dropna()
    if len(pair) < 60:
        return {"same_corr":np.nan,"lag_corr":np.nan,"same_beta":np.nan,"lag_beta":np.nan}
    tail = pair.tail(min(252,len(pair)))
    same_corr = tail["a"].corr(tail["s"])
    same_var = tail["s"].var(ddof=1)
    same_beta = tail["a"].cov(tail["s"])/same_var if same_var>0 else np.nan
    lag = pd.concat([pair["a"],pair["s"].shift(1).rename("s_lag")],axis=1).dropna().tail(min(252,len(pair)))
    lag_corr = lag["a"].corr(lag["s_lag"]) if len(lag)>=60 else np.nan
    lag_var = lag["s_lag"].var(ddof=1) if len(lag)>=60 else np.nan
    lag_beta = lag["a"].cov(lag["s_lag"])/lag_var if pd.notna(lag_var) and lag_var>0 else np.nan
    return {"same_corr":same_corr,"lag_corr":lag_corr,"same_beta":same_beta,"lag_beta":lag_beta}


def build_european_contagion_monitor(close, institutional_results):
    rows=[]; details=_all_institutional_details(institutional_results)
    if "^SOX" not in close.columns:
        sox_r=pd.Series(dtype=float)
    else:
        sox_r=close["^SOX"].pct_change()
    for ticker, meta in EUROPEAN_SEMICONDUCTOR_UNIVERSE.items():
        if ticker not in close.columns or close[ticker].dropna().shape[0] < 30:
            rows.append({"Ticker":ticker,"Company":meta["name"],"Subsector":EUROPE_SEMICONDUCTOR_SUBSECTORS.get(ticker,"N/A"),"Status":"NO DATA"})
            continue
        s=close[ticker].dropna().sort_index(); r=s.pct_change(); ann_vol,vol_pct,daily_sigma=_ewma_latest_from_returns(r)
        one=float(r.iloc[-1]) if len(r)>1 else np.nan
        lr=float(np.log(s.iloc[-1]/s.iloc[-2])) if len(s)>1 else np.nan
        shock_z=lr/daily_sigma if pd.notna(daily_sigma) and daily_sigma>0 else np.nan
        trans=_sox_transmission_metrics(r,sox_r)
        ret252=float(s.iloc[-1]/s.iloc[-253]-1) if len(s)>252 else np.nan
        high252=float(s.tail(252).max()) if len(s)>=60 else np.nan
        dist_high=float(s.iloc[-1]/high252-1) if pd.notna(high252) and high252>0 else np.nan
        drawdown=float(s.iloc[-1]/s.cummax().iloc[-1]-1)
        detail=details.get(ticker,{})
        decision=detail.get("decision",{}) if detail else {}
        inst_score=decision.get("Institutional Score",np.nan); confidence=decision.get("Confidence Score",np.nan); recommendation=decision.get("Recommendation","N/A")
        downside_component=np.clip(max(0,-shock_z)/3 if pd.notna(shock_z) else 0,0,1)
        beta_component=np.clip(max(0,trans["same_beta"],trans["lag_beta"])/2 if any(pd.notna(v) for v in [trans["same_beta"],trans["lag_beta"]]) else 0,0,1)
        corr_component=np.clip(max(0,trans["same_corr"],trans["lag_corr"]) if any(pd.notna(v) for v in [trans["same_corr"],trans["lag_corr"]]) else 0,0,1)
        vol_component=np.clip(vol_pct if pd.notna(vol_pct) else 0,0,1)
        draw_component=np.clip(abs(min(drawdown,0))/0.35,0,1)
        contagion=100*(0.30*downside_component+0.20*beta_component+0.15*corr_component+0.20*vol_component+0.15*draw_component)
        expectation=100*(0.40*np.clip((ret252 if pd.notna(ret252) else 0)/0.80,0,1)+0.30*np.clip(1-abs(min(dist_high if pd.notna(dist_high) else -1,0))/0.30,0,1)+0.30*vol_component)
        if contagion>=75 or (pd.notna(inst_score) and inst_score<35): action="REDUCE / HEDGE"
        elif contagion>=55: action="HOLD / EVENT CONFIRMATION"
        elif pd.notna(inst_score) and inst_score>=75 and contagion<40: action="SELECTIVE ACCUMULATE"
        elif pd.notna(inst_score) and inst_score<50: action="REDUCE"
        else: action="HOLD / MONITOR"
        rows.append({
            "Ticker":ticker,"Company":meta["name"],"Country":meta.get("country","N/A"),"Subsector":EUROPE_SEMICONDUCTOR_SUBSECTORS.get(ticker,"N/A"),"Status":"LIVE",
            "1D Return":one,"5D Return":_window_total_return(s,5),"20D Return":_window_total_return(s,20),"252D Return":ret252,
            "Distance From 52W High":dist_high,"Current Drawdown":drawdown,"EWMA Volatility":ann_vol,"Volatility Percentile":vol_pct,
            "Downside Shock Z":-shock_z if pd.notna(shock_z) else np.nan,"SOX Same-Day Correlation":trans["same_corr"],"SOX Lag-1 Correlation":trans["lag_corr"],
            "SOX Same-Day Beta":trans["same_beta"],"SOX Lag-1 Beta":trans["lag_beta"],"Contagion Score":float(np.clip(contagion,0,100)),
            "Expectation Risk Score":float(np.clip(expectation,0,100)),"Institutional Score":inst_score,"Confidence Score":confidence,
            "Recommendation":recommendation,"Position Action":action,
        })
    return pd.DataFrame(rows)


def build_european_subsector_stress(europe_monitor):
    if europe_monitor is None or europe_monitor.empty or "Subsector" not in europe_monitor:
        return pd.DataFrame()
    live=europe_monitor[europe_monitor["Status"].eq("LIVE")].copy()
    if live.empty: return pd.DataFrame()
    agg=live.groupby("Subsector",as_index=False).agg(
        Names=("Ticker","count"),
        **{"1D Return":("1D Return","mean"),"5D Return":("5D Return","mean"),"20D Return":("20D Return","mean"),
           "Contagion Score":("Contagion Score","mean"),"Expectation Risk Score":("Expectation Risk Score","mean"),
           "EWMA Volatility":("EWMA Volatility","mean"),"Negative Breadth":("1D Return",lambda s: float((s<0).mean()))}
    )
    return agg.sort_values("Contagion Score",ascending=False)


def build_global_semiconductor_contagion_pack(close, institutional_results):
    regional,history=build_regional_semiconductor_baskets(close)
    europe=build_european_contagion_monitor(close,institutional_results)
    segments=build_european_subsector_stress(europe)
    live_eu=europe[europe.get("Status",pd.Series(dtype=str)).eq("LIVE")] if not europe.empty else pd.DataFrame()
    avg_cont=float(live_eu["Contagion Score"].mean()) if not live_eu.empty else np.nan
    severe=int((live_eu["Contagion Score"]>=70).sum()) if not live_eu.empty else 0
    reduce_count=int(live_eu["Position Action"].str.contains("REDUCE|HEDGE",regex=True,na=False).sum()) if not live_eu.empty else 0
    reg_live=regional[regional.get("Status",pd.Series(dtype=str)).eq("LIVE")] if not regional.empty else pd.DataFrame()
    global_negative=float(reg_live["Negative Breadth"].mean()) if not reg_live.empty else np.nan
    global_risk=0.55*(avg_cont if pd.notna(avg_cont) else 50)+45*(global_negative if pd.notna(global_negative) else 0.5)
    if global_risk>=75: stance="DEFENSIVE / HIGH HEDGE"
    elif global_risk>=60: stance="CAUTIOUS / REDUCED GROSS"
    elif global_risk>=45: stance="SELECTIVE / EVENT-DRIVEN"
    else: stance="BALANCED / SELECTIVE RISK-ON"
    summary={
        "Global Contagion Risk Score":float(np.clip(global_risk,0,100)),"Management Stance":stance,
        "Average Europe Contagion Score":avg_cont,"Severe European Names":severe,"Reduce / Hedge Names":reduce_count,
        "Global Negative Breadth":global_negative,"European Live Names":int(len(live_eu)),
        "Executive Interpretation":f"{stance}: U.S. semiconductor weakness is evaluated through same-day and lagged SOX transmission, European breadth, EWMA volatility and institutional positioning. No news return is hard-coded; all live classifications come from Yahoo Finance observations."
    }
    return {"summary":summary,"regional":regional,"regional_history":history,"europe":europe,"segments":segments,"event_register":news_event_register()}


def chart_regional_semiconductor_growth(pack):
    fig=go.Figure()
    for region,d in pack.get("regional_history",{}).items():
        if not d.empty: fig.add_trace(go.Scatter(x=d.index,y=d["Basket Equity"]*100,mode="lines",name=region))
    fig.update_yaxes(title="Equal-weight local-return basket, base 100")
    return layout(fig,"Global Semiconductor Regional Basket Performance",CHART_EXTRA_LARGE_HEIGHT)


def chart_regional_contagion_risk(regional):
    live=regional[regional["Status"].eq("LIVE")].copy() if regional is not None and not regional.empty else pd.DataFrame()
    if live.empty: return layout(go.Figure(),"Regional Semiconductor Risk Pulse",CHART_FULL_HEIGHT)
    live=live.sort_values("Downside Shock Z",ascending=True)
    fig=go.Figure(go.Bar(x=live["Downside Shock Z"],y=live["Region"],orientation="h",customdata=np.stack([live["Negative Breadth"],live["EWMA Volatility"],live["1D Basket Return"]],axis=-1),hovertemplate="%{y}<br>Downside shock=%{x:.2f}σ<br>Negative breadth=%{customdata[0]:.1%}<br>EWMA vol=%{customdata[1]:.1%}<br>1D=%{customdata[2]:.2%}<extra></extra>"))
    fig.add_vline(x=0,line_width=1); fig.add_vline(x=2,line_dash="dash")
    fig.update_xaxes(title="Downside shock intensity (positive = risk pressure)")
    return layout(fig,"Regional Semiconductor Risk Pulse",CHART_FULL_HEIGHT)


def chart_europe_contagion_map(europe):
    live=europe[europe["Status"].eq("LIVE")].copy() if europe is not None and not europe.empty else pd.DataFrame()
    if live.empty: return layout(go.Figure(),"European Semiconductor Contagion Map",CHART_FULL_HEIGHT)
    fig=px.scatter(live,x="Contagion Score",y="Institutional Score",size="EWMA Volatility",color="Position Action",text="Ticker",hover_data=["Company","Subsector","1D Return","20D Return","SOX Same-Day Beta","SOX Lag-1 Beta","Expectation Risk Score"],template=PLOT_TEMPLATE)
    fig.update_traces(textposition="top center"); fig.add_vline(x=55,line_dash="dot"); fig.add_vline(x=75,line_dash="dash"); fig.add_hline(y=50,line_dash="dot")
    fig.update_xaxes(range=[0,100]); fig.update_yaxes(range=[0,100])
    return layout(fig,"European Semiconductor Contagion & Positioning Map",CHART_EXTRA_LARGE_HEIGHT)


def chart_europe_contagion_scores(europe):
    live=europe[europe["Status"].eq("LIVE")].sort_values("Contagion Score") if europe is not None and not europe.empty else pd.DataFrame()
    if live.empty: return layout(go.Figure(),"European Contagion Score Ranking",CHART_FULL_HEIGHT)
    fig=go.Figure(go.Bar(x=live["Contagion Score"],y=live["Ticker"],orientation="h",customdata=np.stack([live["Company"],live["SOX Lag-1 Beta"],live["Downside Shock Z"],live["Position Action"]],axis=-1),hovertemplate="%{y}<br>%{customdata[0]}<br>Score=%{x:.1f}<br>Lag beta=%{customdata[1]:.2f}<br>Shock=%{customdata[2]:.2f}σ<br>%{customdata[3]}<extra></extra>"))
    fig.add_vline(x=55,line_dash="dot"); fig.add_vline(x=75,line_dash="dash"); fig.update_xaxes(range=[0,100])
    return layout(fig,"European Contagion Score Ranking",CHART_FULL_HEIGHT)


def chart_subsector_stress(segments):
    if segments is None or segments.empty: return layout(go.Figure(),"European Subsector Stress",CHART_FULL_HEIGHT)
    d=segments.sort_values("Contagion Score")
    fig=go.Figure(go.Bar(x=d["Contagion Score"],y=d["Subsector"],orientation="h",customdata=np.stack([d["1D Return"],d["Negative Breadth"],d["EWMA Volatility"]],axis=-1),hovertemplate="%{y}<br>Stress=%{x:.1f}<br>1D=%{customdata[0]:.2%}<br>Negative breadth=%{customdata[1]:.1%}<br>EWMA vol=%{customdata[2]:.1%}<extra></extra>"))
    fig.update_xaxes(range=[0,100]); return layout(fig,"European Semiconductor Subsector Stress",CHART_FULL_HEIGHT)


def global_contagion_tab_html(pack):
    figs=[chart_regional_semiconductor_growth(pack),chart_regional_contagion_risk(pack["regional"]),chart_europe_contagion_map(pack["europe"]),chart_europe_contagion_scores(pack["europe"]),chart_subsector_stress(pack["segments"])]
    charts="".join(f'<div class="chart-block">{div(f,False)}</div>' for f in figs)
    return f'<div class="section"><h2>Global Semiconductor Contagion & Positioning Engine</h2><div class="note">{pack["summary"].get("Executive Interpretation","")}</div><h3>Executive KPI Summary</h3>{table(metrics_df(pack["summary"]),"gsc_summary")}<h3>Full-Width Contagion Charts</h3>{charts}<h3>Regional Basket Risk Pulse</h3>{table(pack["regional"],"gsc_regional")}<h3>European Security Contagion Monitor</h3>{table(pack["europe"],"gsc_europe")}<h3>European Subsector Stress</h3>{table(pack["segments"],"gsc_segments")}</div>'


def _render_global_semiconductor_contagion(pack):
    summary=pack["summary"]
    st.markdown(f'<div class="mk-note"><b>Article 5:</b> {NEWS_SOURCE_TITLE_5} ({NEWS_SOURCE_DATE_5}).<br><b>Management interpretation:</b> {summary.get("Executive Interpretation","")}</div>',unsafe_allow_html=True)
    _metric_grid([
        ("Global Contagion Risk",_safe_metric_value(summary.get("Global Contagion Risk Score"),"score")),
        ("Management Stance",summary.get("Management Stance","—")),
        ("Europe Avg Contagion",_safe_metric_value(summary.get("Average Europe Contagion Score"),"score")),
        ("Severe Europe Names",_safe_metric_value(summary.get("Severe European Names"),"int")),
        ("Reduce / Hedge Names",_safe_metric_value(summary.get("Reduce / Hedge Names"),"int")),
        ("Global Negative Breadth",_safe_metric_value(summary.get("Global Negative Breadth"),"percent")),
        ("European Live Names",_safe_metric_value(summary.get("European Live Names"),"int")),
    ],columns=4)
    _section("Regional semiconductor performance","Equal-weight local-return baskets; no synthetic FX conversion.")
    _plot(chart_regional_semiconductor_growth(pack),key="gsc_growth")
    _section("Regional contagion risk pulse")
    _plot(chart_regional_contagion_risk(pack["regional"]),key="gsc_regional_chart")
    _show_df(pack["regional"],height=470,key="gsc_regional_table")
    _section("European contagion and positioning map","SOX same-day and lag-1 transmission is combined with EWMA volatility, drawdown and institutional score.")
    _plot(chart_europe_contagion_map(pack["europe"]),key="gsc_map")
    _section("European contagion score ranking")
    _plot(chart_europe_contagion_scores(pack["europe"]),key="gsc_scores")
    _show_df(pack["europe"].sort_values("Contagion Score",ascending=False) if not pack["europe"].empty else pack["europe"],height=700,key="gsc_europe_table")
    _section("European semiconductor subsector stress")
    _plot(chart_subsector_stress(pack["segments"]),key="gsc_segments_chart")
    _show_df(pack["segments"],height=520,key="gsc_segments_table")

@st.cache_data(ttl=3600, show_spinner=False)
def load_institutional_platform():
    close, ohlcv_map = download_all()
    sox = compute_sox_diagnostics()
    results = [analyze(uname, cfg, close) for uname, cfg in UNIVERSE_CONFIGS.items()]
    institutional_results = analyze_supertrend_institutional(results, ohlcv_map, close)
    cross_listing = compute_cross_listing_analysis(close)
    contagion_pack = build_global_semiconductor_contagion_pack(close, institutional_results)
    asia_ytd_pack = build_asia_origin_ytd_pack(close, institutional_results)
    return close, ohlcv_map, sox, results, institutional_results, cross_listing, contagion_pack, asia_ytd_pack


@st.cache_data(ttl=3600, show_spinner=False)
def generate_qs_reports_cached():
    return compute_qs_engine_reports()


def _render_masthead():
    st.markdown(
        f"""
        <div class="mk-masthead">
          <div class="mk-kicker">MK FinTECH LabGEN · Institutional Analytics</div>
          <div class="mk-title">Global AI / Semiconductor & Asia YTD Institutional Platform</div>
          <div class="mk-subtitle">SupertrendPro Institutional + Asia YTD + Hedge Fund Management Cockpit · Version {STREAMLIT_APP_VERSION} · Daily Yahoo Finance data · No synthetic prices</div>
        </div>
        """, unsafe_allow_html=True,
    )


def _render_selected_asset_kpis(detail, selected_ticker):
    score = detail["score"]
    last = score.iloc[-1]
    decision = detail["decision"]
    cols = st.columns(6)
    values = [
        ("Last Price", _safe_metric_value(last.get("Close"), "price")),
        ("Institutional Score", _safe_metric_value(decision.get("Institutional Score"), "score")),
        ("Confidence", _safe_metric_value(decision.get("Confidence Score"), "score")),
        ("Recommendation", str(decision.get("Recommendation", "—"))),
        ("RSI / ADX", f"{last.get('RSI', np.nan):.1f} / {last.get('ADX', np.nan):.1f}"),
        ("60D Positive Prob.", f"{decision.get('Positive Return Probability 60D %', np.nan):.1f}%" if pd.notna(decision.get('Positive Return Probability 60D %')) else "—"),
    ]
    for col, (label, value) in zip(cols, values):
        col.metric(label, value)


def _render_executive(res, inst, close):
    pm = res["pm"]; pv = res["pf"]["portfolio_value"]
    pack = build_hedge_fund_management_pack(res, inst, close)
    summary = pack["summary"]
    st.markdown(
        f'<div class="mk-note"><b>Management posture:</b> {summary.get("Management Stance")} · '
        f'<b>Risk score:</b> {summary.get("Risk Score", np.nan):.1f}/100 · '
        f'<b>Model gross exposure bias:</b> {summary.get("Model Gross Exposure Bias")} · '
        f'<b>Hedge intensity:</b> {summary.get("Hedge Intensity")}<br>'
        f'{summary.get("Executive Interpretation", "")}</div>',
        unsafe_allow_html=True,
    )
    management_kpis = [
        ("Risk Posture", summary.get("Management Stance", "—")),
        ("Risk Score", _safe_metric_value(summary.get("Risk Score"), "score")),
        ("Buy Breadth", _safe_metric_value(summary.get("Buy Breadth"), "percent")),
        ("Sell Breadth", _safe_metric_value(summary.get("Sell Breadth"), "percent")),
        ("Portfolio EWMA Vol", _safe_metric_value(summary.get("Portfolio EWMA Vol"), "percent")),
        ("News Event Exposure", _safe_metric_value(summary.get("News Event Exposure"), "percent")),
        ("Severe Event Names", _safe_metric_value(summary.get("Severe Event Names"), "int")),
        ("Weight HHI", _safe_metric_value(summary.get("Weight HHI"))),
    ]
    _metric_grid(management_kpis, columns=4)
    _section("Portfolio KPI summary")
    portfolio_kpis = [
        ("Latest Value", _safe_metric_value(pv.iloc[-1], "money")),
        ("Annual Return", _safe_metric_value(pm.get("Annualized Return"), "percent")),
        ("Annual Volatility", _safe_metric_value(pm.get("Annualized Volatility"), "percent")),
        ("Sharpe", _safe_metric_value(pm.get("Sharpe Ratio"))),
        ("Max Drawdown", _safe_metric_value(pm.get("Max Drawdown"), "percent")),
        ("Valid Names", _safe_metric_value(len(res["ud"]["valid"]), "int")),
        ("Portfolio 5D", _safe_metric_value(summary.get("Portfolio 5D"), "percent")),
        ("Portfolio 20D", _safe_metric_value(summary.get("Portfolio 20D"), "percent")),
    ]
    _metric_grid(portfolio_kpis, columns=4)
    _section("Portfolio growth and benchmark comparison")
    _plot(chart_growth(res), key="exec_growth")
    _section("Risk-return positioning")
    _plot(chart_rr(res), key="exec_rr")
    _section("Institutional decision breadth")
    rank = inst.get("ranking", pd.DataFrame())
    _plot(chart_decision_breadth(rank), key="exec_breadth")
    _section("Institutional decision ranking")
    _plot(chart_institutional_ranking(rank, res["name"] + " — Institutional Ranking"), key="exec_rank")
    if not rank.empty:
        cols_keep = [c for c in ["Ticker","Company","Country","Institutional Score","Confidence Score","Recommendation","Technical Grade","Best Strategy","Best Strategy Sharpe","Positive 60D Probability %"] if c in rank.columns]
        _show_df(rank.sort_values("Institutional Score", ascending=False)[cols_keep], height=470, key="exec_table")


def _render_strategy_signal(inst, selected_ticker):
    detail = _selected_detail(inst, selected_ticker)
    if detail is None:
        st.warning("The selected security does not have sufficient institutional OHLCV history.")
        return
    _render_selected_asset_kpis(detail, selected_ticker)
    strategy_name = st.selectbox("Strategy", ["Smart Supertrend", "MACD + ATR"], key="strategy_signal_choice")
    _section("Price, signals and risk control", "Signals are generated from observed adjusted OHLCV data and include estimated trading friction.")
    _plot(chart_strategy_signal(detail, selected_ticker, strategy_name), key="strategy_signal_price")
    _section("Net strategy equity")
    _plot(chart_strategy_equity(detail, selected_ticker, strategy_name), key="strategy_signal_equity")
    trades = detail["supertrend_trades"] if strategy_name == "Smart Supertrend" else detail["macd_trades"]
    _section("Closed trade log")
    _show_df(trades.sort_values("Exit Date", ascending=False) if not trades.empty else trades, height=500, key="strategy_signal_trades")


def _render_market_data(inst, selected_ticker, res):
    detail = _selected_detail(inst, selected_ticker)
    if detail is None:
        st.warning("No selected-security market dataset is available.")
        return
    x = detail["score"].copy().sort_index(ascending=False)
    cols = [c for c in ["Open","High","Low","Close","Volume","Dollar_Volume","Return","Log_Return","EMA_20","EMA_50","EMA_100","EMA_200","RSI","CCI","ATR","ATR_Pct","ADX","MACD","MACD_SIGNAL","MACD_HIST","BB_UPPER","BB_MID","BB_LOWER","ST_Line","ST_Dir","Momentum_20D","Momentum_63D","Momentum_126D","Momentum_252D","Pct_From_52W_High","Pct_From_52W_Low","Drawdown","Institutional Score","Confidence Score","Recommendation"] if c in x.columns]
    _render_selected_asset_kpis(detail, selected_ticker)
    _section("Selected security market data")
    market_table = x[cols].head(1000).reset_index().rename(columns={x.index.name or "index": "Date"})
    _show_df(market_table, height=650, key="market_data_table")
    st.download_button("Download selected security market data", market_table.to_csv(index=False).encode("utf-8"), file_name=f"{selected_ticker}_market_data.csv", mime="text/csv")
    _section("Universe data quality")
    _show_df(res["ud"]["data_quality"], height=500, key="market_data_quality")
    _section("Security exclusion log")
    _show_df(res["ud"]["exclusions"], height=300, key="market_exclusions")


def _render_technical_analytics(inst, selected_ticker):
    detail = _selected_detail(inst, selected_ticker)
    if detail is None:
        st.warning("No technical analytics are available for the selected security.")
        return
    _render_selected_asset_kpis(detail, selected_ticker)
    _section("Price structure")
    _plot(chart_technical_price(detail, selected_ticker), key="technical_price")
    _section("MACD momentum")
    _plot(chart_technical_macd(detail, selected_ticker), key="technical_macd")
    _section("RSI and ADX regime")
    _plot(chart_technical_rsi_adx(detail, selected_ticker), key="technical_rsi_adx")


def _render_ewma_volatility(inst, selected_ticker, res):
    detail = _selected_detail(inst, selected_ticker)
    if detail is None:
        st.warning("No EWMA volatility series are available for the selected security.")
        return
    vol = compute_ewma_volatility_frame(detail["score"]["Close"], input_is_price=True)
    current = vol.dropna(subset=["EWMA 0.94 Ann Vol"]).iloc[-1]
    pctile = current.get("EWMA 0.94 Percentile 252D", np.nan)
    regime = "HIGH" if pd.notna(pctile) and pctile >= .75 else ("LOW" if pd.notna(pctile) and pctile <= .25 else "NORMAL")
    cols = st.columns(6)
    metrics = [
        ("EWMA λ=0.94", _safe_metric_value(current.get("EWMA 0.94 Ann Vol"), "percent")),
        ("EWMA λ=0.97", _safe_metric_value(current.get("EWMA 0.97 Ann Vol"), "percent")),
        ("Rolling 20D", _safe_metric_value(current.get("Rolling 20D Ann Vol"), "percent")),
        ("Rolling 63D", _safe_metric_value(current.get("Rolling 63D Ann Vol"), "percent")),
        ("20D Vol Change", _safe_metric_value(current.get("EWMA 0.94 20D Change"), "percent")),
        ("Volatility Regime", regime),
    ]
    for c, (l, v) in zip(cols, metrics): c.metric(l, v)
    _section("EWMA and rolling volatility")
    _plot(chart_ewma_volatility_levels(vol, selected_ticker), key="ewma_levels")
    _section("Return shocks against EWMA ±2 sigma")
    _plot(chart_ewma_return_shocks(vol, selected_ticker), key="ewma_shocks")
    _section("Universe EWMA volatility ranking")
    snapshot = build_ewma_snapshot(inst)
    _show_df(snapshot, height=600, key="ewma_snapshot")
    _section("Portfolio EWMA volatility")
    portfolio_vol = compute_ewma_volatility_frame(res["pf"]["portfolio_return"], input_is_price=False)
    _plot(chart_ewma_volatility_levels(portfolio_vol, res["name"] + " Portfolio"), key="ewma_portfolio")


def _render_backtest_risk(inst, selected_ticker, res):
    detail = _selected_detail(inst, selected_ticker)
    if detail is None:
        st.warning("No backtest is available for the selected security.")
        return
    strategy_name = st.selectbox("Backtest strategy", ["Smart Supertrend", "MACD + ATR", "Leading Signal Lab"], key="backtest_choice")
    if strategy_name == "Smart Supertrend":
        bt = detail["supertrend_backtest"]; stats = detail["supertrend_stats"]; ret_col = "Strategy Return"
    elif strategy_name == "MACD + ATR":
        bt = detail["macd_backtest"]; stats = detail["macd_stats"]; ret_col = "Strategy Return"
    else:
        bt = detail["leading_lab"]; stats = detail["leading_stats"]; ret_col = "Signal Strategy Return"
    cols = st.columns(6)
    metrics = [
        ("CAGR", _safe_metric_value(stats.get("CAGR"), "percent")),
        ("Ann. Volatility", _safe_metric_value(stats.get("Ann Vol"), "percent")),
        ("Sharpe", _safe_metric_value(stats.get("Sharpe"))),
        ("Sortino", _safe_metric_value(stats.get("Sortino"))),
        ("Max Drawdown", _safe_metric_value(stats.get("Max Drawdown"), "percent")),
        ("Win Rate", _safe_metric_value(stats.get("Win Rate"), "percent")),
    ]
    for c, (l, v) in zip(cols, metrics): c.metric(l, v)
    if strategy_name != "Leading Signal Lab":
        _section("Net equity comparison")
        _plot(chart_strategy_equity(detail, selected_ticker, strategy_name), key="risk_equity")
        _section("Drawdown comparison")
        _plot(chart_strategy_drawdown(detail, selected_ticker, strategy_name), key="risk_drawdown")
    else:
        _section("Leading signal net equity")
        _plot(chart_leading_signal_equity(detail, selected_ticker), key="risk_leading_equity")
    benchmark = res["ud"]["primary_return"].reindex(bt.index)
    rf = res["ud"]["rf"].reindex(bt.index)
    risk_rows = [
        {"Series": strategy_name, **compute_return_metrics(bt[ret_col], benchmark, rf)},
        {"Series": "Buy & Hold", **compute_return_metrics(bt["Return"] if "Return" in bt.columns else bt["Close"].pct_change(), benchmark, rf)},
    ]
    _section("Institutional risk metric set")
    _show_df(pd.DataFrame(risk_rows), height=520, key="risk_metrics")


def _render_strategy_diagnostics(inst, selected_ticker):
    detail = _selected_detail(inst, selected_ticker)
    if detail is None:
        st.warning("No strategy diagnostics are available.")
        return
    diag = build_strategy_diagnostics(detail)
    _section("Constraint funnel")
    _plot(chart_strategy_diagnostics(diag, selected_ticker), key="diag_funnel")
    _show_df(diag, height=400, key="diag_table")
    _section("Strategy comparison")
    rows = []
    for name, stats in [("Smart Supertrend", detail["supertrend_stats"]), ("MACD + ATR", detail["macd_stats"]), ("Leading Signal Lab", detail["leading_stats"])]:
        rows.append({"Strategy": name, **stats})
    _show_df(pd.DataFrame(rows), height=420, key="diag_strategy_table")


def _render_blue_chip_screener(res, inst):
    screener = build_blue_chip_screener(res, inst)
    st.markdown('<div class="mk-note"><b>Methodology note:</b> This is a market-data institutional quality proxy, not a formal market-cap classification. It combines liquidity, volatility, drawdown quality, data depth, momentum and the explainable Institutional Decision Score.</div>', unsafe_allow_html=True)
    _section("Blue-chip quality ranking")
    _plot(chart_blue_chip_screener(screener, res["name"] + " — Blue-Chip Quality Screener"), key="bluechip_chart")
    _show_df(screener, height=650, key="bluechip_table")
    if not screener.empty:
        st.download_button("Download blue-chip screener", screener.to_csv(index=False).encode("utf-8"), file_name="blue_chip_screener.csv", mime="text/csv")


def _render_capital_gain_leaders(inst):
    leaders = build_capital_gain_leaders(inst)
    _section("Short-term capital gain leaders")
    _plot(chart_capital_gain(leaders, "Return 20D", "20-Day Capital Gain Leaders"), key="gain_20d")
    _section("Quarterly capital gain leaders")
    _plot(chart_capital_gain(leaders, "Return 63D", "63-Day Capital Gain Leaders"), key="gain_63d")
    _section("One-year capital gain leaders")
    _plot(chart_capital_gain(leaders, "Return 252D", "252-Day Capital Gain Leaders"), key="gain_252d")
    _section("Composite ranking")
    _show_df(leaders, height=650, key="gain_table")


def _render_portfolio_lab(res):
    cols = st.columns(6)
    pm = res["pm"]
    metrics = [
        ("Annual Return", _safe_metric_value(pm.get("Annualized Return"), "percent")),
        ("Annual Volatility", _safe_metric_value(pm.get("Annualized Volatility"), "percent")),
        ("Sharpe", _safe_metric_value(pm.get("Sharpe Ratio"))),
        ("Sortino", _safe_metric_value(pm.get("Sortino Ratio"))),
        ("Max Drawdown", _safe_metric_value(pm.get("Max Drawdown"), "percent")),
        ("Information Ratio", _safe_metric_value(pm.get("Information Ratio"))),
    ]
    for c, (l, v) in zip(cols, metrics): c.metric(l, v)
    chart_sequence = [
        ("Portfolio and benchmark growth", chart_growth(res), "portfolio_growth"),
        ("Daily portfolio value", chart_nav(res), "portfolio_nav"),
        ("Portfolio drawdown", chart_dd(res), "portfolio_dd"),
        ("Rolling volatility", chart_vol(res), "portfolio_vol"),
        ("Rolling beta", chart_beta(res), "portfolio_beta"),
        ("Current security weights", chart_weights(res), "portfolio_weights"),
        ("Sector exposure", chart_sector(res), "portfolio_sector"),
        ("Risk contribution", chart_rc(res), "portfolio_rc"),
        ("Risk-return map", chart_rr(res), "portfolio_rr"),
        ("Correlation matrix", chart_corr(res), "portfolio_corr"),
        ("Return distribution and VaR", chart_var(res), "portfolio_var"),
        ("Optimization scenario map", chart_opt(res), "portfolio_opt"),
        ("Monthly return heatmap", chart_monthly(res), "portfolio_monthly"),
    ]
    for title, fig, key in chart_sequence:
        _section(title)
        _plot(fig, key=key)
    _section("Portfolio metrics")
    _show_df(metrics_df(res["pm"]), height=520, key="portfolio_metrics")
    _section("Holdings and constituents")
    _show_df(res["pf"]["holdings"], height=560, key="portfolio_holdings")
    _section("Asset metrics")
    _show_df(res["am"].sort_values("Sharpe Ratio", ascending=False), height=620, key="portfolio_asset_metrics")
    _section("Optimization summary")
    _show_df(res["os"], height=400, key="portfolio_opt_summary")
    _show_df(res["ow"], height=560, key="portfolio_opt_weights")
    _section("Stress tests and benchmark comparison")
    _show_df(res["st"], height=420, key="portfolio_stress")
    _show_df(res["bt"], height=460, key="portfolio_bench")


def _render_leading_signal_lab(inst, selected_ticker):
    detail = _selected_detail(inst, selected_ticker)
    if detail is None:
        st.warning("No leading signal analysis is available.")
        return
    stats = detail["leading_stats"]
    cols = st.columns(6)
    metrics = [
        ("CAGR", _safe_metric_value(stats.get("CAGR"), "percent")),
        ("Ann. Volatility", _safe_metric_value(stats.get("Ann Vol"), "percent")),
        ("Sharpe", _safe_metric_value(stats.get("Sharpe"))),
        ("Max Drawdown", _safe_metric_value(stats.get("Max Drawdown"), "percent")),
        ("Win Rate", _safe_metric_value(stats.get("Win Rate"), "percent")),
        ("Beta", _safe_metric_value(stats.get("Beta"))),
    ]
    for c, (l, v) in zip(cols, metrics): c.metric(l, v)
    _section("Leading signal events")
    _plot(chart_leading_signal_events(detail, selected_ticker), key="leading_events")
    _section("Leading signal score")
    _plot(chart_leading_signal_score(detail, selected_ticker), key="leading_score")
    _section("Leading signal net equity")
    _plot(chart_leading_signal_equity(detail, selected_ticker), key="leading_equity")
    _section("Latest leading signal observations")
    lab = detail["leading_lab"].tail(800).reset_index().rename(columns={detail["leading_lab"].index.name or "index": "Date"})
    keep = [c for c in ["Date","Close","Breakout_20","Volume_Pass","Signal Score","Signal Position","Signal Event","Signal Strategy Return","Signal Strategy Equity","Signal Buy Hold Equity"] if c in lab.columns]
    _show_df(lab[keep], height=600, key="leading_table")


def _render_institutional_decision(inst, selected_ticker, res):
    ranking = inst.get("ranking", pd.DataFrame())
    strategies = inst.get("strategies", pd.DataFrame())
    factors = inst.get("factors", pd.DataFrame())
    _section("Decision score ranking")
    _plot(chart_institutional_ranking(ranking, "SupertrendPro Institutional — Decision Score Ranking"), key="decision_rank")
    _section("Net strategy risk-return comparison")
    _plot(chart_strategy_comparison(strategies, "Net Strategy Risk / Return Comparison"), key="decision_strategy")
    detail = _selected_detail(inst, selected_ticker)
    if detail is not None:
        _section("Selected security institutional decision engine")
        _render_selected_asset_kpis(detail, selected_ticker)
        _plot(chart_institutional_asset(detail, selected_ticker), key="decision_asset")
        _section("Factor scorecard")
        _show_df(detail["factors"], height=420, key="decision_factors")
        _section("Decision history")
        score = detail["score"].copy().tail(800).reset_index().rename(columns={detail["score"].index.name or "index": "Date"})
        keep = [c for c in ["Date","Close","EMA_20","EMA_50","EMA_200","RSI","ADX","MACD","MACD_SIGNAL","Institutional Score","Confidence Score","Recommendation","Forward 60D Return","Forward 60D Active Return"] if c in score.columns]
        _show_df(score[keep], height=620, key="decision_history")
    _section("Institutional ranking table")
    _show_df(ranking.sort_values("Institutional Score", ascending=False) if not ranking.empty else ranking, height=650, key="decision_rank_table")
    _section("Factor contribution universe")
    _show_df(factors, height=650, key="decision_factor_universe")
    _section("Institutional exclusion log")
    _show_df(inst.get("exclusions", pd.DataFrame()), height=320, key="decision_exclusions")


def _render_sox(sox):
    _section("SOX historical close")
    _plot(chart_sox_close_index(sox), key="sox_close")
    _section("SOX daily log returns and ±2 sigma bands")
    _plot(chart_sox_log_return_bands(sox), key="sox_bands")
    _section("SOX diagnostic summary")
    _show_df(sox["summary"], height=420, key="sox_sum")
    _section("Largest SOX band breaches")
    _show_df(sox["breaches"].head(SOX_TOP_BREACH_ROWS), height=560, key="sox_br")
    _section("Latest SOX diagnostic observations")
    _show_df(sox["diag"].tail(500).reset_index(), height=600, key="sox_diag")


def _render_cross_listing(cross):
    _section("Cross-listing summary")
    _show_df(cross.get("summary", pd.DataFrame()), height=460, key="xl_sum")
    histories = cross.get("histories", {})
    if histories:
        selected = st.selectbox("Cross-listing pair", list(histories.keys()), key="xl_pair")
        hist = histories[selected]
        _section("Selected cross-listing dislocation")
        _plot(chart_cross_listing(selected, hist), key="xl_chart")
        _section("Cross-listing history")
        _show_df(hist.tail(750).reset_index(), height=600, key="xl_hist")
    _section("Cross-listing exclusion log")
    _show_df(cross.get("exclusions", pd.DataFrame()), height=300, key="xl_ex")



def _render_asia_ytd_performance(pack):
    st.markdown('<div class="mk-note"><b>Governance rule:</b> Strict YTD is measured from the final available close before 1 January. New listings without a prior-year observation are shown as since-listing proxies and are never silently treated as full-year returns. Country summaries prioritize primary local listings to prevent ADR double counting.</div>', unsafe_allow_html=True)
    if not pack or pack.get("securities", pd.DataFrame()).empty:
        st.warning("No Asia-origin current-year price observations are available.")
        if pack and not pack.get("exclusions", pd.DataFrame()).empty:
            _show_df(pack["exclusions"], height=420, key="asia_ytd_exclusions_empty")
        return
    summary = pack["summary"]
    _metric_grid([
        ("As of", summary.get("As of Date", "—")),
        ("Listed Instruments", _safe_metric_value(summary.get("Asian-Origin Listed Instruments"), "int")),
        ("Unique Issuers", _safe_metric_value(summary.get("Unique Asian Issuers"), "int")),
        ("Countries", _safe_metric_value(summary.get("Origin Countries"), "int")),
        ("Gainers / Decliners", f'{summary.get("Gainers",0)} / {summary.get("Decliners",0)}'),
        ("Median YTD", _safe_metric_value(summary.get("Median Security YTD Return"), "percent")),
        ("Best YTD", summary.get("Best YTD Security", "—")),
        ("Worst YTD", summary.get("Worst YTD Security", "—")),
    ], columns=4)

    securities = pack["securities"].copy()
    countries = list(securities["Origin Country"].dropna().unique())
    selected_countries = st.multiselect("Origin country filter", countries, default=countries, key="asia_ytd_country_filter")
    listing_types = list(securities["Listing Type"].dropna().unique())
    selected_listing_types = st.multiselect("Listing type filter", listing_types, default=listing_types, key="asia_ytd_listing_filter")
    direction = st.radio("Performance filter", ["All", "Gainers", "Decliners"], horizontal=True, key="asia_ytd_direction_filter")
    filtered = securities[securities["Origin Country"].isin(selected_countries) & securities["Listing Type"].isin(selected_listing_types)].copy()
    if direction == "Gainers": filtered = filtered[filtered["YTD Return"] > 0]
    elif direction == "Decliners": filtered = filtered[filtered["YTD Return"] < 0]

    _section("Grouped interactive YTD performance", "Each country is displayed as a separate vertical panel; green bars are gains and red bars are losses.")
    _plot(chart_asia_ytd_grouped(filtered), key="asia_ytd_grouped_chart")
    _section("Country performance and market breadth", "Country aggregates use primary local listings where available.")
    _plot(chart_asia_country_breadth(pack["countries"]), key="asia_ytd_country_breadth")
    _show_df(pack["countries"], height=380, key="asia_ytd_country_table")

    _section("Asia-origin security smart table", "Sortable numeric table covering YTD, tactical returns, volatility, drawdown and institutional decision scores.")
    display = filtered.drop(columns=["Country Order"], errors="ignore").copy()
    percent_cols = ["YTD Return","1D Return","5D Return","20D Return","60D Return","Distance to YTD High","YTD Max Drawdown","EWMA Volatility","Volatility Percentile"]
    for c in percent_cols:
        if c in display.columns: display[c] = display[c] * 100
    column_config = {
        c: st.column_config.NumberColumn(c.replace(" Return", " Return %") if "Return" in c else c+" %", format="%.2f")
        for c in percent_cols if c in display.columns
    }
    if "Latest Price" in display.columns: column_config["Latest Price"] = st.column_config.NumberColumn("Latest Price", format="%.2f")
    if "Reference Price" in display.columns: column_config["Reference Price"] = st.column_config.NumberColumn("Reference Price", format="%.2f")
    if "Institutional Score" in display.columns: column_config["Institutional Score"] = st.column_config.NumberColumn("Institutional Score", format="%.1f")
    if "Confidence Score" in display.columns: column_config["Confidence Score"] = st.column_config.NumberColumn("Confidence Score", format="%.1f")
    st.dataframe(display, width="stretch", height=720, hide_index=True, column_config=column_config, key="asia_ytd_smart_table")
    st.download_button("Download Asia YTD smart table CSV", filtered.drop(columns=["Country Order"], errors="ignore").to_csv(index=False).encode("utf-8"), file_name="Asia_Origin_Companies_YTD_Performance.csv", mime="text/csv", width="stretch")

    _section("Subsector performance summary")
    _show_df(pack["subsectors"], height=520, key="asia_ytd_subsector_table")
    _section("Data availability and exclusions")
    if pack["exclusions"].empty: st.success("All configured Asia-origin securities returned usable current-year data.")
    else: _show_df(pack["exclusions"], height=420, key="asia_ytd_exclusion_table")


def _render_hedge_fund_management_brief(res, inst, close):
    pack = build_hedge_fund_management_pack(res, inst, close)
    summary = pack["summary"]
    st.markdown(
        f'<div class="mk-note"><b>Event context:</b> Articles 4–5: {NEWS_SOURCE_TITLE_4}; {NEWS_SOURCE_TITLE_5}.<br>'
        f'<b>Management interpretation:</b> {summary.get("Executive Interpretation", "")}</div>',
        unsafe_allow_html=True,
    )
    kpis = [
        ("Management Stance", summary.get("Management Stance", "—")),
        ("Risk Score", _safe_metric_value(summary.get("Risk Score"), "score")),
        ("Gross Exposure Bias", summary.get("Model Gross Exposure Bias", "—")),
        ("Hedge Intensity", summary.get("Hedge Intensity", "—")),
        ("Portfolio EWMA Vol", _safe_metric_value(summary.get("Portfolio EWMA Vol"), "percent")),
        ("Vol Percentile", _safe_metric_value(summary.get("Portfolio Vol Percentile"), "percent")),
        ("Buy / Sell Breadth", f'{summary.get("Buy Breadth", np.nan):.0%} / {summary.get("Sell Breadth", np.nan):.0%}' if pd.notna(summary.get("Buy Breadth")) else "—"),
        ("News Event Exposure", _safe_metric_value(summary.get("News Event Exposure"), "percent")),
    ]
    _metric_grid(kpis, columns=4)
    _section("Macro and regional risk pulse", "Positive risk-pressure z-scores indicate conditions that historically tighten the risk budget.")
    _plot(chart_macro_risk_pulse(pack["macro"]), key="mgmt_macro_chart")
    _show_df(pack["macro"], height=520, key="mgmt_macro_table")
    _section("Multi-event semiconductor shock monitor", "Standardized daily shocks are measured against each security's EWMA daily volatility.")
    _plot(chart_event_shock_monitor(pack["event"]), key="mgmt_event_chart")
    _show_df(pack["event"], height=620, key="mgmt_event_table")
    _section("Institutional decision breadth")
    _plot(chart_decision_breadth(inst.get("ranking", pd.DataFrame())), key="mgmt_breadth")
    _section("Position action and risk-budget map", "Actions are model classifications for portfolio review; they are not automatic orders.")
    _plot(chart_management_action_map(pack["actions"]), key="mgmt_action_chart")
    _show_df(pack["actions"], height=700, key="mgmt_action_table")
    _section("Structured news event register")
    _show_df(pack["event_register"], height=420, key="mgmt_event_register")


def _render_news_and_governance(res, inst, close, contagion_pack=None):
    st.markdown(f'<div class="mk-note"><b>News 1:</b> {NEWS_SOURCE_TITLE}<br>{NEWS_SOURCE_URL}<br><br><b>News 2:</b> {NEWS_SOURCE_TITLE_2}<br>{NEWS_SOURCE_URL_2}<br><br><b>News 3:</b> {NEWS_SOURCE_TITLE_3}<br>{NEWS_SOURCE_URL_3}<br><br><b>News 4:</b> {NEWS_SOURCE_TITLE_4}<br>{NEWS_SOURCE_URL_4}<br><br><b>News 5:</b> {NEWS_SOURCE_TITLE_5}<br>{NEWS_SOURCE_URL_5}</div>', unsafe_allow_html=True)
    ac, ai = article_tables()
    _section("Structured news event register")
    _show_df(news_event_register(), height=420, key="news_event_register")
    _section("Article companies and transmission roles")
    _show_df(ac, height=700, key="news_companies")
    _section("Regional benchmarks")
    _show_df(ai, height=600, key="news_bench")
    _section("Current event shock monitor")
    pack = build_hedge_fund_management_pack(res, inst, close)
    _show_df(pack["event"], height=620, key="news_event_monitor")
    if contagion_pack:
        _section("Article 5 European contagion governance")
        _show_df(contagion_pack.get("europe", pd.DataFrame()), height=650, key="news_europe_contagion")
    _section("Data governance")
    _show_df(res["ud"]["data_quality"], height=560, key="gov_dq")
    st.markdown(f'<div class="mk-note"><b>TOPIX benchmark rule:</b> {TOPIX_BENCHMARK_PROXY_NOTE}<br><b>Data rule:</b> Yahoo Finance daily observations only; no synthetic security prices and no portfolio ETF constituents.<br><b>Event discipline:</b> News affects the monitoring universe and risk posture, but never overrides quantitative data validation or creates synthetic observations.</div>', unsafe_allow_html=True)


def _render_exports(results, sox, institutional_results, cross_listing, close, contagion_pack=None, asia_ytd_pack=None):
    st.markdown('<div class="mk-note">HTML, Excel and standalone QS Engine reports are generated only when requested. This prevents expensive report generation on every Streamlit rerun.</div>', unsafe_allow_html=True)
    if st.button("Generate full institutional report package", type="primary", width="stretch"):
        with st.spinner("Generating QS Engine, HTML and Excel outputs..."):
            qs_reports = generate_qs_reports_cached()
            management_packs = {r["name"]: build_hedge_fund_management_pack(r, institutional_results.get(r["name"], {}), close) for r in results}
            create_report(results, sox, qs_reports, institutional_results, cross_listing, management_packs, contagion_pack, asia_ytd_pack)
            export_excel(results, sox, qs_reports, institutional_results, cross_listing, management_packs, contagion_pack, asia_ytd_pack)
        st.success("Report package generated.")
    files = [
        (REPORT_OUTPUT, "Full Institutional HTML", "text/html"),
        (EXCEL_OUTPUT, "Institutional Analytics Excel", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"),
        (NIKKEI_QS_HTML, "Nikkei 225 QS Engine HTML", "text/html"),
        (TOPIX_QS_HTML, "TOPIX Proxy QS Engine HTML", "text/html"),
    ]
    for path, label, mime in files:
        p = Path(path)
        if p.exists(): st.download_button(label, p.read_bytes(), file_name=p.name, mime=mime, width="stretch")


def streamlit_main():
    _render_masthead()
    with st.sidebar:
        st.markdown("### Institutional Controls")
        universe_name = st.selectbox("Investment Universe", list(UNIVERSE_CONFIGS.keys()))
        st.caption("Yahoo Finance data and institutional calculations are cached for one hour.")
        if st.button("Refresh Yahoo Finance cache", width="stretch"):
            st.cache_data.clear(); st.rerun()
        st.divider()
        st.caption("Real Yahoo Finance daily data · No synthetic security prices · TOPIX proxy exception only.")

    try:
        with st.spinner("Loading Yahoo Finance data and institutional analytics..."):
            close, ohlcv_map, sox, results, institutional_results, cross_listing, contagion_pack, asia_ytd_pack = load_institutional_platform()
    except Exception as exc:
        st.error("Institutional platform could not complete the Yahoo Finance data pipeline.")
        st.exception(exc)
        st.stop()

    result_map = {r["name"]: r for r in results}
    res = result_map[universe_name]
    inst = institutional_results.get(universe_name, {})
    details = inst.get("details", {})
    with st.sidebar:
        asset_options = list(details.keys())
        selected_asset = st.selectbox("Institutional Asset", asset_options) if asset_options else None
        st.markdown(f"**Sample:** {res['ud']['start'].date()} → {res['ud']['end'].date()}")
        st.markdown(f"**Primary benchmark:** {res['ud']['primary']}")
        st.markdown(f"**Valid securities:** {len(res['ud']['valid'])}")

    tab_labels = [
        "Executive Dashboard",
        "Hedge Fund Management Brief",
        "Global Semiconductor Contagion",
        "Asia YTD Performance",
        "Strategy & Signal",
        "Market Data",
        "Technical Analytics",
        "EWMA Volatility",
        "Backtest & Risk",
        "Strategy Diagnostics",
        "Blue-Chip Screener",
        "Capital Gain Leaders",
        "Portfolio Lab",
        "Leading Signal Lab",
        "Institutional Decision Engine",
        "SOX Diagnostics",
        "ADR / Local",
        "News & Governance",
        "Export Center",
    ]
    tabs = st.tabs(tab_labels)
    with tabs[0]: _render_executive(res, inst, close)
    with tabs[1]: _render_hedge_fund_management_brief(res, inst, close)
    with tabs[2]: _render_global_semiconductor_contagion(contagion_pack)
    with tabs[3]: _render_asia_ytd_performance(asia_ytd_pack)
    with tabs[4]:
        if selected_asset: _render_strategy_signal(inst, selected_asset)
        else: st.info("No security has sufficient history for the selected strategy analysis.")
    with tabs[5]:
        if selected_asset: _render_market_data(inst, selected_asset, res)
        else: st.info("No security has sufficient market data.")
    with tabs[6]:
        if selected_asset: _render_technical_analytics(inst, selected_asset)
        else: st.info("No security has sufficient technical history.")
    with tabs[7]:
        if selected_asset: _render_ewma_volatility(inst, selected_asset, res)
        else: st.info("No security has sufficient EWMA history.")
    with tabs[8]:
        if selected_asset: _render_backtest_risk(inst, selected_asset, res)
        else: st.info("No security has sufficient backtest history.")
    with tabs[9]:
        if selected_asset: _render_strategy_diagnostics(inst, selected_asset)
        else: st.info("No security has sufficient diagnostic history.")
    with tabs[10]: _render_blue_chip_screener(res, inst)
    with tabs[11]: _render_capital_gain_leaders(inst)
    with tabs[12]: _render_portfolio_lab(res)
    with tabs[13]:
        if selected_asset: _render_leading_signal_lab(inst, selected_asset)
        else: st.info("No security has sufficient leading-signal history.")
    with tabs[14]:
        if selected_asset: _render_institutional_decision(inst, selected_asset, res)
        else: st.info("No security has sufficient institutional decision history.")
    with tabs[15]: _render_sox(sox)
    with tabs[16]: _render_cross_listing(cross_listing)
    with tabs[17]: _render_news_and_governance(res, inst, close, contagion_pack)
    with tabs[18]: _render_exports(results, sox, institutional_results, cross_listing, close, contagion_pack, asia_ytd_pack)

    st.caption(AUTHOR_LINE + " · Institutional analytical model; not investment advice or an automatic order system.")


def main():
    """Streamlit entry point; all original analytical and batch-export functions remain available."""
    streamlit_main()


if __name__ == "__main__":
    main()