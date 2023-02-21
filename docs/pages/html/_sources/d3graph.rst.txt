D3graph
#############

.. tip::
	`Read the Medium blog for more details about creating beautiful stand-alone interactive D3 charts with Python. <https://towardsdatascience.com/creating-beautiful-stand-alone-interactive-d3-charts-with-python-804117cb95a7>`_

.. note::
	This page contains a summary of the possiblities what you can do with D3graph. More details can be found on the `D3graph documentation pages <https://erdogant.github.io/d3graph>`_.

-------------------------


.. automodule:: d3blocks.d3blocks.D3Blocks.d3graph
    :members:
    :undoc-members:



Input Data
************

The input dataset is a DataFrame with three column, source, target and weight.

.. code:: python

	#                      source            target   weight
	# 0      Agricultural 'waste'    Bio-conversion  124.729
	# 1            Bio-conversion            Liquid    0.597
	# 2            Bio-conversion            Losses   26.862
	# 3            Bio-conversion             Solid  280.322
	# 4            Bio-conversion               Gas   81.144
	# ..                      ...               ...      ...
	# 63       Thermal generation  District heating   79.329
	# 64                    Tidal  Electricity grid    9.452
	# 65  UK land based bioenergy    Bio-conversion  182.010
	# 66                     Wave  Electricity grid   19.013
	# 67                     Wind  Electricity grid  289.366

	# [68 rows x 3 columns]

Charts
************

Default
'''''''' 

.. raw:: html

   <iframe src="https://erdogant.github.io\docs\d3blocks\d3graph_example1.html" height="800px" width="775px", frameBorder="0"></iframe>


Change node properties
''''''''''''''''''''''''


.. raw:: html

   <iframe src="https://erdogant.github.io\docs\d3blocks\d3graph_example2.html" height="800px" width="775px", frameBorder="0"></iframe>


Change Edge properties
''''''''''''''''''''''''

.. raw:: html

   <iframe src="https://erdogant.github.io\docs\d3blocks\d3graph_example3.html" height="775px" width="775px", frameBorder="0"></iframe>





.. include:: add_bottom.add