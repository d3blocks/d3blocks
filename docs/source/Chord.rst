Chord
#############

.. automodule:: d3blocks.d3blocks.D3Blocks.chord
    :members:
    :undoc-members:



Input Data
***********

The input dataset is a DataFrame with three column, source, target and weight.

.. code:: python

	#       source       target  weight
	# 0      Aemon        Grenn       5
	# 1      Aemon      Samwell      31
	# 2      Aerys        Jaime      18
	# 3      Aerys       Robert       6
	# 4      Aerys       Tyrion       5
	# ..       ...          ...     ...
	# 347   Walder        Petyr       6
	# 348   Walder       Roslin       6
	# 349   Walton        Jaime      10
	# 350  Ygritte       Qhorin       7
	# 351  Ygritte  Rattleshirt       9

	# [352 rows x 3 columns]



Chart
******

.. raw:: html

   <iframe src="https://erdogant.github.io\docs\d3blocks\chord.html" height="750px" width="775px", frameBorder="0"></iframe>





.. include:: add_bottom.add