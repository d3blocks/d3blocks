# Content checks for d3blocks (no d3blocks required).

from pathlib import Path

ROOT = Path(__file__).resolve().parent


def test_skill_md_has_no_inline_streamlit_app():
    text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    assert "examples/streamlit_" in text
    # Full streamlit apps live under examples/, not SKILL.md
    assert "st.set_page_config" not in text
    assert "@st.cache_data" not in text
    assert "d3.scatter(df," not in text.replace(" ", "")


def test_skill_points_to_advanced_examples():
    text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    for name in (
        "scatter_advanced.py",
        "chord_advanced.py",
        "flowgraph_advanced.py",
        "streamlit_scatter.py",
        "streamlit_chord.py",
        "streamlit_flowgraph.py",
    ):
        assert name in text, name


def test_reference_files_exist():
    for name in ("scatter.md", "chord.md", "flowgraph.md", "streamlit.md"):
        p = ROOT / "references" / name
        assert p.is_file() and p.stat().st_size > 200


def test_advanced_examples_exist_and_are_rich():
    cases = {
        "scatter_advanced.py": ("label_radio", "tooltip", "x1="),
        "chord_advanced.py": ("set_node_properties", "Nuclear", "edge_properties"),
        "flowgraph_advanced.py": ('layout="elk"', "stateDiagram", "groups"),
    }
    for name, needles in cases.items():
        text = (ROOT / "examples" / name).read_text(encoding="utf-8")
        for n in needles:
            assert n in text, (name, n)


def test_streamlit_examples_use_iframe_pattern():
    for name in ("streamlit_scatter.py", "streamlit_chord.py", "streamlit_flowgraph.py"):
        text = (ROOT / "examples" / name).read_text(encoding="utf-8")
        assert "return_html=True" in text
        assert "showfig=False" in text
        assert "st.iframe" in text
        assert "@st.cache_data" in text
        assert "color_background" in text


def test_no_basic_stubs_left():
    for name in ("scatter_basic.py", "chord_basic.py", "flowgraph_basic.py"):
        assert not (ROOT / "examples" / name).exists(), name


if __name__ == "__main__":
    for t in [
        test_skill_md_has_no_inline_streamlit_app,
        test_skill_points_to_advanced_examples,
        test_reference_files_exist,
        test_advanced_examples_exist_and_are_rich,
        test_streamlit_examples_use_iframe_pattern,
        test_no_basic_stubs_left,
    ]:
        t()
        print("ok", t.__name__)
    print("All tests passed.")
