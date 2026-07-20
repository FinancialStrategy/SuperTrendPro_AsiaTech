# V2.5.0 Integration Manifest

## Preservation rule

- Source: V2.4.0 Global Semiconductor Contagion.
- Existing source functions removed: **0**.
- Existing analytical modules shortened: **0**.
- Existing 18 Streamlit tabs preserved.
- New Streamlit tab added: **Asia YTD Performance**.

## New analytical functions

1. `_strict_ytd_snapshot`
2. `build_asia_origin_ytd_pack`
3. `chart_asia_ytd_grouped`
4. `chart_asia_country_breadth`
5. `asia_ytd_tab_html`
6. `_render_asia_ytd_performance`

## Governance controls

- Strict YTD reference is the last observed closing price before 1 January.
- New listings without prior-year observations are explicitly marked as since-listing proxies.
- Primary local listings are used for country aggregates where available.
- ADR/cross-listings remain visible at the security level but do not distort country-level issuer performance.
- No synthetic price, proxy security or fabricated observation is created.

## Streamlit behavior

- One full-width interactive chart per section.
- Country and listing-type filters.
- Gainer/decliner filter.
- Sortable smart table and CSV download.
- Institutional thin-font KPI layout retained.

## Report outputs

- Streamlit tab: Asia YTD Performance.
- HTML tab: Asia YTD Performance.
- Five dedicated Excel sheets.

## Static and regression tests

- Python `py_compile`: PASS.
- Original function preservation: PASS.
- 15 configured security test: PASS.
- 3 country aggregation test: PASS.
- 13 subsector aggregation test: PASS.
- New listing / since-listing proxy test: PASS.
- Plotly grouped chart test: PASS.
- Plotly breadth chart test: PASS.
