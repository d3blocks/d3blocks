# Flowgraph

Layered process / architecture diagrams. Nodes sit in ranks; optional groups (swimlanes, boundaries). Input is an **edge list** or a **Mermaid** flowchart / state diagram.

## Input

### Edge list (DataFrame)

| Column | Required | Role |
|--------|----------|------|
| `source` | yes | From node |
| `target` | yes | To node |
| `label` | no | Edge text |
| `weight` | no | Line width |
| `variant` | no | `default`, `emphasis`, `security`, `async`, `error` |
| `style` | no | `solid`, `dashed`, … |
| `animation` / color | no | Per-edge overrides |

### Nodes and groups (optional kwargs)

- `nodes`: dict or DataFrame — per-node `label`, `shape`, `group`, `color`, `tooltip`
- `groups`: dict — group `label`, `parent`, `color`

### Mermaid

Pass a string, Markdown file path, or `.mmd` path. Supported: flowcharts and state diagrams (`stateDiagram-v2`). Unsupported syntax raises `ValueError` naming the line (nothing is dropped silently).

## Main parameters

| Parameter | Default | Notes |
|-----------|---------|--------|
| `direction` | from data / `'LR'` | `LR`, `RL`, `TB`, `BT` (aliases like `td` → `TB`) |
| `layout` | `'dagre'` | `'dagre'` or `'elk'` (ELK bundled only when selected) |
| `shape` | `'process'` | Default node shape |
| `color` | `'group'` | Node colouring strategy |
| `cmap` | `'Set2'` | Colormap |
| `edge_color` | `'#8c8c8c'` | Default edge colour / `'source'` etc. |
| `curve` | `'smooth'` | Edge routing style |
| `animate` | `False` | Global animation (`pulse`, `dash`, `dots`, `comet` as string also accepted in practice via options) |
| `draggable` | `True` | Drag nodes in the browser |
| `show_edge_labels` | `True` | |
| `show_groups` | `True` | |
| `nodesep` / `ranksep` / `edgesep` | spacing | Layout spacing |
| `show_side_panel` / `show_top_panel` | `True` | UI chrome |
| `dark_mode` | `True` | `True` / `False` / `'auto'` |
| `color_background` | `None` | |
| `return_html` | `False` | |
| `filepath` | `'flowgraph.html'` | |

### Node shapes

`process`, `decision`, `terminal`, `io`, `subprocess`, `database`, `queue`, `document`, `external`, `circle`, …

### Edge variants

`default`, `emphasis`, `security`, `async`, `error` — set colour, dash, width; per-edge `color`/`style` override.

## Examples

### Edge list with shapes

```python
import pandas as pd
from d3blocks import D3Blocks

d3 = D3Blocks(frame=False)
df = pd.DataFrame({
    'source': ['Start', 'Valid?', 'Valid?', 'Fix'],
    'target': ['Valid?', 'Done', 'Fix', 'Valid?'],
    'label':  ['', 'yes', 'no', 'retry'],
})
nodes = {
    'Start': {'shape': 'terminal'},
    'Valid?': {'shape': 'decision'},
    'Done': {'shape': 'terminal'},
}
d3.flowgraph(df, nodes=nodes, direction='TB', filepath='flowgraph.html')

# Edit and redraw
d3.node_properties['Fix']['color'] = '#e15759'
d3.show()
```

### Mermaid flowchart (ELK layout)

```python
from d3blocks import D3Blocks

d3 = D3Blocks(frame=False)
d3.flowgraph('''
flowchart LR
  subgraph api [API]
    gw[Gateway] --> svc[Orders]
  end
  svc --> db[(Postgres)]
  svc -.->|events| q[[Worker]]
''', layout='elk', filepath='api.html')
```

### Link to a subgraph / group

```python
# Mermaid: Workers --> PG draws to the group border
d3.flowgraph('''
flowchart LR
    subgraph Workers ["Background workers"]
        W1[scheduler]
        W2[sync]
    end
    Workers --> PG[(PostgreSQL)]
''')

# DataFrame equivalent
edges = pd.DataFrame({'source': ['Workers'], 'target': ['PG']})
nodes = {
    'W1': {'group': 'Workers'},
    'W2': {'group': 'Workers'},
    'PG': {'shape': 'database'},
}
d3.flowgraph(
    edges,
    nodes=nodes,
    groups={'Workers': {'label': 'Background workers'}},
)
```

### State diagram (Mermaid)

```python
d3.flowgraph('''
stateDiagram-v2
    [*] --> pending : created
    pending --> done : ok
    pending --> failed
    done --> [*]
    failed --> [*]
''')
```

### HTML for embedding

```python
html = d3.flowgraph(
    df,
    nodes=nodes,
    direction='TB',
    dark_mode='auto',
    showfig=False,
    return_html=True,
    filepath=None,
)
```

## Notes

- Prefer `D3Blocks(frame=False)` when you will edit `node_properties` as a dict.
- Mermaid file or Markdown path works: `d3.flowgraph('docs/process.md')`.
- Libraries (dagre, optional ELK) are inlined; output stays self-contained.
- Docs / UI: see project `source` Flowgraph page and `UI_controls` if present.

## Full runnable examples

In this skill: `examples/flowgraph_advanced.py and examples/streamlit_flowgraph.py`.
