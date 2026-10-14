"""Tests for the Flowgraph block (process flows and architecture diagrams)."""
import json
import re

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

    edges = {(s, t): (lab, st, w) for s, t, lab, st, w in df.itertuples(index=False)}
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
        'flowchart LR\n clickstream --> kafka\n directions_api --> b\n click kafka callback\n linkStyle 0 stroke:#f00')
    assert list(zip(df['source'], df['target'])) == [('clickstream', 'kafka'), ('directions_api', 'b')]
    assert 'click' not in nodes and 'linkStyle' not in nodes


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
    with pytest.raises(ValueError, match='No Mermaid flowchart nodes'):
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
