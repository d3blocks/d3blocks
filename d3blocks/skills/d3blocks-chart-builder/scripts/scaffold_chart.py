#!/usr/bin/env python3
"""Scaffold the boilerplate for a new d3blocks chart.

Creates (never overwrites):
  <pkg-dir>/<name>/__init__.py
  <pkg-dir>/<name>/<Name>.py            module with the contract d3blocks.py expects
  <pkg-dir>/<name>/d3js/<name>.html.j2  template (from assets/, derived from flowgraph_html.j2)
  <pkg-dir>/<name>/d3js/<name>.css      shared theme/panel CSS block + prefixed chart section
  <pkg-dir>/<name>/d3js/d3.<name>.js    JS shell: data/options, panels, theme, search, export
  <tests-dir>/test_<name>.py            pytest skeleton modelled on test_flowgraph.py
  <demo-dir>/<name>_streamlit_demo.py   Streamlit demo skeleton

Then prints the d3blocks.py edits to make by hand (imports, method, allow-list).

Usage:
  python scaffold_chart.py --name heatflow --prefix hf \
      --pkg-dir d3blocks --tests-dir d3blocks/tests --demo-dir streamlit
"""
import argparse
import re
import sys
from pathlib import Path

MODULE = '''"""{Name} block.

TODO: one-paragraph description of what the chart shows and its input.

Library     : d3blocks
Github      : https://github.com/d3blocks/d3blocks
License     : GPL3
"""
import json
from html import escape as html_escape

import pandas as pd

try:
    from .._shared import check_dark_mode, dark_mode_flag, template_env
    from ..utils import (
        resolve_color_background,
        set_logo,
        set_path,
        update_config,
        write_html_file,
    )
except ImportError:
    from _shared import check_dark_mode, dark_mode_flag, template_env
    from utils import (
        resolve_color_background,
        set_logo,
        set_path,
        update_config,
        write_html_file,
    )


# TODO: chart-specific enumerations, e.g. LAYOUTS = ('a', 'b')


# %% Set configuration properties
def set_config(config={{}}, font={{}}, **kwargs):
    """Set the default configuration setting."""
    logger = kwargs.get('logger', None)
    config['chart'] = '{name}'
    config['title'] = kwargs.get('title', '{Name} - D3blocks')
    config['filepath'] = set_path(kwargs.get('filepath', '{name}.html'), logger)
    config['figsize'] = kwargs.get('figsize', [None, None])
    config['showfig'] = kwargs.get('showfig', True)
    config['overwrite'] = kwargs.get('overwrite', True)
    config['notebook'] = kwargs.get('notebook', False)
    config['reset_properties'] = kwargs.get('reset_properties', True)
    config['font'] = {{**{{'size': 13}}, **font}}
    # TODO: chart-specific options, validated with fallbacks to defaults.
    # GUI conventions (see references/conventions.md)
    config['color_background'] = kwargs.get('color_background', None)
    config['dark_mode'] = check_dark_mode(kwargs.get('dark_mode', True))
    config['save_button'] = kwargs.get('save_button', True)
    config['show_side_panel'] = kwargs.get('show_side_panel', True)
    config['show_top_panel'] = kwargs.get('show_top_panel', True)
    # config['show_bottom_panel'] = kwargs.get('show_bottom_panel', True)  # only if the chart has a bottom panel
    return config


# %% Node properties
def set_node_properties(df=None, logger=None, **kwargs):
    """Set the node properties.

    Returns
    -------
    dict
        {{node_name: {{...properties...}}}}; users may edit it and call d3.show().
    """
    _check_columns(df)
    # TODO: build per-node properties (label, color, ...) from df and kwargs.
    return {{}}


# %% Edge properties
def set_edge_properties(df=None, logger=None, **kwargs):
    """Set the edge properties.

    Returns
    -------
    pd.DataFrame
        Edge table; users may edit it and call d3.show().
    """
    _check_columns(df)
    # TODO: fill defaults (color, weight, label, ...) on a copy of df.
    return df.copy()


# %% Show
def show(df, **kwargs):
    """Build and show the chart.

    Parameters
    ----------
    df : pd.DataFrame
        Edge properties (output of set_edge_properties).
    config : dict
        Configuration keys.
    node_properties : dict or pd.DataFrame
        Node properties (output of set_node_properties).

    Returns
    -------
    str
        The generated HTML.
    """
    logger = kwargs.get('logger', None)
    node_properties = _node_properties_to_dict(kwargs.get('node_properties'))
    config = update_config(kwargs, logger).copy()

    # TODO: derive everything (colours, defaults) from the CURRENT properties so d3.show() can be re-run.
    data = {{
        'nodes': list(node_properties.values()),
        'edges': json.loads(df.to_json(orient='records')),
    }}
    X = json.dumps(data, ensure_ascii=False).replace('</', '<\\\\/')

    config['logo_base64'] = set_logo(filepath=config.get('logo'))
    return write_html(X, config, logger)


def write_html(X, config, logger=None):
    """Write html.

    Parameters
    ----------
    X : str
        JSON string with the chart data.
    config : dict
        Configuration keys.

    Returns
    -------
    str
        The generated HTML.
    """
    bg_dark, bg_light = resolve_color_background(config.get('color_background', None))
    save_button = config.get('save_button', True)
    options = {{
        'fontsize': config['font']['size'],
        'width': config['figsize'][0],
        'height': config['figsize'][1],
        'title': config['title'],
        # TODO: chart-specific options for the JavaScript.
    }}

    content = {{
        'json_data': X,
        'options': json.dumps(options).replace('</', '<\\\\/'),
        'TITLE': html_escape(str(config['title'])),
        'COLOR_BACKGROUND_DARK': bg_dark,
        'COLOR_BACKGROUND_LIGHT': bg_light,
        'fontsize': config['font']['size'],
        'darkMode': dark_mode_flag(config.get('dark_mode', True)),
        'showSidePanel': 'true' if config.get('show_side_panel', True) else 'false',
        'showTopPanel': 'true' if config.get('show_top_panel', True) else 'false',
        'SUPPORT': config.get('support') or '',
        'SAVE_BUTTON_START': '' if save_button else '<!--',
        'SAVE_BUTTON_STOP': '' if save_button else '-->',
        'LOGO_BASE64': config['logo_base64'],
    }}

    html = template_env(__name__, __file__).get_template('{name}.html.j2').render(content)
    write_html_file(config, html, logger)
    if config.get('notebook'):
        return notebook_iframe(html, config)
    return html


def notebook_iframe(html, config):
    """Wrap the chart in an iframe for Jupyter (page uses fixed positioning and fixed element ids)."""
    width, height = (list(config.get('figsize') or [None, None]) + [None, None])[:2]
    width = '%dpx' % width if width else '100%'
    height = '%dpx' % height if height else '650px'
    # Wrapped in a div: IPython warns about HTML that starts with '<iframe'.
    return ('<div class="d3blocks-{name}"><iframe srcdoc="%s" title="%s" '
            'style="width:%s;height:%s;border:0;border-radius:6px" '
            'sandbox="allow-scripts allow-downloads allow-popups"></iframe></div>'
            % (html_escape(html, quote=True), html_escape(str(config.get('title', '{Name}'))), width, height))


# %% Helpers
def _check_columns(df):
    """Raise ValueError when required columns are missing."""
    required = ()  # TODO: e.g. ('source', 'target')
    if df is None:
        raise ValueError('{name}: input data is required.')
    missing = [c for c in required if c not in getattr(df, 'columns', [])]
    if missing:
        raise ValueError("{name}: missing required column(s) %s." % missing)


def _node_properties_to_dict(node_properties):
    """Accept the dict or the DataFrame form of node properties (D3Blocks(frame=True) gives a DataFrame)."""
    if node_properties is None:
        return {{}}
    if isinstance(node_properties, pd.DataFrame):
        return {{str(k): v for k, v in node_properties.to_dict(orient='index').items()}}
    return dict(node_properties)
'''

