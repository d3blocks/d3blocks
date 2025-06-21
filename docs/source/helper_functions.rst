The D3Blocks library also contains various helper functions to get the data in the right shape for the desired chart.

Export to HTML
###############
Each block can be exported to HTML using the return_html parameter.

.. code:: python

    # load library
    from d3blocks import D3Blocks

    # Initialize
    d3 = D3Blocks()
    
    # Get data
    df = d3.import_example(data='energy')
    
    # Return HTML for Sankey
    html = d3.sankey(df, return_html=True)


vec2adjmat
#############

.. automodule:: d3blocks.D3Blocks.vec2adjmat
    :members:
    :undoc-members:



adjmat2vec
#############

.. automodule:: d3blocks.D3Blocks.adjmat2vec
    :members:
    :undoc-members:


Examples
#############

.. automodule:: d3blocks.D3Blocks.import_example
    :members:
    :undoc-members:


Saving Charts
#############

Each d3block contains saving functionality to save your chart to a SVG image.
The save functionality can be enabled by setting the ```

.. include:: add_bottom.add