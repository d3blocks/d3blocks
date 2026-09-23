# UI conventions (prompt for aligning other charts)

Use this document as an input prompt to align other d3blocks charts with the scatter chart conventions.

---

**Align this chart’s UI and config with the scatter chart conventions in d3blocks.**

### 1. Name convention panels
  - Change the variable **`show_controls`** into **`show_side_panel`**
  - Change `showControls` into `showSidePanel` when passing arguments using jinja. Match the variable name in the required files, among them `.html.j2`
  - If the side panel is named `Export`, rename it to `Export /Save`
  - Move the `Export /Save` above all other panels and thus at the top.

### 2. Panel visibility (independent flags)

- Add **`show_side_panel: bool = True`**: show/hide the **left side panels** only (Export, Layout, Physics, etc.). Use Jinja `{% if showSidePanel == 'true' %}…{% endif %}` around the side-panel markup (same pattern as scatter).
- Add **`show_top_panel: bool = True`**: show/hide the **top bar** only. Wrap the top-panel markup independently.
- Controls for sub-sidepanels like `show_stats_panel`, should be removed. The `show_side_panel` should be the only control for the **side panel**.
- Panels that move from the bottom upwards (like `show_node_panel`) should be renamed into `show_bottom_panel`.
- Wire both through `set_config` → template as `'true'`/`'false'` strings.
- When the top bar is missing, layout JS must treat its height as **0** (do not `return` early from positioning if `.top-panel` is absent).
- Document both parameters on the public chart method.

### 3. Theme: `dark_mode`

- Add **`dark_mode: bool = True`**.
- `dark_mode=True` → dark theme (default body, no `light` class).
- `dark_mode=False` → light theme (`<body class="light">`).
- Theme toggle (if present) still switches at runtime; initial state follows `dark_mode`.
- Text, axis, buttons, and chrome follow the theme CSS variables (`--text`, `--btn-*`, etc.).

### 4. Backgrounds: `color_background` as `[dark, light]`

- Change **`color_background`** to a **list of two hex colors**`[dark_hex, light_hex]`  by using `resolve_color_background` from `utils.py`
- Apply **only** to these three surfaces (not fonts, axis, or button text colors):
  1. Page / plot center (`body` background)
  2. Top panel (`.top-panel`)
  3. Side panels (`.stats-panel`)
- CSS pattern (after including the main stylesheet so it wins over theme defaults):

```css
body { background: {{ COLOR_BACKGROUND_DARK }}; }
body .top-panel { background: {{ COLOR_BACKGROUND_DARK }}; }
body .stats-panel { background: {{ COLOR_BACKGROUND_DARK }}; }
body.light { background: {{ COLOR_BACKGROUND_LIGHT }}; }
body.light .top-panel { background: {{ COLOR_BACKGROUND_LIGHT }}; }
body.light .stats-panel { background: {{ COLOR_BACKGROUND_LIGHT }}; }
```

- Switching theme (or the UI toggle) automatically picks the matching list entry.
- Do **not** override `--text`, `--text-muted`, axis colors, or button label colors for custom backgrounds.

### 5. Light-mode top bar polish

- In light mode, **remove the top-panel drop shadow** (`body.light .top-panel { box-shadow: none; }`) so a white/light bar does not sit under a dark shadow.

### 6. Top-panel control alignment

- Right-side controls (search / Find, Select, Density, Theme, etc.) must share the **same vertical alignment**.
- Search/Find often misaligns because of side-panel styles like `.search-wrap { margin-bottom: 6px }` and taller input padding. In the top bar:
  - Zero out bottom margin on the top search wrap.
  - Match input **padding** and **font-size** to `.button-switch` (e.g. `padding: 6px 12px`, `font-size: 1em`).
- Put the **theme (dark/light) button last** on the right: e.g. Find → Select → Density → **Theme**.


- Filtering (and any other) dropdowns must not keep a different native/OS look than Layout.

### 7. Config / template plumbing

- Resolve and pass config in `set_config` / `write_html` (or equivalent).
- Template keys for backgrounds: `COLOR_BACKGROUND_DARK`, `COLOR_BACKGROUND_LIGHT`.
- Template keys for flags: `showSidePanel`, `showTopPanel`, `darkMode` as `'true'`/`'false'`.
- Public API defaults: `show_side_panel=True`, `show_top_panel=True`, `dark_mode=True`, `color_background=[_DEFAULT_BG_DARK, _DEFAULT_BG_LIGHT]`.

### 8. Streamlit embedding (if relevant)

- Prefer **`st.iframe(html, height=700)`** (not deprecated `components.html`; not `st.html` for full interactive charts).
- Pass a **fixed pixel height** (or `"stretch"`); avoid `height="content"` when the chart uses `position: fixed` (content height may collapse).
- Generate with `showfig=False`, `return_html=True`.

### 9. Streamlit example

- Create a minimal streamlit example similar to that of `scatter_streamlit_demo.py` (streamlit folder).
- Match the side panel with some of controls of the chart.
- Put all controls to the streamlit side panel.
- store the file in the folder with `<NAME_CHART>_streamlit_demo.py`

### 10. Top Panel controls
- Make sure the controls in the open panels keep working when other panels are disabled: `show_top_panel=True` and `show_side_panel=False` must keep the controls in the top panel working. When `show_bottom_panel=False` the center chart must keep working as intended.

### 11. Constraints

- Surgical changes only; match existing chart style.
- Side panels and top panel visibility must work **independently**.
- Custom backgrounds must **not** restyle fonts or axes—only the three background surfaces, per dark/light list entry.
