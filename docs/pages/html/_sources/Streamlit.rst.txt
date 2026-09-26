Streamlit
#########

D3Blocks charts are self-contained HTML + JavaScript. You can embed them in a
`Streamlit <https://streamlit.io>`_ app by generating the HTML with
``showfig=False`` and ``return_html=True``, then displaying it with
``st.iframe``.

Recommended pattern
*******************

.. code:: python

   import streamlit as st
   from d3blocks import D3Blocks

   st.set_page_config(page_title="D3Blocks", layout="wide")

   # Optional: put chart options in the Streamlit sidebar
   show_side_panel = st.sidebar.checkbox("Show D3Blocks side panels", value=False)
   show_top_panel = st.sidebar.checkbox("Show D3Blocks top panel", value=True)
   height = st.sidebar.slider("Chart height", 400, 1200, 700, 50)

   d3 = D3Blocks()
   # Build HTML without opening a browser window
   html = d3.scatter(
       x=..., y=...,
       show_side_panel=show_side_panel,
       show_top_panel=show_top_panel,
       dark_mode=False,
       color_background='streamlit',
       showfig=False,
       return_html=True,
   )

   st.iframe(html, height=height, width="stretch")

Rules of thumb
**************

* Prefer **``st.iframe(html, height=...)``**. Do **not** use the deprecated
  ``components.html`` for these charts, and avoid ``st.html`` for full
  interactive charts: it is not iframed, and JavaScript is off unless
  ``unsafe_allow_javascript=True``. Fixed-position CSS from the chart would
  also overlay the Streamlit page.
* Always pass an **explicit pixel height** (or ``height="stretch"``).
  ``height="content"`` is unreliable when the chart uses ``position: fixed``
  and contributes almost no document-flow height.
* Generate with **``showfig=False``** and **``return_html=True``**.
* When Streamlit already owns the controls (sidebar), set
  ``show_side_panel=False`` (and optionally ``show_top_panel=False``) so the
  chart does not duplicate UI. See :doc:`UI_controls`.
* ``color_background='streamlit'`` picks backgrounds that match a typical
  Streamlit light/dark page.

Demo apps
*********

Ready-to-run demos live in the repository under the ``streamlit/`` directory.
Each file is a minimal Streamlit app for one chart. Run from a machine with
``d3blocks`` and ``streamlit`` installed:

.. code-block:: console

   streamlit run streamlit/scatter_streamlit_demo.py

Available demos
===============

.. list-table::
   :header-rows: 1
   :widths: 28 40 32

   * - Chart
     - Demo file
     - Notes
   * - Scatter
     - ``scatter_streamlit_demo.py``
     - Point size/color/tooltip; panel toggles
   * - Sankey
     - ``sankey_streamlit_demo.py``
     - Link color/opacity, node layout
   * - Chord
     - ``chord_streamlit_demo.py``
     - Energy-flow style demo
   * - Heatmap
     - ``heatmap_streamlit_demo.py``
     - Matrix heatmap controls
   * - Violin
     - ``violin_streamlit_demo.py``
     - Distribution view
   * - Timeseries
     - ``timeseries_streamlit_demo.py``
     - Multi-series time chart
   * - MovingBubbles
     - ``movingbubbles_streamlit_demo.py``
     - Animated state transitions
   * - Imageslider
     - ``imageslider_streamlit_demo.py``
     - Before/after images; dark mode & background
   * - Treemap
     - ``treemap_streamlit_demo.py``
     - Hierarchical rectangles
   * - Circlepacking
     - ``circlepacking_streamlit_demo.py``
     - Nested circles
   * - Maps
     - ``maps_streamlit_demo.py``
     - Lat/lon markers
   * - D3graph
     - ``d3graph_streamlit_demo.py``
     - Force-directed network
   * - Elasticgraph
     - ``elasticgraph_streamlit_demo.py``
     - Elastic force network
   * - Radialgraph
     - ``radialgraph_streamlit_demo.py``
     - Focus-centered radial network

Typical layout of a demo
========================

1. **Load data** once with ``@st.cache_data`` (often via
   ``d3.import_example(...)``).
2. **Sidebar** — Streamlit widgets for data encodings and for
   ``show_side_panel`` / ``show_top_panel`` / height.
3. **Build HTML** inside a cached function that calls the D3Blocks chart method
   with ``showfig=False``, ``return_html=True``.
4. **Main area** — ``st.iframe(html, height=height, width="stretch")``.

This keeps the interactive D3 chart inside a fixed-height frame while Streamlit
owns navigation and global controls.

See also
********

* :doc:`UI_controls` — ``show_side_panel``, ``show_top_panel``,
  ``color_background``, ``dark_mode``.
* Per-chart pages under **Blocks** for input data shapes and API details.


.. include:: add_bottom.add