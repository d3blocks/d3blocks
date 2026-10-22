# Sequence

UML-style **sequence diagram**: participants (columns + lifelines), messages in time order, optional regions. Input is a **message DataFrame** or **Mermaid `sequenceDiagram`**.

Built like `flowgraph` (shared Mermaid helpers). Prefer `python -m pydoc d3blocks.D3Blocks.sequence` when the method is present on the installed package.

## Input

**Messages** DataFrame (time order):

| Column | Required | Role |
|--------|----------|------|
| `source` | yes | From participant |
| `target` | yes | To participant |
| `label` | no | Message text |
| `style` | no | `'sync'` (solid call) or `'reply'` (dashed) |
| `variant` | no | `'default'`, `'emphasis'`, `'security'`, `'async'`, `'error'` |

Self-messages are not supported.

**Mermaid**: `sequenceDiagram` text, Markdown fence, or `.mmd` path (via `from_mermaid` / chart entrypoint).

## Useful config keys

| Key | Notes |
|-----|--------|
| `message_spacing` | Vertical spacing between messages |
| `wrap` | Label wrap width |
| `font` | e.g. `{'size': 13}` |
| `groups` | Regions: `[{label, from, to, color}]` (message indexes) |
| `dark_mode` / `color_background` / panels | standard UI |

## Examples

### Edge list of messages

```python
import pandas as pd
from d3blocks import D3Blocks

df = pd.DataFrame({
    'source': ['Alice', 'Bob', 'Alice'],
    'target': ['Bob', 'Alice', 'Bob'],
    'label': ['Hello', 'Hi!', 'OK'],
    'style': ['sync', 'reply', 'sync'],
})
d3 = D3Blocks()
# When available on the installed package:
d3.sequence(df, filepath='sequence.html')
```

### Mermaid

```python
mermaid = """
sequenceDiagram
    Alice->>Bob: Hello
    Bob-->>Alice: Hi!
"""
d3.sequence(mermaid, filepath='sequence_mmd.html')
```

Confirm the live signature with pydoc before inventing kwargs.

## Full runnable examples

`examples/sequence_advanced.py`, `examples/streamlit_sequence.py` when present.
