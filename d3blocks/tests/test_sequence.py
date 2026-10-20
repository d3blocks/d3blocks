"""Tests for the Sequence block (sequence diagrams)."""

import json
import logging
import re
from pathlib import Path

import pandas as pd
import pytest

from d3blocks import D3Blocks
from d3blocks.sequence import Sequence

FIXTURES = Path(__file__).parent / 'fixtures' / 'trade'

_MERMAID = '''%%{init: {"theme": "base"}}%%
sequenceDiagram
    %% a comment
    actor Op as Operator
    participant UI as Trade App (UI)
    participant API
    rect rgb(236, 254, 255)
        Op->>UI: Click "Connect"
        UI->>API: GET /authorize
    end
    rect rgba(254, 243, 199, 0.5)
        API-->>UI: Redirect<br>to consent
    end
    UI->>DB: store: state
'''


def _data(html):
    return json.loads(re.search(r'<script type="application/json" id="sq-data">(.*?)</script>', html, re.S).group(1))


def _options(html):
    return json.loads(re.search(r'<script type="application/json" id="sq-options">(.*?)</script>', html, re.S).group(1))


def _render(df, **kwargs):
    d3 = D3Blocks(frame=False, support=None, verbose='error')
    html = d3.sequence(df, filepath=None, showfig=False, return_html=True, **kwargs)
    return d3, html


def _df():
    return pd.DataFrame(
        {
            'source': ['app', 'auth', 'app'],
            'target': ['auth', 'app', 'api'],
            'label': ['login', 'token', 'call'],
            'style': ['sync', 'reply', 'sync'],
        }
    )


def test_sequence_mermaid_subset():
    df, participants, groups = Sequence.from_mermaid(_MERMAID)
    assert list(participants) == ['Op', 'UI', 'API', 'DB']  # declaration order, then first appearance
    assert participants['Op'] == {'kind': 'actor', 'label': 'Operator'}
    assert participants['UI'] == {'kind': 'participant', 'label': 'Trade App (UI)'}
    assert participants['API'] == {'kind': 'participant'} and participants['DB'] == {}
    assert list(df['style']) == ['sync', 'sync', 'reply', 'sync']
    assert list(df['label']) == ['Click "Connect"', 'GET /authorize', 'Redirect\nto consent', 'store: state']
    assert groups == [
        {'label': '', 'from': 0, 'to': 1, 'color': 'rgb(236,254,255)'},
        {'label': '', 'from': 2, 'to': 2, 'color': 'rgba(254,243,199,0.5)'},
    ]


def test_sequence_renders_mermaid():
    d3, html = _render(_MERMAID)
    data = _data(html)
    by_name = {p['name']: p for p in data['participants']}
    assert by_name['Op']['kind'] == 'actor' and by_name['Op']['label'] == 'Operator'
    assert by_name['DB']['label'] == 'DB' and by_name['DB']['color']
    assert [m['style'] for m in data['messages']] == ['sync', 'sync', 'reply', 'sync']
    assert data['groups'][0]['from'] == 0 and data['groups'][0]['to'] == 1
    assert 'id="sq-svg"' in html and 'd3js.org' in html


@pytest.mark.parametrize(
    'line',
    [
        'autonumber',
        'A->>+B: activate',
        'A-)B: async',
        'A->B: open',
        'note over A: x',
        'loop every minute',
        'alt ok',
        'A->>A: self',
    ],
)
def test_sequence_unsupported_statements_name_the_line(line):
    with pytest.raises(ValueError, match='line 3') as err:
        Sequence.from_mermaid('sequenceDiagram\n  A->>B: hi\n  %s\n' % line)
    assert line in str(err.value)


def test_sequence_unbalanced_rect():
    with pytest.raises(ValueError, match='line 2: "rect" has no "end"'):
        Sequence.from_mermaid('sequenceDiagram\n rect rgb(1,2,3)\n A->>B: x\n')
    with pytest.raises(ValueError, match='line 3: "rect" contains no messages'):
        Sequence.from_mermaid('sequenceDiagram\n A->>B: x\n rect rgb(1,2,3)\n end\n')
    with pytest.raises(ValueError, match='without an open "rect"'):
        Sequence.from_mermaid('sequenceDiagram\n A->>B: x\n end\n')


