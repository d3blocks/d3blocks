Flowgraph
#############

.. automethod:: d3blocks.d3blocks.D3Blocks.flowgraph


Input Data
************

The input is either an edge list (DataFrame) or a Mermaid flowchart (string).
The edge list needs the columns ``source`` and ``target``; all other columns are optional.

.. code:: python

	#        source         target  label   variant animation
	# 0       start          check                       None
	# 1       check           pick    yes  emphasis     comet
	# 2       check      backorder     no     error      None
	# 3   backorder          check  retry     async      dots

Per-node attributes (``label``, ``shape``, ``group``, ``color``, ``tooltip``) are passed with ``nodes``,
and group settings (``label``, ``parent``, ``color``) with ``groups``.

* Shapes: ``process``, ``decision``, ``terminal``, ``io``, ``subprocess``, ``database``, ``queue``, ``document``, ``external``, ``circle``.
* Edge variants: ``default``, ``emphasis``, ``security``, ``async``, ``error``. Each sets a colour, line style and width; an edge's own ``color`` and ``style`` override it.
* Animations: ``pulse``, ``dash``, ``dots``, ``comet`` for the whole chart (``animate=``) or per edge (``animation`` column).


Process flow
************

.. code:: python

	import pandas as pd
	from d3blocks import D3Blocks

	edges = pd.DataFrame({
	    'source': ['start', 'check', 'check', 'fix'],
	    'target': ['check', 'done', 'fix', 'check'],
	    'label':  ['', 'yes', 'no', 'retry'],
	})
	nodes = {
	    'start': {'label': 'Start', 'shape': 'terminal'},
	    'check': {'label': 'Valid?', 'shape': 'decision'},
	    'fix':   {'label': 'Fix input'},
	    'done':  {'label': 'Done', 'shape': 'terminal'},
	}

	d3 = D3Blocks(frame=False)
	d3.flowgraph(edges, nodes=nodes, direction='TB')

	# Change a node and redraw
	d3.node_properties['fix']['color'] = '#e15759'
	d3.show()


.. raw:: html

    <iframe src="https://erdogant.github.io\docs\d3blocks\flowgraph.html" height="600px" width="700px", frameBorder="0"></iframe>



Mermaid input
*************

Node shapes, edge labels, dotted (``-.->``) and thick (``==>``) links, ``&``, chains,
nested subgraphs, node colours from ``style`` / ``classDef`` and edge colours and dashes from
``linkStyle`` are converted.

Mermaid errors
**************

All d3blocks Mermaid readers (flowcharts, state diagrams, ``sequence`` and ``erd``) follow one
rule: every statement is understood, explicitly ignored, or raises a ``ValueError`` that names the
line, before any HTML is written. Nothing is dropped silently.

* Ignored: blank lines, ``%%`` comments, ``%%{init}%%`` directives and the accessibility metadata
  ``accTitle`` / ``accDescr``.