TEST = '''"""Tests for the {Name} block."""
import json
import re

import pandas as pd
import pytest

from d3blocks import D3Blocks
from d3blocks.{name} import {Name}


def _sample_df():
    # TODO: a small, valid input.
    return pd.DataFrame({{'source': ['a', 'b'], 'target': ['b', 'c']}})


def _data(html):
    """The JSON payload the template hands to the renderer."""
    return json.loads(re.search(r'<script type="application/json" id="{prefix}-data">(.*?)</script>', html, re.S).group(1))


def _options(html):
    return json.loads(re.search(r'<script type="application/json" id="{prefix}-options">(.*?)</script>', html, re.S).group(1))


def _render(df, **kwargs):
    d3 = D3Blocks(frame=False, support=None, verbose='error')
    html = d3.{name}(df, filepath=None, showfig=False, return_html=True, **kwargs)
    return d3, html


def test_{name}_returns_standalone_html():
    _, html = _render(_sample_df())
    assert isinstance(html, str)
    assert 'id="{prefix}-svg"' in html  # TODO: the chart's main element id
    assert _data(html)  # TODO: assert on real payload content


def test_{name}_registered_as_chart():
    d3 = D3Blocks(chart='{name}', frame=False, support=None, verbose='error')
    assert d3.chart is {Name}


def test_{name}_missing_columns():
    with pytest.raises(ValueError):
        _render(pd.DataFrame({{'nope': [1]}}))  # TODO: adapt to the required columns


def test_{name}_properties_editable():
    d3, _ = _render(_sample_df())
    # TODO: edit d3.node_properties / d3.edge_properties, then:
    html = d3.show(return_html=True, showfig=False)
    assert _data(html)


def test_{name}_frame_mode_node_properties():
    # Default D3Blocks(frame=True) keeps node properties as a DataFrame.
    d3 = D3Blocks(support=None, verbose='error')
    html = d3.{name}(_sample_df(), filepath=None, showfig=False, return_html=True)
    assert _data(html)


def test_{name}_escapes_html():
    df = pd.DataFrame({{'source': ['</script><b>x'], 'target': ['y']}})  # TODO: adapt to the schema
    _, html = _render(df, title='A <b>title</b>')
    assert '</script><b>x' not in html
    assert '<title>A &lt;b&gt;title&lt;/b&gt;</title>' in html


@pytest.mark.parametrize(
    "dark_mode, flag",
    [(True, "true"), (False, "false"), ("auto", "auto"), ("AUTO", "auto")],
)
def test_{name}_dark_mode_flag(dark_mode, flag):
    _, html = _render(_sample_df(), dark_mode=dark_mode)
    assert 'data-dark-mode="%s"' % flag in html
    assert ('<body class="light"' in html) == (flag == "false")
    assert 'id="themeBtn"' in html and "D3BlocksTheme" in html  # theme.js is included, button is in the top bar


@pytest.mark.parametrize("dark_mode", ["light", 1, None, "yes"])
def test_{name}_dark_mode_rejects_other_values(dark_mode):
    with pytest.raises(ValueError, match="dark_mode"):
        _render(_sample_df(), dark_mode=dark_mode)


def test_{name}_output_stays_self_contained():
    _, html = _render(_sample_df(), dark_mode="auto")
    assert not re.search(r'<script[^>]+src=["\\']https?:', html)
    assert not re.search(r'<link[^>]+href=["\\']https?:', html)


def test_{name}_notebook_mode_returns_isolated_iframe():
    d3 = D3Blocks(frame=False, support=None, verbose='error')
    html = d3.{name}(_sample_df(), notebook=True, filepath=None, return_html=True, figsize=[900, 500])
    assert '<iframe srcdoc="' in html and 'width:900px;height:500px' in html


# --- d3blocks UI conventions -------------------------------------------------
@pytest.mark.parametrize('side', [True, False])
@pytest.mark.parametrize('top', [True, False])
def test_{name}_panel_flags_are_independent(side, top):
    _, html = _render(_sample_df(), show_side_panel=side, show_top_panel=top)
    SIDE_MARKER = 'id="exportPanel"'  # only present when the side panel is rendered
    TOP_MARKER = 'class="top-panel"'  # markup only; the CSS uses .top-panel
    assert (SIDE_MARKER in html) == side
    assert (TOP_MARKER in html) == top
    assert 'id="themeBtn"' in html or not top  # theme button lives in the top bar


def test_{name}_color_background_list():
    _, html = _render(_sample_df(), color_background=['#111111', '#fafafa'])
    assert '#111111' in html and '#fafafa' in html
    assert 'showControls' not in html
'''

