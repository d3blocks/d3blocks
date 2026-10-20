"""Tests for the ERD block (entity-relationship diagrams)."""

import json
import logging
import re
from pathlib import Path

import pandas as pd
import pytest

from d3blocks import D3Blocks
from d3blocks.erd import Erd

FIXTURES = Path(__file__).parent / "fixtures" / "trade"

_MERMAID = """erDiagram
    %% comment
    customers ||--o{ orders : places
    orders }|..|{ products : "lists (M:N)"
    customers |o--o| loyalty : has
    orders o|--|| invoices : billed
    customers {
        uuid id PK
        text email UK "login, unique"
    }
    orders {
        uuid id PK
        uuid customer_id FK
        uuid order_id PK, FK
        numeric total
    }
"""


def _data(html):
    return json.loads(
        re.search(
            r'<script type="application/json" id="er-data">(.*?)</script>', html, re.S
        ).group(1)
    )


def _options(html):
    return json.loads(
        re.search(
            r'<script type="application/json" id="er-options">(.*?)</script>',
            html,
            re.S,
        ).group(1)
    )


def _render(df, **kwargs):
    d3 = D3Blocks(frame=False, support=None, verbose="error")
    html = d3.erd(df, filepath=None, showfig=False, return_html=True, **kwargs)
    return d3, html


def _df():
    return pd.DataFrame(
        {
            "source": ["customers", "orders"],
            "target": ["orders", "lines"],
            "source_card": ["one", "one"],
            "target_card": ["zero_or_more", "one_or_more"],
            "label": ["places", "contains"],
            "identifying": [True, False],
        }
    )


def test_erd_mermaid_subset():
    df, entities, direction = Erd.from_mermaid(_MERMAID)
    assert direction is None
    assert list(
        df[
            ["source", "target", "source_card", "target_card", "label", "identifying"]
        ].itertuples(index=False, name=None)
    ) == [
        ("customers", "orders", "one", "zero_or_more", "places", True),
        ("orders", "products", "one_or_more", "one_or_more", "lists (M:N)", False),
        ("customers", "loyalty", "zero_or_one", "zero_or_one", "has", True),
        ("orders", "invoices", "zero_or_one", "one", "billed", True),
    ]
    assert entities["customers"]["columns"] == [
        {"name": "id", "type": "uuid", "key": "PK", "comment": ""},
        {"name": "email", "type": "text", "key": "UK", "comment": "login, unique"},
    ]
    assert entities["orders"]["columns"][2] == {
        "name": "order_id",
        "type": "uuid",
        "key": "PK,FK",
        "comment": "",
    }
    assert entities["orders"]["columns"][3]["key"] == ""
    assert entities["products"] == {}  # used only in relationships: no columns


def test_erd_renders_mermaid():
    _, html = _render(_MERMAID)
    data = _data(html)
    by_name = {e["name"]: e for e in data["entities"]}
    assert set(by_name) == {"customers", "orders", "products", "loyalty", "invoices"}
    assert (
        by_name["products"]["columns"] == []
        and by_name["customers"]["color"] == Erd.DEFAULT_ENTITY_COLOR
    )
    assert [r["identifying"] for r in data["relationships"]] == [
        True,
        False,
        True,
        True,
    ]
    assert data["steps"] is None
    assert "dagre" in html and "d3js.org" in html


@pytest.mark.parametrize(
    "line",
    [
        "direction XY",
        "customers ||--o< orders : x",
        "customers }}--o{ orders : x",
        'p["Person"]',
        "customers ||-o{ orders : x",
    ],
)
def test_erd_unsupported_statements_name_the_line(line):
    with pytest.raises(ValueError, match="line 3") as err:
        Erd.from_mermaid("erDiagram\n  a ||--o{ b : x\n  %s\n" % line)
    assert repr(line) in str(err.value) or line in str(err.value)


def test_erd_bad_column_and_unclosed_entity():
    with pytest.raises(ValueError, match="line 3: unsupported column"):
        Erd.from_mermaid("erDiagram\n a {\n just_one_token\n }\n")
    with pytest.raises(ValueError, match="line 2: entity 'a' has no closing"):
        Erd.from_mermaid("erDiagram\n a {\n uuid id PK\n")


