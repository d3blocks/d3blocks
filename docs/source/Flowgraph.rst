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
nested subgraphs and colours from ``style`` / ``classDef`` are converted.

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


Interaction
***********

* Hover a node to trace everything upstream and downstream; click to pin.
* **▶ Trace** walks through the flow step by step (from the pinned node, or from all start nodes).
* Drag nodes; edges and groups follow. **Reset layout** recomputes the layout.
* The Layout panel changes direction, spacing, font size, edge curve and animation.
* The Legend panel lists groups and the edge variants in use.
* Export to SVG, PNG or JSON (including computed positions).


.. include:: add_bottom.add
