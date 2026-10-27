"""Tests for the Flowgraph block (process flows and architecture diagrams)."""
import json
import logging
import re
from pathlib import Path

import pandas as pd
import pytest

from d3blocks import D3Blocks
from d3blocks.flowgraph import Flowgraph


def _sample_df():
    # A flow with a decision and a retry loop (cycle).
    return pd.DataFrame({
        'source': ['start', 'check', 'check', 'fix'],
        'target': ['check', 'done', 'fix', 'check'],
        'label': ['', 'yes', 'no', 'retry'],
    })


def _data(html):
    """The JSON payload the template hands to the renderer."""
    return json.loads(re.search(r'<script type="application/json" id="fg-data">(.*?)</script>', html, re.S).group(1))


def _options(html):
    return json.loads(re.search(r'<script type="application/json" id="fg-options">(.*?)</script>', html, re.S).group(1))


def _render(df, **kwargs):
    d3 = D3Blocks(frame=False, support=None, verbose='error')
    html = d3.flowgraph(df, filepath=None, showfig=False, return_html=True, **kwargs)
    return d3, html


def test_flowgraph_returns_standalone_html():
    _, html = _render(_sample_df())
    assert isinstance(html, str)
    assert 'id="fg-svg"' in html
    assert 'dagre' in html and 'd3js.org' in html  # libraries are inlined
    data = _data(html)
    assert [n['name'] for n in data['nodes']] == ['start', 'check', 'done', 'fix']
    assert [e['label'] for e in data['edges']] == ['', 'yes', 'no', 'retry']


def test_flowgraph_elk_is_bundled_only_when_requested():
    _, dagre_html = _render(_sample_df())
    _, elk_html = _render(_sample_df(), layout='elk')
    marker = 'org.eclipse.elk.algorithm'  # only present in the ELK bundle
    assert marker not in dagre_html
    assert marker in elk_html
    assert _options(elk_html)['layout'] == 'elk'


def test_flowgraph_node_attributes_and_isolated_nodes():
    nodes = {'check': {'shape': 'decision', 'label': 'Valid?'},
             'island': {'label': 'Isolated', 'shape': 'hexagon'}}
    _, html = _render(_sample_df(), nodes=nodes)
    by_name = {n['name']: n for n in _data(html)['nodes']}
    assert by_name['check']['shape'] == 'decision' and by_name['check']['label'] == 'Valid?'
    assert by_name['island']['shape'] == 'process'  # unknown shape falls back
    assert by_name['start']['shape'] == 'process'


def test_flowgraph_groups_nest_and_colour_nodes():
    nodes = pd.DataFrame({'name': ['start', 'check', 'done'], 'group': ['inner', 'inner', 'other']})
    d3, html = _render(_sample_df(), nodes=nodes, groups={'inner': 'outer'})
    groups = {g['name']: g for g in _data(html)['groups']}
    assert set(groups) == {'inner', 'other', 'outer'}
    assert groups['inner']['parent'] == 'outer'
    assert d3.node_properties['start']['color'] == groups['inner']['color']


def test_flowgraph_group_cycle_is_rejected():
    nodes = {'start': {'group': 'a'}}
    with pytest.raises(ValueError):
        _render(_sample_df(), nodes=nodes, groups={'a': 'b', 'b': 'a'})


def test_flowgraph_missing_columns():
    with pytest.raises(ValueError):
        _render(pd.DataFrame({'from': ['a'], 'to': ['b']}))


def test_flowgraph_node_properties_editable():
    d3, _ = _render(_sample_df())
    d3.node_properties['fix']['shape'] = 'database'
    d3.node_properties['fix']['color'] = '#000000'
    d3.edge_properties.loc[0, 'label'] = 'begin'
    html = d3.show(return_html=True, showfig=False)
    fix = next(n for n in _data(html)['nodes'] if n['name'] == 'fix')
    assert fix['shape'] == 'database' and fix['color'] == '#000000'
    assert _data(html)['edges'][0]['label'] == 'begin'


def test_flowgraph_frame_mode_node_properties():
    # Default D3Blocks(frame=True) keeps node properties as a DataFrame.
    d3 = D3Blocks(support=None, verbose='error')
    html = d3.flowgraph(_sample_df(), nodes={'start': {'group': 'g'}}, filepath=None, showfig=False, return_html=True)
    assert isinstance(d3.node_properties, pd.DataFrame)
    assert [g['name'] for g in _data(html)['groups']] == ['g']


