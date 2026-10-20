"""Sequence block.

Sequence diagrams: participants are columns with lifelines, messages are rows in
time order (calls and replies), and regions highlight a run of messages. Input is
a Mermaid sequenceDiagram or a DataFrame of messages.

Library     : d3blocks
Github      : https://github.com/d3blocks/d3blocks
License     : GPL3
"""

import json
import re
from html import escape as html_escape

import pandas as pd

try:
    from .._shared import (
        check_dark_mode,
        dark_mode_flag,
        index_in,
        normalize_steps,
        notebook_iframe,
        ref_in,
        template_env,
    )
    from ..flowgraph import Flowgraph as fg
    from ..utils import (
        resolve_color_background,
        set_logo,
        set_path,
        update_config,
        write_html_file,
    )
except ImportError:
    import flowgraph.Flowgraph as fg
    from _shared import (
        check_dark_mode,
        dark_mode_flag,
        index_in,
        normalize_steps,
        notebook_iframe,
        ref_in,
        template_env,
    )
    from utils import (
        resolve_color_background,
        set_logo,
        set_path,
        update_config,
        write_html_file,
    )

KINDS = ("participant", "actor")
STYLES = ("sync", "reply")
# Semantic message colours, shared with flowgraph (after archify). The line style
# comes from 'style': a call is solid, a reply is dashed.
VARIANTS = tuple(fg.EDGE_VARIANTS)
DEFAULT_REGION_COLOR = "#4e79a7"

is_mermaid_source = fg.is_mermaid_source
merge_node_attributes = fg.merge_node_attributes


# %% Set configuration properties
def set_config(config={}, font={}, **kwargs):
    """Set the default configuration setting."""
    logger = kwargs.get("logger", None)
    config["chart"] = "sequence"
    config["title"] = kwargs.get("title", "Sequence - D3blocks")
    config["filepath"] = set_path(kwargs.get("filepath", "sequence.html"), logger)
    config["figsize"] = kwargs.get("figsize", [None, None])
    config["showfig"] = kwargs.get("showfig", True)
    config["overwrite"] = kwargs.get("overwrite", True)
    config["notebook"] = kwargs.get("notebook", False)
    config["reset_properties"] = kwargs.get("reset_properties", True)
    config["font"] = {**{"size": 13}, **font}
    config["message_spacing"] = kwargs.get("message_spacing", 44)
    config["wrap"] = kwargs.get("wrap", 28)
    config["cmap"] = kwargs.get("cmap", "Set2")
    # Regions: [{'label': str, 'from': i, 'to': j, 'color': hex}] with message indexes.
    config["groups"] = kwargs.get("groups") or []
    # Captioned walkthrough: None steps through every message.
    config["steps"] = kwargs.get("steps", None)
    # GUI
    config["color_background"] = kwargs.get("color_background", None)
    config["dark_mode"] = check_dark_mode(kwargs.get("dark_mode", True))
    config["save_button"] = kwargs.get("save_button", True)
    config["show_side_panel"] = kwargs.get("show_side_panel", True)
    config["show_top_panel"] = kwargs.get("show_top_panel", True)
    return config


# %% Participants
def set_node_properties(df, participants=None, cmap="Set2", logger=None, **kwargs):
    """Set the participant properties.

    Parameters
    ----------
    df : pd.DataFrame()
        Messages with at least the columns 'source' and 'target'.
    participants : pd.DataFrame or dict, (default: None)
        Per-participant attributes keyed by participant id: 'label', 'kind'
        ('participant' or 'actor'), 'color' and 'tooltip'. A DataFrame may hold the id
        in a 'name' column or in its index. Listed participants come first, in the
        given order; the others follow in order of first appearance in `df`.
    cmap : str, (default: 'Set2')
        Colormap for participants without their own colour.

    Returns
    -------
    dict
        {participant id: {'name', 'label', 'kind', 'color', 'tooltip'}}

    """
    fg._check_columns(df)
    attrs = fg._nodes_to_dict(participants)
    order = list(attrs)
    order += [
        n
        for n in pd.unique(df[["source", "target"]].astype(str).values.ravel())
        if n not in attrs
    ]
    palette = fg._colors_for(order, cmap)

    props = {}
    for name in order:
        a = attrs.get(name, {})
        props[name] = {
            "name": name,
            "label": str(fg._get(a, "label", name)),
            "kind": fg._check_choice(
                fg._get(a, "kind", "participant"),
                KINDS,
                f"kind of '{name}'",
                "participant",
                logger,
            ),
            "color": fg._get(a, "color", None) or palette[name],
            "tooltip": fg._optional_str(fg._get(a, "tooltip", None)),
        }
    return props


