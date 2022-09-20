from d3blocks.d3blocks import D3Blocks

# import chord.Chord as Chord
# import imageslider.Imageslider as Imageslider
# import movingbubbles.Movingbubbles as Movingbubbles
# import sankey.Sankey as Sankey
# import scatter.Scatter as Scatter
# import timeseries.Timeseries as Timeseries
# import violin.Violin as Violin
# import particles.Particles as Particles

__author__ = 'Erdogan Taskesen, Oliver Verver'
__email__ = 'erdogant@gmail.com, mail@oliver3.nl'
__version__ = '1.0.5'

# module level doc-string
__doc__ = """
d3blocks
=====================================================================

Description
-----------
d3blocks is for the creation of exclusive stand alone and interactive graphs in d3 javascript.

Example
-------
>>> from d3blocks import d3blocks
>>> #
>>> # Initialize
>>> d3 = D3Blocks()
>>> #
>>> # Load example data
>>> df = d3.import_example(graph='random_time', n=10000, c=300, date_start="2000-1-1 00:10:05", date_stop="2000-1-1 23:59:59")
>>> #
>>> # Plot
>>> d3.movingbubbles(df, speed={"slow": 1000, "medium": 200, "fast": 10})
>>> #

References
----------
https://d3blocks.github.io/d3blocks/

"""