def test_erd_dataframe_input_and_entities():
    entities = {
        "customers": {
            "label": "Customers",
            "color": "#ff0000",
            "tooltip": "People",
            "columns": [{"name": "id", "type": "uuid", "key": "pk"}, "email"],
        },
        "audit": {"columns": [{"name": "id", "key": "PK, FK"}]},
    }
    _, html = _render(_df(), entities=entities)
    data = _data(html)
    by_name = {e["name"]: e for e in data["entities"]}
    assert [e["name"] for e in data["entities"]] == [
        "customers",
        "audit",
        "orders",
        "lines",
    ]
    assert by_name["customers"]["columns"] == [
        {"name": "id", "type": "uuid", "key": "PK", "comment": ""},
        {"name": "email", "type": "", "key": "", "comment": ""},
    ]
    assert (
        by_name["audit"]["columns"][0]["key"] == "PK,FK"
    )  # isolated entity, comma list normalized
    assert data["relationships"][1]["identifying"] is False


def test_erd_cardinality_defaults_and_unknown_values():
    df = pd.DataFrame(
        {"source": ["a", "b"], "target": ["b", "c"], "source_card": ["many", None]}
    )
    _, html = _render(df)
    rels = _data(html)["relationships"]
    assert rels[0]["source_card"] is None and rels[0]["target_card"] is None
    assert rels[0]["identifying"] is True and rels[0]["label"] == ""


def test_erd_bad_keys_and_missing_columns():
    with pytest.raises(ValueError, match="unknown key"):
        _render(
            _df(),
            entities={"customers": {"columns": [{"name": "id", "key": "PRIMARY"}]}},
        )
    with pytest.raises(ValueError, match="missing column"):
        _render(pd.DataFrame({"target": ["a"]}))


def test_erd_escapes_html():
    entities = {
        "<script>x</script>": {
            "columns": [{"name": "</script><b>", "type": "<i>", "comment": "</script>"}]
        }
    }
    df = pd.DataFrame(
        {"source": ["<script>x</script>"], "target": ["b"], "label": ["</script>"]}
    )
    _, html = _render(df, entities=entities)
    assert "<script>x</script>" not in html and "</script><b>" not in html
    assert _data(html)["entities"][0]["columns"][0]["name"] == "</script><b>"


def test_erd_options():
    _, html = _render(
        _df(),
        direction="td",
        show_columns="keys",
        show_types=False,
        nodesep=10,
        ranksep=20,
    )
    opts = _options(html)
    assert (
        opts["direction"],
        opts["showColumns"],
        opts["showTypes"],
        opts["nodesep"],
        opts["ranksep"],
    ) == (
        "TB",
        "keys",
        False,
        10,
        20,
    )
    _, html = _render(_df(), show_columns="bogus")
    assert _options(html)["showColumns"] == "all"


def test_erd_steps():
    steps = [
        {
            "title": "Orders",
            "caption": "A customer places orders.",
            "highlight": {"nodes": ["customers"], "edges": [("orders", "customers")]},
        }
    ]
    _, html = _render(_df(), steps=steps)
    # Relationship references work in either order and are stored as written in the data.
    assert _data(html)["steps"][0]["highlight"] == {
        "nodes": ["customers"],
        "edges": [["customers", "orders"]],
    }
    with pytest.raises(ValueError, match=r"steps\[0\]: unknown entity 'nope'"):
        _render(_df(), steps=[{"highlight": {"nodes": ["nope"]}}])
    with pytest.raises(
        ValueError, match=r"steps\[0\]: unknown relationship \('customers', 'lines'\)"
    ):
        _render(_df(), steps=[{"highlight": {"edges": [("customers", "lines")]}}])
    with pytest.raises(ValueError, match="not supported by erd"):
        _render(_df(), steps=[{"highlight": {"messages": [0]}}])


def test_erd_output_is_self_contained():
    _, html = _render(_MERMAID, dark_mode="auto", steps=[{"title": "x"}])
    assert not re.search(r'<script[^>]+src=["\']https?:', html)
    assert not re.search(r'<link[^>]+href=["\']https?:', html)


def test_erd_registered_as_chart():
    d3 = D3Blocks(chart="erd", frame=False, verbose="error")
    assert d3.chart is Erd and d3.config["chart"] == "Erd"


def test_erd_notebook_and_panels():
    _, html = _render(_df(), notebook=True)
    assert (
        html.startswith('<div class="d3blocks-erd"><iframe srcdoc=')
        and "width:100%;height:650px" in html
    )
    _, html = _render(_df(), show_side_panel=False, show_top_panel=False)
    assert 'id="exportPanel"' not in html and 'class="top-panel"' not in html