def test_sequence_dataframe_input_and_participants():
    participants = {
        'app': {'label': 'Mobile app', 'kind': 'actor', 'color': '#ff0000', 'tooltip': 'iOS'},
        'api': {'label': 'API'},
    }
    d3, html = _render(_df(), participants=participants)
    data = _data(html)
    assert [p['name'] for p in data['participants']] == ['app', 'api', 'auth']
    assert data['participants'][0] == {
        'name': 'app',
        'label': 'Mobile app',
        'kind': 'actor',
        'color': '#ff0000',
        'tooltip': 'iOS',
    }
    assert [m['style'] for m in data['messages']] == ['sync', 'reply', 'sync']
    assert data['messages'][0]['color'] is None  # default messages use the theme colour


def test_sequence_variants_and_unknown_style():
    df = _df().assign(variant=['emphasis', 'default', 'nope'], style=['sync', 'bogus', 'reply'])
    _, html = _render(df)
    msgs = _data(html)['messages']
    assert msgs[0]['variant'] == 'emphasis' and msgs[0]['color'] and msgs[0]['width'] > 1.5
    assert msgs[1]['style'] == 'sync' and msgs[2]['variant'] == 'default'


def test_sequence_missing_columns_and_self_messages():
    with pytest.raises(ValueError, match='missing column'):
        _render(pd.DataFrame({'source': ['a']}))
    with pytest.raises(ValueError, match='Self-messages'):
        _render(pd.DataFrame({'source': ['a'], 'target': ['a']}))


def test_sequence_escapes_html():
    df = pd.DataFrame({'source': ['<script>alert(1)</script>'], 'target': ['b'], 'label': ['</script><b>x']})
    _, html = _render(df, title='<script>t</script>')
    assert '<script>alert(1)</script>' not in html and '</script><b>x' not in html
    assert '<title>&lt;script&gt;t&lt;/script&gt;</title>' in html
    assert _data(html)['messages'][0]['label'] == '</script><b>x'


def test_sequence_default_steps_one_per_message():
    _, html = _render(_df(), participants={'app': {'label': 'App'}})
    steps = _data(html)['steps']
    assert len(steps) == 3
    assert steps[0] == {'title': '1. App → auth', 'caption': 'login', 'highlight': {'messages': [0]}}


def test_sequence_custom_steps_and_validation():
    steps = [
        {'title': 'Sign in', 'caption': 'Get a token', 'highlight': {'messages': [0, 1], 'participants': ['auth']}}
    ]
    _, html = _render(_df(), steps=steps)
    assert _data(html)['steps'] == [
        {'title': 'Sign in', 'caption': 'Get a token', 'highlight': {'messages': [0, 1], 'participants': ['auth']}}
    ]
    _, html = _render(_df(), steps=[])
    assert _data(html)['steps'] == []
    with pytest.raises(ValueError, match=r'steps\[0\]: unknown message 3'):
        _render(_df(), steps=[{'highlight': {'messages': [3]}}])
    with pytest.raises(ValueError, match=r"steps\[1\]: unknown participant 'db'"):
        _render(_df(), steps=[{}, {'highlight': {'participants': ['db']}}])
    with pytest.raises(ValueError, match=r"not supported by sequence"):
        _render(_df(), steps=[{'highlight': {'nodes': ['app']}}])


def test_sequence_groups_validation():
    _, html = _render(_df(), groups=[{'label': 'Auth', 'from': 0, 'to': 1}])
    assert _data(html)['groups'] == [{'label': 'Auth', 'from': 0, 'to': 1, 'color': Sequence.DEFAULT_REGION_COLOR}]
    with pytest.raises(ValueError, match='out of range'):
        _render(_df(), groups=[{'from': 1, 'to': 5}])


def test_sequence_output_is_self_contained():
    _, html = _render(_MERMAID, dark_mode='auto')
    assert not re.search(r'<script[^>]+src=["\']https?:', html)
    assert not re.search(r'<link[^>]+href=["\']https?:', html)
    assert 'D3BlocksWalkthrough' in html and 'D3BlocksTheme' in html


def test_sequence_registered_as_chart():
    d3 = D3Blocks(chart='sequence', frame=False, verbose='error')
    assert d3.chart is Sequence
    assert d3.config['chart'] == 'Sequence'