def test_flowgraph_edge_variants_colours_and_overrides():
    df = _sample_df().assign(variant=['default', 'emphasis', 'async', 'bogus'],
                             color=[None, None, '#123456', None])
    d3, html = _render(df, edge_color='source', nodes={'start': {'color': '#abcdef'}})
    edges = _data(html)['edges']
    assert edges[0]['color'] == '#abcdef'                      # default edge takes the source colour
    assert edges[1]['variant'] == 'emphasis' and edges[1]['color'] == '#f28e2b'
    assert edges[1]['width'] > edges[0]['width']               # emphasis is wider
    assert edges[2]['style'] == 'dashed' and edges[2]['color'] == '#123456'  # explicit colour wins
    assert edges[3]['variant'] == 'default'                    # unknown variant falls back


def test_flowgraph_animation_options():
    _, html = _render(_sample_df(), animate='comet')
    assert _options(html)['animate'] is True and _options(html)['animation'] == 'comet'
    _, html = _render(_sample_df(), animate=False)
    assert _options(html)['animate'] is False
    # A per-edge animation plays even when the chart-wide animation is off.
    df = _sample_df().assign(animation=[None, 'dots', None, None])
    _, html = _render(df)
    assert _options(html)['animate'] is True and _options(html)['animation'] == 'none'
    assert _data(html)['edges'][1]['animation'] == 'dots'


def test_flowgraph_escapes_html():
    df = pd.DataFrame({'source': ['</script><b>x'], 'target': ['y']})
    _, html = _render(df, title='A <b>title</b>')
    assert '</script><b>x' not in html
    assert '<title>A &lt;b&gt;title&lt;/b&gt;</title>' in html


def test_flowgraph_mermaid_shapes_links_and_subgraphs():
    text = '''
    flowchart TB
        %% comment
        start([Order received]) --> check{In stock?}
        check -->|yes| pick[Pick & pack]
        check -- no --> back[[Backorder]] -.->|restocked| check
        subgraph wh [Warehouse]
            pick --> ship[/Ship parcel/]
            subgraph qa [Quality]
                inspect((Inspect))
            end
        end
        ship ==> done([Delivered]); ship --> db[(Orders DB)]
        A & B --> start
        q>"Quoted (label)"] --> start
        style done fill:#59a14f
        classDef hot fill:#e15759
        class back hot
    '''
    df, nodes, groups, direction = Flowgraph.from_mermaid(text)
    assert direction == 'TB'
    shapes = {k: v.get('shape') for k, v in nodes.items()}
    assert shapes['start'] == 'terminal' and shapes['check'] == 'decision'
    assert shapes['back'] == 'subprocess' and shapes['ship'] == 'io'
    assert shapes['inspect'] == 'circle' and shapes['db'] == 'database' and shapes['q'] == 'document'
    assert nodes['q']['label'] == 'Quoted (label)'
    assert nodes['pick']['group'] == 'wh' and nodes['inspect']['group'] == 'qa'
    assert groups['qa']['parent'] == 'wh' and groups['wh']['label'] == 'Warehouse'
    assert nodes['done']['color'] == '#59a14f' and nodes['back']['color'] == '#e15759'

    edges = {
        (s, t): (lab, st, w)
        for s, t, lab, st, w in df[['source', 'target', 'label', 'style', 'weight']].itertuples(
            index=False, name=None
        )
    }
    assert edges[('check', 'pick')][0] == 'yes'
    assert edges[('check', 'back')][0] == 'no'
    assert edges[('back', 'check')] == ('restocked', 'dotted', 1)
    assert edges[('ship', 'done')][2] == 3          # thick link
    assert ('A', 'start') in edges and ('B', 'start') in edges


def test_flowgraph_accepts_mermaid_string():
    d3, html = _render('graph LR; a[Start] --> b{Ok?}; b -->|yes| c([End])')
    assert d3.config['direction'] == 'LR'
    data = _data(html)
    assert [n['shape'] for n in data['nodes']] == ['process', 'decision', 'terminal']
    # Explicit arguments override what the Mermaid text defines.
    d3, html = _render('graph LR; a --> b', direction='TB', nodes={'a': {'shape': 'circle'}})
    assert d3.config['direction'] == 'TB'
    assert _data(html)['nodes'][0]['shape'] == 'circle'


def test_flowgraph_registered_as_chart():
    d3 = D3Blocks(chart='flowgraph', frame=False, support=None, verbose='error')
    assert d3.chart is Flowgraph


