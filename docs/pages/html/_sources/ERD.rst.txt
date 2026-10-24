ERD
#############

.. automethod:: d3blocks.d3blocks.D3Blocks.erd


Input Data
************

The input is either a Mermaid ``erDiagram`` (string, Markdown or file) or a DataFrame of
relationships with the columns ``source`` and ``target``; all other columns are optional.

.. code:: python

	#       source       target source_card   target_card     label  identifying
	# 0  customers       orders         one  zero_or_more    places         True
	# 1     orders  order_lines         one   one_or_more  contains        False

* Cardinalities: ``one``, ``zero_or_one``, ``one_or_more``, ``zero_or_more``; drawn as crow's-foot
  markers. A missing cardinality draws no marker.
* ``identifying=False`` draws a dashed line.

Per-entity attributes (``label``, ``color``, ``tooltip``, ``columns``) are passed with
``entities``. ``columns`` is a list of ``{'name', 'type', 'key', 'comment'}`` where ``key`` is ``''``,
``'PK'``, ``'FK'``, ``'UK'`` or a comma list such as ``'PK,FK'``.


Mermaid input
*************

Supported: relationships with all four markers per end (``||``, ``|o``/``o|``, ``}|``/``|{``,
``}o``/``o{``), ``--`` (identifying) and ``..`` (non-identifying) lines, entity blocks with
``type name PK "comment"`` rows, keys ``PK``, ``FK``, ``UK`` and comma lists, entities that are only
used in relationships, a top-level ``direction`` (``direction=`` wins over it) and ``%%`` comments.
Other statements raise a ``ValueError`` naming the line (see *Mermaid errors* on the Flowgraph page).

.. code:: python

	from d3blocks import D3Blocks

	d3 = D3Blocks(frame=False)
	d3.erd('''
	erDiagram
	    strategy_definitions ||--o{ strategy_runs : "has runs"
	    strategy_runs o|--o{ signals : contains
	    signals o|--o{ orders : "may produce"
	    orders ||--o{ order_fills : "has fills"
	    strategy_definitions {
	        uuid id PK
	        text name
	        bool enabled
	    }
	    signals {
	        uuid id PK
	        uuid run_id FK "nullable"
	        text status
	    }
	''')

From Markdown, the first ``erDiagram`` block is used.


DataFrame input
***************

.. code:: python

	import pandas as pd

	df = pd.DataFrame({
	    'source': ['customers', 'orders'],
	    'target': ['orders', 'order_lines'],
	    'source_card': ['one', 'one'],
	    'target_card': ['zero_or_more', 'one_or_more'],
	    'label': ['places', 'contains'],
	})
	entities = {
	    'customers': {'columns': [{'name': 'id', 'type': 'uuid', 'key': 'PK'},
	                              {'name': 'email', 'type': 'text', 'key': 'UK'}]},
	    'orders': {'columns': [{'name': 'id', 'type': 'uuid', 'key': 'PK'},
	                           {'name': 'customer_id', 'type': 'uuid', 'key': 'FK', 'comment': 'who ordered'}]},
	}
	d3.erd(df, entities=entities, direction='TB')



.. raw:: html

    <iframe src="https://raw.githack.com/d3blocks/d3blocks/main/docs/figs/erd/erd.html" height="600px" width="700px", frameBorder="0"></iframe>



Large schemas
*************

Tables without relationships, and separate groups of related tables, are laid out on their own and
packed in rows, so the diagram keeps the window's proportions. **Columns** in the top panel switches
between all columns, keys only (PK/FK/UK, with a "+N more columns" row) and table names only, and
re-runs the layout. ``show_columns='keys'`` starts there. Search finds tables and columns; a column
hit pins its table and marks the row.


Walkthrough
***********

Pass ``steps`` for a captioned walkthrough (**▶ Walk through** in the top panel). A step highlights
entities (``nodes``) and relationships (``edges``, as ``(a, b)`` pairs in either order), dims the
rest and zooms to them.

.. code:: python

	steps = [
	    {'title': 'Customers place orders', 'caption': 'One customer has zero or more orders.',
	     'highlight': {'nodes': ['customers', 'orders'], 'edges': [('customers', 'orders')]}},
	    {'title': 'Order lines', 'caption': 'Every order has at least one line.',
	     'highlight': {'edges': [('orders', 'order_lines')]}},
	]
	d3.erd(df, entities=entities, steps=steps)

Without ``steps`` there is no walkthrough. Keys: ← and → move, Space plays or pauses, Esc closes.


Theme
*****

The theme button switches between dark and light at runtime; lines, crow's-foot markers, table
boxes, key badges and the caption bar follow the theme. ``dark_mode='auto'`` follows the operating
system theme until the theme button is used. Exports keep the theme shown.


Interaction
***********

* Hover a table to highlight it, its relationships and its neighbours; click to pin.
* Hover a relationship to see both cardinalities in words.
* The Layout panel changes direction, columns, column types, spacing and font size.
* The Legend panel lists the cardinalities, line styles and keys in use.
* Export to SVG, PNG or JSON (including computed positions).


Jupyter and Streamlit
*********************

In a notebook, pass ``notebook=True``. In Streamlit, generate the HTML with ``return_html=True`` and
embed it with ``st.iframe``; see ``streamlit/erd_streamlit_demo.py``.


.. include:: add_bottom.add
