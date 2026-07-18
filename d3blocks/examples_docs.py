import pandas as pd
from d3blocks import D3Blocks

# PageRank-focused graph
# Many nodes point to A with strong weights → A has highest PageRank
df = pd.DataFrame({
    'source': ['B','C','D','E','F','G','H','I'],
    'target': ['A','A','A','A','A','A','A','A'],
    'weight': [1,2,3,4,5,2,1,3]
})

# Most important node for PageRank: A
d3 = D3Blocks()
d3.d3graph(df, filepath='pagerank_graph.html', directed=True, showfig=True)

# %%

import pandas as pd
from d3blocks import D3Blocks

# HITS-focused graph
# Hubs (H1,H2) → Authorities (A1,A2,A3)
df = pd.DataFrame({
    'source': ['H1','H1','H1','H2','H2','H2'],
    'target': ['A1','A2','A3','A1','A2','A3'],
    'weight': [3,2,1,3,2,1]
})

# Most important nodes:
#   Authorities: A1, A2, A3
#   Hubs: H1, H2

d3 = D3Blocks()
d3.d3graph(df, filepath='hits_graph.html')

# %%

import pandas as pd
from d3blocks import D3Blocks

# Closeness-focused synthetic graph
# C is the center of a star → shortest paths to all nodes → highest closeness
df = pd.DataFrame({
    'source': ['C','C','C','C','C'],
    'target': ['A','B','D','E','F'],
    'weight': [1,1,1,1,1]
})

# Most important node for Closeness Centrality: C

d3 = D3Blocks()
d3.d3graph(df, filepath='closeness_graph.html')

# %%

import pandas as pd
from d3blocks import D3Blocks

# Betweenness-focused synthetic graph
# M is the only connector between two clusters → highest betweenness
df = pd.DataFrame({
    'source': ['A','B','C','M','M','X','Y','Z'],
    'target': ['M','M','M','X','Y','M','M','M'],
    'weight': [1,1,1,3,3,1,1,1]
})

# Most important node for Betweenness Centrality: M

d3 = D3Blocks()
d3.d3graph(df, filepath='betweenness_graph.html')


# %%
import pandas as pd
from d3blocks import D3Blocks

# Degree-focused graph
# X connects to many nodes with strong weights → highest degree centrality
df = pd.DataFrame({
    'source': ['X','X','X','X','X','A','B','C'],
    'target': ['A','B','C','D','E','F','G','H'],
    'weight': [5,4,3,2,1,1,1,1]
})

# Most important node for Degree Centrality: X

d3 = D3Blocks()
d3.d3graph(df, filepath='degree_graph.html')


# %%


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

# %%
# =============================================================================
# CHORD
# =============================================================================
# Load d3blocks
from d3blocks import D3Blocks
#
# Initialize
d3 = D3Blocks()
#
# Load example data
df = d3.import_example('energy')
#
# Plot
d3.chord(df,
         filepath=r'D:\REPOS\erdogant.github.io\docs\d3blocks\chord_energy1.html',
         )
#

# =============================================================================
# 
# =============================================================================

from d3blocks import D3Blocks
#
# Initialize
d3 = D3Blocks()
#
# Load example data
df = d3.import_example('energy')
#
# Plot with very large margins for long labels
d3.chord(df,
         filepath=r'D:\REPOS\erdogant.github.io\docs\d3blocks\chord_energy2.html',
         # figsize=[650, 450],  # Even larger figure size
         margin=300,  # Large margin for long labels
         text_offset=50,  # Large text offset
         )

# =============================================================================
# 
# =============================================================================

# Load d3blocks
from d3blocks import D3Blocks
#
# Initialize
d3 = D3Blocks(chart='Chord', frame=False)
#
# Import example
df = d3.import_example('energy')
#
# Node properties
d3.set_node_properties(df, opacity=0.2, cmap='tab20')
d3.set_edge_properties(df, color='source', opacity='source')
#

# Make some edits to highlight the Nuclear node
# d3.node_properties
d3.node_properties.get('Nuclear')['color']='#ff0000'
d3.node_properties.get('Nuclear')['opacity']=1
# Make edits to highlight the Nuclear Edge
d3.edge_properties.loc[(d3.edge_properties['source'] == 'Nuclear') & (d3.edge_properties['target'] == 'Thermal generation'), 'color'] = '#ff0000'
d3.edge_properties.loc[(d3.edge_properties['source'] == 'Nuclear') & (d3.edge_properties['target'] == 'Thermal generation'), 'opacity'] = 0.8
d3.edge_properties.loc[(d3.edge_properties['source'] == 'Nuclear') & (d3.edge_properties['target'] == 'Thermal generation'), 'weight'] = 1000
#
# Show the chart
d3.show(filepath=r'D:\REPOS\erdogant.github.io\docs\d3blocks\chord_energy3.html')