DEMO = '''"""
Minimal Streamlit demo: embed a d3blocks {name} chart.

Run from a machine with d3blocks + streamlit installed:

    streamlit run {name}_streamlit_demo.py

API notes (Streamlit 1.56+)
---------------------------
* Prefer ``st.iframe(html, height=700)`` for full HTML + JavaScript.
* Do **not** use ``st.html`` for this chart: it is not iframed, and JS is off unless
  ``unsafe_allow_javascript=True``. Fixed-position CSS would also overlay the Streamlit page.
* Always pass an explicit pixel height (or height="stretch").
"""

import pandas as pd
import streamlit as st
from d3blocks import D3Blocks

# =============================================================================
# Import your data here
# =============================================================================
@st.cache_data
def load_data():
    # TODO: small sample data for the chart (or d3.import_example("...")).
    return pd.DataFrame({{'source': ['a', 'b'], 'target': ['b', 'c']}})

# =============================================================================
# Streamlit configuration
# =============================================================================
st.set_page_config(page_title="D3Blocks - {Name}", layout="wide")
df = load_data()

# =============================================================================
# Sidebar - chart controls (mirror some of the chart's own side-panel controls)
# =============================================================================
st.sidebar.subheader("Layout")
# TODO: e.g. option = st.sidebar.selectbox("Option", [...], index=0)

# D3Blocks UI
st.sidebar.subheader("D3Blocks UI")
show_side_panel = st.sidebar.checkbox("Show D3Blocks controls", value=False)
show_top_panel = st.sidebar.checkbox("Show D3Blocks top panel", value=True)

# Streamlit iframe
st.sidebar.subheader("Display")
height = st.sidebar.slider("Chart height", min_value=400, max_value=1200, value=700, step=50)

# =============================================================================
# Build D3Blocks {name}
# =============================================================================
@st.cache_data(show_spinner="Building {name}...")
def build_{name}_html(df, show_side_panel, show_top_panel):  # TODO: add the chart controls as arguments
    d3 = D3Blocks()
    html = d3.{name}(
        df,
        show_side_panel=show_side_panel,
        show_top_panel=show_top_panel,
        dark_mode=False,
        color_background="streamlit",
        filepath=None,
        showfig=False,
        return_html=True,
    )
    return html

# =============================================================================
# Main page
# =============================================================================
html = build_{name}_html(df, show_side_panel, show_top_panel)
st.caption("Interactive {name} powered by D3Blocks and controlled by Streamlit.")
if hasattr(st, "iframe"):
    st.iframe(html, height=height, width="stretch")
else:
    import streamlit.components.v1 as components

    st.warning("st.iframe is missing (Streamlit < 1.56). Falling back to deprecated components.html.")
    components.html(html, height=height, scrolling=False)
'''

