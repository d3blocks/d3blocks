# Tests, Streamlit demo and documentation

## Contents
1. Tests (modelled on `test_flowgraph.py`)
2. Streamlit demo
3. Documentation pages

---

## 1. Tests

File: `test_<blockname>.py`, in the folder where `test_flowgraph.py` lives. Start from the generated skeleton and keep these helpers, which every flowgraph test uses:

```python
def _sample_df(): ...                       # small, valid input
def _data(html):                            # the JSON payload the template hands to the renderer
    return json.loads(re.search(r'<script type="application/json" id="XX-data">(.*?)</script>', html, re.S).group(1))
def _options(html): ...                     # same for id="XX-options"
def _render(df, **kwargs):
    d3 = D3Blocks(frame=False, support=None, verbose='error')
    html = d3.<blockname>(df, filepath=None, showfig=False, return_html=True, **kwargs)
    return d3, html
```

`support=None` and `verbose='error'` keep output clean; `filepath=None, showfig=False, return_html=True` avoid touching disk or opening a browser.

### Categories to cover (names mirror test_flowgraph.py)

| Category | What it asserts | flowgraph example |
|---|---|---|
| Standalone HTML | returns `str`; the main SVG/canvas id is present; libraries are inlined; payload content is right | `test_flowgraph_returns_standalone_html` |
| Registered as chart | `D3Blocks(chart='<blockname>').chart is <Module>` | `test_flowgraph_registered_as_chart` |
| Input validation | missing/wrong columns raise `ValueError`; unknown enum values fall back to defaults | `..._missing_columns`, `..._node_attributes_...` |
| Editable properties | edit `d3.node_properties` / `d3.edge_properties`, call `d3.show(return_html=True, showfig=False)`, change appears in payload | `..._node_properties_editable` |
| Frame mode | default `D3Blocks(support=None, verbose='error')` keeps `node_properties` a DataFrame and still renders | `..._frame_mode_node_properties` |
| Escaping | `</script><b>x` in data and `<b>` in title never appear raw; title is `html_escape`d in `<title>` | `..._escapes_html` |
| Option plumbing | each chart option lands in `_options(html)` | `..._animation_options`, `..._direction_aliases` (parametrised) |
| `dark_mode` flag | `True/False/'auto'/'AUTO'` -> `data-dark-mode="true|false|auto"`, `<body class="light"` only for False, `id="themeBtn"` and `D3BlocksTheme` present | `..._dark_mode_flag` |
| `dark_mode` rejects | `"light"`, `1`, `None`, `"yes"` raise `ValueError` matching `dark_mode` | `..._dark_mode_rejects_other_values` |
| Self-contained | no `<script src="http...">`, no `<link href="http...">` | `..._output_stays_self_contained` |
| Notebook | `notebook=True` returns `<iframe srcdoc="`, size from `figsize`, inner page parses | `..._notebook_mode_returns_isolated_iframe` |
| Empty/edge input | defined behaviour for empty frame, single row | `..._without_edges_draws_isolated_nodes` |

### Added for the d3blocks UI conventions (not in test_flowgraph.py; add them)

```python
@pytest.mark.parametrize('side', [True, False])
@pytest.mark.parametrize('top', [True, False])
def test_<blockname>_panel_flags_are_independent(side, top):
    _, html = _render(_sample_df(), show_side_panel=side, show_top_panel=top)
    SIDE_MARKER = 'id="exportPanel"'   # only inside {% if showSidePanel == 'true' %}
    TOP_MARKER = 'class="top-panel"'   # only inside {% if showTopPanel == 'true' %}
    assert (SIDE_MARKER in html) == side
    assert (TOP_MARKER in html) == top
```

The scaffolded markers are `id="exportPanel"` (only exists inside `{% if showSidePanel == 'true' %}`) and `class="top-panel"` (markup only; the CSS uses `.top-panel`, the JS `'.top-panel'`). Those blocks omit the markup entirely, so the markers are reliable. Also assert:

- `color_background=['#111111', '#fafafa']` -> both hex values appear in the output CSS; default is `['#222222', '#ffffff']`.
- `color_background` does not appear in any `--text` rule.
- Legacy names are gone: `'showControls' not in html`, `'show_stats_panel'` not a parameter (`inspect.signature`).
- Method signature defaults: `show_side_panel=True`, `show_top_panel=True`, `dark_mode=True`.

Parametrised tests that call into the renderer should use `pytest.mark.parametrize` with readable ids. Run `pytest test_<blockname>.py -q`, then the whole suite to confirm nothing else broke (the `set_chart_func` allow-list and import edits touch shared code).

### Browser-free smoke test (run after the pytest file passes)

pytest checks the HTML text; this runs the page's JavaScript. Generate the eight pages, then run `scripts/smoke_jsdom.js`:

