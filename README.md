# Global AI / Semiconductor Institutional Platform — V2.5.0

## Asia-Origin YTD Smart Analytics

This Streamlit release preserves the complete V2.4.0 Global Semiconductor Contagion and SupertrendPro Institutional codebase and adds an institutional Asia-origin year-to-date performance cockpit.

### New Streamlit tab

**Asia YTD Performance** provides:

- South Korea, Taiwan and Japan origin-country grouping.
- Local primary listings and ADR/cross-listings displayed separately.
- Strict YTD performance from the final observed close before 1 January.
- Explicit since-listing proxy labels where a new security has no prior-year close.
- Full-width vertically grouped interactive Plotly chart.
- Gain/loss coloring and institutional hover details.
- Country-level median YTD and positive breadth analysis.
- Smart sortable table with country, subsector and listing filters.
- 1D, 5D, 20D and 60D tactical returns.
- EWMA volatility, volatility percentile and YTD maximum drawdown.
- Institutional Score, Confidence Score and Recommendation.
- Country and subsector summary tables.
- CSV download and data-availability log.

### Asia-origin securities configured

- South Korea: Samsung Electronics, SK hynix, LG Innotek and SKHY ADR.
- Taiwan: TSMC local/ADR, Foxconn and MediaTek.
- Japan: Kioxia, Ibiden, Murata, Furukawa Electric, Mitsui Mining & Smelting, SoftBank Group and Kakaku.com.

Country aggregates prioritize primary local listings to prevent ADR double counting. No missing security price is synthetically filled.

### Export integration

The full HTML report receives an **Asia YTD Performance** tab. Excel receives:

- `Asia_YTD_Summary`
- `Asia_YTD_Securities`
- `Asia_YTD_Countries`
- `Asia_YTD_Subsectors`
- `Asia_YTD_Exclusions`

### Deployment

Upload these files to the Streamlit Cloud repository root:

- `app.py`
- `requirements.txt`
- `runtime.txt`

Main module: `app.py`

### Validation completed

- Python 3.10 syntax / `py_compile`: passed.
- All V2.4.0 functions preserved.
- Asia YTD engine controlled-series regression: passed.
- Strict YTD and new-listing proxy governance: passed.
- Country, subsector and ranking calculations: passed.
- Grouped YTD and country-breadth Plotly chart generation: passed.

Live Yahoo Finance execution must be validated on Streamlit Cloud because the local build environment does not contain yfinance, Streamlit or QuantStats.
