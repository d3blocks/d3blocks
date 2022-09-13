Chord
####################

A chord graph represents flows or connections between several entities or nodes. Each entity is represented by a fragment on the outer part of the circular layout. Then, arcs are drawn between each entity. The size of the arc is proportional to the importance of the flow. The javascript code is forked from Mike Bostock and then Pythonized.


Input Parameters
---------------------


.. automodule:: d3blocks.d3blocks.D3Blocks.chord
    :members:
    :undoc-members:



Input Data
-----------

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
-----------

.. raw:: html

   <iframe src="https://erdogant.github.io\docs\d3blocks\chord.html" height="750px" width="775px", frameBorder="0"></iframe>



.. raw:: html

	<hr>
	<center>
		<script async type="text/javascript" src="//cdn.carbonads.com/carbon.js?serve=CEADP27U&placement=erdogantgithubio" id="_carbonads_js"></script>
	</center>
	<hr>