```python
import itertools, os
from d3blocks import D3Blocks
os.makedirs('smoke', exist_ok=True)
for side, top, dm in itertools.product([True, False], [True, False], [False, 'auto']):
    d3 = D3Blocks(frame=False, support=None, verbose='error')
    html = d3.<blockname>(df, show_side_panel=side, show_top_panel=top, dark_mode=dm,
                          filepath=None, showfig=False, return_html=True)
    open('smoke/%s_%s_%s.html' % ('side' if side else 'noside', 'top' if top else 'notop', dm), 'w').write(html)
```

```bash
mkdir -p /tmp/jsdom && (cd /tmp/jsdom && npm i jsdom --silent)
NODE_PATH=/tmp/jsdom/node_modules node <skill>/scripts/smoke_jsdom.js smoke --prefix <xx>
```

Per page it fails on any uncaught script error, a missing `theme.js`, a chart script that did not finish, an empty chart svg, a theme button that does not flip the theme, or a panel title that does not toggle. Controls whose panel is not rendered are reported `n/a`, never as failures. The typical failure it catches is a control bound with `getElementById(id).addEventListener(...)` when `show_side_panel=False` removed the element. jsdom stubs (matchMedia, ResizeObserver, SVG `width.baseVal`) are in the script; the chart itself must not need them in a real browser. jsdom has no layout, so also open at least one page in a browser and look at it, or state that you could not.

---

## 2. Streamlit demo

File: `<blockname>_streamlit_demo.py`, in the same folder as `scatter_streamlit_demo.py` and `flowgraph_streamlit_demo.py`. Both existing demos follow one structure; the scaffold reproduces it, so edit the skeleton rather than writing from scratch:

1. Module docstring: what it is, `streamlit run <file>`, and the "API notes (Streamlit 1.56+)" block (`st.iframe`, not `st.html`, explicit pixel height).
2. `# Import your data here`: `@st.cache_data def load_data()` (scatter uses `d3.import_example("cancer")`; flowgraph uses an inline Mermaid string). Keep data small.
3. `st.set_page_config(page_title="D3Blocks - <Name>", layout="wide")`.
4. **All controls in `st.sidebar`**, grouped with `st.sidebar.subheader(...)`: first the chart's own controls (mirror some of its side-panel controls: layout choice, a size/spacing slider, a toggle), then `"D3Blocks UI"` with `show_side_panel` (default `False`, label "Show D3Blocks controls") and `show_top_panel` (default `True`, label "Show D3Blocks top panel"), then `"Display"` with a chart-height slider (400-1200, default 700).
5. `@st.cache_data(show_spinner="Building <name>...") def build_<name>_html(...)`: every sidebar value is a parameter (that is what invalidates the cache); inside, `d3 = D3Blocks()` and `d3.<name>(..., show_side_panel=..., show_top_panel=..., dark_mode=False, color_background="streamlit", filepath=None, showfig=False, return_html=True)`. Unhashable inputs (large frames, lists) are fine for `st.cache_data`; avoid passing the `D3Blocks` object.
6. Main page: `st.caption("Interactive <name> powered by D3Blocks and controlled by Streamlit.")`, then `st.iframe(html, height=height, width="stretch")` (flowgraph wraps it in `if hasattr(st, "iframe")` with a `components.html` fallback + `st.warning`; keep that).

Do not use `components.html` as the primary path, `st.html`, or `height="content"` (the chart is `position: fixed`, so content height collapses).

Run `streamlit run <file>` if streamlit is installed; otherwise `python -m py_compile <file>` and say that it was not run.

---

## 3. Documentation pages

File: `Blockname.rst`, next to `Flowgraph.rst` / `Scatter.rst` (find the docs folder with `find . -name "Flowgraph.rst"`). Open both and mirror the section order and heading style. Typical content (confirm against the real page):

1. Title and one-paragraph description - what data it shows and when to use it.
2. Short "when to use / strengths" notes.
3. Input format: the DataFrame columns and optional `nodes` / property tables, with a tiny example.
4. Quick-start code block that runs as written.
5. Feature sections, each with a short code block (layouts, theming `dark_mode` / `color_background`, panels `show_side_panel` / `show_top_panel`, saving, notebook, Streamlit).
6. Embedded example output, matching how the flowgraph page embeds HTML (generate the example HTML with the documented code into the docs' static folder using the same naming convention).
7. API reference / link to the method docstring (autodoc target `d3blocks.d3blocks.D3Blocks.<blockname>`; copy the directive flowgraph uses).
8. References and links.

Then wire it up:
- Add the page to the toctree / index that lists the other charts, and to any "all charts" overview or gallery.
- Add the chart to the README chart list if one exists.
- Confirm the docs reference the correct public URL pattern: `https://d3blocks.github.io/d3blocks/pages/html/Blockname.html`.
- If a docs build is possible (`sphinx-build` / `make html`), run it and fix warnings for the new page; if not, say so in the final summary.

The docs page, like every other file of the new block, must not mention flowgraph or another existing chart (no "similar to flowgraph" sentences, no copied example names). Write examples so they are copy-paste runnable, import `D3Blocks` as the other chart pages do, and keep the data small.
