UI controls (panels and theme)
##############################

Most D3Blocks charts share a small set of **UI parameters** that control the
browser chrome (top bar, side panels) and the page theme. These parameters are
passed on the chart method itself (for example ``d3.scatter(...)``) and are
documented on each method via the API reference.

Show or hide panels
*******************

* ``show_side_panel`` (``bool``, default ``True``) — show or hide the **left
  side panels** (Export / Save, Layout, Filtering, Physics, and chart-specific
  panels). Use this when embedding a chart in a dashboard and you already
  expose the same controls in the host UI (e.g. Streamlit sidebar).
* ``show_top_panel`` (``bool``, default ``True``) — show or hide the **top bar**
  (search, theme toggle, and other toolbar actions).

The two flags are independent: you can keep the top bar and hide the side
panels, or the other way around. Chart interaction in the center of the page
keeps working when panels are disabled.

.. code:: python

   from d3blocks import D3Blocks

   d3 = D3Blocks()
   d3.scatter(
       x=..., y=...,
       show_side_panel=False,   # hide left control stack
       show_top_panel=True,     # keep top toolbar
   )

Theme and background color
**************************

* ``dark_mode`` (``bool``, default ``True``) — initial theme.
  ``True`` → dark theme; ``False`` → light theme (``body.light``). If the chart
  exposes a theme toggle in the top bar, the user can still switch at runtime;
  the initial state follows ``dark_mode``.
* ``color_background`` — page / panel background as a **list of two hex
  colors** ``[dark_hex, light_hex]``. Accepts also:

  * a single hex string (same color for both themes),
  * ``'streamlit'`` — backgrounds matched to a Streamlit app,
  * ``'darkblue'`` — dark navy / soft light blue-gray,
  * ``None`` — theme defaults (``#222222`` / ``#ffffff``).

  Custom backgrounds apply only to the page center, top bar, and side panels.
  Text, axes, and button label colors follow the theme CSS variables and are
  not overridden.

.. code:: python

   d3.sankey(
       df,
       dark_mode=False,
       color_background=['#12141c', '#e8eef5'],  # or 'streamlit' / 'darkblue'
       show_side_panel=True,
       show_top_panel=True,
   )

Which charts support these parameters?
**************************************

The panel and theme parameters are available on the chart methods that ship
with interactive browser chrome, including:

* ``scatter``, ``violin``, ``chord``, ``sankey``, ``heatmap``
* ``timeseries``, ``movingbubbles``
* ``d3graph``, ``elasticgraph``, ``radialgraph``
* ``tree``, ``treemap``, ``circlepacking``, ``maps``

``imageslider`` supports ``dark_mode`` and ``color_background`` (page
background only; it has no side/top control panels).

``particles`` and ``matrix`` use a simpler HTML shell and do not expose the
panel flags.

See also
********

* :doc:`Streamlit` — embedding charts in Streamlit apps, including how to
  mirror panel controls in the Streamlit sidebar.
* Per-chart API pages under **Blocks** (parameters are listed on each
  ``automethod``).
