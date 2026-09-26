Elasticgraph
#############


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


.. automethod:: d3blocks.d3blocks.D3Blocks.elasticgraph


.. raw:: html

   <iframe src="https://erdogant.github.io\docs\d3blocks\elasticgraph_stormofswords.html" height="600px" width="700px", frameBorder="0"></iframe>


.. code:: python

    from d3blocks import D3Blocks
    
    # Initialize
    d3 = D3Blocks()
    
    # Import example
    # df = d3.import_example('stormofswords')
    df = d3.import_example('energy')
    
    # Create force-directed-network (without cluster labels)
    d3.elasticgraph(df, filepath='Elasticgraph.html', showfig=False, collision=1, charge=2500)
    
    # Set all colors to the same color
    # d3.Elasticgraph.D3graph.set_node_properties(fontcolor='#000000')
    
    d3.Elasticgraph.D3graph.node_properties
    d3.Elasticgraph.D3graph.node_properties['Wind']
    d3.Elasticgraph.D3graph.node_properties['Wind']['size']=15
    d3.Elasticgraph.D3graph.node_properties['Wind']['edge_color']='#FFFFFF'
    d3.Elasticgraph.D3graph.node_properties['Wind']['edge_size']=5
    d3.Elasticgraph.D3graph.node_properties['Wind']['fontsize']=20
    d3.Elasticgraph.D3graph.node_properties['Wind']['fontcolor']='#000000'
    d3.Elasticgraph.D3graph.node_properties['Wind']['group']='new group'
    
    # Update another node
    d3.Elasticgraph.D3graph.node_properties['Wave']['size']=8
    d3.Elasticgraph.D3graph.node_properties['Wave']['fontcolor']='#000000'
    d3.Elasticgraph.D3graph.node_properties['Wave']['group']='new group'
    
    d3.Elasticgraph.D3graph.node_properties['Coal']['size']=10
    d3.Elasticgraph.D3graph.node_properties['Biomass_imports']['size']=1
    
    # Set edge properties
    d3.Elasticgraph.D3graph.edge_properties
    d3.Elasticgraph.D3graph.edge_properties[('Wind', 'Electricity_grid')]['label']='TEST'
    #
    # Show elasticgraph
    d3.Elasticgraph.show()


.. raw:: html

   <iframe src="https://erdogant.github.io\docs\d3blocks\elasticgraph_energy.html" height="600px" width="700px", frameBorder="0"></iframe>


.. code:: python

    from d3blocks import D3Blocks
    
    # Initialize
    d3 = D3Blocks()
    df = d3.import_example('socialmedia')
    df = df[0:1000]

    # Create graph
    d3.elasticgraph(df, collision=0.1, charge=2000, size=4, hull_offset=15, showfig=True, figsize=[2500, 2500], filepath=r'socialmedia_1000.html')


Interactive example:

`View the social media network visualization <https://erdogant.github.io\docs\d3blocks\elasticgraph_socialmedia_1000.html>`_

.. raw:: html

   <iframe src="https://erdogant.github.io\docs\d3blocks\elasticgraph_socialmedia_1000.html" height="600px" width="700px", frameBorder="0"></iframe>


.. include:: add_bottom.add