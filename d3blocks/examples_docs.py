# =============================================================================
# D3BLOCKS - ELASTICGRAPH
# =============================================================================
from d3blocks import D3Blocks

# Initialize
d3 = D3Blocks()

# Import example
# df = d3.import_example('stormofswords')
df = d3.import_example('energy')

# Create force-directed-network (without cluster labels)
d3.elasticgraph(df, filepath='Elasticgraph.html', showfig=False, collision=1, charge=2500, figsize=[650, 450],)

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
d3.Elasticgraph.show(figsize=[650, 450], 
                     filepath=r'D:\REPOS\erdogant.github.io\docs\d3blocks\elasticgraph_energy.html',
                     )

# =============================================================================
# EXAMPLE 2
# =============================================================================
from d3blocks import D3Blocks
import pandas as pd

# Initialize
d3 = D3Blocks()
df = d3.import_example('socialmedia')

# df = pd.read_csv('https://github.com/d3blocks/d3blocks/files/11995798/Df.csv', sep=',', index_col=False)
# del df['Unnamed: 0']
df = df[0:1000]

d3.elasticgraph(df, collision=0.1, charge=2000, size=4, hull_offset=15, showfig=True, figsize=[2500, 2500], 
                filepath=r'D:\REPOS\erdogant.github.io\docs\d3blocks\elasticgraph_socialmedia_1000.html')


# =============================================================================
# EXAMPLE 3
# =============================================================================
# Load library
from d3blocks import D3Blocks
#
# Initialize
d3 = D3Blocks()
#
# Import example
df = d3.import_example('stormofswords')
#
# Create force-directed-network (without cluster labels)
d3.elasticgraph(df,
                figsize=[650, 450],
                collision=1,
                charge=2500,
                filepath=r'D:\REPOS\erdogant.github.io\docs\d3blocks\elasticgraph_stormofswords.html')

# %%
# =============================================================================
# D3GRAPH
# =============================================================================

# Load library
from d3blocks import D3Blocks
#
# Initialize
d3 = D3Blocks()
#
# Import example
df = d3.import_example('energy')
#
# Create network using default
d3.d3graph(df,
           figsize=[650, 450],
           filepath=r'D:\REPOS\erdogant.github.io\docs\d3blocks\d3graph_example1.html')


# Change scaler
d3.d3graph(df, 
           scaler='minmax',
           figsize=[650, 450],
           filepath=r'D:\REPOS\erdogant.github.io\docs\d3blocks\d3graph_example2.html',
           )

# Change node properties
d3.D3graph.set_node_properties(color=None)
d3.D3graph.node_properties['Solar']['size']=30
d3.D3graph.node_properties['Solar']['color']='#FF0000'
d3.D3graph.node_properties['Solar']['edge_color']='#000000'
d3.D3graph.node_properties['Solar']['edge_size']=5
d3.D3graph.show(figsize=[650, 450],
                filepath=r'D:\REPOS\erdogant.github.io\docs\d3blocks\d3graph_example3.html',
                )

# Change edge properties
d3.D3graph.set_edge_properties(directed=True, marker_end='arrow')
d3.D3graph.show(figsize=[650, 450],
                filepath=r'D:\REPOS\erdogant.github.io\docs\d3blocks\d3graph_example4.html',
                )

# %%
from d3blocks import D3Blocks

# Initialize
d3 = D3Blocks()

# Load example data
df = d3.import_example('socialmedia')
# Slice first 10000 rows
df = df[0:10000]

# Create network using default
d3.d3graph(df, filepath='d3graph.html', showfig=False)

d3.d3graph(df, 
           density_grid_size=60,
           density_blur=10,
           density_opacity=0.6,
           dark_mode=True,
           show_density=True,
           filepath=r'D:\REPOS\erdogant.github.io\docs\d3blocks\d3graph_socialmedia.html',
           )