@pytest.mark.parametrize('direction, expected', [('LR', 'LR'), ('tb', 'TB'), ('TD', 'TB'), ('td', 'TB'), ('RL', 'RL'), ('BT', 'BT')])
def test_flowgraph_direction_aliases(direction, expected):
    d3, html = _render(_sample_df(), direction=direction)
    assert d3.config['direction'] == expected
    assert _options(html)['direction'] == expected


_MARKDOWN = '''# Process

Some text.

```mermaid
sequenceDiagram
    A->>B: not a flowchart
```

```mermaid
flowchart TD
    a([Start]) --> b{Ok?}
    b -->|yes| c[Done]
```

```mermaid
graph LR
    x --> y
```
'''


def test_flowgraph_mermaid_from_markdown_text():
    d3, html = _render(_MARKDOWN)
    assert d3.config['direction'] == 'TB'  # first *flowchart* block, sequence diagram skipped
    assert [n['name'] for n in _data(html)['nodes']] == ['a', 'b', 'c']


def test_flowgraph_mermaid_from_files(tmp_path):
    md = tmp_path / 'process.md'
    md.write_text(_MARKDOWN, encoding='utf-8')
    mmd = tmp_path / 'flow.mmd'
    mmd.write_text('graph LR\n    p --> q --> r\n', encoding='utf-8')
    for source in (md, str(md)):
        d3, html = _render(source)
        assert [n['name'] for n in _data(html)['nodes']] == ['a', 'b', 'c']
    d3, html = _render(mmd)
    assert d3.config['direction'] == 'LR'
    assert [n['name'] for n in _data(html)['nodes']] == ['p', 'q', 'r']


def test_flowgraph_mermaid_file_errors(tmp_path):
    with pytest.raises(FileNotFoundError):
        _render(str(tmp_path / 'missing.md'))
    md = tmp_path / 'nothing.md'
    md.write_text('```mermaid\nsequenceDiagram\n    A->>B: hi\n```\n', encoding='utf-8')
    with pytest.raises(ValueError):
        _render(md)


# --- Regression tests for the pre-PR review --------------------------------

def test_flowgraph_without_edges_draws_isolated_nodes():
    # Mermaid with node declarations only.
    _, html = _render('flowchart LR\n    A[Start]\n    B[End]')
    data = _data(html)
    assert [n['name'] for n in data['nodes']] == ['A', 'B'] and data['edges'] == []
    # Empty edge list plus nodes.
    _, html = _render(pd.DataFrame(columns=['source', 'target']), nodes={'solo': {'label': 'Solo'}})
    assert [n['name'] for n in _data(html)['nodes']] == ['solo']


def test_flowgraph_group_overrides_merge_with_mermaid_subgraphs():
    text = 'flowchart LR\n subgraph cloud [Cloud]\n  subgraph api [API]\n   a --> b\n  end\n end'
    d3, html = _render(text, groups={'api': {'color': '#ff0000'}})
    groups = {g['name']: g for g in _data(html)['groups']}
    assert groups['api']['label'] == 'API' and groups['api']['parent'] == 'cloud'
    assert groups['api']['color'] == '#ff0000'
    # Short form {group: parent} also keeps the Mermaid label.
    _, html = _render('flowchart LR\n subgraph api [API]\n  a --> b\n end', groups={'api': 'outer'})
    groups = {g['name']: g for g in _data(html)['groups']}
    assert groups['api']['label'] == 'API' and groups['api']['parent'] == 'outer'


def test_flowgraph_mermaid_ids_starting_with_keywords():
    df, nodes, _, _ = Flowgraph.from_mermaid(
        'flowchart LR\n clickstream --> kafka\n directions_api --> b\n linkStyle 0 stroke:#f00')
    assert list(zip(df['source'], df['target'])) == [('clickstream', 'kafka'), ('directions_api', 'b')]
    assert 'linkStyle' not in nodes and df['color'][0] == '#f00' and pd.isna(df['color'][1])


def test_flowgraph_mermaid_trapezoids_do_not_swallow_the_line():
    df, nodes, _, _ = Flowgraph.from_mermaid('flowchart LR\n A[/in\\] --> B[/out/] --> C[\\alt/]')
    assert list(zip(df['source'], df['target'])) == [('A', 'B'), ('B', 'C')]
    assert (nodes['A']['label'], nodes['B']['label'], nodes['C']['label']) == ('in', 'out', 'alt')
    assert {nodes[k]['shape'] for k in 'ABC'} == {'io'}