# %% Messages
def set_edge_properties(df, logger=None, **kwargs):
    """Set the message properties.

    Parameters
    ----------
    df : pd.DataFrame()
        One row per message, in time order. Required columns: 'source', 'target'.
        Optional columns:
            * 'label': message text.
            * 'style': 'sync' (a call: solid line, filled arrowhead) or 'reply'
              (dashed line, open arrowhead).
            * 'variant': 'default', 'emphasis', 'security', 'async' or 'error';
              sets the colour and line width, as in flowgraph.

    Returns
    -------
    pd.DataFrame
        One row per message with the columns source, target, label, style, variant,
        color and width.

    """
    fg._check_columns(df)
    out = pd.DataFrame(
        {
            "source": df["source"].astype(str).values,
            "target": df["target"].astype(str).values,
        }
    )
    selfloops = [
        i for i, (s, t) in enumerate(zip(out["source"], out["target"])) if s == t
    ]
    if selfloops:
        raise ValueError(
            "Self-messages are not supported (message %d: %s -> %s)."
            % (selfloops[0], out["source"][selfloops[0]], out["target"][selfloops[0]])
        )
    out["label"] = fg._column(df, "label", "").fillna("").astype(str).values

    styles = fg._column(df, "style", "sync").fillna("sync").astype(str).str.lower()
    fg._warn_unknown(styles, STYLES, "message style", "sync", logger)
    out["style"] = styles.where(styles.isin(STYLES), "sync").values

    variants = (
        fg._column(df, "variant", "default").fillna("default").astype(str).str.lower()
    )
    fg._warn_unknown(variants, VARIANTS, "message variant", "default", logger)
    out["variant"] = variants.where(variants.isin(VARIANTS), "default").values
    # None: the theme's line colour, so default messages follow dark/light mode.
    out["color"] = [fg.EDGE_VARIANTS[v]["color"] for v in out["variant"]]
    out["width"] = [
        round(1.5 + fg.EDGE_VARIANTS[v]["width"], 2) for v in out["variant"]
    ]
    return out


def set_group_properties(groups, n_messages, logger=None):
    """Validate the regions: [{'label', 'from', 'to', 'color'}] with message indexes."""
    out = []
    for i, g in enumerate(groups or []):
        if not isinstance(g, dict) or "from" not in g or "to" not in g:
            raise ValueError(
                "groups[%d]: expected {'label': str, 'from': i, 'to': j, 'color': hex}; got %r."
                % (i, g)
            )
        lo, hi = int(g["from"]), int(g["to"])
        if not 0 <= lo <= hi < n_messages:
            raise ValueError(
                "groups[%d]: messages %d..%d are out of range; there are %d messages."
                % (i, lo, hi, n_messages)
            )
        out.append(
            {
                "label": str(g.get("label") or ""),
                "from": lo,
                "to": hi,
                "color": str(g.get("color") or DEFAULT_REGION_COLOR),
            }
        )
    return out


def default_steps(df, participants):
    """One step per message, captioned with the message label."""

    def name(p):
        return participants.get(p, {}).get("label", p).replace("\n", " ")

    return [
        {
            "title": "%d. %s → %s" % (i + 1, name(s), name(t)),
            "caption": label,
            "highlight": {"messages": [i]},
        }
        for i, (s, t, label) in enumerate(zip(df["source"], df["target"], df["label"]))
    ]


# %% Show
def show(df, **kwargs):
    """Build and show the diagram.

    Parameters
    ----------
    df : pd.DataFrame()
        Message properties (output of set_edge_properties).
    config : dict
        Configuration keys.
    node_properties : dict or pd.DataFrame
        Participant properties (output of set_node_properties).

    Returns
    -------
    str
        The generated HTML.

    """
    logger = kwargs.get("logger", None)
    participants = fg._node_properties_to_dict(kwargs.get("node_properties"))
    config = update_config(kwargs, logger).copy()

    # Messages may reference participants that were added after set_node_properties().
    missing = [
        n
        for n in pd.unique(df[["source", "target"]].values.ravel())
        if n not in participants
    ]
    palette = fg._colors_for(missing, config.get("cmap", "Set2"))
    for name in missing:
        participants[name] = {
            "name": name,
            "label": name,
            "kind": "participant",
            "color": palette[name],
            "tooltip": None,
        }

    groups = set_group_properties(config.get("groups"), len(df), logger=logger)
    steps = config.get("steps")
    steps = normalize_steps(
        default_steps(df, participants) if steps is None else steps,
        {
            "messages": index_in(len(df), "message"),
            "participants": ref_in(participants, "participant"),
        },
        "sequence",
    )

    data = {
        "participants": [fg._jsonable(p) for p in participants.values()],
        "messages": [fg._jsonable(r) for r in df.to_dict(orient="records")],
        "groups": groups,
        "steps": steps,
    }
    X = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
    config["logo_base64"] = set_logo(filepath=config.get("logo"))
    return write_html(X, config, logger)


