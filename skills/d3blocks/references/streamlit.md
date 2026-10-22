# Streamlit embedding

D3Blocks charts are self-contained HTML + JavaScript. Embed with `st.iframe` after generating HTML with `showfig=False` and `return_html=True`.

## Rules

- Prefer **`st.iframe(html, height=...)`**. Avoid `st.html` for full interactive charts (JS off unless `unsafe_allow_javascript=True`; fixed CSS can overlay the page). Use `components.html` only as a fallback for Streamlit < 1.56.
- Always pass an **explicit pixel height** or `height="stretch"`. `height="content"` is unreliable when the chart uses `position: fixed`.
- Generate with **`showfig=False`** and **`return_html=True`**. Use `filepath=None` if you do not need a file on disk.
- When Streamlit owns the controls, set **`show_side_panel=False`** (and optionally `show_top_panel=False`) so the chart does not duplicate UI.
- **`color_background='streamlit'`** and often **`dark_mode=False`** match a typical light Streamlit page.
- Put every control that affects the chart into a **`@st.cache_data`** builder as arguments so the cache key stays correct.

## Minimal skeleton

```python
import streamlit as st
from d3blocks import D3Blocks

st.set_page_config(layout="wide")
show_side = st.sidebar.checkbox("Side panel", False)
show_top = st.sidebar.checkbox("Top panel", True)
height = st.sidebar.slider("Height", 400, 1200, 700, 50)

# Build html with showfig=False, return_html=True, color_background="streamlit"
html = ...

if hasattr(st, "iframe"):
    st.iframe(html, height=height, width="stretch")
else:
    import streamlit.components.v1 as components
    components.html(html, height=height, scrolling=False)
```

## Full runnable apps (this skill)

Discover apps under `examples/streamlit_*.py` (one file per chart that has a demo). Examples:

```bash
streamlit run examples/streamlit_violin.py
streamlit run examples/streamlit_treemap.py
streamlit run examples/streamlit_tree.py
streamlit run examples/streamlit_heatmap.py
```

Each app follows the same pattern: sidebar controls → `@st.cache_data` builder → `st.iframe`.

Repo demos (if present): `streamlit/<chart>_streamlit_demo.py`. Project docs: `source/Streamlit.rst`.
