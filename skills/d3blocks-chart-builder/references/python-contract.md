# Python contract for a block

Derived from `flowgraph/Flowgraph.py`, `scatter/Scatter.py`, `_shared/__init__.py` and `d3blocks.py`. Re-open those files if anything here seems out of date.

**Flowgraph and scatter are references, not names.** The new block is a folder `d3blocks/<name>/` with its own name, ids, classes and wording. Nothing in it (code, comments, docstrings, tests, demo, docs) may mention flowgraph or reuse its identifiers (`fg-*`, `Flowgraph`). `scripts/scaffold_chart.py --check` scans for leaks.

## Contents
1. What `d3blocks.py` calls on your module
2. `set_config` keys
3. `write_html` template keys
4. Imports and fallbacks
5. Registration in `d3blocks.py` (four edits)
6. Public method skeleton
7. Gotchas

## 1. What `d3blocks.py` calls on your module

`D3Blocks` stores your module as `self.chart` and calls these module-level functions:

| Called from | Call | Notes |
|---|---|---|
| `D3Blocks.__init__` -> `set_config()` | `chart.set_config(self.config, logger=logger)` | Must work with **no** kwargs (defaults only) |
| `D3Blocks.<blockname>()` | `chart.set_config(config=self.config, font=..., title=..., ...)` | All public args forwarded as kwargs |
| `D3Blocks.set_node_properties(*a, **kw)` | `chart.set_node_properties(*a, **kw)` | Result passes through `utils.convert_dataframe_dict(labels, frame=..., logger=...)` |
| `D3Blocks.set_edge_properties(*a, **kw)` | `chart.set_edge_properties(*a, config=self.config, node_properties=self.node_properties, **kw)` | Stored as `self.edge_properties` |
| `D3Blocks.show(**kw)` | `chart.show(self.edge_properties, config=self.config, node_properties=self.node_properties, logger=logger, **kw)` | Must return the HTML string |

So `show(df, **kwargs)` receives the **edge-properties frame as `df`**. In `show`, start with `config = update_config(kwargs, logger).copy()` (as flowgraph does) so `d3.show(title=..., filepath=...)` overrides work. Accept `node_properties` as dict **or** DataFrame (flowgraph does this with `_node_properties_to_dict`) because `D3Blocks(frame=True)` is the default.

Users edit `d3.node_properties` / `d3.edge_properties` and call `d3.show()` again; `show` must therefore be re-runnable and derive everything (e.g. colours) from the current properties on each call.

## 2. `set_config` keys

Signature: `def set_config(config={}, font={}, **kwargs)` (flowgraph) - returns `config`.

Always present (copy defaults from flowgraph unless the chart needs otherwise):

```python
config['chart'] = 'blockname'
config['title'] = kwargs.get('title', 'Blockname - D3blocks')
config['filepath'] = set_path(kwargs.get('filepath', 'blockname.html'), logger)
config['figsize'] = kwargs.get('figsize', [None, None])
config['showfig'] = kwargs.get('showfig', True)
config['overwrite'] = kwargs.get('overwrite', True)
config['notebook'] = kwargs.get('notebook', False)
config['reset_properties'] = kwargs.get('reset_properties', True)
config['font'] = {**{'size': 13}, **font}
config['save_button'] = kwargs.get('save_button', True)
# GUI conventions
config['color_background'] = kwargs.get('color_background', None)    # [dark_hex, light_hex] | named theme | None
config['dark_mode'] = check_dark_mode(kwargs.get('dark_mode', True)) # True | False | 'auto'; raises ValueError otherwise
config['show_side_panel'] = kwargs.get('show_side_panel', True)
config['show_top_panel'] = kwargs.get('show_top_panel', True)
# config['show_bottom_panel'] = kwargs.get('show_bottom_panel', True)  # only if the chart has a bottom panel
```

Then the chart's own options. Validate enumerations with a helper like flowgraph's `_check_choice(value, CHOICES, name, default, logger)`: unknown values fall back to the default with a warning rather than crashing; structural errors (missing columns, cycles) raise `ValueError`.

Remove any legacy flags if you are porting an older chart: `show_controls`, `show_stats_panel`, `show_node_panel` (-> `show_bottom_panel`).

## 3. `write_html` template keys

Flowgraph's `write_html(X, config, logger)` builds this dict and renders `<blockname>.html.j2`:

