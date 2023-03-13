Treemap
#############

-------------------------

.. automodule:: d3blocks.d3blocks.D3Blocks.treemap
    :members:
    :undoc-members:


Input Data
************

The input dataset is a DataFrame that is hierarchically ordered from left to right. 
The number can be 3 levels and the column weight is obligatory.

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


Three levels and the column weight.

.. code:: python

	#    group1  group2 group3  weight
	# 0  Animal  Mammal    Fox   35000
	# 1  Animal  Mammal   Lion   25000
	# 2  Animal    Fish    Cod   10000
	# 3   Plant    Tree    Oak    1500
	# 4  Animal    Fish    Ape    1750


Charts
************

.. raw:: html

   <iframe src="https://erdogant.github.io\docs\d3blocks\Treemap_energy.html" height="600px" width="775px", frameBorder="0"></iframe>


.. include:: add_bottom.add
