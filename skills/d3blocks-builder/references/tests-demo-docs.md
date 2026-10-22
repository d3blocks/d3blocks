# Tests, smoke, Streamlit demo, and docs

Derived from `tests/test_flowgraph.py`, the scaffold’s `TEST` / `DEMO` templates, `scripts/smoke_jsdom.js`, `streamlit/scatter_streamlit_demo.py`, and docs pages such as `source/Scatter.rst` / `tests/Flowgraph.rst` (or wherever Phase 1 found them). Re-open those files if anything here seems out of date.

**Flowgraph and scatter are references, not names.** The new block’s tests, demo and docs must not mention flowgraph/scatter or reuse their ids (`fg-*`, etc.). Adapt the patterns below to the chart’s schema and prefix.

## Contents

1. Pytest file (Phase 6)
2. Smoke test with jsdom (Phase 3 gate / Phase 9)
3. Streamlit demo (Phase 7)
4. Sphinx documentation (Phase 8)

---

## 1. Pytest file (Phase 6)

The scaffold writes `test_<name>.py` with helpers and a starter set of tests. Fill the TODOs; keep the helpers.

### Helpers (always)

| Helper | Role |
|--------|------|
| `_sample_df()` | Small valid input for the chart |
| `_data(html)` | Parse `<script type="application/json" id="{prefix}-data">` |
| `_options(html)` | Parse `id="{prefix}-options"` |
| `_render(df, **kwargs)` | `D3Blocks(frame=False, support=None, verbose='error')` → `d3.<name>(..., filepath=None, showfig=False, return_html=True)` → `(d3, html)` |

Use the chart’s real JSON script ids (the 2–3 letter prefix from naming). Tests that assert payload content depend on these parsers.

### Required test categories

Mirror `test_flowgraph.py` categories that apply to every block. Chart-specific cases (layout engines, Mermaid, groups, …) are extra.

| Category | What to assert |
|----------|----------------|
| **Standalone HTML** | `return_html=True` returns a string; main element id present (e.g. `id="{prefix}-svg"`); `_data(html)` is non-empty and matches the sample |
| **Registration** | `D3Blocks(chart='{name}', ...).chart is {Name}` |
| **Input validation** | Missing/wrong columns → `ValueError` (message should name the bad column/value when the module does) |
| **Editable properties + `d3.show()`** | Mutate `d3.node_properties` / `d3.edge_properties` (or chart equivalent), call `d3.show(return_html=True, showfig=False)`, assert the payload reflects the edits |
| **Frame mode** | Default `D3Blocks()` (`frame=True`) still renders; node properties may be a DataFrame |
| **HTML escaping** | Payload and title containing `</script>`, `<b>`, etc. do not appear unescaped in the outer HTML; title is escaped in `<title>` |
| **`dark_mode` flag** | Parametrize `(True, "true")`, `(False, "false")`, `("auto", "auto")`, `("AUTO", "auto")`. Assert `data-dark-mode="..."` and that `<body class="light"` appears only for `"false"`. Theme control present when the top panel is on |
| **`dark_mode` rejection** | Values like `"light"`, `1`, `None`, `"yes"` raise `ValueError` matching `dark_mode` |
| **Self-contained output** | No `<script src="http...">` or `<link href="http...">` (inlined libraries only) |
| **Notebook iframe** | `notebook=True` returns markup with `<iframe srcdoc="...">` and size from `figsize`; inner `srcdoc` (unescaped) still contains the chart id and data |
| **Panel flags** | At least one test (or the smoke suite below) that renders with independent combinations of `show_side_panel` / `show_top_panel` (and `show_bottom_panel` if the chart has a bottom panel). Hidden panels must not leave script errors or require their DOM nodes |

### Conventions

- Prefer `D3Blocks(frame=False, support=None, verbose='error')` in `_render` so tests stay quiet and dict-style properties are easy to edit.
- Do not hard-code another chart’s sample data or assert on `fg-*` ids.
- Run: `pytest tests/test_<name>.py -q` (adjust path from Phase 1). Existing chart tests must still pass.

---

## 2. Smoke test with jsdom (Phase 3 gate / Phase 9)

`scripts/smoke_jsdom.js` is a browser-free wiring check. It does **not** prove layout or looks.

### Prepare HTML pages

Render eight pages (all combinations of `show_side_panel` × `show_top_panel` × `dark_mode` in `{False, 'auto'}` is the skill’s minimum; more is fine) into a directory of `.html` files, e.g.:

```text
smoke_out/
  side1_top1_dark.html
  side1_top1_auto.html
  side1_top0_dark.html
  ...
```

