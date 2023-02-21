MovingBubbles
###############

.. tip::
	`D3Blocks: How to Create Storytelling Moving Bubbles Charts in d3js with Python. <https://towardsdatascience.com/how-to-create-storytelling-moving-bubbles-charts-in-d3js-with-python-b31cec7b8226>`_


.. automodule:: d3blocks.d3blocks.D3Blocks.movingbubbles
    :members:
    :undoc-members:



Input Data
***********

The input data is a dataframe that should contain the columns datatime, sample_id and state.
If the column names are different, then the column name can be specified.

.. code:: python

	#                 datetime sample_id     state
	# 0    2000-01-01 00:10:32        30      Sick
	# 1    2000-01-01 00:10:36        23      Work
	# 2    2000-01-01 00:11:16       179  Sleeping
	# 3    2000-01-01 00:11:28       122     Sport
	# 4    2000-01-01 00:13:02       226  Sleeping
	#                  ...       ...       ...
	# 9994 2000-01-01 23:59:56       300  Sleeping
	# 9995 2000-01-01 23:59:57       217      Home
	# 9996 2000-01-01 23:59:57        89  Sleeping
	# 9997 2000-01-01 23:59:58        42  Sleeping
	# 9998 2000-01-01 23:59:58       237      Work

	# [9999 rows x 3 columns]


Chart
******

.. raw:: html

   <iframe src="https://erdogant.github.io\docs\d3blocks\movingbubbles.html" height="900px" width="900px", frameBorder="0"></iframe>



.. include:: add_bottom.add