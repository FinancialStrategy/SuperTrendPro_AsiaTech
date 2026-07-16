# Multi-Universe AI / Chip SupertrendPro Institutional V2.3.0

## Purpose

Streamlit-based institutional equity, semiconductor and AI-supply-chain platform using real daily Yahoo Finance observations only. The V2.3.0 release preserves the V2.2.0 full-width chart architecture, EWMA volatility engine, strategy tabs and institutional decision framework while adding a consolidated Hedge Fund Management Cockpit.

## New in V2.3.0

- Fourth Investing.com event integrated: **Asia stocks slide as S. Korea chip stocks tumble; TSMC earnings in focus**.
- Structured four-event news register.
- New `Hedge Fund Management Brief` tab.
- Cross-market macro and regional risk pulse.
- Article-four semiconductor event shock monitor.
- Management posture and 0–100 risk score.
- Model gross-exposure bias and hedge-intensity classification.
- BUY/SELL breadth and institutional decision breadth.
- Position action matrix: Add, Accumulate, Hold, Event Confirmation, Reduce and Exit Watch.
- Current-weight versus risk-contribution discipline.
- Article-four event exposure and severe-event-name count.
- Regional benchmark expansion: Taiwan `^TWII`, Hong Kong `^HSI`, Singapore `^STI`.
- Macro monitoring factors: WTI `CL=F`, DXY `DX-Y.NYB`, US 10Y yield `^TNX`.
- HTML and Excel exports extended with management summaries, macro pulse, event monitor and action matrix.

## Existing structure preserved

- Executive Dashboard
- Strategy & Signal
- Market Data
- Technical Analytics
- EWMA Volatility
- Backtest & Risk
- Strategy Diagnostics
- Blue-Chip Screener
- Capital Gain Leaders
- Portfolio Lab
- Leading Signal Lab
- Institutional Decision Engine
- SOX Diagnostics
- ADR / Local Cross-Listing
- News & Governance
- Export Center

All charts remain full-width and vertically stacked. `st.columns()` is used only for KPI cards.

## Data policy

- Yahoo Finance daily data only.
- No synthetic security prices.
- Missing observations are not fabricated.
- New listings are retained in event monitoring when long-history tests cannot be completed.
- `1306.T` remains the explicit TOPIX benchmark proxy exception and is never a portfolio constituent.
- News events influence the monitored risk channels, not the underlying market observations.

## Streamlit Cloud deployment

Upload the following files to the repository root:

- `app.py`
- `requirements.txt`
- `runtime.txt`
- `.streamlit/config.toml`

Set the main module to `app.py`, then reboot the application.
