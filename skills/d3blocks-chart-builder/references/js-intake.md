# Phase 0: reading the user's JavaScript

The goal is to decide, before touching the repo, (1) what Python hands to the chart, (2) what must be rewritten so the chart fits the d3blocks shell, and (3) which controls go where. Spend the time here; a wrong input schema is expensive to change after tests, demo and docs exist.

## Contents
1. Inventory checklist
2. From inventory to Python input schema
3. Mapping controls to panels
4. Things to rewrite
5. Summary to show the user

## 1. Inventory checklist

Read the file fully and write down:

**Data in**
- Where does data come from? Inline array/object, `d3.csv`/`d3.json`/`fetch`, a global variable? Each of these becomes the JSON payload.
- Exact field names the code reads (`d.source`, `d.value`, `d.x`...). These become DataFrame columns.
- Which fields are required vs optional, and what the code does with missing ones.
- Is the data tabular (rows), relational (edges + nodes), hierarchical (tree), or time-indexed? This decides whether `set_node_properties` / `set_edge_properties` carry real content or one is trivial.

**Dependencies**
- d3 version and modules (`d3.v7`, `d3-sankey`, `d3-force`...), plus any other library (dagre, elk, topojson, lodash...). All must be inlined, pinned, and licence-compatible with GPL3 shipping.
- Any CDN URL, `import ... from 'https://...'`, web font or remote image. All must go.

**Environment assumptions**
- Hard-coded element ids/selectors (`#chart`, `body`), hard-coded `width/height/margin`, `window.innerWidth` use, resize handling.
- Hard-coded colours, fonts and CSS (will conflict with the theme variables).
- Globals, `localStorage` use, `window.onload`, auto-run code at the bottom.

**Interactions**
- Zoom/pan, drag, brush, hover tooltip, click-to-highlight, search, filter, sort, legends, animation, export.
- Any parameters the user can currently change by editing code (radius, strength, scale...) - candidates for side-panel controls and Python kwargs.

## 2. From inventory to Python input schema

Prefer the shapes flowgraph and scatter already use so users see consistency:

- Relational data: `df` with `source`, `target` (+ optional `weight`, `label`, `color`...), optional `nodes` dict/DataFrame keyed by node name. Missing required columns -> `ValueError`.
- Point data: array-likes or columns, with optional per-point properties (`size`, `color`, `tooltip`).
- Hierarchies: parent/child columns or nested dict; say which.

For every field decide: name, type, required/optional, default, validation. Chart *options* (things the JS had as constants) become keyword arguments with defaults, validated in `set_config`, forwarded to JS through the `options` JSON.

If the JS has nodes-like entities, per-entity styling lives in `node_properties`; per-link styling lives in `edge_properties`. Users must be able to edit those and call `d3.show()`.

## 3. Mapping controls to panels

Use the existing vocabulary (see `conventions.md`):

| Panel | Holds | Controlled by |
|---|---|---|
| Side panel (left) | `Export / Save` first, then Layout / Physics / Legend / Stats-style panels specific to the chart | `show_side_panel` (the only switch; no per-subpanel flags) |
| Top panel | Logo, search/Find, Select, Density, **theme button last** | `show_top_panel` |
| Bottom panel | Detail/inspector panels that slide up from the bottom | `show_bottom_panel` |
| Centre | The chart itself | always on |

Anything the chart needs to function must not live exclusively in a panel that can be hidden. If a control matters, give it a Python kwarg equivalent so `show_side_panel=False` users can still set it.

## 4. Things to rewrite

(`template-css-js.md` shows the target shape: the skeleton `d3.blockname.js` already contains the shell; you are porting the chart into its `render()`.)

- Data loading -> read `JSON.parse(document.getElementById('XX-data').textContent)`.
- Options -> `JSON.parse(document.getElementById('XX-options').textContent)`.
- Sizing -> viewport- or `figsize`-based; recompute on resize; subtract top-panel height only if the panel exists.
- Colours -> `var(--text)`, `var(--text-muted)`, `var(--btn-*)` etc.; data colours come from the payload.
- Selectors -> scope under the chart container so the page-level chrome is untouched.
- Auto-run -> an explicit `render()` called after the DOM and theme are ready.
- Library imports -> inlined `<script>` content or Jinja includes.
- Jinja collisions -> any literal `{{`, `{%`, `{#` in the JS.
- Export -> SVG/PNG save buttons via the shared save mechanism, hidden when `save_button=False`.

## 5. Summary to show the user (then wait for go-ahead)

```
Block: <blockname>   (class alias: <Blockname>, JSON prefix: <xx>)
Input: df columns [...required...] + [...optional...]; nodes=<dict|None>
Options -> kwargs: a=..., b=..., c=...
Libraries to inline: d3 v7.x, <others>
To remove/replace: <CDN URLs, fetch, hard-coded colours/sizes>
Controls -> panels: Export/Save (side, top), <Layout> (side), Find + Theme (top), <Detail> (bottom)
Open questions: <at most one>
```
