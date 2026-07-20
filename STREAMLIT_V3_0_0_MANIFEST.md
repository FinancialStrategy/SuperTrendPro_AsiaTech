# V3.0.0 Integration Manifest — USD-Normalized Global Portfolio Engine

## Preservation control

- V2.5.0 functions: 168
- Functions retained: 168
- Removed functions: 0
- New USD Engine functions: 13
- Previous code length: 3,033 lines
- V3.0.0 code length: 3469 lines

## New functions

1. `infer_instrument_currency`
2. `_normalize_datetime_index`
3. `align_observed_fx_to_price_dates`
4. `convert_local_series_to_usd`
5. `build_usd_normalized_market_data`
6. `build_usd_engine_pack`
7. `chart_usd_portfolio_basis`
8. `chart_usd_instrument_impact`
9. `chart_fx_return_contribution`
10. `chart_fx_coverage`
11. `chart_usd_correlation_delta`
12. `usd_engine_tab_html`
13. `_render_usd_engine`

## Main pipeline change

The application downloads local-market prices and observed FX data once. It then creates:

- `local_close` / `local_ohlcv_map`: audit and attribution layer
- `usd_close` / `usd_ohlcv_map`: authoritative analytical layer

The main universe analysis, institutional engine, management risk pack and global contagion pack now use the USD-normalized layer.

## Asia YTD enhancement

The Asia YTD table now includes:

- Local YTD return
- USD YTD return
- FX YTD contribution
- Local and USD reference prices
- USD-based rankings, breadth, volatility and generic YTD risk metrics

## Export additions

- `USD_Engine_Summary`
- `USD_FX_Audit`
- `USD_Currency_Summary`
- `USD_Universe_Comparison`
- Per-universe USD/local portfolio comparison history
- Per-universe correlation-change matrix
- Local audit metrics, prices and returns

Existing institutional, SOX, cross-listing, contagion, Asia YTD, HTML, Excel and QS Engine outputs remain available.

## Validation completed

- Python 3.10 syntax / `py_compile`: PASS
- FX formula tests for KRW, TWD, EUR and USD identity: PASS
- USD OHLCV conversion test: PASS
- Currency mapping across 93 configured securities, indices and factors: PASS
- Local vs USD universe analysis test: PASS
- USD portfolio comparison test: PASS
- FX contribution chart test: PASS
- Correlation-delta chart test: PASS
- USD HTML tab generation test: PASS
- Asia USD YTD test: PASS
- Previous function preservation test: PASS

## Runtime note

Live Yahoo Finance and Streamlit Cloud execution must be verified after deployment because the local build environment does not include Streamlit, yfinance or QuantStats and has no external runtime data session.
