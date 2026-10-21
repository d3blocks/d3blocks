# D3Blocks Visualizer Skill

Interactive D3Blocks charts from Python data, with advanced examples and Streamlit apps.

## When to use

- User has (or wants) a DataFrame and an interactive HTML chart
- Chart selection (scatter, chord, flowgraph, networks, …)
- Streamlit embedding

## References (parameters)

| Chart | File |
|-------|------|
| Scatter | `references/scatter.md` |
| Chord | `references/chord.md` |
| Flowgraph | `references/flowgraph.md` |
| Streamlit rules | `references/streamlit.md` |

## Examples (runnable code — prefer these over inventing snippets)

### Standalone Python

| File | Focus |
|------|--------|
| `examples/scatter_advanced.py` | Multi-coord (tSNE/PCA), size/color/tooltip, scale |
| `examples/chord_advanced.py` | Property edits, Nuclear highlight, large margins |
| `examples/flowgraph_advanced.py` | Shapes, groups, variants, Mermaid+ELK, state diagram |

### Streamlit apps

| File | Focus |
|------|--------|
| `examples/streamlit_scatter.py` | Sidebar encodings + panel toggles + cache |
| `examples/streamlit_chord.py` | Ordering, colour mode, margin, dark mode |
| `examples/streamlit_flowgraph.py` | Edge list vs Mermaid, dagre/ELK, direction |

```bash
pip install d3blocks streamlit
python examples/scatter_advanced.py
streamlit run examples/streamlit_chord.py
```

## API notes

- Scatter: `x=` / `y=` arrays — never `d3.scatter(df)` alone
- Chord: `source`, `target`, `weight`
- Flowgraph: edge list or Mermaid; `frame=False` for dict-style node edits
- Streamlit: `showfig=False`, `return_html=True`, `st.iframe`, often `color_background='streamlit'`
