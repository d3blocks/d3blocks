"""Code shared by the flowgraph, sequence and erd blocks.

* template_env(): a Jinja environment over a block's own d3js/ folder and
  d3blocks/_shared/d3js/ (walkthrough.js/.css, theme.js and the d3.v7.min.js
  used by sequence and erd), so a template can {% include %} both and the
  output stays self-contained.
* notebook_iframe(): the Jupyter iframe wrapper.
* dark_mode_flag(): validates dark_mode (True, False or 'auto').
* normalize_steps(): validates the captioned walkthrough steps.

Library     : d3blocks
Github      : https://github.com/d3blocks/d3blocks
License     : GPL3
"""

from html import escape as html_escape
from pathlib import Path

import numpy as np
from jinja2 import ChoiceLoader, Environment, FileSystemLoader, PackageLoader

DARK_MODES = (True, False, 'auto')
STEP_KEYS = ('title', 'caption', 'highlight')


def template_env(package_name, block_file):
    """Jinja environment over the block's d3js/ folder, then _shared/d3js/.

    Parameters
    ----------
    package_name : str
        __name__ of the block module, e.g. 'd3blocks.sequence.Sequence'.
    block_file : str
        __file__ of the block module (used when the package loader is unavailable).
    """

    def loader(package, folder):
        try:
            return PackageLoader(package_name=package, package_path='d3js')
        except Exception:
            return FileSystemLoader(str(Path(folder).resolve().parent / 'd3js'))

    return Environment(loader=ChoiceLoader([loader(package_name, block_file), loader(__name__, __file__)]))


def notebook_iframe(html, config, block):
    """Wrap a chart page in an iframe for Jupyter.

    The page fills its window (fixed positioning, own body background) and uses
    fixed element ids, so it is isolated in an iframe instead of being injected
    into the notebook page. Size: figsize, else full width x 650 px.
    """
    width, height = (list(config.get('figsize') or [None, None]) + [None, None])[:2]
    width = '%dpx' % width if width else '100%'
    height = '%dpx' % height if height else '650px'
    # Wrapped in a div: IPython warns about HTML that starts with '<iframe'.
    return (
        '<div class="d3blocks-%s"><iframe srcdoc="%s" title="%s" '
        'style="width:%s;height:%s;border:0;border-radius:6px" '
        'sandbox="allow-scripts allow-downloads allow-popups"></iframe></div>'
        % (block, html_escape(html, quote=True), html_escape(str(config.get('title', block))), width, height)
    )


def dark_mode_flag(dark_mode):
    """Template flag for dark_mode: 'true', 'false' or 'auto'.

    * True: dark theme.
    * False: light theme.
    * 'auto': follow the operating system theme until the viewer uses the theme toggle.
    """
    if isinstance(dark_mode, (bool, np.bool_)):
        return 'true' if dark_mode else 'false'
    if isinstance(dark_mode, str) and dark_mode.lower() == 'auto':
        return 'auto'
    raise ValueError("dark_mode must be True, False or 'auto'; got %r." % (dark_mode,))


def check_dark_mode(dark_mode):
    """dark_mode as True, False or 'auto'; raises ValueError for anything else."""
    flag = dark_mode_flag(dark_mode)
    return 'auto' if flag == 'auto' else flag == 'true'


def normalize_steps(steps, refs, block):
    """Validate walkthrough steps and return them as JSON-ready dicts.

    Parameters
    ----------
    steps : list of dict or None
        [{'title': str, 'caption': str, 'highlight': {key: [ref, ...]}}]
    refs : dict
        {highlight key: check(ref, step_index) -> resolved ref}. Only these
        highlight keys are accepted; a check raises ValueError for an unknown ref.
    block : str
        Block name, used in error messages.

    Returns
    -------
    list of dict or None
        [{'title', 'caption', 'highlight'}], or None when steps is None.

    """
    if steps is None:
        return None
    if isinstance(steps, (str, dict)) or not hasattr(steps, '__iter__'):
        raise ValueError('steps must be a list of dicts or None; got %s.' % type(steps).__name__)
    out = []
    for i, step in enumerate(steps):
        if not isinstance(step, dict):
            raise ValueError('steps[%d]: expected a dict with %s; got %s.' % (i, STEP_KEYS, type(step).__name__))
        unknown = sorted(set(step) - set(STEP_KEYS))
        if unknown:
            raise ValueError('steps[%d]: unknown key(s) %s; use %s.' % (i, unknown, STEP_KEYS))
        highlight = step.get('highlight') or {}
        if not isinstance(highlight, dict):
            raise ValueError("steps[%d]: 'highlight' must be a dict; got %s." % (i, type(highlight).__name__))
        unsupported = sorted(set(highlight) - set(refs))
        if unsupported:
            raise ValueError(
                'steps[%d]: highlight key(s) %s are not supported by %s; use %s.' % (i, unsupported, block, tuple(refs))
            )
        resolved = {}
        for key, values in highlight.items():
            if values is None:
                continue
            if isinstance(values, (str, int, np.integer)):
                values = [values]
            resolved[key] = [refs[key](v, i) for v in values]
        out.append(
            {
                'title': str(step.get('title') or 'Step %d' % (i + 1)),
                'caption': str(step.get('caption') or ''),
                'highlight': resolved,
            }
        )
    return out


def ref_in(names, what):
    """Check for a reference that must be one of `names`."""
    names = set(names)

    def check(ref, i):
        key = str(ref)
        if key not in names:
            raise ValueError('steps[%d]: unknown %s %r.' % (i, what, ref))
        return key

    return check


def pair_in(pairs, what, undirected=False):
    """Check for a (source, target) reference that must be in `pairs`."""
    pairs = {(str(s), str(t)) for s, t in pairs}

    def check(ref, i):
        if isinstance(ref, str) or not hasattr(ref, '__len__') or len(ref) != 2:
            raise ValueError('steps[%d]: %s must be (source, target) pairs; got %r.' % (i, what, ref))
        s, t = str(ref[0]), str(ref[1])
        if (s, t) in pairs:
            return [s, t]
        if undirected and (t, s) in pairs:
            return [t, s]
        raise ValueError('steps[%d]: unknown %s %r.' % (i, what, tuple(ref)))

    return check


def index_in(count, what):
    """Check for an integer index in range(count)."""

    def check(ref, i):
        if isinstance(ref, (bool, np.bool_)) or not isinstance(ref, (int, np.integer)) or not 0 <= ref < count:
            raise ValueError('steps[%d]: unknown %s %r; use an index from 0 to %d.' % (i, what, ref, count - 1))
        return int(ref)

    return check
