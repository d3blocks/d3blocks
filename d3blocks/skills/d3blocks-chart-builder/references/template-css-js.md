# Template, CSS and JS anatomy

Derived from `flowgraph.html.j2`, `flowgraph.css`, `d3.flowgraph.js`, `scatter.html.j2` and `scatter.css`. The scaffold copies `assets/blockname.html.j2`, `assets/blockname.css` and `assets/d3.blockname.js`, which implement everything below. When the repo's current flowgraph files differ from the assets, the repo wins; update the new chart to match.

## Contents
1. File naming
2. Template (`<name>.html.j2`)
3. CSS (`<name>.css`)
4. JavaScript (`d3.<name>.js`)
5. Flowgraph vs scatter: why flowgraph is the model
6. Panel-independence rules (conventions section 10)

## 1. File naming

| File | Name | Notes |
|---|---|---|
| Template | `<name>.html.j2` | Loaded by `template_env(__name__, __file__).get_template('<name>.html.j2')` |
| Stylesheet | `<name>.css` | `{% include "<name>.css" %}` |
| Chart JS | `d3.<name>.js` | `{% include "d3.<name>.js" %}` (the `d3.` prefix is the convention; an upload may show `d3_<name>.js` because dots get sanitised) |
| Shared, not copied | `theme.js`, `d3.v7.min.js`, `dagre.min.js`, `elk.bundled.js`, `walkthrough.js/.css` | Included by bare filename, so the Jinja loader must search both the chart's `d3js/` and the shared `d3js/`. Open `_shared/__init__.py` (`template_env`) and check where each lives before assuming. |

Library files are inlined (`<script>{% include "d3.v7.min.js" %}</script>`), which is why output is self-contained. Optional heavy libraries are included conditionally: `{% if layout == 'elk' %}<script>{% include "elk.bundled.js" %}</script>{% endif %}`.

## 2. Template

Order in `flowgraph.html.j2`, which the asset keeps:

1. `<title>{{ TITLE }}</title>` then `{{ SUPPORT }}` in `<head>`.
2. `<style>{% include "<name>.css" %}</style>`, then **a second `<style>` that sets the backgrounds after the main stylesheet** so it wins over the theme defaults:
   ```css
   body { background: {{ COLOR_BACKGROUND_DARK }}; --bg: {{ COLOR_BACKGROUND_DARK }}; }
   body .top-panel, body .stats-panel { background: {{ COLOR_BACKGROUND_DARK }}; }
   body.light { background: {{ COLOR_BACKGROUND_LIGHT }}; --bg: {{ COLOR_BACKGROUND_LIGHT }}; }
   body.light .top-panel, body.light .stats-panel { background: {{ COLOR_BACKGROUND_LIGHT }}; }
   ```
   Flowgraph also sets `--bg` because its edge-label boxes fill with `var(--bg)`. Keep that only if the chart uses `--bg` for knock-out fills; it is still a background surface, not a text/axis colour.
3. Library scripts in `<head>`.
4. `<body{% if darkMode == 'false' %} class="light"{% endif %} data-dark-mode="{{ darkMode }}">` followed immediately by `<script>{% include "theme.js" %}</script>`. `theme.js` reads `data-dark-mode` (`true|false|auto`) and applies the theme before first paint; it exposes `D3BlocksTheme.bind('themeBtn')`. Do not write a second theme implementation.
5. Chart container (`<div id="XX-main"><svg id="XX-svg" role="img" aria-label="{{ TITLE }}"></svg></div>`) and tooltip div.
6. `{% if showTopPanel == 'true' %} ... {% endif %}`: a `.top-panel` with `top-panel-left` (logo), `top-panel-center` (search), `top-panel-right` (controls, **theme button last**).
7. `{% if showSidePanel == 'true' %} ... {% endif %}`: `.stats-panel collapsed` blocks, **`exportPanel` first**. Export buttons are wrapped in `{{ SAVE_BUTTON_START }} ... {{ SAVE_BUTTON_STOP }}` (renders `<!-- -->` when `save_button=False`). Panel markup: `.stats-panel-title` (with the chevron svg) + `.stats-panel-body`.
8. Data and options at the end: `<script type="application/json" id="XX-data">{{ json_data }}</script>`, `id="XX-options"`, then `<script>{% include "d3.<name>.js" %}</script>`.

Notes:
- `{{ json_data }}` and `{{ options }}` are emitted as-is (no `|safe`, no `|tojson`): Python already ran `json.dumps(...).replace('</', '<\\/')`. Escaping happens in Python, once.
- The panels are removed from the markup (not hidden with CSS) when the flag is `'false'`, which is what the panel-flag tests assert on.
- Scatter's template passes extra values (`WIDTH`, `HEIGHT`, `MIN_X`...) straight into inline JS. Prefer flowgraph's JSON options object over scattering Jinja values through JS.

## 3. CSS

