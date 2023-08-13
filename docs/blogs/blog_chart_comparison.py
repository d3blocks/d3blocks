# %%
# Source node names
source = ['Penny', 'Penny', 'Amy', 'Bernadette', 'Bernadette', 'Sheldon', 'Sheldon', 'Sheldon', 'Rajesh']
# Target node names
target = ['Leonard', 'Amy', 'Bernadette', 'Rajesh', 'Howard', 'Howard', 'Leonard', 'Amy', 'Penny']
# Edge Weights
weight = [5, 3, 2, 2, 5, 2, 3, 5, 2]

# Import and Initialize
from d3blocks import D3Blocks
d3 = D3Blocks()
# Convert
adjmat = d3.vec2adjmat(source, target, weight)
# Print
print(adjmat)

# %%

# Load library
from d3blocks import D3Blocks

# Initialize
d3 = D3Blocks()
# Load stormofswords data sets
df = d3.import_example(data='stormofswords')

# %% Create network graph

# Initialize
d3 = D3Blocks()
# Network graph
d3.d3graph(df, charge=800, collision=2, showfig=True)
# d3.elasticgraph(df, charge=800, collision=2, scaler='zscore')
# Extract the node colors from the network graph.
node_colors = d3.D3graph.node_properties

# %%  Heatmap
# Initialize
d3 = D3Blocks()
# Create the heatmap but do not show it yet because we first need to adjust the colors
d3.heatmap(df, showfig=False)
# Update the colors of the network graph to be consistent with the colors
d3.node_properties

for i, label in enumerate(d3.node_properties['label']):
    if node_colors.get(label) is not None:
        d3.node_properties['color'].iloc[i] = node_colors.get(label)['color']

d3.show(showfig=True, figsize=[600, 600], filepath='c:/temp/heatmap.html', fontsize=8, scaler='zscore')

# %%  Sankey
# Initialize
d3 = D3Blocks()
# Create sankey graph
d3.sankey(df, filepath='c:/temp/sankey.html', showfig=True)
