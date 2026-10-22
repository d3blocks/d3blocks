# ERD

**Entity–relationship** diagram: entities with optional columns/keys, relationships with cardinalities. Input is a **relationship DataFrame** or **Mermaid `erDiagram`**.

Same family as `flowgraph` / `sequence`. Prefer `python -m pydoc d3blocks.D3Blocks.erd` when the method is present.

## Input

**Relationships** DataFrame:

| Column | Required | Role |
|--------|----------|------|
| `source` | yes | From entity |
| `target` | yes | To entity |
| `source_card` / `target_card` | no | `'one'`, `'zero_or_one'`, `'one_or_more'`, `'zero_or_more'` |
| label / other edge attrs | no | As supported by the package |

**Entities** (optional): per-entity `columns` list of `{name, type, key, comment}` with `key` in `PK` / `FK` / `UK` / comma lists.

**Mermaid**: `erDiagram` text or file (`||--o{`, entity attribute blocks, `direction LR|TB`).

## Useful config keys

| Key | Notes |
|-----|--------|
| `direction` | `'LR'`, `'TB'`, … |
| `show_columns` | `'all'`, `'keys'`, `'none'` |
| `show_types` | bool |
| `nodesep` / `ranksep` | Layout spacing |
| `dark_mode` / `color_background` / panels | standard UI |

## Examples

```python
import pandas as pd
from d3blocks import D3Blocks

df = pd.DataFrame({
    'source': ['Customer', 'Order'],
    'target': ['Order', 'LineItem'],
    'source_card': ['one', 'one'],
    'target_card': ['zero_or_more', 'one_or_more'],
})
d3 = D3Blocks()
d3.erd(df, filepath='erd.html')  # when available on installed package
```

```python
mermaid = """
erDiagram
    CUSTOMER ||--o{ ORDER : places
    ORDER ||--|{ LINE-ITEM : contains
"""
d3.erd(mermaid, filepath='erd_mmd.html')
```

Confirm the live signature with pydoc before inventing kwargs.

## Full runnable examples

`examples/erd_advanced.py`, `examples/streamlit_erd.py` when present.