INIT = '"""{Name} block."""\n'

METHOD_HINT = """
================  Edit d3blocks.py by hand (4 places)  ================
1) Top of file - add to BOTH import blocks (try: and the 'DEBUG ONLY' except:), next to Flowgraph:
       import d3blocks.{name}.{Name} as {Name}
       import {name}.{Name} as {Name}
2) Add `def {name}(self, df, ..., show_side_panel=True, show_top_panel=True, dark_mode=True,
   color_background=None, return_html=False, reset_properties=True)` next to flowgraph().
   Follow references/python-contract.md section 6.
3) set_chart_func(): add '{Name}' to the np.isin(chart, [...]) allow-list.
4) Only if the chart has no nodes: add it to ['Violin', 'Scatter'] in set_edge_properties().

Also: d3js/ now holds {name}.html.j2, {name}.css, d3.{name}.js (from assets/). The template also includes
shared files (theme.js, d3.v7.min.js): confirm template_env finds them (see _shared/__init__.py).
Check package_data/MANIFEST so d3js/* ships; keep CRLF line endings consistent with the repo.
"""


def write(path: Path, text: str, force: bool) -> None:
    if path.exists() and not force:
        print(f"skip (exists): {path}")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")
    print(f"created:       {path}")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--name", required=True, help="block name, lowercase single word (e.g. heatflow)")
    ap.add_argument("--prefix", default=None, help="2-3 letter prefix for element ids (default: first 2 letters)")
    ap.add_argument("--pkg-dir", default="d3blocks", help="folder that contains the chart folders (e.g. flowgraph/)")
    ap.add_argument("--tests-dir", default="d3blocks/tests", help="folder that contains test_flowgraph.py")
    ap.add_argument("--demo-dir", default="streamlit", help="folder that contains scatter_streamlit_demo.py")
    ap.add_argument("--force", action="store_true", help="overwrite existing files")
    args = ap.parse_args()

    name = args.name.strip().lower()
    if not re.fullmatch(r"[a-z][a-z0-9]*", name):
        print("--name must be lowercase letters/digits, starting with a letter (no underscores or spaces).", file=sys.stderr)
        return 2
    Name = name.capitalize()  # d3blocks.py resolves charts with str.capitalize(); the import alias must match
    prefix = (args.prefix or name[:2]).lower()
    fmt = dict(name=name, Name=Name, prefix=prefix)

    pkg = Path(args.pkg_dir) / name
    write(pkg / "__init__.py", INIT.format(**fmt), args.force)
    write(pkg / f"{Name}.py", MODULE.format(**fmt), args.force)
    assets = Path(__file__).resolve().parent.parent / "assets"
    tokens = {"__NAME__": name, "__PREFIX__": prefix}
    for src, dst in (("blockname.html.j2", f"{name}.html.j2"), ("blockname.css", f"{name}.css"), ("d3.blockname.js", f"d3.{name}.js")):
        text = (assets / src).read_text(encoding="utf-8")
        for k, v in tokens.items():
            text = text.replace(k, v)
        write(pkg / "d3js" / dst, text, args.force)
    write(Path(args.tests_dir) / f"test_{name}.py", TEST.format(**fmt), args.force)
    write(Path(args.demo_dir) / f"{name}_streamlit_demo.py", DEMO.format(**fmt), args.force)

    print(METHOD_HINT.format(**fmt))
    return 0


if __name__ == "__main__":
    sys.exit(main())