def write_html(X, config, logger=None):
    """Write html.

    Parameters
    ----------
    X : str
        JSON string with participants, messages, groups and steps.
    config : dict
        Configuration keys.

    Returns
    -------
    str
        The generated HTML.

    """
    bg_dark, bg_light = resolve_color_background(config.get("color_background", None))
    save_button = config.get("save_button", True)
    options = {
        "messageSpacing": config["message_spacing"],
        "wrap": config["wrap"],
        "fontsize": config["font"]["size"],
        "width": config["figsize"][0],
        "height": config["figsize"][1],
        "title": config["title"],
    }
    content = {
        "json_data": X,
        "options": json.dumps(options).replace("</", "<\\/"),
        "TITLE": html_escape(str(config["title"])),
        "COLOR_BACKGROUND_DARK": bg_dark,
        "COLOR_BACKGROUND_LIGHT": bg_light,
        "fontsize": config["font"]["size"],
        "messageSpacing": config["message_spacing"],
        "wrap": config["wrap"],
        "darkMode": dark_mode_flag(config.get("dark_mode", True)),
        "showSidePanel": "true" if config.get("show_side_panel", True) else "false",
        "showTopPanel": "true" if config.get("show_top_panel", True) else "false",
        "SUPPORT": config.get("support") or "",
        "SAVE_BUTTON_START": "" if save_button else "<!--",
        "SAVE_BUTTON_STOP": "" if save_button else "-->",
        "LOGO_BASE64": config["logo_base64"],
    }
    html = (
        template_env(__name__, __file__)
        .get_template("sequence.html.j2")
        .render(content)
    )
    write_html_file(config, html, logger)
    if config.get("notebook"):
        return notebook_iframe(html, config, "sequence")
    return html


# %% Mermaid
# Participant id: no spaces, arrows or separators; hyphens only inside (auth-svc).
_ID = r"([^\s\-<>:;,+]+(?:-[^\s\-<>:;,+]+)*)"
_PARTICIPANT = re.compile(r"^(participant|actor)\s+" + _ID + r"(?:\s+as\s+(.+))?$")
_MESSAGE = re.compile(r"^" + _ID + r"\s*(-->>|->>)\s*" + _ID + r"\s*:(.*)$")
_RECT = re.compile(r"^rect\s+(rgba?\([^)]*\))$")


def from_mermaid(text, logger=None):
    """Convert a Mermaid sequenceDiagram into Sequence inputs.

    Supported: 'participant A', 'participant A as Label', 'actor A', messages
    'A->>B: text' (call) and 'A-->>B: text' (reply), 'rect rgb(...)' / 'rect rgba(...)'
    ... 'end' regions and '%%' comments (accTitle / accDescr are ignored too). Other
    statements raise a ValueError naming the line.

    Parameters
    ----------
    text : str or path-like
        Mermaid text, Markdown with a ```mermaid block, or a path to a .md / .markdown /
        .mmd / .mermaid file. From Markdown, the first sequenceDiagram block is used.

    Returns
    -------
    tuple
        (messages DataFrame, participants dict, groups list)

    """
    text = fg.read_mermaid(text, logger=logger, kinds=("sequenceDiagram",))
    if fg._first_statement(text).split()[:1] != ["sequenceDiagram"]:
        raise ValueError(
            "Expected a Mermaid sequenceDiagram; the first statement is %r."
            % fg._first_statement(text)
        )
    participants, messages, groups, stack = {}, [], [], []
    header = True

    for lineno, stmt in fg._mermaid_lines(text):
        if header:
            header = False
            if stmt == "sequenceDiagram":
                continue
        m = _PARTICIPANT.match(stmt)
        if m:
            p = participants.setdefault(m.group(2), {})
            p["kind"] = m.group(1)
            if m.group(3):
                p["label"] = fg._mermaid_label(m.group(3))
            continue
        m = _MESSAGE.match(stmt)
        if m:
            source, arrow, target = m.group(1), m.group(2), m.group(3)
            if source == target:
                raise ValueError(
                    "Mermaid sequenceDiagram line %d: self-messages are not supported: %r."
                    % (lineno, stmt)
                )
            participants.setdefault(source, {})
            participants.setdefault(target, {})
            messages.append(
                (
                    source,
                    target,
                    fg._mermaid_label(m.group(4)),
                    "reply" if arrow == "-->>" else "sync",
                )
            )
            continue
        m = _RECT.match(stmt)
        if m:
            stack.append(
                {
                    "label": "",
                    "from": len(messages),
                    "color": m.group(1).replace(" ", ""),
                    "line": lineno,
                }
            )
            continue
        if stmt == "end":
            if not stack:
                raise ValueError(
                    'Mermaid sequenceDiagram line %d: "end" without an open "rect".'
                    % lineno
                )
            g = stack.pop()
            if len(messages) == g["from"]:
                raise ValueError(
                    'Mermaid sequenceDiagram line %d: "rect" contains no messages.'
                    % g["line"]
                )
            groups.append(
                {
                    "label": g["label"],
                    "from": g["from"],
                    "to": len(messages) - 1,
                    "color": g["color"],
                }
            )
            continue
        raise fg._mermaid_error(
            "sequenceDiagram",
            lineno,
            stmt,
            'participant/actor (with "as"), A->>B: text, A-->>B: text, rect rgb(...) ... end and %% comments',
        )
    if stack:
        raise ValueError(
            'Mermaid sequenceDiagram line %d: "rect" has no "end".' % stack[-1]["line"]
        )
    if not messages:
        raise ValueError(
            "No Mermaid sequence messages found. Expected text such as "
            '"sequenceDiagram\\n  A->>B: request\\n  B-->>A: response".'
        )
    df = pd.DataFrame(messages, columns=["source", "target", "label", "style"])
    return df, participants, groups