```python
bg_dark, bg_light = resolve_color_background(config.get('color_background', None))
options = {...chart options..., 'fontsize': config['font']['size'],
           'width': config['figsize'][0], 'height': config['figsize'][1], 'title': config['title']}
content = {
    'json_data': X,                                              # JSON string, '</' escaped as '<\\/'
    'options': json.dumps(options).replace('</', '<\\/'),
    'TITLE': html_escape(str(config['title'])),
    'COLOR_BACKGROUND_DARK': bg_dark,
    'COLOR_BACKGROUND_LIGHT': bg_light,
    'darkMode': dark_mode_flag(config.get('dark_mode', True)),   # 'true' | 'false' | 'auto'
    'showSidePanel': 'true' if config.get('show_side_panel', True) else 'false',
    'showTopPanel': 'true' if config.get('show_top_panel', True) else 'false',
    'SUPPORT': config.get('support') or '',
    'SAVE_BUTTON_START': '' if save_button else '<!--',
    'SAVE_BUTTON_STOP': '' if save_button else '-->',
    'LOGO_BASE64': config['logo_base64'],
}
html = template_env(__name__, __file__).get_template('blockname.html.j2').render(content)
write_html_file(config, html, logger)
if config.get('notebook'):
    return notebook_iframe(html, config, 'blockname')
return html
```

`show()` sets `config['logo_base64'] = set_logo(filepath=config.get('logo'))` before calling `write_html`.

`notebook_iframe(html, config, block)` comes from `_shared`: it wraps the page in `<div class="d3blocks-<block>"><iframe srcdoc="..." sandbox="allow-scripts allow-downloads allow-popups">`, sized by `figsize` or `100% x 650px`. Import it and pass the block name; do not write a local copy (the older `Flowgraph.py` still carries one, a duplicate to leave alone).

Scatter's older `write_html` also passes `SAVE_TO_SVG_SCRIPT` via `include_save_to_svg_script`; check whether the shared template you copy still needs it.

## 4. Imports, `_shared` and fallbacks

Charts use a package import with a flat fallback so the module also works when run from inside the source tree:

```python
try:
    from .._shared import check_dark_mode, dark_mode_flag, notebook_iframe, template_env
    from ..utils import resolve_color_background, set_logo, set_path, update_config, write_html_file
except ImportError:
    from _shared import check_dark_mode, dark_mode_flag, notebook_iframe, template_env
    from utils import resolve_color_background, set_logo, set_path, update_config, write_html_file
```

What `d3blocks/_shared/` provides (code shared by the diagram blocks):

| Item | Behaviour |
|---|---|
| `template_env(package_name, block_file)` | Jinja `Environment` with a `ChoiceLoader`: the block's own `d3js/` first, then `_shared/d3js/`. A template can `{% include %}` files from both, and a block can **override** a shared file by shipping one with the same name. Falls back to a `FileSystemLoader` on `<block_file's folder>/d3js` when the package loader is unavailable. Call it as `template_env(__name__, __file__)`. |
| `_shared/d3js/` | `theme.js`, `walkthrough.js`, `walkthrough.css`, `d3.v7.min.js`. A chart on d3 v7 includes `d3.v7.min.js` without shipping its own copy; a chart needing another d3 version ships its own file under a different name (for example `d3.v4.min.js`). Chart-specific libraries (layout engines, etc.) belong in the chart's own `d3js/`. |
| `check_dark_mode(v)` / `dark_mode_flag(v)` | `True`, `False`, `'auto'` (case-insensitive) accepted; anything else (`'light'`, `1`, `None`) raises `ValueError("dark_mode must be True, False or 'auto'; got ...")`. `check_dark_mode` returns `True/False/'auto'`; `dark_mode_flag` returns `'true'/'false'/'auto'`. |
| `notebook_iframe(html, config, block)` | Jupyter wrapper, see section 3. |
| `normalize_steps`, `ref_in`, `pair_in`, `index_in` | Optional captioned walkthrough, see 4b. |

The chart folder's `__init__.py` can be empty (confirm with `cat <existing chart>/__init__.py`). `_shared/d3js/` must ship in the wheel, as it already does for the existing diagram blocks.

## 4b. Optional: captioned walkthrough (`steps=`)

Only for charts with a natural step-through story. Shared pieces: `normalize_steps` (Python), `walkthrough.js` / `walkthrough.css` (browser).

Python: add `config['steps'] = kwargs.get('steps', None)` in `set_config`, accept `steps` in the public method (list of `{'title', 'caption', 'highlight': {key: [ref, ...]}}`), and in `show()` validate against the data actually drawn:

```python
steps = normalize_steps(
    config.get('steps'),
    {'nodes': ref_in(node_names, 'node'),                     # highlight key -> checker
     'edges': pair_in(edge_pairs, 'edge', undirected=False),  # (source, target) pairs
     'rows': index_in(len(df), 'row')},                       # integer index in range
    'blockname')
