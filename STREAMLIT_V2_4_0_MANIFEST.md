# V2.4.0 Integration Manifest

## Baseline

Source baseline: V2.3.0 Hedge Fund Management Streamlit application.

- Previous top-level functions: 142
- Preserved previous functions: 142
- Removed previous functions: 0
- Added functions: 15
- Previous lines: 2,424
- New lines: 2,720

## Added functions

1. `_all_institutional_details`
2. `_basket_return_series`
3. `_ewma_latest_from_returns`
4. `build_regional_semiconductor_baskets`
5. `_sox_transmission_metrics`
6. `build_european_contagion_monitor`
7. `build_european_subsector_stress`
8. `build_global_semiconductor_contagion_pack`
9. `chart_regional_semiconductor_growth`
10. `chart_regional_contagion_risk`
11. `chart_europe_contagion_map`
12. `chart_europe_contagion_scores`
13. `chart_subsector_stress`
14. `global_contagion_tab_html`
15. `_render_global_semiconductor_contagion`

## New universe

`European Semiconductor Contagion Universe` with 9 direct local listings and broad European/index benchmarks.

## New Streamlit tab

`Global Semiconductor Contagion`

The tab includes:

- Management KPI layout
- Regional performance baskets
- Regional risk pulse
- European contagion/positioning map
- Contagion ranking
- Subsector stress
- Full institutional tables

## Export integration

HTML and Excel now include:

- Global contagion summary
- Regional basket summary and histories
- European security contagion monitor
- European subsector stress
- Fifth event in the structured news register

## Verification

- Python 3.10 syntax / `py_compile`: passed
- Core contagion regression test: passed
- 3 regional baskets: passed
- 9 European securities: passed
- 5 Plotly chart functions: passed
- Existing function preservation: passed
- `background_gradient`: 0
- `use_container_width`: 0