def test_flowgraph_mermaid_semicolon_in_edge_label():
    df, _, _, _ = Flowgraph.from_mermaid('flowchart LR\n A -->|retry; backoff| B; B --> C')
    assert df[['source', 'target', 'label']].values.tolist() == [['A', 'B', 'retry; backoff'], ['B', 'C', '']]


def test_flowgraph_rejects_unsupported_text_and_files(tmp_path):
    with pytest.raises(ValueError, match='Unsupported input file'):
        _render('edges.csv')
    with pytest.raises(ValueError, match='Unsupported input file'):
        _render(tmp_path / 'edges.csv')
    with pytest.raises(ValueError, match="first statement is 'hello world'"):
        _render('hello world')


def test_flowgraph_groups_resolved_on_every_draw():
    nodes = {'start': {'group': 'g1'}, 'check': {'group': 'g1'}}
    d3, html = _render(_sample_df(), nodes=nodes, cmap='tab10')
    assert d3.config['groups'] == {}          # only user settings live in config
    # Move a node into a new group and redraw: the group appears, coloured like its node.
    d3.node_properties['done']['group'] = 'g2'
    groups = {g['name']: g for g in _data(d3.show(return_html=True, showfig=False))['groups']}
    assert set(groups) == {'g1', 'g2'}
    assert groups['g2']['color'] == d3.node_properties['done']['color']
    # Group settings edited in config take effect on redraw.
    d3.config['groups']['g1'] = {'label': 'Intake', 'color': '#123456'}
    groups = {g['name']: g for g in _data(d3.show(return_html=True, showfig=False))['groups']}
    assert groups['g1']['label'] == 'Intake' and groups['g1']['color'] == '#123456'


def test_flowgraph_tooltip_defaults_to_none_and_follows_label_edits():
    d3, html = _render(_sample_df(), nodes={'start': {'label': 'x < y & z'}, 'check': {'tooltip': '<b>Gate</b>'}})
    by_name = {n['name']: n for n in _data(html)['nodes']}
    assert by_name['start']['tooltip'] is None
    assert by_name['check']['tooltip'] == '<b>Gate</b>'   # explicit tooltips are kept as given
    d3.node_properties['start']['label'] = 'Renamed'
    by_name = {n['name']: n for n in _data(d3.show(return_html=True, showfig=False))['nodes']}
    assert by_name['start']['label'] == 'Renamed' and by_name['start']['tooltip'] is None


def test_flowgraph_notebook_mode_returns_isolated_iframe():
    d3 = D3Blocks(frame=False, support=None, verbose='error')
    html = d3.flowgraph(_sample_df(), notebook=True, filepath=None, return_html=True, figsize=[900, 500])
    assert '<iframe srcdoc="' in html and 'width:900px;height:500px' in html
    assert 'id="fg-svg"' not in html          # page markup is escaped inside srcdoc
    import html as htmllib
    inner = htmllib.unescape(re.search(r'srcdoc="(.*?)" title=', html, re.S).group(1))
    assert 'id="fg-svg"' in inner and _data(inner)['nodes']


# --- State diagrams, walkthrough steps and dark_mode='auto' (2.3.0) ----------

FIXTURES = Path(__file__).parent / "fixtures" / "trade"
_STATE = """stateDiagram-v2
    %% comment
    [*] --> pending : created
    pending --> done : ok: all checks
    pending --> failed
    done --> [*]
    failed --> [*]
    note right of pending
        Waits for <b>review</b>
        then continues
    end note
    note left of done : finished
    classDef good fill:#dcfce7,stroke:#16a34a;
    class done good;
"""


def test_flowgraph_state_diagram_subset():
    df, nodes, groups, direction = Flowgraph.from_mermaid(_STATE)
    assert direction == "TB" and groups == {}
    assert list(zip(df["source"], df["target"], df["label"])) == [
        ("__start__", "pending", "created"),
        ("pending", "done", "ok: all checks"),
        ("pending", "failed", ""),
        ("done", "__end__", ""),
        ("failed", "__end__", ""),
    ]
    assert nodes["__start__"] == {
        "label": "",
        "shape": "circle",
        "color": "#8c8c8c",
        "tooltip": "start",
    }
    assert nodes["__end__"]["tooltip"] == "end"
    # Notes go to the tooltip, escaped (tooltips may hold HTML), with their newlines kept.
    assert (
        nodes["pending"]["tooltip"]
        == "Waits for &lt;b&gt;review&lt;/b&gt;<br>then continues"
    )
    assert nodes["done"]["tooltip"] == "finished"
    assert nodes["done"]["color"] == "#dcfce7"