* Errors: statements that do not parse (for example ``A[Start] --> B{ok?``), a wrong first statement,
  an ``end`` without ``subgraph`` (or a ``subgraph`` without ``end``), and Mermaid features without an
  equivalent here, such as ``click``, a ``direction`` inside a subgraph and links to subgraphs (link to
  a node inside the subgraph instead).

Line numbers count from the first line of the diagram (in Markdown: of the fenced block).

.. code:: python

	d3.flowgraph('flowchart LR\n  A[Start] --> B{ok?')
	# ValueError: Mermaid flowchart line 2 could not be parsed: 'A[Start] --> B{ok?' (...)

.. code:: python

	d3.flowgraph('''
	flowchart LR
	    start([Order received]) --> check{In stock?}
	    check -->|yes| pick[Pick & pack]
	    check -- no --> back[[Backorder]] -.->|restocked| check
	    subgraph wh [Warehouse]
	        pick --> ship[/Ship parcel/]
	    end
	    ship ==> done([Delivered])
	''')

The diagram can also live in a Markdown file as a fenced ``mermaid`` block, so GitHub renders it
too; pass the file path (``.md``, ``.markdown``, ``.mmd`` or ``.mermaid``). From Markdown, the first
flowchart block is used.

.. code:: python

	d3.flowgraph('docs/order_process.md')


State diagrams
**************

Mermaid ``stateDiagram`` and ``stateDiagram-v2`` are read too, so lifecycle diagrams render with
the same layout, interaction and export as flowcharts. ``[*]`` becomes one start and one end
pseudo-state (small circles), transition labels are kept (everything after the first ``:``), notes
are added to the state's tooltip and ``classDef`` / ``class`` colours are applied. State diagrams are
laid out top to bottom unless the diagram has a ``direction`` statement or ``direction`` is
passed. Composite states, ``<<choice>>``, ``state "x" as A`` and ``A : description`` raise a
``ValueError`` naming the line.

.. code:: python

	d3.flowgraph('''
	stateDiagram-v2
	    [*] --> pending : Signal created
	    pending --> awaiting_approval : Risk checks pass
	    pending --> cancelled : Strategy disabled
	    awaiting_approval --> approved : Operator approves
	    awaiting_approval --> rejected : Operator rejects
	    approved --> executed : Order sent to broker
	    executed --> [*]
	    rejected --> [*]
	    cancelled --> [*]

	    note right of awaiting_approval
	        Agent-generated signals
	        enter here directly
	    end note

	    classDef review fill:#e0f2fe,stroke:#0284c7
	    class awaiting_approval review
	''')

From Markdown, the first flowchart or state diagram block is used; other diagram types are skipped.


Architecture diagram
********************

Groups can be nested with ``parent``. ``layout='elk'`` uses ELK's layered layout with orthogonal
edge routing; it suits nested architecture diagrams but adds about 1.5 MB to the HTML file.

.. code:: python

	groups = {
	    'Cloud': {'label': 'Cloud account'},
	    'VPC': {'parent': 'Cloud'},
	    'App subnet': {'parent': 'VPC'},
	    'Data subnet': {'parent': 'VPC'},
	}
	nodes = {
	    'api': {'label': 'API', 'group': 'App subnet'},
	    'worker': {'label': 'Worker', 'group': 'App subnet'},
	    'db': {'label': 'PostgreSQL', 'shape': 'database', 'group': 'Data subnet'},
	    'bus': {'label': 'Event bus', 'shape': 'queue', 'group': 'Data subnet'},
	    'users': {'label': 'Users', 'shape': 'circle'},
	}
	edges = pd.DataFrame({
	    'source':  ['users', 'api', 'api', 'bus'],
	    'target':  ['api', 'db', 'bus', 'worker'],
	    'label':   ['HTTPS', 'SQL', 'publish', 'consume'],
	    'variant': ['emphasis', 'default', 'async', 'async'],
	})
	d3.flowgraph(edges, nodes=nodes, groups=groups, layout='elk', animate='dots')


Jupyter and Streamlit
*********************

In a notebook, pass ``notebook=True``; the chart is shown inline, isolated in an iframe sized by
``figsize`` (default: full width x 650 px). See ``notebooks/flowgraph.ipynb``.

.. code:: python

	d3 = D3Blocks(frame=False)
	d3.flowgraph(edges, nodes=nodes, notebook=True, filepath=None, figsize=[None, 520])

In Streamlit, generate the HTML with ``return_html=True`` and embed it with ``st.iframe``.
``streamlit/flowgraph_streamlit_demo.py`` edits a Mermaid flowchart in the sidebar and
re-renders it with the chosen layout, direction and animation.

.. code:: python

	html = D3Blocks().flowgraph(flowchart, filepath=None, showfig=False, return_html=True)
	st.iframe(html, height=700, width="stretch")


Walkthrough
***********

``steps`` adds a captioned walkthrough. **▶ Walk through** in the top panel opens a caption bar with
the step title, the caption, "Step 3 of 9", a row of step stops and Prev / Play / Next. Each step
highlights its nodes and edges, dims the rest and zooms to them. Keys: ← and → move, Space plays or
pauses, Esc closes. Play advances every 3 seconds and stops on the last step.

.. code:: python

	steps = [
	    {'title': 'Check', 'caption': 'Every order is validated first.',
	     'highlight': {'nodes': ['check'], 'edges': [('start', 'check')]}},
	    {'title': 'Retry', 'caption': 'Invalid input is fixed and checked again.',
	     'highlight': {'edges': [('check', 'fix'), ('fix', 'check')]}},
	]
	d3.flowgraph(edges, nodes=nodes, steps=steps)

Without ``steps`` the button is **▶ Trace**, the uncaptioned walk through the flow. Unknown nodes or
edges and unsupported keys raise a ``ValueError`` with the step index. The same walkthrough is used by
``sequence`` and ``erd``.


Theme
*****

The theme button (last on the right of the top panel) switches between dark and light at runtime.
``dark_mode=True`` (default) starts dark, ``False`` starts light, and ``dark_mode='auto'`` follows the
operating system theme, also when it changes, until the theme button is used. In ``'auto'`` mode a
``?theme=light`` or ``?theme=dark`` URL parameter picks the theme. Exports keep the theme shown.


Interaction
***********

* Hover a node to trace everything upstream and downstream; click to pin.
* **▶ Trace** walks through the flow step by step (from the pinned node, or from all start nodes);
  with ``steps`` it is **▶ Walk through**, the captioned walkthrough.
* Drag nodes; edges and groups follow. **Reset layout** recomputes the layout.
* The Layout panel changes direction, spacing, font size, edge curve and animation.
* The Legend panel lists groups and the edge variants in use.
* Export to SVG, PNG or JSON (including computed positions).


.. include:: add_bottom.add
