Sequence
#############

.. automethod:: d3blocks.d3blocks.D3Blocks.sequence


Input Data
************

The input is either a Mermaid ``sequenceDiagram`` (string, Markdown or file) or a DataFrame with one
row per message, in time order. The DataFrame needs the columns ``source`` and ``target``; all other
columns are optional.

.. code:: python

	#   source target            label  style   variant
	# 0    app   auth            login   sync  security
	# 1   auth    app            token  reply   default
	# 2    app    api  call with token   sync  emphasis

* ``style``: ``sync`` (a call: solid line, filled arrowhead) or ``reply`` (dashed line, open arrowhead).
* ``variant``: ``default``, ``emphasis``, ``security``, ``async``, ``error``; sets the colour and width,
  as in ``flowgraph``.

Per-participant attributes (``label``, ``kind``, ``color``, ``tooltip``) are passed with
``participants``. ``kind='actor'`` draws a stick figure; the layout is the same. Participants that
are not listed are added in order of first appearance. Regions are passed with ``groups`` as
``[{'label': str, 'from': i, 'to': j, 'color': hex}]`` with message indexes.


Mermaid input
*************

Supported: ``participant A``, ``participant A as Label``, ``actor A``, ``A->>B: text`` (call),
``A-->>B: text`` (reply), ``rect rgb(...)`` / ``rect rgba(...)`` ... ``end`` (a region) and ``%%``
comments. Other statements (activations, notes, ``alt``/``loop``, ``autonumber``, self-messages, ...)
raise a ``ValueError`` naming the line, so nothing is dropped silently (see *Mermaid errors* on the
Flowgraph page).

.. code:: python

	from d3blocks import D3Blocks

	d3 = D3Blocks(frame=False)
	d3.sequence('''
	sequenceDiagram
	    actor Operator
	    participant UI as Trade App (UI)
	    participant API as Trade API
	    participant Schwab as Schwab OAuth

	    rect rgb(236, 254, 255)
	        Operator->>UI: Click "Connect Schwab"
	        UI->>API: GET /api/v1/brokers/schwab/authorize
	        API-->>UI: Redirect to Schwab authorization URL
	    end
	    rect rgb(220, 252, 231)
	        Schwab->>API: GET /callback?code=…
	        API->>Schwab: POST token exchange
	        Schwab-->>API: access_token + refresh_token
	        API-->>UI: Settings shows "Connected"
	    end
	''')

The diagram can also live in a Markdown file as a fenced ``mermaid`` block; the first
``sequenceDiagram`` block is used, so one file can hold several diagram kinds.

.. code:: python

	d3.sequence('docs/schwab-connection.md')


DataFrame input
***************

.. code:: python

	import pandas as pd

	df = pd.DataFrame({
	    'source': ['app', 'auth', 'app', 'api'],
	    'target': ['auth', 'app', 'api', 'app'],
	    'label': ['login', 'token', 'GET /orders with token', '200 JSON'],
	    'style': ['sync', 'reply', 'sync', 'reply'],
	})
	participants = {'app': {'label': 'Mobile app', 'kind': 'actor'}, 'auth': {'label': 'Auth server'}}
	d3.sequence(df, participants=participants, groups=[{'label': 'Sign in', 'from': 0, 'to': 1}])


Walkthrough
***********

**▶ Walk through** steps through the messages with a caption bar at the bottom: the step title, the
caption, "Step 3 of 9", a row of step stops and Prev / Play / Next. By default there is one step per
message, captioned with the message label. Pass ``steps`` to write your own; a step highlights
messages (by index) and participants, dims the rest and scrolls them into view.

.. code:: python

	steps = [
	    {'title': 'Sign in', 'caption': 'The app exchanges credentials for a token.',
	     'highlight': {'messages': [0, 1]}},
	    {'title': 'Call the API', 'caption': 'The token authorizes the request.',
	     'highlight': {'messages': [2, 3], 'participants': ['api']}},
	]
	d3.sequence(df, steps=steps)

Keys: ← and → move, Space plays or pauses, Esc closes. ``steps=[]`` removes the walkthrough.


.. raw:: html

    <iframe src="https://raw.githack.com/d3blocks/d3blocks/main/docs/figs/sequence/sequence.html" height="600px" width="700px", frameBorder="0"></iframe>

Theme
*****

The theme button switches between dark and light at runtime; every colour (lines, arrowheads,
regions, the caption bar) follows the theme. ``dark_mode='auto'`` follows the operating system theme
until the theme button is used. Exports keep the theme shown.


Interaction
***********

* Hover a participant to highlight its lifeline and every message touching it; click to pin.
* Hover a message to highlight it and see its index and text.
* Search finds participants and message text.
* **Fit** fits the diagram to the window width; wide diagrams keep a readable text size and pan.
  The participant headers stay visible when scrolling down a long sequence.
* The Layout panel changes message spacing, label wrapping and font size.
* Export to SVG, PNG or JSON (including computed positions).


Jupyter and Streamlit
*********************

In a notebook, pass ``notebook=True``. In Streamlit, generate the HTML with ``return_html=True`` and
embed it with ``st.iframe``; see ``streamlit/sequence_streamlit_demo.py``.

.. code:: python

	html = D3Blocks().sequence(diagram, filepath=None, showfig=False, return_html=True)
	st.iframe(html, height=700, width="stretch")


.. include:: add_bottom.add
