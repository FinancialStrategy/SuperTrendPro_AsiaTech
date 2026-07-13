# Streamlit V2.1.1 Syntax Hotfix Manifest

- Baseline: Streamlit V2.1.0
- Corrected file: `app.py`
- Corrected function: `institutional_engine_tab_html`
- Root cause: escaped quotes/backslashes inside an f-string expression under Python 3.10
- Resolution: precompute `uid` and `chart_html` outside the final f-string
- Python compile validation: passed
- Existing analytical functions and tabs: preserved