def test_sequence_notebook_and_panels():
    _, html = _render(_df(), notebook=True, figsize=[800, 500])
    assert html.startswith('<div class="d3blocks-sequence"><iframe srcdoc=') and 'width:800px;height:500px' in html
    _, html = _render(_df(), show_side_panel=False, show_top_panel=False, save_button=False)
    assert 'id="exportPanel"' not in html and 'class="top-panel"' not in html


@pytest.mark.parametrize('dark_mode, flag', [(True, 'true'), (False, 'false'), ('auto', 'auto')])
def test_sequence_dark_mode(dark_mode, flag):
    _, html = _render(_df(), dark_mode=dark_mode)
    assert 'data-dark-mode="%s"' % flag in html and 'id="themeBtn"' in html


def test_sequence_dark_mode_rejects_other_values():
    with pytest.raises(ValueError, match='dark_mode'):
        _render(_df(), dark_mode='dark')


def test_sequence_node_properties_editable():
    d3, _ = _render(_df())
    d3.node_properties['app']['label'] = 'Edited'
    html = d3.show()
    assert _data(html)['participants'][0]['label'] == 'Edited'


def test_sequence_frame_mode():
    d3 = D3Blocks(support=None, verbose='error')  # frame=True: properties as DataFrames
    html = d3.sequence(_df(), filepath=None, showfig=False, return_html=True)
    assert isinstance(d3.node_properties, pd.DataFrame)
    assert [p['name'] for p in _data(html)['participants']] == ['app', 'auth', 'api']


def test_sequence_finds_its_block_in_mixed_markdown(tmp_path):
    md = tmp_path / 'doc.md'
    md.write_text(
        '```mermaid\nflowchart LR\n a --> b\n```\n\n```mermaid\nsequenceDiagram\n X->>Y: hi\n```\n', encoding='utf-8'
    )
    _, html = _render(md)
    assert [p['name'] for p in _data(html)['participants']] == ['X', 'Y']


@pytest.mark.parametrize('path', sorted(FIXTURES.glob('*sequenceDiagram*.mmd')), ids=lambda p: p.stem)
def test_sequence_trade_fixtures(path, caplog):
    log = logging.getLogger('test_sequence_fixtures')
    with caplog.at_level(logging.WARNING, logger=log.name):
        df, participants, groups = Sequence.from_mermaid(path, logger=log)
    assert not caplog.records
    _, html = _render(path)
    data = _data(html)
    text = path.read_text(encoding='utf-8')
    # Every participant and message in the source appears in the payload.
    declared = re.findall(r'^\s*(?:participant|actor)\s+(\S+)', text, re.M)
    names = [p['name'] for p in data['participants']]
    assert names[: len(declared)] == declared
    assert len(data['messages']) == len(re.findall(r'-?->>', text))
    assert len(data['groups']) == len(re.findall(r'^\s*rect\b', text, re.M))
    assert len(data['steps']) == len(data['messages'])


def test_sequence_hyphenated_ids_and_quoted_aliases():
    df, participants, _ = Sequence.from_mermaid(
        'sequenceDiagram\n participant auth-svc as "Auth service"\n api-gw->>auth-svc: login\n auth-svc-->>api-gw: "token"\n'
    )
    assert list(participants) == ['auth-svc', 'api-gw']
    assert participants['auth-svc']['label'] == 'Auth service'
    assert list(zip(df['source'], df['target'], df['style'])) == [
        ('api-gw', 'auth-svc', 'sync'),
        ('auth-svc', 'api-gw', 'reply'),
    ]
    assert df['label'][1] == 'token'


def test_sequence_ignores_accessibility_metadata_and_init():
    df, participants, _ = Sequence.from_mermaid(
        '%%{init: {"theme": "base"}}%%\nsequenceDiagram\n  accTitle: Login\n  accDescr: The login flow\n  A->>B: hi\n'
    )
    assert list(participants) == ['A', 'B'] and len(df) == 1


def test_sequence_header_typo():
    with pytest.raises(ValueError, match="first statement is 'sequenceDiagra'"):
        Sequence.from_mermaid('sequenceDiagra\n  A->>B: hi')