data['steps'] = steps                                         # None when no steps were given
```

Unknown keys or references raise `ValueError` naming `steps[i]`. Only highlight keys listed in the refs dict are accepted, so list exactly what the JS can highlight.

Template: `<style>{% include "walkthrough.css" %}</style>` and `<script>{% include "walkthrough.js" %}</script>` before the chart script. JS: see `template-css-js.md`.

## 5. Registration in `d3blocks.py` (four edits)

1. **Imports, twice.** The top of the file has a `try:` block (`import d3blocks.flowgraph.Flowgraph as Flowgraph`) and an `except:` block marked `DEBUG ONLY` (`import flowgraph.Flowgraph as Flowgraph`). Add the new chart to both, in the same position.
2. **Public method** `def blockname(self, ...)`, placed with the other chart methods (flowgraph is around line 3087, followed by `sequence` and `erd`).
3. **`set_chart_func`** (bottom of file): add `'Blockname'` to the `np.isin(chart, [...])` list. Without this the chart silently resolves to `None` ("is not yet implemented in such manner").
4. **Nodeless charts only**: `set_edge_properties` has `if (not hasattr(self, 'node_properties')) and np.any(np.isin(self.config['chart'], ['Violin', 'Scatter'])):` - add the chart there if its `set_node_properties()` may legitimately return nothing.

## 6. Public method skeleton

```python
    def blockname(self,
                  df,
                  # ...chart-specific parameters, each with a default...
                  font: dict = {'size': 13},
                  title: str = 'Blockname - D3blocks',
                  filepath: str = 'blockname.html',
                  figsize=[None, None],
                  showfig: bool = True,
                  overwrite: bool = True,
                  notebook: bool = False,
                  save_button: bool = True,
                  show_side_panel: bool = True,
                  show_top_panel: bool = True,
                  dark_mode=True,
                  color_background=None,
                  return_html: bool = False,
                  reset_properties: bool = True):
        """Blockname block: one-line summary.

        Longer description.

        Parameters
        ----------
        df : pd.DataFrame
            ...
        show_side_panel : bool, (default: True)
            Show the left side panels (Export / Save, ...).
        show_top_panel : bool, (default: True)
            Show the top bar (logo, search, theme).
        dark_mode : bool or 'auto', (default: True)
            Initial theme; the theme button switches at runtime in every mode.
                * True: start in the dark theme.
                * False: start in the light theme.
                * 'auto': follow the operating system theme until the theme button is used.
        color_background : list of str, str, or None, (default: None)
            Backgrounds for center / top / side panels as ``[dark_hex, light_hex]``.
            Named themes: ``'streamlit'``, ``'darkblue'``. None -> ``['#222222', '#ffffff']``.
        ...
        """
        self._clean(clean_config=reset_properties, logger=logger)
        self.chart = set_chart_func('Blockname', logger)
        self.config = self.chart.set_config(
            config=self.config, font=font, title=title, filepath=filepath, figsize=figsize,
            showfig=showfig, overwrite=overwrite, notebook=notebook, save_button=save_button,
            show_side_panel=show_side_panel, show_top_panel=show_top_panel,
            dark_mode=dark_mode, color_background=color_background,
            reset_properties=reset_properties, logger=logger,
            # ...chart-specific...
        )
        if self.config['reset_properties'] or (not hasattr(self, 'node_properties')):
            self.set_node_properties(df, logger=logger)
        self.set_edge_properties(df, logger=logger)
        html = self.show()
        if return_html:
            return html
```

## 7. Gotchas

- `str.capitalize` lowercases the tail: `HeatFlow` -> `Heatflow`. The alias in step 5.1 must match.
- `eval(chart)` in `set_chart_func` means a typo in the alias raises `NameError` only at call time - test registration (`D3Blocks(chart='blockname').chart is Blockname`).
- `_clean(clean_config=reset_properties)` wipes `self.config` down to `chart/frame/curpath/notebook/support`; that is why `set_config` is called right after with every default.
- `self.config['support']` is set in `__init__` (`utils.get_support`); the template's `SUPPORT` comes from `config.get('support') or ''`, so tests use `support=None`.
- JSON into HTML: always `.replace('</', '<\\/')`, and `html_escape` anything that lands in markup (title). Tests assert both.
- Edge-case input (empty frame, one row, NaN) should degrade gracefully or raise a clear `ValueError`, never produce a blank page.
- CRLF line endings: edit in a way that preserves them.