`flowgraph.css` = **shared theme/panel block** (lines 1-225: `:root` and `body.light` variables, `.search-*`, `.stats-panel*`, `.button-switch`, `.top-panel*`, `.top-search*`) + **chart section** (`#fg-*`, `.fg-*`). The same shared block exists in `scatter.css` and `tree.css`, so charts look and behave alike. Keep the shared block byte-identical (it carries the conventions: light-mode `box-shadow: none`, `.top-search { margin-bottom: 0 }`, `.top-search .search-input { padding: 6px 12px; font-size: 1em }`, grid top bar with `pointer-events: none` and children `auto`). Put chart rules after it, prefixed with the chart's 2-3 letter prefix so selectors cannot clash.

Rules for chart CSS: colours of text/chrome come only from the variables (`--text`, `--text-muted`, `--btn-*`, `--panel-*`, `--accent`); per-element data colours come from the payload (flowgraph passes `--c` per node). Chart controls inside panels reuse `.button-switch`, `.physics-control` (slider rows) and a prefixed button-row/section-label/hint set. Dropdowns must look like the other charts' dropdowns (scatter.css "Panel dropdowns" block), not native OS selects.

## 4. JavaScript

`d3.flowgraph.js` is one IIFE. The shell parts (all in the asset) are reusable verbatim:

| Pattern | Why |
|---|---|
| `DATA = JSON.parse(getElementById('XX-data').textContent)`, same for `OPTS` | Only channel from Python; tests parse the same tags |
| `on(id, ev, fn)` null-safe binder, plus `querySelectorAll('[data-...]')` for button groups | Controls live in panels that may not exist; `getElementById(...).addEventListener` would throw and kill the chart |
| `viewportInsets()` with `bar ? bar.getBoundingClientRect().bottom + 12 : 16` and `max` over visible `.stats-panel` rects | Fit/zoom must work with any panel combination; absent top bar = height 0, never an early `return` |
| `setupPanels()` stacks `.stats-panel` under the top bar (`y = (bar ? bottom : 0) + 8`), toggles `collapsed` on title click, `ResizeObserver` + `resize` repositions | Works with zero panels (empty NodeList) |
| `D3BlocksTheme.bind('themeBtn')` | Runtime toggle; `bind` must tolerate a missing button (top bar off) - confirm in `theme.js` |
| `setupSearch()` starts with `if (!input \|\| !results) return;` | Same reason |
| Export: `serializeSvg` (inline computed styles, background rect from `body` colour), `download`, `saveSvg`, `savePng` (2x canvas), `exportJson` | Copy; adapt the viewport class and the JSON payload |
| Empty state: `.XX-empty` message and `return` | `D3Blocks` with no data must not render a blank page |
| `window.__<name>` debug handle (`state`, `fit`, ...) | Handy for manual checks |

Flowgraph-specific code you do not copy: layout (dagre/ELK), shapes, trace/walkthrough, edge animation, highlight/pinning. Reuse the **walkthrough** (`walkthrough.js/.css`, `steps=` parameter, `normalize_steps`) only if the chart genuinely has a step-through story.

`legendPanel` shows the pattern for a panel the JS may *hide itself*: `if (!panel || !list) return;` and `panel.style.display = 'none'` when empty - `setupPanels` already skips `display: none` panels.

## 5. Flowgraph vs scatter: why flowgraph is the model

| | scatter | flowgraph |
|---|---|---|
| Theme toggle | hand-written in the template (`toggleTheme`, `themeBtn` wiring inline) | shared `theme.js` + `D3BlocksTheme.bind`; supports `dark_mode='auto'` |
| `dark_mode` | `'true' if dark_mode else 'false'` | `check_dark_mode` / `dark_mode_flag`, rejects invalid values |
| Body markup | `<body class="light">` only | also `data-dark-mode="..."`, which tests and `theme.js` rely on |
| Template loading | `Environment(PackageLoader(...))` | `template_env(__name__, __file__)` |
| JS | one huge inline script in the template | separate `d3.<name>.js`, included |
| Data in | `var jsonData = {{ json_data }};` | `<script type="application/json">` |

Scatter remains the reference for **panel look and the shared flags**; do not copy its theme code or inline-JS style.

## 6. Panel-independence rules (conventions section 10)

Verify by rendering all four `show_side_panel` x `show_top_panel` combinations (the scaffolded `test_<name>_panel_flags_are_independent` checks the markup) and opening each in a browser:

- `show_top_panel=True, show_side_panel=False`: Find, Fit, theme and any other top-bar control work; nothing references an element that only exists in the side panel.
- `show_side_panel=True, show_top_panel=False`: panels stack from the top (`y` starts at 8); fit leaves 16px at the top.
- both `False`: chart still renders, pans and zooms; export is unavailable by design; the Python kwargs remain the way to configure it.
- If the chart has a bottom panel (`show_bottom_panel`): with it `False` the centre chart behaves as before, and `viewportInsets().bottom` does not reserve space for it.
- Controls that change chart state must have a Python kwarg equivalent so users without a side panel can set them.
