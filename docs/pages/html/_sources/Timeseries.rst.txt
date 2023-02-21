Timeseries
#############

.. automodule:: d3blocks.d3blocks.D3Blocks.timeseries
    :members:
    :undoc-members:



Input Data
***********

The input dataset is a DataFrame for which the index column is the datetime, and the columns are plotted with their column name.

.. code:: python

	#            Adj Close                      ...    Volume                    
	#                 AAPL      AMZN      META  ...      META      TSLA      TWTR
	# Date                                      ...                              
	# 2018-12-31  1.000000  1.000000  1.000000  ...  1.000000  1.000000  1.000000
	# 2019-01-02  1.001141  1.024741  1.035014  ...  1.142979  1.849896  0.942329
	# 2019-01-03  0.901420  0.998875  1.004958  ...  0.922543  1.105184  1.192595
	# 2019-01-04  0.939901  1.048882  1.052330  ...  1.177736  1.173238  1.465577
	# 2019-01-07  0.937809  1.084915  1.053093  ...  0.815799  1.198166  1.246811

	# [5 rows x 30 columns]



Chart
***********

.. raw:: html

   <iframe src="https://erdogant.github.io\docs\d3blocks\timeseries.html" height="600px" width="775px", frameBorder="0"></iframe>



.. include:: add_bottom.add