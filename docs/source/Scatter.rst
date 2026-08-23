Scatter
#############

.. tip::
	`Get the Most Out of Your Scatterplot by Making It Interactive Using D3js and Python. <https://erdogant.medium.com/>`_

-------------------------

.. automethod:: d3blocks.d3blocks.D3Blocks.scatter



Strengths
***********

The scatter chart is one of the most flexible building blocks in ``d3blocks`` because it is not limited to plotting x/y coordinates. It is designed to turn a table of samples and properties into an *explorable* map:

* **Interactive by design.** Points can be panned, zoomed, hovered, and brushed (rectangular selection) directly in the browser, without regenerating the plot.
* **Multiple visual encodings at once.** Color, size, opacity and labels can each be mapped to a different column, so several dimensions of the data can be inspected simultaneously on top of the x/y layout.
* **Adjustable, intuitive controls.** Sliders — including dual-thumb range sliders for things such as the pixel bounds a point is allowed to render at — let the end-user reshape the chart live, without touching code.
* **Transitions between coordinate systems.** The same set of points can smoothly animate between two or three different x/y layouts (e.g. PCA vs. t-SNE vs. UMAP coordinates), which makes it easy to compare embeddings or track how samples move between representations.
* **Scales to large datasets.** Because rendering happens with D3/SVG in the browser, scatter plots with thousands of points remain responsive.
* **Built-in statistical exploration.** Selecting a subset of points (e.g. via brushing) triggers an on-the-fly statistical association test against every other column in the dataset, surfacing which features are significantly enriched in the selection. This is described in detail in the *Statistical Associations* section below.
* **Composable output.** Like other ``d3blocks`` charts, the result is a self-contained, shareable HTML file that requires no server or notebook to view it.


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



Statistical Associations
**************************

Alongside the visual encodings, the scatter chart can compute **statistical associations** between a selection of points and every other property column in the dataset. Selecting a group of points (e.g. by brushing a region of the plot) defines a binary label ``y`` — 1 for samples inside the selection, 0 for the rest — and each remaining column is then tested for whether it is significantly enriched in that selection. The results are ranked and shown in a stats panel next to the chart, so associations can be discovered interactively rather than being computed up front in a notebook.

The methodology mirrors the enrichment approach used in `HNet: Graphical Hypergeometric Networks <https://arxiv.org/abs/2005.04679>`_, applied here at plot-interaction time instead of over an entire graph. Two different tests are used depending on the data type of the column being compared against the selection.

Categorical features: hypergeometric test
'''''''''''''''''''''''''''''''''''''''''

For a categorical column, each category is treated as a separate binary feature (present / absent per sample), and its overlap with the selection is tested with a one-sided hypergeometric test — the same "over-representation" test HNet uses to decide whether an edge between two categorical nodes is significant.

Given:

* :math:`M` — the total number of samples,
* :math:`n` — the number of samples that have the category of interest,
* :math:`N` — the number of samples in the selection,
* :math:`x` — the observed overlap between the category and the selection,

the probability of seeing an overlap at least as large as the one observed, by chance, is:

.. math::

	P(X \geq x) = \sum_{i=x}^{\min(n, N)} \frac{\binom{n}{i}\binom{M-n}{N-i}}{\binom{M}{N}}

A small p-value means the category is over-represented in the selection far more than would be expected if samples were assigned to it at random — i.e. the category and the selection are statistically associated. Categories with fewer than two occurrences are skipped as too small to test meaningfully, and where a column only has two categories (e.g. ``True``/``False`` or ``0``/``1``), the background/negative class is not tested on its own — only the positive class is, matching HNet's two-class handling.

Numerical features: Mann-Whitney U test
'''''''''''''''''''''''''''''''''''''''

For a numeric column, the values of samples inside the selection are compared against the values of the samples outside it using the **Mann-Whitney U test** (equivalently, the Wilcoxon rank-sum test) — a non-parametric test that does not assume the values are normally distributed, which is what HNet uses for numeric-to-categorical comparisons.

All values are pooled and ranked (tied values receive the average of the ranks they span). If the selection group has :math:`n_1` samples with summed rank :math:`R_1`, and the rest of the data has :math:`n_2` samples, the U statistic and its normal approximation are:

.. math::

	U_1 = R_1 - \frac{n_1 (n_1 + 1)}{2}

.. math::

	z = \frac{U_1 - \dfrac{n_1 n_2}{2}}{\sqrt{\dfrac{n_1 n_2 (n_1 + n_2 + 1)}{12}}}

The two-sided p-value is then obtained from the standard normal CDF, :math:`\Phi`:

.. math::

	P = 2 \left(1 - \Phi(|z|)\right)

A small p-value indicates the numeric column's distribution differs meaningfully between the selected samples and the rest (e.g. the selection tends to have systematically higher or lower values), rather than the difference being attributable to chance. Alongside the p-value, the mean, sample standard deviation and median are also reported for both groups, so an association can be interpreted in terms of effect direction and size — not only significance.

Multiple testing correction
'''''''''''''''''''''''''''''

Because a p-value is computed independently for every category and every numeric column, testing many columns at once inflates the chance of false positives. To control this, the raw p-values are corrected before filtering on significance, using one of:

* **Holm-Bonferroni** (default) — a step-down procedure that is less conservative than a plain Bonferroni correction while still strongly controlling the family-wise error rate.
* **Bonferroni** — the classical correction, which simply scales each p-value by the number of tests performed.

Only associations whose adjusted p-value (``Padj``) falls below the significance threshold ``alpha`` (default ``0.05``) are kept, and the surviving associations are sorted by ``Padj`` so the strongest, most reliable associations surface first in the stats panel.

.. tip::
	The underlying enrichment engine is dependency-free JavaScript (no server round-trip needed) and can also be called directly, independent of the chart: ``D3BlocksAssociations.enrichment(columns, yBits, alpha, dtypeOverrides, multtest)`` returns the filtered, sorted list of significant associations for a set of columns and a binary selection mask.


.. include:: add_bottom.add