def test_flowgraph_state_referenced_before_declared_and_v1_header():
    df, nodes, _, _ = Flowgraph.from_mermaid(
        "stateDiagram\n class idle quiet\n classDef quiet fill:#eee\n idle --> busy"
    )
    assert list(nodes)[:2] == ["idle", "busy"] and nodes["idle"]["color"] == "#eee"
    assert len(df) == 1


@pytest.mark.parametrize(
    "line",
    [
        "state A {",
        "state c <<choice>>",
        'state "Long name" as A',
        "direction XY",
        "A : description",
        "}",
        "class A",
        "classDef x",
    ],
)
def test_flowgraph_state_unsupported_syntax_names_the_line(line):
    with pytest.raises(ValueError, match="line 3 is not supported") as err:
        Flowgraph.from_mermaid("stateDiagram-v2\n  [*] --> A\n  %s\n" % line)
    assert repr(line) in str(err.value)


def test_flowgraph_state_unterminated_note():
    with pytest.raises(ValueError, match="end note"):
        Flowgraph.from_mermaid(
            "stateDiagram-v2\n  A --> B\n  note right of A\n  text\n"
        )


def test_flowgraph_renders_state_diagram():
    d3, html = _render(_STATE)
    assert d3.config["direction"] == "TB"
    names = [n["name"] for n in _data(html)["nodes"]]
    assert names[:2] == ["__start__", "pending"] and "__end__" in names


_MIXED_MARKDOWN = """# Several diagrams

```mermaid
sequenceDiagram
    A->>B: hi
```

```mermaid
erDiagram
    A ||--o{ B : has
```

```mermaid
stateDiagram-v2
    [*] --> s1
```

```mermaid
flowchart LR
    f1 --> f2
```
"""


def test_read_mermaid_kinds_picks_first_matching_block():
    assert Flowgraph.read_mermaid(_MIXED_MARKDOWN).startswith("stateDiagram-v2")
    assert Flowgraph.read_mermaid(
        _MIXED_MARKDOWN, kinds=Flowgraph.FLOWCHART_KINDS
    ).startswith("flowchart")
    assert Flowgraph.read_mermaid(
        _MIXED_MARKDOWN, kinds=("sequenceDiagram",)
    ).startswith("sequenceDiagram")
    assert Flowgraph.read_mermaid(_MIXED_MARKDOWN, kinds=("erDiagram",)).startswith(
        "erDiagram"
    )
    with pytest.raises(ValueError, match="journey"):
        Flowgraph.read_mermaid(_MIXED_MARKDOWN, kinds=("journey",))


@pytest.mark.parametrize(
    "path",
    sorted(FIXTURES.glob("*stateDiagram*.mmd"))
    + sorted(FIXTURES.glob("*flowchart*.mmd")),
    ids=lambda p: p.stem,
)
def test_flowgraph_trade_fixtures(path, caplog):
    log = logging.getLogger("test_flowgraph_fixtures")
    with caplog.at_level(logging.WARNING, logger=log.name):
        df, nodes, groups, _ = Flowgraph.from_mermaid(path, logger=log)
    assert not caplog.records, [r.getMessage() for r in caplog.records]
    _, html = _render(path)
    names = {n["name"] for n in _data(html)["nodes"]}
    assert set(nodes) <= names
    # Every state / node id written in the source appears in the payload.
    text = path.read_text(encoding="utf-8")
    if "stateDiagram" in text:
        ids = set(re.findall(r"^\s*(\w+|\[\*\])\s*-->\s*(\w+|\[\*\])", text, re.M))
        for a, b in ids:
            for ref in (a, b):
                assert (ref in names) or ref == "[*]"
        assert len(_data(html)["edges"]) == len(re.findall(r"-->", text))


def _steps():
    return [
        {
            "title": "Check",
            "caption": "Validate the input.",
            "highlight": {"nodes": ["check"], "edges": [("start", "check")]},
        },
        {"title": "Retry", "highlight": {"edges": [["fix", "check"]]}},
        {"caption": "No highlight: everything stays visible."},
    ]