Use `filepath=<path>, showfig=False, return_html=False` (or write the returned HTML) with the chart’s defaults otherwise.

### Run

```bash
# once, in a scratch dir
npm i jsdom
export NODE_PATH="$(pwd)/node_modules"

node path/to/skills/d3blocks-builder/scripts/smoke_jsdom.js smoke_out/ --prefix xx
```

`--prefix` is the chart’s id prefix (e.g. `hf` for heatflow). Required.

### What counts as pass

Per page the script checks:

- No uncaught script errors
- `theme.js` / theme plumbing loaded
- Chart script finished (`window.__d3blocks_chart` or equivalent marker the skeleton sets)
- `#<prefix>-svg` has content
- Where controls exist: theme toggle flips theme, Fit works, Export panel title toggles collapse, search input yields results

Missing panels are **n/a**, not failures: pages with `show_side_panel=False` or `show_top_panel=False` must still run without errors.

jsdom has no layout engine. Say so in the final summary if you could not open a real browser; do not claim the chart looks correct from smoke alone.

---

## 3. Streamlit demo (Phase 7)

Scaffold writes `<name>_streamlit_demo.py` next to the other demos (Phase 1 path; in this tree often `streamlit/`).

### Structure (match scatter / scaffold)

1. Module docstring with run line and Streamlit 1.56+ notes (`st.iframe`, not `st.html`; explicit pixel height or `"stretch"`).
2. `@st.cache_data` `load_data()` — sample DataFrame or `d3.import_example(...)`.
3. `st.set_page_config(..., layout="wide")`.
4. Sidebar:
   - Chart-specific controls (a few real options).
   - **D3Blocks UI**: checkboxes for `show_side_panel` and `show_top_panel`.
   - **Display**: height slider (e.g. 400–1200, default 700).
5. `@st.cache_data` `build_<name>_html(...)` that takes **every** control used as an argument (including the two UI flags), calls:

   ```python
   d3 = D3Blocks()
   html = d3.<name>(
       df,  # or chart-specific args
       show_side_panel=show_side_panel,
       show_top_panel=show_top_panel,
       dark_mode=False,
       color_background="streamlit",
       filepath=None,
       showfig=False,
       return_html=True,
   )
   ```

6. Main page: `st.iframe(html, height=height, width="stretch")` with the scaffold’s `components.html` fallback for Streamlit &lt; 1.56.

### Rules

- Pass UI flags into the cached builder; do not read `st.session_state` inside the cache key path in a way that skips them.
- Prefer `color_background="streamlit"` and `dark_mode=False` so the iframe matches the Streamlit page.
- Do not leave TODOs or flowgraph/scatter sample code in the finished demo.

---

## 4. Sphinx documentation (Phase 8)

### Page location

Phase 1 records where existing chart pages live (e.g. `source/Scatter.rst`, or a `Flowgraph.rst` next to tests/docs). Add `Blockname.rst` (capitalized name) in the same place.

### Page structure (mirror Scatter / Flowgraph)

Typical sections:

1. Title (`Blockname` / `#############`).
2. `.. automethod:: d3blocks.d3blocks.D3Blocks.<blockname>` so the public method docstring is the API reference.
3. Short intro / strengths (what the chart shows; keep factual).
4. **Input Data** — required columns or argument shape, optional attributes (`nodes`, `groups`, …).
5. One or more **runnable examples** (`.. code:: python`) that match the method docstring examples.
6. Optional embedded preview:

   ```rst
   .. raw:: html

       <iframe src="..." height="600px" width="700px" frameBorder="0"></iframe>
   ```

   Generate any local example HTML the page embeds the same way other charts do (do not invent a hosting URL).

7. Chart-specific sections only if the chart has them (encodings, layouts, etc.).

### Index / toctree

Add the page under the **Blocks** (or equivalent) toctree in `index.rst` (or the project’s docs index), alphabetically or in the same order style as neighbouring charts. Do not leave the page orphaned.

### Packaging note

Docs are separate from the wheel, but example HTML linked from docs must still be produced by the real API so they stay in sync with tests.

---

## Quick checklist (Phases 6–8)

- [ ] `test_<name>.py` helpers use the chart’s prefix; TODOs filled
- [ ] Registration, validation, editable properties, frame mode, escaping, dark_mode, self-contained, notebook covered
- [ ] `pytest tests/test_<name>.py -q` green; existing tests still green
- [ ] Eight (or more) HTML pages smoke-tested with `smoke_jsdom.js --prefix <prefix>`
- [ ] Streamlit demo: real data, UI checkboxes, cached builder, `st.iframe`
- [ ] `Blockname.rst` present, automethod + examples, linked from index toctree
