# Multi-Universe AI / Chip + SupertrendPro Institutional — Streamlit V2.1.1

This hotfix corrects a Python 3.10 compilation error in `institutional_engine_tab_html()`.

## Fix

The prior version built chart HTML inside an f-string expression using escaped quotes. Python 3.10 rejects backslashes inside f-string expression blocks. Chart markup is now prepared in a separate `chart_html` variable and inserted into the final HTML safely.

## Preserved

- All investment universes and benchmarks
- Yahoo Finance real daily data policy
- Institutional Decision Engine
- Smart Supertrend and MACD/ATR backtests
- SOX diagnostics
- ADR/local cross-listing analysis
- QS Engine, HTML and Excel exports
- Hedge-fund Streamlit interface

## Deploy

Upload `app.py`, `requirements.txt`, `runtime.txt`, and `.streamlit/config.toml` to the repository root, then reboot the Streamlit Cloud app.