def test_flowgraph_steps_in_payload():
    _, html = _render(_sample_df(), steps=_steps())
    steps = _data(html)["steps"]
    assert steps[0] == {
        "title": "Check",
        "caption": "Validate the input.",
        "highlight": {"nodes": ["check"], "edges": [["start", "check"]]},
    }
    assert (
        steps[1]["caption"] == ""
        and steps[2]["title"] == "Step 3"
        and steps[2]["highlight"] == {}
    )
    assert "D3BlocksWalkthrough" in html and "d3b-walk" in html


def test_flowgraph_without_steps_keeps_trace():
    _, html = _render(_sample_df())
    assert _data(html)["steps"] is None
    assert 'id="traceButton"' in html


@pytest.mark.parametrize(
    "steps, match",
    [
        ([{"highlight": {"nodes": ["nope"]}}], r"steps\[0\]: unknown node 'nope'"),
        (
            [{}, {"highlight": {"edges": [("done", "start")]}}],
            r"steps\[1\]: unknown edge \('done', 'start'\)",
        ),
        (
            [{"highlight": {"edges": ["start"]}}],
            r"steps\[0\]: edge must be \(source, target\) pairs",
        ),
        (
            [{"highlight": {"messages": [0]}}],
            r"steps\[0\]: highlight key\(s\) \['messages'\] are not supported by flowgraph",
        ),
        ([{"note": "x"}], r"steps\[0\]: unknown key\(s\) \['note'\]"),
        (["title"], r"steps\[0\]: expected a dict"),
        ({"title": "x"}, "steps must be a list"),
    ],
)
def test_flowgraph_steps_validation(steps, match):
    with pytest.raises(ValueError, match=match):
        _render(_sample_df(), steps=steps)


def test_flowgraph_steps_escaped_in_json():
    _, html = _render(
        _sample_df(),
        steps=[{"title": "</script><script>alert(1)</script>", "caption": "<b>x</b>"}],
    )
    assert "</script><script>alert(1)" not in html
    assert _data(html)["steps"][0]["title"] == "</script><script>alert(1)</script>"


@pytest.mark.parametrize(
    "dark_mode, flag",
    [(True, "true"), (False, "false"), ("auto", "auto"), ("AUTO", "auto")],
)
def test_flowgraph_dark_mode_flag(dark_mode, flag):
    _, html = _render(_sample_df(), dark_mode=dark_mode)
    assert 'data-dark-mode="%s"' % flag in html
    assert ('<body class="light"' in html) == (flag == "false")
    assert 'id="themeBtn"' in html and "D3BlocksTheme" in html


@pytest.mark.parametrize("dark_mode", ["light", 1, None, "yes"])
def test_flowgraph_dark_mode_rejects_other_values(dark_mode):
    with pytest.raises(ValueError, match="dark_mode"):
        _render(_sample_df(), dark_mode=dark_mode)


def test_flowgraph_output_stays_self_contained():
    _, html = _render(_sample_df(), steps=_steps(), dark_mode="auto")
    assert not re.search(r'<script[^>]+src=["\']https?:', html)
    assert not re.search(r'<link[^>]+href=["\']https?:', html)


# --- One rule for every Mermaid parser: understood, ignored, or a line-naming error ---


@pytest.mark.parametrize(
    "body, match",
    [
        ("A[Start] --> B{ok?", r"line 2 could not be parsed: 'A\[Start\] --> B\{ok\?'"),
        ("A --> B\n  click A callback", r"line 3 is not supported: 'click A callback'"),
        (
            "subgraph g\n  direction TB\n  A --> B\n  end",
            r"line 3 is not supported: 'direction TB'",
        ),
        ("A --> B\n  end", r'line 3: "end" without an open "subgraph"'),
        ("subgraph g [Group]\n  A --> B", r"line 2: subgraph 'g' has no \"end\""),
        (
            "subgraph g\n  A --> B\n  end\n  g --> A",
            r"line 5: 'A' is inside group 'g'",
        ),
        ("A --> B\n  class A", r"line 3 is not supported: 'class A'"),
        (
            "A --> B\n  linkStyle 1 stroke:#f00",
            r"line 3: linkStyle refers to link 1, but the diagram has 1 links",
        ),
        (
            "A --> B\n  linkStyle x stroke:#f00",
            r"line 3 is not supported: 'linkStyle x stroke:#f00'",
        ),
    ],
)
def test_flowgraph_flowchart_errors_name_the_line(body, match):
    with pytest.raises(ValueError, match=match):
        Flowgraph.from_mermaid("flowchart LR\n  %s\n" % body)


