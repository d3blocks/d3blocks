.. _radialgraph-label:

RadialGraph
'''''''''''

``RadialGraph`` is a force-directed network visualization arranged in concentric
rings around a focal node, built to mirror how tools like Obsidian's graph view
let you explore a network outward from wherever you start — one hop at a time,
or all at once, or as a rippling wave. Unlike a tree or dendrogram, RadialGraph
makes no assumption that your data has a single root or a strict parent/child
shape: it works on general many-to-many graphs, including cycles and nodes
reachable through more than one path.

The input is the same ``source``/``target``/``weight`` edge list every other
network-oriented block in d3blocks uses, and node/edge appearance (color,
size, opacity, edge width) is computed via the same delegation
:func:`d3graph.d3graph` already provides for :ref:`d3graph-label` — so a
:func:`RadialGraph` and a :func:`d3graph` built from the same data and the
same settings agree on how the network looks; only the layout differs.


What problem does this solve?
------------------------------

Global, all-at-once network layouts (like the default :ref:`d3graph-label`
view) work well up to a few hundred nodes, but get overwhelming past that —
everything competes for the same canvas at once. RadialGraph is for the
opposite situation: **exploring** a large network starting from one node you
care about, revealing more of the graph only as you ask for it.

This is the right tool when:

* You want to start at *one* node (a person, a document, a focal account) and
  see its immediate neighborhood first, expanding outward as needed.
* The network is large enough that rendering everything at once would be
  unreadable, but you still want the *option* to see it all.
* You want a visual sense of *how far* something is from your starting
  point — RadialGraph's concentric rings are literally hop-distance from the
  focus, so "close" and "far" are immediately visible, not just implied by
  force-layout clustering.
* You want to explore the network interactively (tap to expand/collapse,
  preview what's hidden before committing to it, watch connections ripple
  outward) rather than look at one static picture.


Two layout modes
-----------------

RadialGraph has two ways to arrange nodes, both driven by the same
``center`` parameter:

* **Local mode** (``center='<node name>'``): nodes settle into concentric
  rings by BFS hop-distance from that node — depth 0 is the focus itself,
  depth 1 its direct neighbors, depth 2 their neighbors, and so on. This is
  the "local graph" experience: your focus node anchored in the middle,
  everything else positioned by how far it is from that anchor.
* **Global mode** (``center=None``): a plain force layout with no imposed
  rings — nodes find their own position purely from the pull of their
  connections and the push of mutual repulsion. RadialGraph still picks the
  highest-degree node as an implicit focus for depth bookkeeping, but
  doesn't force it to the center. Note: if you want the "no ring, just a
  free-floating force graph" toggle, that's the ``layoutMode`` control in the
  side panel; the Python-side ``center`` parameter always resolves to *some*
  node (explicit, or the highest-degree fallback) so a focus is always
  available if you switch to ring mode from the UI.


Input data
----------

RadialGraph expects the same tabular input as :ref:`d3graph-label`: a
``pd.DataFrame`` with a ``source`` column, a ``target`` column, and an
optional ``weight`` column (defaults to ``1`` for every edge if omitted).
Each row is one edge:

.. code-block:: python

    import pandas as pd

    df = pd.DataFrame({
        'source': ['A', 'A', 'B', 'C'],
        'target': ['B', 'C', 'D', 'D'],
        'weight': [3, 1, 2, 1],
    })

Nothing about this input needs to form a tree or have a single root — cycles,
multiple paths between two nodes, and nodes with many connections are all
expected and handled correctly; RadialGraph computes hop-distance from the
focus dynamically as you expand the graph rather than assuming a fixed
hierarchy.


Quickstart
----------

.. code-block:: python

    from d3blocks import D3Blocks

    # Initialize
    d3 = D3Blocks()

    # Import example dataset (source-target-weight)
    df = d3.import_example('energy')

    # Plot, centered on the highest-degree node by default
    d3.radialgraph(df)


.. raw:: html

    <iframe src="https://erdogant.github.io\docs\d3blocks\radialgraph_quickstart.html" height="700px" width="700px", frameBorder="0"></iframe>



Focusing on a specific node
----------------------------

.. code-block:: python

    from d3blocks import D3Blocks

    d3 = D3Blocks()
    df = d3.import_example('energy')

    # Anchor the layout on a node you care about; rings become hop-distance
    # from THIS node instead of the highest-degree default.
    d3.radialgraph(df, center='Solar')


Coloring and sizing nodes
--------------------------

Node appearance is delegated to the same logic :ref:`d3graph-label` uses, so
the same keyword values work in both:

.. code-block:: python

    from d3blocks import D3Blocks

    d3 = D3Blocks()
    df = d3.import_example('energy')

    d3.radialgraph(
        df,
        center='Solar',
        color='cluster',       # Louvain community color (default)
        size='degree',         # node size scaled by degree (default)
        opacity='degree',
        cmap='Set2',
        scaler='zscore',
        minmax=[8, 13],
        edge_color='#808080',
        edge_opacity='weight', # edge opacity scaled by edge weight
        min_weight=1.0,
    )

``color``/``size``/``opacity`` accept the same values as
:func:`d3graph.d3graph.set_node_properties`: a fixed value (e.g. a hex color,
or a fixed size), or the strings ``'cluster'``/``'degree'`` for the
data-driven defaults shown above.


Network statistics
-------------------

Beyond the default cluster-color/degree-size appearance, RadialGraph ships an
interactive **Network Statistic** panel (collapsed by default, matching
d3graph's own panel convention) that recomputes a chosen centrality measure
**live**, against whatever part of the network is currently visible — expand
a node, apply an edge filter, and the coloring updates to reflect the
filtered graph, not a stale snapshot of the original data.

Which statistic is useful depends heavily on what kind of network you're
looking at. Two recurring cases — a social network (accounts following/
mentioning each other) and a note/file network (Obsidian-style backlinks) —
call for different measures, and the same number means something different
in each. The sections below go through each statistic with both in mind.

PageRank
~~~~~~~~

*What it measures:* importance based on being linked to by other important
nodes — a link from a well-connected node counts for more than a link from
an obscure one.

* **Social network**: separates raw follower count from actual influence.
  An account followed by a handful of highly-influential accounts can
  outrank one with ten times the followers but only from other low-influence
  accounts. Use this when the question is "who actually matters here," not
  just "who has the most connections."
* **Obsidian-style vault**: surfaces your foundational notes — the ones
  that a lot of *other important* notes link to, not just the ones with the
  most raw backlinks. A "Zettelkasten" index note or a core concept note
  that underpins many others will rank highly here even if any single note
  linking to it looks unremarkable.
* **Interpreting it**: high PageRank = "the rest of the network structurally
  depends on this node." Low PageRank on a node with high raw degree is a
  signal that its connections are mostly to other low-importance nodes —
  it's locally busy but not globally central.

HITS: Hub and Authority
~~~~~~~~~~~~~~~~~~~~~~~~

*What it measures:* HITS splits importance into two roles on **directed**
graphs — a good **hub** points to many good authorities; a good
**authority** is pointed to by many good hubs. Each score is only useful
alongside the other.

* **Social network**: on a follow graph, hubs are the curators — accounts
  that follow a lot of accounts worth following (good at finding signal).
  Authorities are the recognized experts those curators follow. If you're
  trying to find new accounts worth following, look for high-hub nodes and
  see who *they* follow; if you're trying to find the actual experts in a
  topic, look at authority scores directly.
* **Obsidian-style vault**: hub notes are your reading lists, MOCs (maps of
  content), and index pages — notes whose value is in linking *out* to good
  material. Authority notes are the canonical reference notes those hub
  notes point to. A high-hub note with low authority is doing its job as a
  signpost; a high-authority note is one worth expanding on further, since
  a lot of your own structure already treats it as a reference point.
* **Interpreting it**: don't compare hub and authority scores to each other
  on the same node — they're answering different questions. A node can
  legitimately be high on one and near-zero on the other.

Degree Centrality
~~~~~~~~~~~~~~~~~~

*What it measures:* the simplest measure — what fraction of all possible
connections a node actually has. No structure beyond direct neighbors is
considered.

* **Social network**: raw reach — how many people a post from this account
  could directly touch. Doesn't distinguish a thousand disengaged followers
  from a thousand active ones.
* **Obsidian-style vault**: which notes are the most directly linked-to or
  linking-out, at a glance. A quick first pass to find obvious hubs before
  reaching for a more structural measure like PageRank or betweenness.
* **Interpreting it**: cheap and intuitive, but purely local — it can't tell
  you whether those connections themselves matter. Use it as a first look,
  not a final answer, on anything but small networks.

Closeness Centrality
~~~~~~~~~~~~~~~~~~~~~~

*What it measures:* how few hops it takes, on average, to reach every other
node in the network from this one.

* **Social network**: flags accounts well-positioned to spread something
  quickly across the *whole* network — not because they have the most
  followers, but because they're structurally close to everyone. Useful for
  thinking about how fast information could realistically propagate from a
  given account.
* **Obsidian-style vault**: identifies notes that would make a good starting
  point for someone new to the vault — from here, most other notes are only
  a few links away. A high-closeness note is a reasonable candidate for a
  "start here" or overview page, whether or not it was designed to be one.
* **Interpreting it**: about efficient reachability, not about being heavily
  referenced. A note can have high closeness with relatively few direct
  links, if those links happen to reach into well-connected territory.

Betweenness Centrality
~~~~~~~~~~~~~~~~~~~~~~~~

*What it measures:* how often a node sits on the shortest path between two
*other* nodes — it identifies bridges and bottlenecks, not popularity.

* **Social network**: finds accounts that connect otherwise-separate
  communities — the person who's in both the local tech scene and the local
  arts scene, for example. These are often not the highest-follower
  accounts, but they matter disproportionately for how information (or
  rumors) cross between groups that otherwise wouldn't interact.
* **Obsidian-style vault**: finds notes that bridge two otherwise-unrelated
  topic clusters — an interdisciplinary note connecting, say, a
  "programming" cluster and a "gardening" cluster. This is frequently the
  single most useful stat for spotting *structurally important but easy to
  overlook* notes: a note with only two or three links can still have very
  high betweenness if those links are the only path between two large parts
  of your vault.
* **Interpreting it**: a node with high betweenness but low degree is a
  single point of failure — losing it (or just failing to notice it)
  effectively disconnects the parts of the network it was bridging. This is
  usually the most actionable stat: it points at exactly the connections
  worth protecting or deliberately reinforcing with a second link.

Network Clustering
~~~~~~~~~~~~~~~~~~~~

*What it measures:* live connected-components over whichever edges are
*currently visible* (after any filtering) — this is different from the
Louvain-based ``color='cluster'`` default, which is computed once from the
full, unfiltered graph.

* **Social network**: reveals what happens to the network's shape as you
  tighten a filter — e.g. keeping only mutual (reciprocal) follows, or only
  edges above a certain interaction weight. If the network fragments into
  disconnected islands once weak ties are removed, that tells you those weak
  ties were doing real structural work holding otherwise-separate groups
  together.
* **Obsidian-style vault**: reveals orphaned topic islands — filter down to
  only strong/explicit links, and any notes that fall into their own
  disconnected component are candidates for more deliberate cross-linking to
  the rest of the vault.
* **Interpreting it**: this stat is less about ranking individual nodes and
  more about reading the shape of the *whole* filtered network at a glance —
  watch how many components exist and how large each is as you adjust
  filters, rather than focusing on any one node's value.

Significance
~~~~~~~~~~~~~~

*What it measures:* whether a node's score on a chosen statistic (PageRank,
betweenness, closeness, or HITS hub/authority) is more extreme than you'd
expect from a *random* network with the same degree sequence — computed by
generating many degree-preserving randomized networks and seeing how often a
random node scores as high as this one does, reusing
:func:`d3graph.d3graph.network_significance` directly.

* **Social network**: separates "this account is unusually influential given
  its size" from "this account just happens to have a lot of followers, and
  a randomly-connected network of the same size would produce someone like
  this anyway." Useful for filtering out noise when a network is large
  enough that some nodes look important by chance alone.
* **Obsidian-style vault**: flags notes whose structural role (as a bridge,
  a hub, or a reference point) is unlikely to be a coincidence of how the
  vault happened to grow — worth a second look, since it often surfaces a
  structural role in your own thinking you hadn't consciously designed.
* **Interpreting it**: this produces a p-value per node (exposed as
  ``node_proba``) — lower means the observed score is less likely under
  random rewiring, i.e. more likely a genuine structural property rather
  than noise. It is not a measure of importance by itself; use it alongside
  whichever statistic you ran the significance test against.

Choosing a statistic
~~~~~~~~~~~~~~~~~~~~~~

As a rough guide: start with **PageRank** or **Degree Centrality** for "who/
what matters overall," reach for **Betweenness** when you specifically care
about bridges and single points of failure, use **Closeness** when the
question is about reachability or a good starting point, use **HITS** only
when the graph is directed and the hub/authority distinction is meaningful
(follow graphs, citation graphs), use **Network Clustering** to see how
filtering fragments the network rather than to rank individual nodes, and
add **Significance** on top of any of these when the network is large enough
that "looks important" and "is structurally unusual" might not be the same
thing.

Selecting a statistic drives both node color *and* size together, exactly as
it does in :ref:`d3graph-label`'s own statistics panel — so switching between
a D3graph and a RadialGraph view of the same data feels like the same tool,
not two different ones.


Statistical significance testing
----------------------------------

RadialGraph can test whether a node's centrality is more extreme than you'd
expect by chance, by comparing it against many degree-preserving randomized
versions of the same network — reusing :func:`d3graph.d3graph.network_significance`
directly rather than reimplementing it:

.. code-block:: python

    from d3blocks import D3Blocks

    d3 = D3Blocks()
    df = d3.import_example('energy')

    d3.radialgraph(
        df,
        center='Solar',
        significance_test='pagerank',   # or 'betweenness', 'closeness',
                                         # 'hits_hub', 'hits_authority'
        significance_n_random=1000,     # number of randomized networks
    )

This populates each node's **Significance** value (``node_proba`` — a
p-value; lower means the node's score is less likely to have arisen by
chance under random rewiring) and makes it available as a selectable stat in
the Network Statistic panel. Because this involves generating and re-scoring
many randomized networks, it's opt-in and off by default
(``significance_test=None``) — it isn't free computation.

.. note::
   ``'degree'`` is deliberately not a valid ``significance_test`` choice.
   Degree-preserving randomization has no meaningful null distribution for
   degree itself — the same restriction :func:`d3graph.d3graph.network_significance`
   applies.


Exploring interactively
-------------------------

The parts of RadialGraph that make it feel like an explorer rather than a
static picture:

* **Tap to expand/collapse** — a node with hidden neighbors shows a subtle
  ring indicator; tapping it reveals those neighbors (or hides them again on
  a second tap). Newly revealed nodes animate outward from the node you
  tapped, and existing nodes are briefly frozen in place so the graph makes
  room locally instead of reshuffling everywhere.
* **Ghost preview** — hovering (desktop) or press-and-holding (touch) a node
  with hidden neighbors draws faint, dashed preview markers showing where
  they'd land if revealed, before you commit to expanding.
* **Ripple expand** — reveals the network one hop at a time from the focus
  outward, each ring settling before the next appears, instead of everything
  popping in simultaneously. Useful for showing "how the network grows" —
  e.g. a person, then their direct connections, then connections of
  connections — almost like a wave. Configurable via ``ripple_delay_ms``.
* **Expand all / collapse all** — reveal (or hide back down to) the entire
  network in one action.
* **Ring spacing, auto or manual** — by default, spacing between rings is
  computed from how crowded each ring actually is (``auto_ring_spacing=True``),
  so a ring with many nodes automatically gets pushed further out. Turn this
  off (``auto_ring_spacing=False``) to control spacing directly via
  ``ring_spacing``.
* **Labels that fade in with zoom** — labels for nodes close to the focus
  appear first; deeper, more numerous nodes' labels only appear as you zoom
  in, with collision-avoidance so crowded rings don't turn into overlapping
  text.


Configuring layout and pacing
-------------------------------

.. code-block:: python

    from d3blocks import D3Blocks

    d3 = D3Blocks()
    df = d3.import_example('energy')

    d3.radialgraph(
        df,
        center='Solar',
        ring_spacing=80,
        auto_ring_spacing=True,
        radial_strength=0.8,     # how rigidly nodes snap to their ring
        ripple_delay_ms=900,     # time between each hop reveal during ripple
        charge=-120,             # node repulsion strength
        collision=1.0,
        link_distance=40,
        sticky=True,             # dragged nodes stay where you drop them
    )


Showing or hiding the panels
------------------------------

.. code-block:: python

    from d3blocks import D3Blocks

    d3 = D3Blocks()
    df = d3.import_example('energy')

    d3.radialgraph(
        df,
        show_stats_panel=True,   # the Network Statistic / layout panel
        show_node_panel=True,    # the node-detail panel shown on selection
    )

Both default to ``True``, matching :func:`d3graph.d3graph`'s
``show_slider``-style convention of showing optional UI by default and
letting you opt out.


Node and edge properties
--------------------------

For fine-grained control beyond what the ``radialgraph()`` call itself
exposes, ``node_properties`` and ``edge_properties`` can be inspected and
edited directly, the same way as every other d3blocks chart:

.. code-block:: python

    from d3blocks import D3Blocks

    d3 = D3Blocks()
    df = d3.import_example('energy')

    d3.radialgraph(df, center='Solar', showfig=False)

    # Inspect or override individual node properties before the final show()
    print(d3.node_properties['Solar'])
    d3.node_properties['Solar']['color'] = '#e45756'

    d3.show()


References
----------

    * `d3blocks source code <https://github.com/d3blocks/d3blocks/tree/main/d3blocks/radialgraph>`_
    * `d3graph documentation <https://d3blocks.github.io/d3blocks/pages/html/d3graph.html>`_


.. include:: add_bottom.add
