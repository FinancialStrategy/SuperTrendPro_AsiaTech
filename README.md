# Global Semiconductor SupertrendPro Institutional — Streamlit V2.4.0

Institutional hedge-fund style Streamlit platform using real daily Yahoo Finance data only. This release preserves the full V2.3.0 analytics layer and adds Article 5, a dedicated European semiconductor universe, and a Global Semiconductor Contagion & Positioning Engine.

## New Article 5 integration

Source: **European chip stocks fall after sharp U.S. peers' selloff** (Investing.com, 17 July 2026).

New local listings:

- `ASML.AS` — ASML Holding
- `ASM.AS` — ASM International
- `BESI.AS` — BE Semiconductor Industries
- `SOI.PA` — Soitec
- `IFX.DE` — Infineon Technologies
- `AIXA.DE` — AIXTRON
- `STMPA.PA` — STMicroelectronics
- `WAF.DE` — Siltronic
- `AMS.SW` — ams-OSRAM

U.S. shock-source names include `INTC`, `WDC`, `STX`, `SNDK`, `TSM`, and `^SOX`.

## New institutional modules

- European Semiconductor Contagion Universe
- U.S. / Europe / Asia equal-weight regional chip baskets
- SOX same-day and lag-1 correlation/beta transmission
- EWMA-standardized downside shock measurement
- European security Contagion Score, 0–100
- Expectations Risk Score, 0–100
- Subsector stress for WFE, packaging, wafers/materials, power/automotive and sensors
- Position actions: Selective Accumulate, Hold/Monitor, Hold/Event Confirmation, Reduce, Reduce/Hedge
- Full-width vertical charts
- Streamlit, HTML and Excel integration

## Data governance

- Yahoo Finance daily observed data only
- No synthetic security prices
- No missing-price substitution
- No ETF portfolio constituents
- TOPIX `1306.T` remains a benchmark-only exception
- Mixed-currency European and regional baskets are local-return baskets; no synthetic FX conversion
- News context defines monitoring scope but does not hard-code returns or force signals

## Streamlit Cloud

Place these files at the repository root:

- `app.py`
- `requirements.txt`
- `runtime.txt`
- `.streamlit/config.toml`

Set the main module to `app.py`, then reboot the app.