@pytest.mark.parametrize(
    "dark_mode, flag", [(True, "true"), (False, "false"), ("auto", "auto")]
)
def test_erd_dark_mode(dark_mode, flag):
    _, html = _render(_df(), dark_mode=dark_mode)
    assert 'data-dark-mode="%s"' % flag in html and 'id="themeBtn"' in html


def test_erd_dark_mode_rejects_other_values():
    with pytest.raises(ValueError, match="dark_mode"):
        _render(_df(), dark_mode=0)


def test_erd_frame_mode_and_editing():
    d3 = D3Blocks(support=None, verbose="error")  # frame=True
    d3.erd(_MERMAID, filepath=None, showfig=False)
    assert isinstance(d3.node_properties, pd.DataFrame)
    d3.node_properties.loc[d3.node_properties["name"] == "orders", "label"] = "Orders"
    html = d3.show()
    by_name = {e["name"]: e for e in _data(html)["entities"]}
    assert (
        by_name["orders"]["label"] == "Orders"
        and len(by_name["orders"]["columns"]) == 4
    )


def test_erd_finds_its_block_in_mixed_markdown(tmp_path):
    md = tmp_path / "doc.md"
    md.write_text(
        "```mermaid\nsequenceDiagram\n A->>B: x\n```\n```mermaid\nerDiagram\n a ||--o{ b : has\n```\n",
        encoding="utf-8",
    )
    _, html = _render(md)
    assert [e["name"] for e in _data(html)["entities"]] == ["a", "b"]


@pytest.mark.parametrize(
    "path", sorted(FIXTURES.glob("*erDiagram*.mmd")), ids=lambda p: p.stem
)
def test_erd_trade_fixtures(path, caplog):
    log = logging.getLogger("test_erd_fixtures")
    with caplog.at_level(logging.WARNING, logger=log.name):
        df, entities, _ = Erd.from_mermaid(path, logger=log)
    assert not caplog.records
    _, html = _render(path)
    data = _data(html)
    text = path.read_text(encoding="utf-8")
    names = {e["name"] for e in data["entities"]}
    # Every entity (blocks and relationship ends) and every relationship appears in the payload.
    blocks = set(re.findall(r"^\s*(\w+)\s*\{\s*$", text, re.M))
    ends = set()
    for a, b in re.findall(
        r"^\s*(\w+)\s*[|}o]{2}(?:--|\.\.)[|{o]{2}\s*(\w+)", text, re.M
    ):
        ends |= {a, b}
    assert blocks | ends == names
    assert len(data["relationships"]) == len(
        re.findall(r"[|}o]{2}(?:--|\.\.)[|{o]{2}", text)
    )
    n_columns = sum(len(e["columns"]) for e in data["entities"])
    assert n_columns == sum(len(v.get("columns", [])) for v in entities.values())


@pytest.mark.parametrize(
    "value, expected",
    [
        ("false", False),
        ("No", False),
        ("0", False),
        (0, False),
        (False, False),
        ("true", True),
        ("yes", True),
        (1, True),
        (None, True),
        (float("nan"), True),
    ],
)
def test_erd_identifying_from_text_and_numbers(value, expected):
    df = pd.DataFrame(
        {
            "source": ["a"],
            "target": ["b"],
            "identifying": pd.Series([value], dtype=object),
        }
    )
    _, html = _render(df)
    assert _data(html)["relationships"][0]["identifying"] is expected


def test_erd_direction_from_mermaid_and_argument():
    d3, html = _render("erDiagram\n  direction TB\n  a ||--o{ b : has")
    assert _options(html)["direction"] == "TB"
    _, html = _render(
        "erDiagram\n  direction TB\n  a ||--o{ b : has", direction="RL"
    )  # the argument wins
    assert _options(html)["direction"] == "RL"
    _, html = _render("erDiagram\n  a ||--o{ b : has")
    assert _options(html)["direction"] == "LR"
    _, entities, _ = Erd.from_mermaid(
        "erDiagram\n  direction ||--o{ b : has"
    )  # an entity called direction
    assert set(entities) == {"direction", "b"}


def test_erd_ignores_accessibility_metadata():
    df, entities, _ = Erd.from_mermaid(
        "erDiagram\n  accTitle: Shop\n  accDescr {\n    two\n    lines\n  }\n  a ||--o{ b : has\n"
    )
    assert set(entities) == {"a", "b"} and len(df) == 1
