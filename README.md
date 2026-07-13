# Multi-Universe AI / Chip + SupertrendPro Institutional Streamlit V2.2.0

This release preserves the complete analytical codebase and rebuilds the Streamlit presentation layer for full-width institutional use.

## Core changes

- Every Plotly chart is rendered separately, vertically and at full width.
- New dedicated EWMA Volatility tab with RiskMetrics lambda 0.94 and 0.97, rolling volatility comparisons, shock bands and cross-sectional ranking.
- Added the requested SupertrendPro Institutional tabs:
  - Strategy & Signal
  - Market Data
  - Technical Analytics
  - Backtest & Risk
  - Strategy Diagnostics
  - Blue-Chip Screener
  - Capital Gain Leaders
  - Portfolio Lab
  - Leading Signal Lab
  - Institutional Decision Engine
- Existing Executive Dashboard, SOX Diagnostics, ADR/Local, News & Governance and Export Center are preserved.
- Thin institutional typography, professional KPI cards and hedge-fund style visual hierarchy.
- Original analytics, report generation, Excel export, QS Engine, optimization, stress testing and cross-listing logic remain available.

## Deployment

Upload the following to the root of the Streamlit Cloud repository:

- app.py
- requirements.txt
- runtime.txt
- .streamlit/config.toml

Then reboot the application.
