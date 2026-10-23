import colourmap
import pandas as pd

from d3blocks.movingbubbles.Movingbubbles import set_config, set_edge_properties


def _make_df():
    return pd.DataFrame(
        {
            "row_id": [0, 1, 2, 3],
            "datetime": pd.to_datetime(
                [
                    "2023-01-01 00:00:00",
                    "2023-01-01 00:01:00",
                    "2023-01-01 00:02:00",
                    "2023-01-01 00:03:00",
                ]
            ),
            "sample_id": [1, 2, 1, 2],
            "state": ["A", "B", "A", "B"],
        }
    )


def test_movingbubbles_color_series_categories_uses_cmap():
    df = _make_df()
    categories = pd.Series(["Netherlands", "Germany", "Netherlands", "Norway"])

    out = set_edge_properties(
        df,
        datetime="datetime",
        sample_id="sample_id",
        state="state",
        color=categories,
        standardize="samplewise",
        timedelta="minutes",
        config={"cmap": "Dark2"},
    )

    expected = [
        str(c)
        for c in colourmap.fromlist(
            categories.astype(str).values,
            cmap="Dark2",
            scheme="hex",
            method="matplotlib",
            verbose=0,
        )[0]
    ]

    out_by_input_order = out.sort_values("row_id").reset_index(drop=True)
    assert out_by_input_order["color"].tolist() == expected


def test_movingbubbles_color_method_auto_resolves_to_node_when_color_given():
    cfg = set_config(config={}, color_method="auto", color=["A", "B"])
    assert cfg["color_method"] == "NODE"


def test_movingbubbles_color_method_auto_resolves_to_state_without_color():
    cfg = set_config(config={}, color_method="auto", color=None)
    assert cfg["color_method"] == "STATE"


def test_movingbubbles_color_dict_categories_uses_cmap():
    df = _make_df()
    category_by_sample = {1: "group_a", 2: "group_b"}

    out = set_edge_properties(
        df,
        datetime="datetime",
        sample_id="sample_id",
        state="state",
        color=category_by_sample,
        standardize="samplewise",
        timedelta="minutes",
        cmap="Set2",
    )

    mapped = [
        str(c)
        for c in colourmap.fromlist(
            list(category_by_sample.values()),
            cmap="Set2",
            scheme="hex",
            method="matplotlib",
            verbose=0,
        )[0]
    ]
    expected_by_row = [mapped[0], mapped[1], mapped[0], mapped[1]]

    out_by_input_order = out.sort_values("row_id").reset_index(drop=True)
    assert out_by_input_order["color"].tolist() == expected_by_row
