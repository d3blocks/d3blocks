# AGENTS.md

Guidance for coding agents working in this repository (d3blocks library and related skills).

## Development setup

1. Install: `pip install -e .` or `pip install -r requirements.txt` (for the latest charts, often `pip install git+https://github.com/d3blocks/d3blocks` until a release is on PyPI).
2. Tests: `pytest` or `python -m pytest tests/`
3. Docs: `make docs` when Sphinx sources under `source/` apply.
4. Lint: `flake8` / `pylint` as configured in the repo.

Quick smoke check:

```bash
python -c "from d3blocks import D3Blocks; d3 = D3Blocks(); df = d3.import_example('energy'); d3.chord(df, showfig=False)"
```

## Common commands

- `python -m pytest tests/` — full suite
- `python -m pytest tests/test_<chart>.py` — one chart
- `pytest skills/d3blocks` — skill content checks + standalone examples (when d3blocks is installed)
- `streamlit run streamlit/<chart>_streamlit_demo.py` — interactive embed demos

## Code architecture

1. **`d3blocks.py`** — `D3Blocks` class: chart methods, `import_example`, `set_node_properties` / `set_edge_properties`, `show`, HTML return paths.
2. **Per-chart packages** — e.g. `scatter/`, `chord/`, `sankey/`, `d3graph/`, `radialgraph/`, `elasticgraph/`, `flowgraph/`, `heatmap/`, `matrix/`, `tree/`, `treemap/`, `circlepacking/`, `maps/`, `timeseries/`, `movingbubbles/`, `violin/`, `particles/`, `imageslider/`, `sequence/`, `erd/`, each with a Python module and `d3js/` assets.
3. **`utils.py`** — preprocessing, paths, HTML write, colour backgrounds, shared helpers.
4. **`_shared/`** (when present) — template env, theme, panel conventions shared by modern charts.
5. **`streamlit/`** — minimal Streamlit demos (`showfig=False`, `return_html=True`, `st.iframe`).
6. **`source/`** — Sphinx `.rst` docs per chart.
7. **`skills/d3blocks/`** — agent skill: ask-first workflow, `references/<chart>.md`, `examples/*_advanced.py`, `examples/streamlit_*.py`.

Charts expose a consistent surface where possible: `filepath`, `figsize`, `showfig`, `return_html`, `overwrite`, `notebook`, `save_button`, `show_side_panel`, `show_top_panel`, `dark_mode`, `color_background` (including `'streamlit'`).

## Chart families (entry points on `D3Blocks`)

| Family | Methods (typical) | Typical input |
|--------|-------------------|---------------|
| Points / distributions | `scatter`, `violin` | `x=`, `y=` arrays (not a lone DataFrame) |
| Flows | `chord`, `sankey` | `source`, `target`, `weight` |
| Networks | `d3graph`, `elasticgraph`, `radialgraph` | edge list; radialgraph optional `center` |
| Hierarchy | `tree`, `treemap`, `circlepacking` | edge list or level columns |
| Matrix | `heatmap`, `matrix` | matrix DataFrame or network sample |
| Geo / time | `maps`, `timeseries`, `movingbubbles` | lon/lat; datetime + series; datetime/sample_id/state |
| Diagrams | `flowgraph`, `sequence`, `erd` | edge list and/or Mermaid |
| Other | `particles`, `imageslider` | text string; before/after image paths |

Confirm live signatures with:

```bash
python -m pydoc d3blocks.D3Blocks.<chart>
```

Some builds may omit newer methods (e.g. `sequence`, `erd`); check `hasattr(D3Blocks(), "sequence")` before calling.

## Key methods

- Chart methods: `scatter`, `violin`, `chord`, `sankey`, `d3graph`, `elasticgraph`, `radialgraph`, `heatmap`, `matrix`, `tree`, `treemap`, `circlepacking`, `maps`, `timeseries`, `movingbubbles`, `flowgraph`, `sequence`, `erd`, `particles`, `imageslider`, …
- `import_example(name, ...)` — load sample data (`energy`, `stormofswords`, `cancer`, `climate`, `surfspots`, `random_time`, `southern_nebula_internet`, …)
- `set_node_properties` / `set_edge_properties` — then `show()` for property-edit workflows
- `show()` — open browser or continue the configured chart
- `return_html=True` + `showfig=False` — HTML string for Streamlit / notebooks

## Example usage patterns

**One-shot:**

```python
from d3blocks import D3Blocks

d3 = D3Blocks()
df = d3.import_example("energy")
d3.sankey(df, filepath="sankey.html")
```

**Properties then show:**

```python
d3 = D3Blocks(chart="Chord", frame=True)
df = d3.import_example("energy")
d3.set_node_properties(df)
d3.set_edge_properties(df, color="source")
d3.show()
```

**Streamlit embed:**

```python
html = d3.chord(
    df,
    showfig=False,
    return_html=True,
    color_background="streamlit",
    show_side_panel=False,
)
# st.iframe(html, height=700)
```

## Agent skill (`skills/d3blocks`)

When creating or modifying charts for users via the skill:

1. Ask for **data location** (path / CSV / example name).
2. Ask which **columns** matter; map to the chart’s expected roles.
3. **Suggest** 2–3 chart types from data + goal; **user chooses**.
4. Implement only after confirmation; use `references/<chart>.md` and `examples/`.

Do not invent APIs — use pydoc and the reference files. Discover chart coverage by listing `references/` and `examples/`, not by hardcoding names in prose.

## Testing strategy

- `tests/` — package behaviour per chart, preprocessing, examples.
- `skills/d3blocks/test_skill.py` — skill structure (no d3blocks required).
- `skills/d3blocks/test_examples.py` — runs each `examples/*_advanced.py` against installed d3blocks (skips optional methods if missing).

## Conventions for changes

- Prefer surgical edits to the chart package and matching Streamlit / docs / skill reference.
- Keep Streamlit demos on the `st.iframe` + `return_html=True` pattern.
- New chart skill coverage: `references/<chart>.md`, `examples/<chart>_advanced.py`, optional `examples/streamlit_<chart>.py`; avoid hardcoding full chart lists in `SKILL.md` discovery sections.
