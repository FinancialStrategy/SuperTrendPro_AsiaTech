# Multi-Universe AI / Chip SupertrendPro Institutional — Streamlit V2.1.0

Institutional Streamlit conversion of the complete Colab analytics engine.

## Preserved analytical scope

- US Major Stocks portfolio
- Article Shock AI / Chip universe
- US Technology + AI + Chip universe
- Real Yahoo Finance daily data only
- SOX log-return ±2 sigma diagnostics
- Portfolio risk, stress, benchmarking and optimization
- SupertrendPro Institutional indicator and decision engine
- Smart Supertrend, MACD + ATR and Leading Signal Lab
- ADR / local cross-listing analytics
- QS Engine HTML reports
- Full HTML and Excel exports

## Streamlit architecture

- Wide institutional hedge-fund layout
- Cached Yahoo Finance and analytics pipeline (`ttl=3600`)
- Universe and asset selectors
- Eight interactive top-level tabs
- Report generation only on user request
- No runtime pip installation
- No Pandas Styler / `background_gradient` dependency

## Deploy

Place these files in the root of a Streamlit Cloud repository:

- `app.py`
- `requirements.txt`

Set `app.py` as the main file and reboot the app.

## Data policy

Real Yahoo Finance daily observations only. No synthetic security prices. `1306.T` remains the explicitly disclosed TOPIX benchmark proxy exception and is not a portfolio constituent.
