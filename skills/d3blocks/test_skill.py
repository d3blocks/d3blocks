# Content checks for d3blocks (no d3blocks required).

from pathlib import Path

ROOT = Path(__file__).resolve().parent
EXAMPLES = ROOT / "examples"
REFS = ROOT / "references"


def test_skill_md_has_no_inline_streamlit_app():
    text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    assert "examples/streamlit_" in text
    # Full streamlit apps live under examples/, not SKILL.md
    assert "st.set_page_config" not in text
    assert "@st.cache_data" not in text
    assert "d3.scatter(df," not in text.replace(" ", "")


def test_skill_describes_discovery_pattern():
    """SKILL.md should tell agents how to find docs/examples, not list every chart."""
    text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    assert "references/<chart>.md" in text
    assert "examples/<chart>_advanced.py" in text or "examples/" in text
    assert "python -m pydoc d3blocks.D3Blocks.<chart>" in text
    assert "references/streamlit.md" in text


def test_reference_files_exist():
    refs = sorted(p for p in REFS.glob("*.md"))
    assert refs, "references/ is empty"
    assert (REFS / "streamlit.md").is_file()
    for p in refs:
        assert p.stat().st_size > 100, p.name


def test_advanced_examples_exist_and_are_rich():
    # Known richness markers for charts we ship; any extra *_advanced.py only needs to exist.
    markers = {
        "scatter_advanced.py": ("label_radio", "tooltip", "x1="),
        "chord_advanced.py": ("set_node_properties", "Nuclear", "edge_properties"),
        "radialgraph_advanced.py": ("center=", "ring_spacing", "significance_test"),
        "flowgraph_advanced.py": ('layout="elk"', "stateDiagram", "groups"),
        "sankey_advanced.py": ("link=", "set_node_properties", "stroke_opacity"),
        "movingbubbles_advanced.py": ("random_time", "color_method", "set_node_properties"),

        "tree_advanced.py": ("hierarchy", "set_node_properties", "link_length"),
        "treemap_advanced.py": ("value=", "set_node_properties", "tooltip"),
        "violin_advanced.py": ("bins=", "x_order", "set_edge_properties"),

        "heatmap_advanced.py": ("cluster_params", "stormofswords", "bigbang"),
        "maps_advanced.py": ("surfspots", "country_names", "include_overseas"),
        "timeseries_advanced.py": ("climate", "datetime=", "dt_format"),

        "d3graph_advanced.py": ("scaler", "D3graph", "node_properties"),
        "elasticgraph_advanced.py": ("Elasticgraph", "hull_offset", "charge"),
        "circlepacking_advanced.py": ("size=", "zoom=", "border"),

        "matrix_advanced.py": ("scale=", "cmap=", "stroke"),
        "particles_advanced.py": ("particles", "shape=", "spacing"),
        "imageslider_advanced.py": ("southern_nebula", "imageslider", "before"),
        "sequence_advanced.py": ("sequenceDiagram", "style", "sequence"),
        "erd_advanced.py": ("erDiagram", "source_card", "erd"),
    }
    advanced = sorted(EXAMPLES.glob("*_advanced.py"))
    assert advanced, "no examples/*_advanced.py"
    for path in advanced:
        text = path.read_text(encoding="utf-8")
        for needle in markers.get(path.name, ()):
            assert needle in text, (path.name, needle)


def test_streamlit_examples_use_iframe_pattern():
    apps = sorted(EXAMPLES.glob("streamlit_*.py"))
    assert apps, "no examples/streamlit_*.py"
    for path in apps:
        text = path.read_text(encoding="utf-8")
        assert "return_html=True" in text, path.name
        assert "showfig=False" in text, path.name
        assert "st.iframe" in text, path.name
        assert "@st.cache_data" in text, path.name
        assert "color_background" in text, path.name


def test_no_basic_stubs_left():
    for name in ("scatter_basic.py", "chord_basic.py", "flowgraph_basic.py"):
        assert not (EXAMPLES / name).exists(), name


if __name__ == "__main__":
    for t in [
        test_skill_md_has_no_inline_streamlit_app,
        test_skill_describes_discovery_pattern,
        test_reference_files_exist,
        test_advanced_examples_exist_and_are_rich,
        test_streamlit_examples_use_iframe_pattern,
        test_no_basic_stubs_left,
    ]:
        t()
        print("ok", t.__name__)
    print("All tests passed.")
