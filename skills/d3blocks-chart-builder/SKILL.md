---
name: d3blocks-chart-builder
description: Turn a JavaScript (.js) d3 chart into a fully integrated d3blocks block - chart folder with __init__.py, Blockname.py and d3js/ assets, a new method in d3blocks.py, themed top/side panels per the d3blocks UI conventions, a pytest file modelled on test_flowgraph.py, a Streamlit demo, and Sphinx docs modelled on Flowgraph.rst/Scatter.rst. Use this whenever the user provides a .js file (or d3 snippet) and asks to create, add, port, wrap or integrate a "block", "chart" or "d3blocks chart", or says things like "make this a d3blocks block", "add a new chart to d3blocks", or "align this chart with the scatter/flowgraph conventions" - even if they only mention one of the deliverables (tests, demo, docs, theme).
metadata:
  author: Erdogan Taskesen
  version: "1.0.1"
---

# d3blocks chart builder

Turn a user-supplied `.js` chart into a block that behaves exactly like the existing ones (flowgraph is the reference implementation; scatter is the reference for panel conventions). "Integrated" means all six deliverables below exist and pass their checks. A chart that renders but is missing the `d3blocks.py` method, the theme plumbing, tests, demo or docs is not done.

## Ground rules

- **Read before writing.** The repo is the source of truth; this skill describes patterns, but file contents drift. Before generating anything, open the real files named in each step (flowgraph's `.html.j2`, `_shared/`, `utils.py`, the docs page, the existing demo). Never invent a helper's signature.
- **Copy flowgraph's structure, not scatter's, where they differ.** Flowgraph is the newer pattern: `template_env(__name__, __file__)` instead of `Environment(PackageLoader(...))`, `check_dark_mode` / `dark_mode_flag` (supports `'auto'`) instead of a bare bool, the shared `theme.js` instead of a theme toggle written inline in the template, data via `<script type="application/json">` tags instead of `var jsonData = {{ json_data }}`, and the chart JS in its own included file. `references/template-css-js.md` has the full comparison.
- **Surgical changes.** `d3blocks.py` is ~4800 lines. Add to it; do not reformat or reorder it.
- **Preserve line endings.** The existing `.py` / `.md` files use CRLF. Match the file you edit, and check with `file <path>` before and after.
- **Flowgraph and scatter are references, not names.** The deliverable is a new folder `d3blocks/<name>/` inside the package (next to `flowgraph/`, `scatter/`, ...). Study the existing charts, but nothing you create or edit for the new block may mention flowgraph or another existing chart, or reuse its identifiers (`fg-*` ids/classes, `Flowgraph`, `d3.flowgraph.js`, "like flowgraph" comments, test or docs text). Rename anything you carry over. `scripts/scaffold_chart.py --check` finds leaks; run it in Phase 9.
- **Name once, derive the rest.** Pick `blockname` (lowercase, single word, not an existing chart's name; the examples below use the made-up name `heatflow`). Everything derives from it - see "Naming".

## Naming (get this right first; it is the most common source of breakage)

`d3blocks.py` resolves a chart with `str.capitalize(chart)` and then `eval(...)` on the result, so the **import alias must equal `blockname.capitalize()`**. `str.capitalize` lowercases everything after the first letter.

| What | Value for `blockname = "heatflow"` |
|---|---|
| Folder | `d3blocks/heatflow/` |
| Module file | `Heatflow.py` |
| Import alias in `d3blocks.py` | `Heatflow` |
| Public method | `def heatflow(self, ...)` |
| `config['chart']` | `'heatflow'` or `'Heatflow'` - match what Flowgraph does |
| Template / CSS / JS | `d3js/heatflow.html.j2`, `d3js/heatflow.css`, `d3js/d3.heatflow.js` |
| JSON script ids | `hf-data`, `hf-options` (pick a 2-3 letter prefix; tests rely on it) |
| Test | `test_heatflow.py` |
| Demo | `heatflow_streamlit_demo.py` |
| Docs | `Heatflow.rst` |

If the user wants a camel-case name (`HeatFlow`), tell them it collapses to `Heatflow` internally.

## The plan

Work through these phases in order. Each ends with a gate; do not start the next phase until the gate holds. Use `scripts/scaffold_chart.py` in phase 2 to create the boilerplate deterministically.

### Phase 0 - Intake the JavaScript

Read `references/js-intake.md`. In short: read the `.js` file end to end and write down (a) the data shape it consumes, (b) the libraries it needs, (c) hard-coded DOM ids / sizes / colours / CDN URLs / `fetch` calls, (d) the interactions it offers. From that, propose the Python input schema (DataFrame columns, optional `nodes`/`groups`-style attributes) and the list of controls and which panel each belongs in.

Gate: show the user a short summary (input schema, controls -> panels, libraries to inline, anything you will have to remove) and get a go-ahead. If the input format is genuinely ambiguous, ask one question; otherwise state your assumption and continue.

### Phase 1 - Locate the reference files

Run `find . -name "Flowgraph.py" -o -name "flowgraph.html.j2" -o -name "test_flowgraph.py" -o -name "Flowgraph.rst" -o -name "scatter_streamlit_demo.py" -o -name "_shared" -o -name "utils.py"` and open the ones you will mirror. Record the real paths for tests, demos and docs; the scaffold script takes them as arguments.

### Phase 2 - Chart folder (deliverable 1)

Run the scaffold, then fill it in:

```bash
python scripts/scaffold_chart.py --name blockname --prefix bn \
    --pkg-dir <dir containing flowgraph/> \
    --tests-dir <dir containing test_flowgraph.py> \
    --demo-dir <dir containing scatter_streamlit_demo.py>
```

The folder must end up as:

```
d3blocks/blockname/
├── __init__.py          # copy what flowgraph/__init__.py does (the markdown rendering of "__init__" often shows as **init**)
├── Blockname.py         # set_config, set_node_properties, set_edge_properties, show, write_html, notebook_iframe
└── d3js/
    ├── blockname.html.j2    # from assets/: top panel, Export/Save-first side panel, theme.js, backgrounds, JSON data tags
    ├── blockname.css        # from assets/: the shared theme/panel block (byte-identical across charts) + a prefixed chart section
    └── d3.blockname.js      # from assets/: data/options, null-safe controls, panels, theme, search, export; render() is the TODO
```

The scaffold writes all three `d3js/` files from `assets/` (tokens `__NAME__` / `__PREFIX__` replaced). They already implement the shell that the conventions require, so phase 3 is about the chart itself. The template includes `theme.js` and `d3.v7.min.js` from `_shared/d3js/` by bare name: `template_env` searches the chart's own `d3js/` first, then `_shared/d3js/` (see `references/python-contract.md` section 4). Import `notebook_iframe` from `_shared`; do not write a local copy. The scaffold refuses names and prefixes that belong to existing charts and refuses to overwrite an existing chart folder.

Read `references/python-contract.md` for the module contract (what `d3blocks.py` calls, config keys, template keys). Implement the data layer: validate input (raise `ValueError` with a message naming the bad column/value), build the JSON payload, `json.dumps(...).replace('</', '<\\/')` it, `html_escape` the title.

Gate: `d3js/` contains the three generated files with no leftover `__NAME__`/`__PREFIX__`; `python -c "from d3blocks.blockname import Blockname"` imports and `Blockname.set_config({})` returns a dict containing every key in the contract.

### Phase 3 - Port the user's JavaScript into `d3.blockname.js`

Read `references/template-css-js.md` first (what each file contains and why). Implement the chart inside the skeleton's `render()`, keeping its shell code (null-safe `on()`, `viewportInsets`, `setupPanels`, theme bind, search, export). Apply the findings from phase 0:

- Replace hard-coded DOM ids with the template's ids; read data from `<script type="application/json" id="XX-data">` and options from `id="XX-options"` (tests parse these). Add chart-specific side panels to the template (same `.stats-panel collapsed` markup, after `exportPanel`) and top-bar controls (before the theme button).
- Bind every control through `on(id, ...)` or `querySelectorAll`, never `getElementById(id).addEventListener`: the panel may not exist.
- Inline every library the chart needs, the way flowgraph inlines dagre/d3. The output HTML must be self-contained: no `<script src="http...">`, no `<link href="http...">`. Heavy optional libraries (flowgraph's ELK) are included only when the option that needs them is selected.
- Replace hard-coded colours with the theme CSS variables (`--text`, `--text-muted`, `--btn-*`, ...). Remove any `fetch`, CDN import and global `localStorage` assumptions.
- Jinja collides with JS: the JS is pulled in with `{% include %}`, so Jinja parses it. A literal `{{`, `{%` or `{#` in the chart JS (for example in a template string) will break rendering; wrap that part in `{% raw %}...{% endraw %}` or split the sequence.
- Size from the viewport (or `figsize` when given); never `return` early from layout code because `.top-panel` is absent - treat its height as 0 (the skeleton's `viewportInsets` and `setupPanels` already do).
- Reuse `theme.js` for dark/light/auto. Do not write a second theme implementation (scatter has one inline; do not copy it).
- Keep the shared block at the top of the CSS untouched; add chart rules below it with the chart's prefix.

Gate: render with defaults - no external requests - then run the browser-free smoke test (`scripts/smoke_jsdom.js`, described in `references/tests-demo-docs.md`) over the eight pages from `show_side_panel` x `show_top_panel` x `dark_mode` in `{False, 'auto'}`: no script errors, the chart script finishes, theme toggle / Fit / panel collapse / search work where their panel exists. jsdom has no layout, so it proves wiring, not looks: if you cannot open a real browser, say so in the final summary and do not claim the chart looks right.

### Phase 4 - Apply the UI conventions (deliverable 3)

Read `references/conventions.md` in full and apply every numbered section to the new template and config. It is the spec, not a suggestion. The scaffolded template and CSS already implement sections 1-7 (Export / Save first, independent `{% if showSidePanel %}` / `{% if showTopPanel %}` blocks, `dark_mode` via `theme.js`, `[dark, light]` backgrounds on exactly three surfaces, light-mode top bar without shadow, aligned top-bar controls with the theme button last) - verify them rather than re-deriving them, and apply them to any chart-specific panels and controls you add. The checks that most often fail:

1. Side panel order: `Export / Save` first (top), then chart-specific panels.
2. `show_side_panel`, `show_top_panel` (and `show_bottom_panel` if the chart has a bottom panel) work **independently**. Test all four side x top combinations, plus bottom on/off. Top-bar controls must still work with the side panel hidden; the chart must still work with the bottom panel hidden.
3. `dark_mode` is `True | False | 'auto'` and the theme button is the last control on the right of the top bar.
4. `color_background=[dark_hex, light_hex]` via `resolve_color_background`, applied to exactly three surfaces (body, `.top-panel`, `.stats-panel`) and nothing else. No overriding of `--text` etc.
5. Light mode: `body.light .top-panel { box-shadow: none; }`.
6. Top-bar controls share one vertical alignment (search wrap margin-bottom 0, inputs match `.button-switch` padding/font-size); dropdowns look the same as the Layout dropdowns.

Gate: the smoke test passes for every flag combination (section 10 of the conventions: top-bar controls work with the side panel hidden; the centre chart works with the bottom panel hidden), and `references/conventions.md` is satisfied point by point.

### Phase 5 - Register in d3blocks.py (deliverable 2)

Read the registration section of `references/python-contract.md`. Four edits, all required:

1. Add the import to **both** import blocks at the top (the `d3blocks.<name>.<Name>` one and the "DEBUG ONLY" fallback).
2. Add `def blockname(self, ...)` next to the other chart methods. Mirror an existing chart method (flowgraph's is the reference): `self._clean(...)` -> `self.chart = set_chart_func('Blockname', logger)` -> `self.config = self.chart.set_config(...)` -> `self.set_node_properties(...)` -> `self.set_edge_properties(...)` -> `html = self.show()` -> `if return_html: return html`. Signature must include `title`, `filepath`, `figsize`, `showfig`, `overwrite`, `notebook`, `save_button`, `show_side_panel`, `show_top_panel`, `dark_mode`, `color_background`, `return_html`, `reset_properties` with the documented defaults.
3. Add `'Blockname'` to the allow-list inside `set_chart_func`.
4. If the chart has no node concept, add it to the `['Violin', 'Scatter']` special case in `set_edge_properties` (otherwise "Set the node_properties first" is raised).

Write the numpydoc docstring like flowgraph's: parameters (document `show_side_panel`, `show_top_panel`, `dark_mode` with the True/False/'auto' bullets, `color_background`), Returns (`d3.node_properties`, `d3.edge_properties`, `d3.config`), Examples (runnable `>>>` snippets), References (including the docs URL `https://d3blocks.github.io/d3blocks/pages/html/Blockname.html`).

Gate: `D3Blocks(chart='blockname')` gives `d3.chart is Blockname`, and `D3Blocks().blockname(df, filepath=None, showfig=False, return_html=True)` returns HTML.

### Phase 6 - Tests (deliverable 4)

Read `references/tests-demo-docs.md`, then fill in the generated `test_blockname.py`. Mirror `test_flowgraph.py`: helpers `_sample_df`, `_data`, `_options`, `_render`; the same test categories (standalone HTML, registration, editable properties + `d3.show()`, frame mode, HTML escaping, input validation, `dark_mode` parametrisation and rejection, self-contained output, notebook iframe) plus panel-flag tests. Run `pytest <test file> -q` and fix until green.

### Phase 7 - Streamlit demo (deliverable 5)

Edit the scaffolded `blockname_streamlit_demo.py` (same folder as `scatter_streamlit_demo.py` / `flowgraph_streamlit_demo.py`), following sections 8-9 of the conventions. Both existing demos share one structure, which the skeleton reproduces: module docstring with the API notes, "Import your data here", `st.set_page_config(layout="wide")`, sidebar subheaders (chart controls, **D3Blocks UI** with the two checkboxes, **Display** with a height slider), a `@st.cache_data` `build_<name>_html(...)` that calls `D3Blocks().<name>(..., dark_mode=False, color_background="streamlit", filepath=None, showfig=False, return_html=True)`, then `st.iframe(html, height=height, width="stretch")` with flowgraph's `components.html` fallback for Streamlit < 1.56. Replace the TODOs with real data and a handful of the chart's own controls, passing every control into the cached builder as an argument.

### Phase 8 - Documentation (deliverable 6)

Read `references/tests-demo-docs.md` (docs section). Open `Flowgraph.rst` (and `Scatter.rst`) and mirror their structure for `Blockname.rst`: intro, parameters/API via the method docstring, runnable examples, embedded example outputs, links. Add the page to whatever index/toctree lists the other charts. Generate any example HTML the page embeds, the same way the flowgraph page does.

### Phase 9 - Final verification

Run `python scripts/scaffold_chart.py --check --name blockname --prefix xx --pkg-dir ... --tests-dir ... --demo-dir ...`, then the checklist at the bottom of this file, then summarise for the user: files created, files edited (with the exact functions touched in `d3blocks.py`), test result, and anything you could not verify (for example, a docs build you could not run).

## Bundled files

- `scripts/scaffold_chart.py` - writes the Python module, `__init__.py`, the three `d3js/` files (from `assets/`), the test skeleton and the Streamlit demo skeleton; prints the `d3blocks.py` edits. `--check` scans the finished block for leaked reference names and prefixes.
- `scripts/smoke_jsdom.js` - browser-free smoke test of rendered pages (needs `npm i jsdom`).
- `assets/blockname.html.j2`, `assets/blockname.css`, `assets/d3.blockname.js` - the template, shared CSS block and JS shell, derived from flowgraph's.
- `references/python-contract.md` - module API, config/template keys, `d3blocks.py` registration.
- `references/template-css-js.md` - anatomy of the template, CSS and JS, flowgraph vs scatter, panel-independence rules.
- `references/js-intake.md` - how to analyse the user's `.js` before building.
- `references/conventions.md` - the UI conventions spec (verbatim).
- `references/tests-demo-docs.md` - test categories, Streamlit demo structure, documentation pages.

## Packaging and housekeeping (easy to forget)

- New `d3js/` files must ship in the wheel: check `setup.py` / `pyproject.toml` `package_data` / `MANIFEST.in` to see how flowgraph's `d3js/*` is included, and add the new folder the same way.
- Add the chart to any chart list in the README, the docs index and the `D3Blocks` class docs; check the changelog/version convention.
- If `utils.convert_dataframe_dict` or other `utils.py` helpers branch on chart name, check whether the new chart needs an entry.

## Final checklist

- [ ] Folder has `__init__.py`, `Blockname.py`, `d3js/` with every `.js`/`.css`/`.j2` the template includes
- [ ] Import alias == `blockname.capitalize()`; imported in both blocks; in `set_chart_func` allow-list
- [ ] `d3.blockname(...)` works with defaults and with `return_html=True, filepath=None, showfig=False`
- [ ] `set_config` exposes `show_side_panel`, `show_top_panel`, `dark_mode`, `color_background`, `save_button`, `notebook`, `figsize`, `title`, `filepath`, `showfig`, `overwrite`, `reset_properties`
- [ ] Template receives `COLOR_BACKGROUND_DARK/LIGHT`, `darkMode`, `showSidePanel`, `showTopPanel` as strings
- [ ] No `show_controls` / `showControls` / `show_stats_panel` / `show_node_panel` left anywhere
- [ ] `python scripts/scaffold_chart.py --check ...` reports 0 leaks (no mention of flowgraph or another existing chart, no `fg-` ids/classes) and the new block lives in `d3blocks/<name>/`
- [ ] `scripts/smoke_jsdom.js` passes for all eight flag/theme combinations
- [ ] `notebook_iframe` is imported from `_shared`, not copied
- [ ] Output has no external `http(s)` script/link references
- [ ] Title and data payload are escaped (`</script>` test passes)
- [ ] Side/top/bottom panel flags are independent (all combinations tried)
- [ ] `pytest` for the new block passes; existing chart tests still pass
- [ ] Streamlit demo runs and uses `st.iframe`
- [ ] Docs page exists, is linked from the index, examples run
- [ ] Packaging includes `d3js/*`; line endings match the repo
