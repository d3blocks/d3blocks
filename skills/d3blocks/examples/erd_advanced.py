"""Advanced erd: relationships (+ Mermaid if supported).

Requires: d3blocks with erd support
Run: python erd_advanced.py
"""
import pandas as pd
from d3blocks import D3Blocks

df = pd.DataFrame(
    {
        "source": ["Customer", "Order"],
        "target": ["Order", "LineItem"],
        "source_card": ["one", "one"],
        "target_card": ["zero_or_more", "one_or_more"],
    }
)
d3 = D3Blocks()
if not hasattr(d3, "erd"):
    raise SystemExit(
        "This d3blocks build has no D3Blocks.erd; upgrade or skip this example."
    )
d3.erd(df, filepath="erd_relations.html", title="ERD — relations")
mermaid = """
erDiagram
    CUSTOMER ||--o{ ORDER : places
    ORDER ||--|{ LINE-ITEM : contains
"""
d3.erd(mermaid, filepath="erd_mermaid.html", title="ERD — Mermaid")
