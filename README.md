# Global AI / Semiconductor Institutional Platform — V3.0.0 USD-Normalized Engine

## Purpose

This Streamlit platform evaluates a global technology, AI, semiconductor, memory, foundry, equipment, electronics and supply-chain universe under one institutional hedge-fund analytics framework.

The authoritative analytical basis is now USD. Local-market adjusted OHLCV observations are retained, but every eligible non-USD instrument and regional benchmark is converted with an observed Yahoo Finance FX quote before instrument returns, portfolio NAV, risk contribution, optimization, correlation, contagion and institutional decision analytics are calculated.

## Controlled data flow

Yahoo Finance market data  
→ Local-currency adjusted OHLCV  
→ Observed FX conversion to USD  
→ Multi-market calendar alignment  
→ USD instrument-level analytics  
→ USD portfolio-level analytics  
→ USD risk contribution and optimization  
→ USD correlation and contagion analytics  
→ Streamlit dashboard + tabbed HTML report + Excel data pack

## FX governance

- No synthetic security prices.
- No synthetic or proxy FX series.
- FX is matched backward only: an FX observation must exist on or before the local-market date.
- Maximum FX tolerance is five calendar days to cover weekends and non-overlapping market holidays.
- Future FX observations are never backfilled.
- Instruments below the 90% FX coverage threshold are flagged `REVIEW` in the audit table.
- Local-currency analytics remain available only for local-vs-USD attribution and validation.

## Supported currencies

USD, KRW, TWD, JPY, EUR, CHF, AUD, INR, IDR, CNY, HKD and SGD.

The code explicitly records the Yahoo FX ticker and quote direction for every currency.

## Main USD Engine outputs

- Instrument-level FX conversion audit
- FX coverage and staleness controls
- Local-return vs USD-return comparison
- FX contribution to security returns
- Local-currency vs USD-normalized portfolio path
- Portfolio performance impact by universe
- USD benchmark returns
- USD correlation matrices
- Correlation change after USD normalization
- USD risk contribution
- USD portfolio optimization
- USD-based EWMA, Supertrend, Leading Signal and Institutional Decision analytics
- USD-based regional semiconductor contagion
- USD-based Asia YTD rankings and breadth

## Streamlit tabs

1. Executive Dashboard
2. USD-Normalized Engine
3. Hedge Fund Management Brief
4. Global Semiconductor Contagion
5. Asia YTD Performance
6. Strategy & Signal
7. Market Data
8. Technical Analytics
9. EWMA Volatility
10. Backtest & Risk
11. Strategy Diagnostics
12. Blue-Chip Screener
13. Capital Gain Leaders
14. Portfolio Lab
15. Leading Signal Lab
16. Institutional Decision Engine
17. SOX Diagnostics
18. ADR / Local
19. News & Governance
20. Export Center

## Deployment

Upload the following to the root of the Streamlit Cloud repository:

- `app.py`
- `requirements.txt`
- `runtime.txt`
- `.streamlit/config.toml`

Set the main file path to `app.py`, clear the app cache and reboot the application.

## Data policy

Real Yahoo Finance daily data only. TOPIX uses `1306.T` solely as a documented benchmark proxy when the direct index series is unavailable. It is not a portfolio constituent.

## Disclaimer

Institutional analytical research and decision support only. It is not investment advice and does not generate automatic orders.