@pytest.mark.parametrize(
    "text",
    ["flowchrt LR\n A --> B", "flowchart XY\n A --> B", "sequenceDiagram\n A->>B: x"],
)
def test_flowgraph_wrong_header(text):
    with pytest.raises(
        ValueError, match="(Expected a Mermaid flowchart|line 1 is not supported)"
    ):
        Flowgraph.from_mermaid(text)


def test_flowgraph_link_style():
    df, _, _, _ = Flowgraph.from_mermaid(
        "flowchart LR\n A --> B --> C\n A ~~~ C\n C --> D\n"
        " linkStyle default stroke:#999,stroke-width:2px\n linkStyle 3 stroke:#e15759,stroke-dasharray:4 2"
    )
    # The invisible link (index 2) counts for the numbering but is not drawn.
    assert list(zip(df["source"], df["target"])) == [("A", "B"), ("B", "C"), ("C", "D")]
    assert list(df["color"]) == ["#999", "#999", "#e15759"]
    assert list(df["style"]) == ["solid", "solid", "dashed"]
    _, html = _render("flowchart LR\n A --> B\n linkStyle 0 stroke:#e15759")
    assert _data(html)["edges"][0]["color"] == "#e15759"


def test_flowgraph_state_direction():
    _, _, _, direction = Flowgraph.from_mermaid(
        "stateDiagram-v2\n direction LR\n [*] --> a"
    )
    assert direction == "LR"
    d3, _ = _render("stateDiagram-v2\n direction LR\n [*] --> a")
    assert d3.config["direction"] == "LR"
    d3, _ = _render(
        "stateDiagram-v2\n direction LR\n [*] --> a", direction="TB"
    )  # the argument wins
    assert d3.config["direction"] == "TB"


_ACC = """  accTitle: Checkout
  accDescr: How an order is paid
  accDescr {
    A longer description
    over two lines
  }
  %% a comment
"""


def test_flowgraph_ignores_accessibility_metadata_and_comments():
    df, nodes, _, _ = Flowgraph.from_mermaid(
        '%%{init: {"theme": "base"}}%%\nflowchart LR\n' + _ACC + "  A --> B\n"
    )
    assert list(nodes) == ["A", "B"] and len(df) == 1
    df, nodes, _, _ = Flowgraph.from_mermaid(
        "stateDiagram-v2\n" + _ACC + "  [*] --> a\n"
    )
    assert "a" in nodes and len(df) == 1


# --- Links to and from subgraphs / groups ----------------------------------------

_WORKERS = """flowchart LR
  subgraph Workers ["Background Workers"]
    W1[scheduler]
    W2[sync]
    subgraph AgentWorkers ["AI agents"]
      A1[narrator]
    end
  end
  subgraph Adapters
    S[Schwab]
  end
  Workers --> PG[(PostgreSQL)]
  AgentWorkers --> LLM[LLM factory]
  Workers --> Adapters
"""


def test_flowgraph_mermaid_links_to_subgraphs():
    df, nodes, groups, _ = Flowgraph.from_mermaid(_WORKERS)
    assert list(zip(df["source"], df["target"])) == [
        ("Workers", "PG"),
        ("AgentWorkers", "LLM"),
        ("Workers", "Adapters"),
    ]
    # Linked subgraphs are groups, not nodes.
    assert not {"Workers", "AgentWorkers", "Adapters"} & set(nodes)
    assert groups["AgentWorkers"]["parent"] == "Workers"
    _, html = _render(_WORKERS)
    data = _data(html)
    names = {n["name"] for n in data["nodes"]}
    assert names == {"W1", "W2", "A1", "S", "PG", "LLM"}
    assert {g["name"] for g in data["groups"]} >= {
        "Workers",
        "AgentWorkers",
        "Adapters",
    }
    assert ("Workers", "PG") in {(e["source"], e["target"]) for e in data["edges"]}


def test_flowgraph_link_before_its_subgraph():
    df, nodes, groups, _ = Flowgraph.from_mermaid(
        "flowchart LR\n  G --> B\n  subgraph G\n    A\n  end\n"
    )
    assert "G" not in nodes and "G" in groups
    assert list(zip(df["source"], df["target"])) == [("G", "B")]


def test_flowgraph_group_with_only_a_nested_group_is_a_link_end():
    text = "flowchart LR\n  subgraph Outer\n    subgraph Inner\n      A\n    end\n  end\n  Outer --> B\n"
    _, nodes, groups, _ = Flowgraph.from_mermaid(text)
    assert "Outer" not in nodes
    _, html = _render(text)
    assert "Outer" not in {n["name"] for n in _data(html)["nodes"]}


