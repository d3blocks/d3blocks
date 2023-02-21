Scatter
#############

.. tip::
	`Get the Most Out of Your Scatterplot by Making It Interactive Using D3js and Python. <https://towardsdatascience.com/get-the-most-out-of-your-scatterplot-by-making-it-interactive-using-d3js-19939e3b046>`_

-------------------------

.. automodule:: d3blocks.d3blocks.D3Blocks.scatter
    :members:
    :undoc-members:



Input Data
***********

The input dataset are the x-coordinates and y-coordinates that needs to be specified seperately.

.. code:: python

	#                 x          y   age  ... labels
	# labels                              ...                             
	# acc     37.204296  24.162813  58.0  ...    acc 
	# acc     37.093090  23.423557  44.0  ...    acc  
	# acc     36.806297  23.444910  23.0  ...    acc 
	# acc     38.067886  24.411770  30.0  ...    acc  
	# acc     36.791195  21.715324  29.0  ...    acc  
	#           ...        ...   ...  ...    ...     
	# brca     0.839383  -8.870781   NaN  ...   brca 
	# brca    -5.842904   2.877595   NaN  ...   brca
	# brca    -9.392038   1.663352  71.0  ...   brca
	# brca    -4.016389   6.260741   NaN  ...   brca
	# brca     0.229801  -8.227086   NaN  ...   brca 

	# [4674 rows x 9 columns]




Chart
***********

Default scatterplot
''''''''''''''''''''

.. raw:: html

   <iframe src="https://erdogant.github.io\docs\d3blocks\scatter.html" height="600px" width="775px", frameBorder="0"></iframe>


Transitions (2 coordinates)
''''''''''''''''''''''''''''

.. raw:: html

   <iframe src="https://erdogant.github.io\docs\d3blocks\scatter_transitions2.html" height="600px" width="775px", frameBorder="0"></iframe>


Transitions (3 coordinates)
''''''''''''''''''''''''''''

.. raw:: html

   <iframe src="https://erdogant.github.io\docs\d3blocks\scatter_transitions3.html" height="600px" width="775px", frameBorder="0"></iframe>



.. include:: add_bottom.add