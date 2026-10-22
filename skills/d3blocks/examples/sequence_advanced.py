"""Advanced sequence: message list (+ Mermaid if supported).

Requires: d3blocks with sequence support
Run: python sequence_advanced.py
"""
import pandas as pd
from d3blocks import D3Blocks

df = pd.DataFrame(
    {
        "source": ["Alice", "Bob", "Alice"],
        "target": ["Bob", "Alice", "Bob"],
        "label": ["Hello", "Hi!", "OK"],
        "style": ["sync", "reply", "sync"],
    }
)
d3 = D3Blocks()
if not hasattr(d3, "sequence"):
    raise SystemExit(
        "This d3blocks build has no D3Blocks.sequence; upgrade or skip this example."
    )
d3.sequence(df, filepath="sequence_messages.html", title="Sequence — messages")
mermaid = """
sequenceDiagram
    Alice->>Bob: Hello
    Bob-->>Alice: Hi!
"""
d3.sequence(mermaid, filepath="sequence_mermaid.html", title="Sequence — Mermaid")