def test_flowgraph_link_to_empty_subgraph_is_a_node_with_its_title():
    _, nodes, _, _ = Flowgraph.from_mermaid(
        'flowchart LR\n  subgraph E ["Empty box"]\n  end\n  A --> E\n'
    )
    assert nodes["E"]["label"] == "Empty box"


def test_flowgraph_style_on_unlinked_subgraph_unchanged():
    # As before: a style on a subgraph that no link names gives it a stray node entry.
    _, nodes, groups, _ = Flowgraph.from_mermaid(
        "flowchart LR\n  subgraph G\n    A --> B\n  end\n  style G fill:#f00\n"
    )
    assert nodes["G"]["color"] == "#f00" and "G" in groups


@pytest.mark.parametrize(
    "text, match",
    [
        ("subgraph G\n    A\n  end\n  G --> G", r"line 5: .*'G'.* itself"),
        ("subgraph G\n    A\n  end\n  G --> A", r"line 5: .*'A' is inside group 'G'"),
        (
            "subgraph G\n    subgraph H\n      A\n    end\n  end\n  H --> G",
            r"line 7: .*'H' is inside group 'G'",
        ),
        (
            "subgraph G\n    A\n  end\n  G[Label] --> B",
            r"line 5: .*'G' is a subgraph and also a node",
        ),
        (
            "subgraph G\n    A\n  end\n  G --> B\n  style G fill:#f00",
            r"line 6: .*'G' is a subgraph and also a node",
        ),
        (
            "subgraph G\n    A\n  end\n  G --> B\n  class G warm",
            r"line 6: .*'G' is a subgraph and also a node",
        ),
    ],
)
def test_flowgraph_subgraph_link_errors(text, match):
    with pytest.raises(ValueError, match=match):
        Flowgraph.from_mermaid("flowchart LR\n  %s\n" % text)


def test_flowgraph_dataframe_group_endpoints():
    edges = pd.DataFrame({"source": ["G", "a"], "target": ["b", "c"]})
    nodes = {"a": {"group": "G"}}
    d3, html = _render(edges, nodes=nodes, groups={"G": {"label": "Group G"}})
    data = _data(html)
    assert "G" not in {n["name"] for n in data["nodes"]}
    assert "G" in {g["name"] for g in data["groups"]}
    assert "G" not in d3.node_properties


def test_flowgraph_dataframe_backward_compatible_names_stay_nodes():
    edges = pd.DataFrame({"source": ["G", "H"], "target": ["b", "c"]})
    # G is only implied by a node's group attribute; H is in groups= but has no members.
    d3, html = _render(edges, nodes={"a": {"group": "G"}}, groups={"H": {}})
    names = {n["name"] for n in _data(html)["nodes"]}
    assert {"G", "H"} <= names


def test_flowgraph_dataframe_group_link_errors():
    edges = pd.DataFrame({"source": ["G"], "target": ["a"]})
    with pytest.raises(
        ValueError, match=r"Edge \('G', 'a'\): .*'a' is inside group 'G'"
    ):
        _render(edges, nodes={"a": {"group": "G"}}, groups={"G": {}})


def test_flowgraph_steps_name_group_edges():
    _, html = _render(
        _WORKERS,
        steps=[{"title": "Writes", "highlight": {"edges": [("Workers", "PG")]}}],
    )
    assert _data(html)["steps"][0]["highlight"]["edges"] == [["Workers", "PG"]]


def test_flowgraph_trade_system_overview_group_links():
    path = FIXTURES / "system-architecture_0_flowchart.mmd"
    _, html = _render(path)
    data = _data(html)
    pairs = {(e["source"], e["target"]) for e in data["edges"]}
    names = {n["name"] for n in data["nodes"]}
    groups = {g["name"] for g in data["groups"]}
    text = path.read_text(encoding="utf-8")
    for a, b in [
        ("Workers", "PG"),
        ("Workers", "SchwabAdapter"),
        ("AgentWorkers", "FinnhubAdapter"),
        ("AgentWorkers", "LLMFactory"),
    ]:
        assert (a, b) in pairs and a in groups and a not in names
    # Every link written in the source is in the payload.
    assert len(data["edges"]) == len(re.findall(r"-->|-\.->|==>", text))
