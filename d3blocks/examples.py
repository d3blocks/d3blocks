# %%
# import d3blocks
# print(dir(d3blocks))
# print(d3blocks.__version__)
# import pandas as pd
# import numpy as np

# df = d3.import_example('bigbang')
# df1 = df.groupby(['source', 'target'])['weight'].sum()
# df1 = df1.reset_index()

# %%
# Scatter
from d3blocks import D3Blocks
d3 = D3Blocks()
df = d3.import_example('cancer')
html = d3.scatter(df['x'].values, df['y'].values, c_gradient='opaque', color=df['labels'].values, stroke='#000000')

# %%
import pandas as pd
import numpy as np
from d3blocks import D3Blocks

# Initialize
d3 = D3Blocks(verbose=10, support='text')

# Import example
df = d3.import_example('energy')
html = d3.chord(df)

# Import example
df = d3.import_example('stormofswords')
df = d3.vec2adjmat(df['source'], df['target'], weight=df['weight'], symmetric=True)
d3.heatmap(df, classlabel='cluster', stroke='red', vmax=1)

df = pd.DataFrame(np.random.randint(0, 10, size=(6, 20)))
d3.matrix(df, cmap='interpolateGreens')

df = d3.import_example('energy')
html = d3.particles('D3blocks')

df = d3.import_example(data='energy')
d3.sankey(df, link={"color":"source-target"})

df = d3.import_example('cancer')
html = d3.scatter(df['x'].values, df['y'].values)

df = d3.import_example('climate')
html = d3.timeseries(df, datetime='date', dt_format='%Y-%m-%d %H:%M:%S')

df = d3.import_example('energy')
html = d3.treemap(df)

df = d3.import_example('cancer')
html = d3.violin(x=df['labels'].values, y=df['age'].values)

# %%
# group by source and target, and count occurrences
# counts = dfnew.groupby(['source', 'target']).count()
# add weight column with count values
# counts['weight'] = counts['weight']
# reset index to make columns from groupby into columns of the dataframe
# counts = counts.reset_index()


# %% Treemap
from d3blocks import D3Blocks
# Initialize
d3 = D3Blocks(verbose='info')
# Import example
# df = d3.import_example('animals')
df = d3.import_example('energy')
# df = d3.import_example('stormofswords')
# df = d3.import_example('bigbang')
# Create treemap
html = d3.treemap(df, notebook=False, filepath=None)
# html = d3.treemap(df, notebook=False, filepath=r'c:\temp\treemap.html', figsize=[1400, 800], font={'size':8}, border={'color': '#000000', 'width': 1})
# html = d3.treemap(df, notebook=False, filepath=r'c:\temp\treemap.html', figsize=[None, None], font={'size':8}, border={'color': '#000000', 'width': 1})


# %% Fontsize in violin map
# Import example dataset
from d3blocks import D3Blocks

# Initialize
d3 = D3Blocks()

df = d3.import_example('cancer')

# Create the chart
d3.violin(x=df['labels'].values,
          y=df['age'].values,
          tooltip=df['labels'].values + ' <br /> Survival: ' + df['survival_months'].astype(str).values,
          bins=50,
          fontsize_axis=10,
          fontsize=10,
          size=df['survival_months'].values/10,
          x_order=['acc','kich', 'brca','lgg','blca','coad','ov'],
          filepath=r'c:\temp\violine.html', figsize=[900, None])


# %% VIOLIN - EXAMPLE
from d3blocks import D3Blocks

# Initialize
d3 = D3Blocks()

# Import example dataset
df = d3.import_example('cancer')

# Set some input variables.
tooltip = df['labels'].values + ' <br /> Survival: ' + df['survival_months'].astype(str).values
fontsize = df['survival_months'].values/10

# Create the chart
d3.violin(x=df['labels'].values,
          y=df['age'].values,
          fontsize=fontsize,
          tooltip=tooltip,
          bins=50,
          size=df['survival_months'].values/10,
          x_order=['acc','kich', 'brca','lgg','blca','coad','ov'],
          filepath=r'c:\temp\violine.html', figsize=[900, None])


from d3blocks import D3Blocks
# Initialize
d3 = D3Blocks(chart='Violin', frame=True)
# Import example
df = d3.import_example('cancer')
# Edge properties
tooltip = df['labels'].values + ' <br /> Survival: ' + df['survival_months'].astype(str).values
d3.set_edge_properties(x=df['labels'].values,
                        y=df['age'].values,
                        fontsize=16,
                        tooltip=tooltip,
                        size=df['survival_months'].values/10,
                        x_order=['acc','kich', 'brca','lgg','blca','coad','ov'],
                        filepath='violine_demo.html')
# d3.edge_properties
d3.show(filepath='c://temp//violin1.html')


# %%
from d3blocks import D3Blocks

# Initialize
d3 = D3Blocks(verbose=10)
# Import example
df = d3.import_example('energy')
html = d3.chord(df, filepath=None, notebook=True)

# Link settings
# d3.chord(df, filepath=None, color='target', showfig=False)
# html = d3.chord(df, filepath=None, showfig=True)


d3.chord(df, filepath=r'c:\temp\chord\chord.html', color='target', notebook=False)


# %% Movingbubbles - Make manual dataset to test the working

# This is an example to demonstrate standardize='samplewise'.
# 

import pandas as pd
from d3blocks import D3Blocks
d3 = D3Blocks()

df1 = pd.DataFrame(columns=['datetime', 'sample_id', 'state'])
df1['datetime'] = ['01-01-2000 00:00:00',
                   '01-01-2000 00:05:00',
                   '01-01-2000 00:10:00',
                   '01-01-2000 00:15:00',
                   '01-01-2000 00:20:00',
                   '01-01-2000 00:25:00']
df1['sample_id'] = [1, 1, 1, 1, 1, 1]
df1['state'] = ['home', 'school', 'work', 'eating', 'coffee', 'sleeping']

df2 = pd.DataFrame(columns=['datetime', 'sample_id', 'state'])
df2['datetime'] = ['01-01-2000 00:00:00',
                   '01-01-2000 00:10:00',
                   '01-01-2000 00:15:00',
                   '01-01-2000 00:20:00',
                   '01-01-2000 00:25:00',
                   '01-01-2000 00:30:00']
df2['sample_id'] = [2, 2, 2, 2, 2, 2]
df2['state'] = ['home', 'school', 'work', 'eating', 'coffee', 'sleeping']

df3 = pd.DataFrame(columns=['datetime', 'sample_id', 'state'])
df3['datetime'] = ['01-01-2000 01:00:00',
                   '01-01-2000 01:15:00',
                   '01-01-2000 01:20:00',
                   '01-01-2000 01:25:00',
                   '01-01-2000 01:30:00',
                   '01-01-2000 01:35:00']
df3['sample_id'] = [3, 3, 3, 3, 3, 3]
df3['state'] = ['home', 'school', 'work', 'eating', 'coffee', 'sleeping']

# Concatenate the dataframes
df = pd.concat([df1, df2, df3], axis=0)

print(df)
#               datetime  sample_id     state
# 0  01-01-2000 00:00:00          1      home
# 1  01-01-2000 00:05:00          1    school
# 2  01-01-2000 00:10:00          1      work
# 3  01-01-2000 00:15:00          1    eating
# 4  01-01-2000 00:20:00          1    coffee
# 5  01-01-2000 00:25:00          1  sleeping
# 
# 0  01-01-2000 00:00:00          2      home
# 1  01-01-2000 00:10:00          2    school
# 2  01-01-2000 00:15:00          2      work
# 3  01-01-2000 00:20:00          2    eating
# 4  01-01-2000 00:25:00          2    coffee
# 5  01-01-2000 00:30:00          2  sleeping
# 
# 0  12-12-2000 00:00:00          3      home
# 1  12-12-2000 00:15:00          3    school
# 2  12-12-2000 00:20:00          3      work
# 3  12-12-2000 00:25:00          3    eating
# 4  12-12-2000 00:30:00          3    coffee
# 5  12-12-2000 00:35:00          3  sleeping

# standardize the time per sample id and make the starting-point the same
# df = d3.standardize(df, sample_id='sample_id', datetime='datetime')

# # Compute delta (this is automatically done if not seen in datafame available)
# df = d3.compute_time_delta(df, sample_id='sample_id', datetime='datetime', state='state')

# Notes that are shown between two time points.
time_notes = [{"start_minute": 1, "stop_minute": 5, "note": "In the first 5 minutes, nothing will happen and every entity is waiting in it's current state."}]
time_notes.append({"start_minute": 6, "stop_minute": 10, "note": "The first entity will move to school. The rest is still at home."})
time_notes.append({"start_minute": 11, "stop_minute": 15, "note": "The first entity will move to work and the second entity to school. There is still one at home."})
time_notes.append({"start_minute": 16, "stop_minute": 40, "note": "From this point, the entities will move behind each other towards threir final destination: sleeping."})


# df['size']=4
# df['size'][df['sample_id']==1]=10
# df['size'][df['sample_id']==3]=40
size = {1: 60, 2: 40, 3: 10}
color = {1: '#000000', 2: '#000FFF', 3: '#FFF000'}

# Make the moving bubbles
d3.movingbubbles(df, 
                 datetime='datetime',
                 state='state',
                 sample_id='sample_id',
                 size=size,
                 color=color,
                 color_method='node',
                 timedelta='minutes',
                 speed={"slow": 1000, "medium": 100, "fast": 10},
                 time_notes=time_notes,
                 filepath=r'c:\temp\movingbubbles.html',
                 cmap='Set2',
                 # standardize='minimum',
                  standardize='samplewise',
                 # standardize='relative',
                 )

df1=d3.edge_properties


# %% Moving bubbles
from d3blocks import D3Blocks
# Initialize
d3 = D3Blocks(chart='movingbubbles', frame=False)
# Import example
df = d3.import_example('random_time', n=1000, c=100, date_start="1-1-2000 00:10:05", date_stop="1-1-2000 23:59:59")

# Add node size and adjust for some sample_ids
# df['size']=4
# df['size'][df['sample_id']==1]=20
# df['size'][df['sample_id']==3]=40

# size = {1: 20, 3: 40}
# color = {1: '#000000', 3: '#000FFF'}
size = {1: 20}
color = {1: '#FF0000'}

# Node properties
d3.set_node_properties(labels=df['state'])
# d3.node_properties
d3.node_properties.get('Sleeping')['color'] = '#000000'
# d3.node_properties
d3.set_edge_properties(df, size=size, color=color)
# d3.edge_properties
# Show
d3.show(color_method='node', filepath=r'c:\temp\movingbubbles.html', title='Movingbubbles with adjusted configurations.')
d3.show(standardize='samplewise', color_method='node', filepath=r'c:\temp\movingbubbles.html', title='Movingbubbles with adjusted configurations.')
d3.show(standardize='sequential', color_method='node', filepath=r'c:\temp\movingbubbles.html', title='Movingbubbles with adjusted configurations.')



df1 = d3.edge_properties
# or

from d3blocks import D3Blocks
# Initialize
d3 = D3Blocks(frame=False)
# Import example
df = d3.import_example('random_time', n=1000, c=100, date_start="1-1-2000 00:10:05", date_stop="1-1-2000 23:59:59")

# Show with size=5
d3.movingbubbles(df, size=5, filepath='c://temp/movingbubbles.html')

# Set node size for specifiek sample_id
size = {17: 20, 8: 40}
d3.movingbubbles(df, size=size, filepath='c://temp/movingbubbles.html')


# %%
from d3blocks import D3Blocks

d3 = D3Blocks(chart='Sankey', frame=True)
df = d3.import_example(data='energy')
d3.set_node_properties(df)
d3.set_edge_properties(df, color='target', opacity='target')
d3.show()


d3 = D3Blocks()
df = d3.import_example(data='energy')
d3.sankey(df, filepath='sankey.html', link={"color":"source-target"})
d3.show()




# %% 
df = pd.read_csv(r'D:\REPOS\d3blocks\d3blocks\data\test_AL.csv')

# Notes that are shown between two time points.
time_notes = [{"start_minute": 1, "stop_minute": 10, "note": "The first 10 minutes start in the state Regarder la TV."}]
time_notes.append({"start_minute": 11, "stop_minute": 360, "note": "Then we stay in this state up to 12:00"})
time_notes.append({"start_minute": 361, "stop_minute": 390, "note": "Finally the Consulter de l actualite happens and is up to 13:30."})
time_notes.append({"start_minute": 391 , "stop_minute": 450, "note": "aaaand we go back to the first state.."})


from d3blocks import D3Blocks
d3 = D3Blocks()
d3.movingbubbles(df,
                 standardize='sequential',
                 dt_format='%Y-%m-%d %H:%M:%S',
                 time_notes=time_notes,
                 title='d3blocks_movingbubbles',
                 speed={"slow": 1000,
                        "medium": 200,
                        "fast": 20},
                 )

df1 = d3.edge_properties
d3.edge_properties['time_in_state'].cumsum()

# %% 

df = pd.read_csv(r'D:\REPOS\d3blocks\d3blocks\data\test_3_AL.csv')

size={2386: 20, 10197: 10}
color={2386: '#FF0000'}

d3.movingbubbles(df,
                 standardize='samplewise',
                 size=size,
                 color=color,
                 color_method='node',
                 dt_format='%Y-%m-%d %H:%M:%S',
                 title='d3blocks_movingbubbles',
                 cmap='Set1',
                 timedelta='minutes',
                 speed={"slow": 1000,
                        "medium": 200,
                        "fast": 20},
                 )

df1 = d3.edge_properties

for i, _ in enumerate(df1.index):
    df1['sample_id'].iloc[i]

# %% Matrix
import pandas as pd
import numpy as np
from d3blocks import D3Blocks
d3 = D3Blocks()
df = pd.DataFrame(np.random.randint(0, 10, size=(6, 20)))
d3.matrix(df, filepath='c:/temp/matrix/matrix.html', cmap='interpolateGreens')

from d3blocks import D3Blocks
d3 = D3Blocks()
df = d3.import_example('stormofswords')
df = d3.vec2adjmat(df['source'], df['target'], weight=df['weight'], symmetric=True)
d3.matrix(df, filepath='c:/temp/matrix/matrix.html', cmap='interpolateGreens', vmax=20, figsize=[1000, 800])

# %% Heatmap
from d3blocks import D3Blocks

# Initialize
d3 = D3Blocks()
# Import example
# df = d3.import_example('bigbang')
df = d3.import_example('stormofswords')
# df = d3.import_example('energy')
df = d3.vec2adjmat(df['source'], df['target'], weight=df['weight'], symmetric=True)

# d3.heatmap(df, filepath='c:/temp/heatmap.html', classlabel=[1,1,1,2,2,2,3])
d3.heatmap(df, filepath='c:/temp/heatmap.html', classlabel='cluster', stroke='red', vmax=1, figsize=(400, 400))
html = d3.heatmap(df, filepath=None, notebook=False)
d3.heatmap(df, notebook=True)


# %% Notebook examples

# Violin
from d3blocks import D3Blocks
d3 = D3Blocks()
df = d3.import_example('cancer')
html = d3.violin(x=df['labels'].values, y=df['age'].values, filepath=None, notebook=False)
assert html is not None
html = d3.violin(x=df['labels'].values, y=df['age'].values, filepath=None, notebook=True)
assert html is None
html = d3.violin(x=df['labels'].values, y=df['age'].values, filepath='./test.html', notebook=False)
assert html is None


# Timeseries
from d3blocks import D3Blocks
d3 = D3Blocks()
df = d3.import_example('climate')
html = d3.timeseries(df, datetime='date', dt_format='%Y-%m-%d %H:%M:%S', filepath=None, notebook=False)
assert html is not None
html = d3.timeseries(df, datetime='date', dt_format='%Y-%m-%d %H:%M:%S', filepath=None, notebook=True)
assert html is None
html = d3.timeseries(df, datetime='date', dt_format='%Y-%m-%d %H:%M:%S', filepath='./test.html', notebook=False)
assert html is None

# Scatter
from d3blocks import D3Blocks
d3 = D3Blocks()
df = d3.import_example('cancer')
html = d3.scatter(df['x'].values, df['y'].values, filepath=None, notebook=False)
assert html is not None
html = d3.scatter(df['x'].values, df['y'].values, filepath=None, notebook=True)
assert html is None
html = d3.scatter(df['x'].values, df['y'].values, filepath='./test.html', notebook=False)
assert html is None

# Sankey
from d3blocks import D3Blocks
d3 = D3Blocks()
df = d3.import_example('energy')
html = d3.sankey(df, filepath=None, notebook=False)
assert html is not None
html = d3.sankey(df, filepath=None, notebook=True)
assert html is None
html = d3.sankey(df, filepath='./test.html', notebook=False)
assert html is None


# Particles
from d3blocks import D3Blocks
d3 = D3Blocks()
df = d3.import_example('energy')
html = d3.particles('D3blocks', filepath=None, notebook=False)
assert html is not None
html = d3.particles('D3blocks', filepath=None, notebook=True)
assert html is None
html = d3.particles('D3blocks', filepath='test.html', notebook=False)
assert html is None


# Movingbubbles
from d3blocks import D3Blocks
d3 = D3Blocks()
df = d3.import_example('random_time', n=10000, c=100, date_start="1-1-2000 00:10:05", date_stop="1-1-2000 23:59:59")
html = d3.movingbubbles(df, speed={"slow": 1000, "medium": 200, "fast": 10}, filepath=None, notebook=False)
assert html is not None
html = d3.movingbubbles(df, speed={"slow": 1000, "medium": 200, "fast": 10}, filepath=None, notebook=True)
assert html is None
html = d3.movingbubbles(df, speed={"slow": 1000, "medium": 200, "fast": 10}, filepath='test.html', notebook=False)
assert html is None


# Imageslider
from d3blocks import D3Blocks
d3 = D3Blocks()
img_before, img_after = d3.import_example('southern_nebula_internet')
html = d3.imageslider(img_before, img_after, filepath=None, notebook=False)
assert html is not None
html = d3.imageslider(img_before, img_after, filepath=None, notebook=True)
assert html is None
html = d3.imageslider(img_before, img_after, filepath='test.html', notebook=False)
assert html is None

# Chord
from d3blocks import D3Blocks
d3 = D3Blocks()
df = d3.import_example('energy')
html = d3.chord(df, filepath=None, notebook=False)
assert html is not None
html = d3.chord(df, filepath=None, notebook=True)
assert html is None
html = d3.chord(df, filepath='test.html', notebook=False)
assert html is None



# %%
from d3blocks import D3Blocks

# Initialize
d3 = D3Blocks(verbose=10)
# Import example
df = d3.import_example('energy')
html = d3.chord(df, filepath=None, notebook=True)

# Link settings
# d3.chord(df, filepath=None, color='target', showfig=False)
# html = d3.chord(df, filepath=None, showfig=True)


d3.chord(df, filepath=None, color='target', notebook=False)

d3.chord(df, filepath='chord_demo2.html', color='source')
d3.chord(df, filepath='chord_demo3.html', color='source-target')


# %% Force directed clustered graphs
# Load library
from d3blocks import D3Blocks
#
# Initialize
d3 = D3Blocks()
#
# Import example
df = d3.import_example('energy') # 'stormofswords'
#
# Create force-directed-network (without cluster labels)
d3.elasticgraph(df, filepath='Elasticgraph.html', figsize=[700, 700])
#
# Show elasticgraph
d3.Elasticgraph.show()
# Show original graph with the same properties
d3.Elasticgraph.D3graph.show()
#
# Add cluster labels (no need to do it again because it is the default)
# d3.Elasticgraph.set_node_properties(color=None)
#
# After making changes, show the graph again using show()
d3.Elasticgraph.show()
# Show original graph
d3.Elasticgraph.D3graph.show()
#
# Node properties
d3.Elasticgraph.D3graph.node_properties
#
# Node properties
d3.Elasticgraph.D3graph.edge_properties


# %% Create scatter chart
from d3blocks import D3Blocks
import numpy as np

# Initialize
d3 = D3Blocks()

# Load example data
df = d3.import_example('mnist')

size=np.random.randint(0, 8, df.shape[0])
opacity=np.random.randint(0, 8, df.shape[0])/10
tooltip = df['y'].values.astype(str)

# Set all propreties
d3.scatter(df['PC1'].values,                   # PC1 x-coordinates
           df['PC2'].values,                   # PC2 y-coordinates
           x1=df['tsne_1'].values,             # tSNE x-coordinates
           y1=df['tsne_2'].values,             # tSNE y-coordinates
           color=df['y'].values.astype(str),   # Hex-colors or classlabels
           tooltip=tooltip,                    # Tooltip
           size=size,                          # Node size
           opacity=opacity,                    # Opacity
           stroke='#000000',
           cmap='tab20',                       # Colormap
           scale=True,                         # Scale the datapoints
           label_radio=['PCA', 'tSNE'],
           figsize=[1024, 768], 
           filepath='scatter_demo.html',
           )

d3.edge_properties

#      label         x         y        x1  ...  size   stroke  opacity tooltip
# 0        0  0.472107  0.871347  0.294228  ...     0  #000000      0.1       0
# 1        1  0.624696  0.116735  0.497958  ...     0  #000000      0.5       1
# 2        2  0.608419  0.305549  0.428529  ...     4  #000000      0.6       2
# 3        3  0.226929  0.532931  0.555316  ...     4  #000000      0.0       3
# 4        4  0.866292  0.553489  0.589746  ...     1  #000000      0.6       4
#    ...       ...       ...       ...  ...   ...      ...      ...     ...
# 1792     9  0.262069  0.709428  0.693593  ...     5  #000000      0.5       9
# 1793     0  0.595571  0.837987  0.352114  ...     6  #000000      0.5       0
# 1794     8  0.668742  0.359209  0.520301  ...     6  #000000      0.4       8
# 1795     9  0.416983  0.694063  0.683949  ...     6  #000000      0.4       9
# 1796     8  0.489814  0.588109  0.529971  ...     1  #000000      0.4       8

# [1797 rows x 12 columns]

d3.show(filepath='scatter_demo.html', label_radio=['PCA', 'tSNE'])

# %% Create scatter chart with movements example
from d3blocks import D3Blocks

# Initialize
d3 = D3Blocks(frame=True)
# Import example
x=[1, 1, 1]
y=[1, 2, 3]

x1=[1,  1, 1]
y1=[10, 9, 5]

x2=[5, 6, 7]
y2=[5, 5, 5]

size=[15, 20, 25]
color=['#FF0000', '#0000FF', '#00FF00']
stroke=['#FFFFFF', '#FFFFFF', '#FFFFFF']
opacity=[0.7, 0.8, 0.8]
tooltip=['1st datapoint', '2nd datapoint', '3th datapoint']

# Set all propreties
d3.scatter(x,              # tSNE x-coordinates
           y,              # tSNE y-coordinates
           x1=x1,         # PC1 x-coordinates
           y1=y1,         # PC2 y-coordinates
           x2=x2,         # PC1 x-coordinates
           y2=y2,         # PC2 y-coordinates
           size=size,                   # Size
           color=color,   # Hex-colors or classlabels
           stroke=stroke,            # Edge color
           opacity=opacity,                 # Opacity
           tooltip=tooltip,             # Tooltip
           cmap='tab20',                # Colormap
           scale=False,                  # Scale the datapoints
           label_radio=['(x, y)', '(x1, y1)', '(x2, y2)'],
           figsize=[1024, 768],
           filepath='c://temp//scatter_demo.html',
           )


# %% Issue: 
import pandas as pd
import numpy as np

source=['A','A','B','C','E','F']
target=['B','B','C','D','D','D']
weights=[1,1,2,1,1,1]

df = pd.DataFrame(data=np.c_[source, target, weights], columns=['source','target','weight'])
from d3blocks import D3Blocks

# Initialize
d3 = D3Blocks(frame=True)
d3.chord(df)

# Edit any of the properties you want in the dataframe:
d3.node_properties

#        id label    color  opacity
# label                            
# A       0     A  #1f77b4      0.8
# B       1     B  #2ca02c      0.8
# C       2     C  #9467bd      0.8
# D       3     D  #e377c2      0.8
# E       4     E  #bcbd22      0.8
# F       5     F  #9edae5      0.8

d3.edge_properties
d3.edge_properties['color'].iloc[1]='#000000'

#   source target weight  opacity    color
# 0      A      B      1      0.8  #1f77b4
# 1      A      B      1      0.8  #1f77b4
# 2      B      C      2      0.8  #2ca02c
# 3      C      D      1      0.8  #9467bd
# 4      E      D      1      0.8  #bcbd22
# 5      F      D      1      0.8  #9edae5

# Plot again
d3.show()




# %% Force directed graphs
from d3blocks import D3Blocks

# Initialize
d3 = D3Blocks()

# Load example data
df = d3.import_example('energy')

# Plot
d3.d3graph(df, filepath='c:/temp/d3graph.html', showfig=True, charge=400, support=True)

# Set clusters
d3.D3graph.set_node_properties(color='cluster')
d3.D3graph.edge_properties['UK_land_based_bioenergy', 'Bio-conversion']['label'] = 'test'
d3.D3graph.show()


d3.D3graph.set_node_properties(color='#000000')
d3.D3graph.show()

# %% CHORD - EXAMPLE
from d3blocks import D3Blocks

# Initialize
d3 = D3Blocks(chart='Chord', frame=False)
# Import example
df = d3.import_example('energy')
# Node properties
d3.set_node_properties(df, opacity=0.2, cmap='tab20')
d3.set_edge_properties(df, color='source', opacity='source')
# Show the chart
d3.show()
# Make some edits to highlight the Nuclear node
# d3.node_properties
d3.node_properties.get('Nuclear')['color']='#ff0000'
d3.node_properties.get('Nuclear')['opacity']=1
# Show the chart
d3.show()
# Make edits to highlight the Nuclear Edge
d3.edge_properties.get(('Nuclear', 'Thermal generation'))['color']='#ff0000'
d3.edge_properties.get(('Nuclear', 'Thermal generation'))['opacity']=0.8
d3.edge_properties.get(('Nuclear', 'Thermal generation'))['weight']=1000
# Show the chart
d3.show()


# Initialize
d3 = D3Blocks(chart='Chord', frame=False)
# Import example
df = d3.import_example('energy')
# Node properties
d3.set_node_properties(df, opacity=0.2, cmap='tab20')
d3.set_edge_properties(df)
# Show the chart
d3.show()
# Make some edits to highlight the Nuclear node
# d3.node_properties
d3.node_properties.get('Electricity grid')['color']='#000000'
d3.node_properties.get('Electricity grid')['opacity']=1
d3.show()
# Make edits to highlight the link Thermal generation <-> Thermal generation
d3.edge_properties.get(('Thermal generation', 'Electricity grid'))['color']='#ff0000'
d3.edge_properties.get(('Thermal generation', 'Electricity grid'))['opacity']=0.8
# d3.edge_properties.get(('Thermal generation', 'Electricity grid'))['weight']=1000
# Show the chart
d3.show()
# Use the opacity color of the nodes to color the edges/links
d3.set_edge_properties(df, opacity='source')
d3.show()

# or

# Create chord diagram
from d3blocks import D3Blocks
# Initialize
d3 = D3Blocks()
# Import example
df = d3.import_example('energy')
# Create chord diagram
d3.chord(df)
d3.chord(df, color='target', opacity=0.8, filepath='chord_demo1.html')
d3.chord(df, color='#000000', opacity=0.4, filepath='chord_demo2.html')


# %% SCATTER - prevent overplotting by including density
# Load library
from d3blocks import D3Blocks

# Initialize
d3 = D3Blocks(frame=True)
# Import example
df = d3.import_example('cancer')

# Setup the tooltip
tooltip=df['labels'].values + ' <br /> Survival: ' + df['survival_months'].astype(str).str[0:4].values
# Set the size
size = df['survival_months'].fillna(1).values / 10

# Set all propreties
d3.scatter(df['x'].values,              # tSNE x-coordinates
           df['y'].values,              # tSNE y-coordinates
           x1=df['PC1'].values,         # PC1 x-coordinates
           y1=df['PC2'].values,         # PC2 y-coordinates
           size=size,                   # Size
           color=df['labels'].values,   # Hex-colors or classlabels
           stroke='#000000',            # Edge color
           opacity=0.7,                 # Opacity
           tooltip=tooltip,             # Tooltip
           cmap='tab20',                # Colormap
           scale=True,                  # Scale the datapoints
           label_radio=['tSNE', 'PCA'],
           figsize=[1024, 768],
           filepath='c://temp//scatter_demo.html',
           )


# Make edits in the dataframe.
d3.edge_properties

#      label         x         y  ...   stroke  opacity                     tooltip
# 0      acc  0.796433  0.745925  ...  #000000      0.8   acc <br /> Survival: 44.5
# 1      acc  0.795550  0.739818  ...  #000000      0.8   acc <br /> Survival: 55.0
# 2      acc  0.793272  0.739995  ...  #000000      0.8   acc <br /> Survival: 63.8
# 3      acc  0.803293  0.747982  ...  #000000      0.8   acc <br /> Survival: 11.9
# 4      acc  0.793152  0.725707  ...  #000000      0.8   acc <br /> Survival: 79.7
#    ...       ...       ...  ...      ...      ...                         ...
# 4669  brca  0.507579  0.473040  ...  #000000      0.8   brca <br /> Survival: nan
# 4670  brca  0.454501  0.570091  ...  #000000      0.8   brca <br /> Survival: nan
# 4671  brca  0.426309  0.560061  ...  #000000      0.8  brca <br /> Survival: 6.80
# 4672  brca  0.469009  0.598039  ...  #000000      0.8   brca <br /> Survival: nan
# 4673  brca  0.502737  0.478357  ...  #000000      0.8   brca <br /> Survival: nan
# [4674 rows x 12 columns]

# Show the updated chart!
d3.show(filepath='c://temp//scatter_update.html', figsize=[1020, 768], label_radio=['t-SNE', 'PCA'])

# Initialize
d3 = D3Blocks(chart='Scatter', frame=True)
# Import example
df = d3.import_example('cancer')

d3.set_edge_properties(df['x'].values,
                        df['y'].values,
                        x1=df['PC1'].values,
                        y1=df['PC2'].values,
                        # size=df['survival_months'].fillna(1).values / 10,
                        size=10,
                        color=df.index.values,
                        tooltip=df['labels'].values + ' <br /> Survival: ' + df['survival_months'].astype(str).str[0:4].values,
                        c_gradient = '#FFFFFF',
                        stroke = None,
                        opacity=0.1,
                        scale=True,
                        )




# Show the chart
d3.show(filepath='c://temp//scatter_demo.html', figsize=[800, 600], label_radio=['tSNE', 'PCA'])



# %% SCATTER
from d3blocks import D3Blocks

# Initialize
d3 = D3Blocks(chart='Scatter', frame=False)
# Import example
df = d3.import_example('cancer')
# Edge properties
d3.set_edge_properties(df['x'].values, df['y'].values, x1=df['PC1'].values, y1=df['PC2'].values, label_radio=['tSNE','PCA'], size=df['survival_months'].fillna(1).values / 10, color=df.index.values, tooltip=df['labels'].values + ' <br /> Survival: ' + df['survival_months'].astype(str).str[0:4].values, scale=True)
# Show the chart
d3.show(filepath='c://temp//scatter_demo.html', figsize=[600, 400])


from d3blocks import D3Blocks
# # Initialize
d3 = D3Blocks(frame=False)
# # import example
df = d3.import_example('cancer')
df = df.loc[(df.index.values=='kich') | (df.index.values=='brca') | (df.index.values=='laml'), :]
size = df['survival_months'].fillna(1).values / 10
tooltip=df['labels'].values + ' <br /> Survival: ' + df['survival_months'].astype(str).str[0:4].values

# # No transition
# d3.scatter(df['x'].values, df['y'].values, size=df['survival_months'].values/10, tooltip=tooltip, color=df.index.values, filepath='c://temp//scatter.html')

# Two transitions
d3.scatter(df['x'].values,
           df['y'].values,
           x1=df['PC1'].values,
           y1=df['PC2'].values,
           size=size,
           color=df.index.values,
           tooltip=tooltip,
           filepath='c://temp//scatter_transitions1.html')

d3.scatter(df['x'].values,
           df['y'].values,
           x1=df['PC1'].values,
           y1=df['PC2'].values,
           label_radio=['tSNE','PCA'],
           size=size,
           color=df.index.values,
           tooltip=tooltip,
           scale=True,
           figsize=[600, 400],
           filepath='c://temp//scatter_transitions2.html')

d3.scatter(df['x'].values,
           df['y'].values,
           x1=df['PC1'].values,
           y1=df['PC2'].values,
           x2=df['PC2'].values,
           y2=df['PC1'].values,
           label_radio=['tSNE', 'PCA', 'Magic'],
           size=size,
           color=df.index.values,
           tooltip=tooltip,
           scale=True,
           filepath='c://temp//scatter_transitions2.html')

# Three transitions
d3.scatter(df['x'].values,
            df['y'].values,
            x1=df['PC1'].values,
            y1=df['PC2'].values,
            x2=df['PC2'].values,
            y2=df['PC1'].values,
            size=size,
            color=df.index.values,
            tooltip=tooltip,
            scale=True,
            filepath='c://temp//scatter_transitions10.html')


d3.scatter(df['x'].values,
           df['y'].values,
           x1=df['PC1'].values,
           y1=df['PC2'].values,
           x2=df['PC2'].values,
           y2=df['PC1'].values,
           label_radio=['tSNE', 'PCA', 'PCA_reverse'],
           size=size,
           color=df.index.values,
           tooltip=tooltip,
           scale=True,
           figsize=[1024, 768],
           filepath='c://temp//scatter_transitions3.html')


# %% VIOLIN - EXAMPLE
from d3blocks import D3Blocks

# Initialize
d3 = D3Blocks(chart='Violin', frame=True)
# Import example
df = d3.import_example('cancer')
# Edge properties
d3.set_edge_properties(x=df['labels'].values,
                        y=df['age'].values,
                        size=df['survival_months'].values/10,
                        x_order=['acc','kich', 'brca','lgg','blca','coad','ov'],
                        filepath='violine_demo.html')
# d3.edge_properties
d3.show(filepath='c://temp//violin1.html')

# or

# Create violin diagram
from d3blocks import D3Blocks
# Initialize
d3 = D3Blocks()
# Import example
df = d3.import_example('cancer')
# Create chord diagram
d3.violin(x=df['labels'].values, # class labels on the x axis
          y=df['age'].values,    # Age
          size=df['survival_months'].values/10, # Dotsize
          x_order=['acc','kich', 'brca','lgg','blca','coad','ov'], # Keep only these classes and plot in this order.
          figsize=[None, None],   # Figure size is automatically determined.
          filepath='violine_demo.html',
          reset_properties=True)

# %% Movingbubbles - Make manual dataset to test the working
import pandas as pd
from d3blocks import D3Blocks
d3 = D3Blocks()

df1 = pd.DataFrame(columns=['datetime', 'sample_id', 'state'])
df1['datetime'] = ['01-01-2000 00:00:00', '01-01-2000 00:00:05', '01-01-2000 00:00:10', '01-01-2000 00:00:15', '01-01-2000 00:00:20', '01-01-2000 00:00:25']
df1['sample_id'] = [1, 1, 1, 1, 1, 1]
df1['state'] = ['home', 'school', 'work', 'eating', 'coffee', 'sleeping']

df2 = pd.DataFrame(columns=['datetime', 'sample_id', 'state'])
df2['datetime'] = ['01-01-2000 00:00:00', '01-01-2000 00:00:10', '01-01-2000 00:00:15', '01-01-2000 00:00:20', '01-01-2000 00:00:25', '01-01-2000 00:00:30']
df2['sample_id'] = [2, 2, 2, 2, 2, 2]
df2['state'] = ['home', 'school', 'work', 'eating', 'coffee', 'sleeping']

df3 = pd.DataFrame(columns=['datetime', 'sample_id', 'state'])
df3['datetime'] = ['12-12-2000 00:00:00', '12-12-2000 00:00:15', '12-12-2000 00:00:20', '12-12-2000 00:00:25', '12-12-2000 00:00:30', '12-12-2000 00:00:35']
df3['sample_id'] = [3, 3, 3, 3, 3, 3]
df3['state'] = ['home', 'school', 'work', 'eating', 'coffee', 'sleeping']

# Concatenate the dataframes
df = pd.concat([df1, df2, df3], axis=0)

print(df)
#               datetime  sample_id     state
# 0  01-01-2000 00:00:00          1      home
# 1  01-01-2000 00:00:05          1    school
# 2  01-01-2000 00:00:10          1      work
# 3  01-01-2000 00:00:15          1    eating
# 4  01-01-2000 00:00:20          1    coffee
# 5  01-01-2000 00:00:25          1  sleeping
# 0  01-01-2000 00:00:00          2      home
# 1  01-01-2000 00:00:10          2    school
# 2  01-01-2000 00:00:15          2      work
# 3  01-01-2000 00:00:20          2    eating
# 4  01-01-2000 00:00:25          2    coffee
# 5  01-01-2000 00:00:30          2  sleeping
# 0  12-12-2000 00:00:00          3      home
# 1  12-12-2000 00:00:15          3    school
# 2  12-12-2000 00:00:20          3      work
# 3  12-12-2000 00:00:25          3    eating
# 4  12-12-2000 00:00:30          3    coffee
# 5  12-12-2000 00:00:35          3  sleeping

# standardize the time per sample id and make the starting-point the same
# df = d3.standardize(df, sample_id='sample_id', datetime='datetime')

# # Compute delta (this is automatically done if not seen in datafame available)
# df = d3.compute_time_delta(df, sample_id='sample_id', datetime='datetime', state='state')

# Notes that are shown between two time points.
time_notes = [{"start_minute": 1, "stop_minute": 5, "note": "In the first 5 minutes, nothing will happen and every entity is waiting in it's current state."}]
time_notes.append({"start_minute": 6, "stop_minute": 10, "note": "The first entity will move to school. The rest is still at home."})
time_notes.append({"start_minute": 11, "stop_minute": 15, "note": "The first entity will move to work and the second entity to school. There is still one at home."})
time_notes.append({"start_minute": 16, "stop_minute": 40, "note": "From this point, the entities will move behind each other towards threir final destination: sleeping."})

# Make the moving bubbles
df = d3.movingbubbles(df, datetime='datetime', state='state', sample_id='sample_id', speed={"slow": 1000, "medium": 200, "fast": 10}, time_notes=time_notes, filepath='movingbubbles.html', cmap='Set2_r', standardize='samplewise')

df = d3.movingbubbles(df, center='sleeping', datetime='datetime', state='state', sample_id='sample_id', speed={"slow": 1000, "medium": 200, "fast": 10}, time_notes=time_notes, filepath='movingbubbles.html', cmap='Set2_r', standardize='samplewise')


# %% Sankey
from d3blocks import D3Blocks
# Initialize
d3 = D3Blocks()
# Import example
df = d3.import_example('energy')
# Link settings
html = d3.sankey(df, filepath=None, notebook=False)

# Initialize
d3 = D3Blocks(chart='Sankey', frame=True)
# Import example
df = d3.import_example('energy')
# Node properties
d3.set_node_properties(df)
# d3.node_properties
d3.set_edge_properties(df, color='target', opacity='target')
# d3.edge_properties
# Show the chart
d3.show()

# Initialize
d3 = D3Blocks()
# Import example
df = d3.import_example('energy')
# Link settings
d3.sankey(df, link={"color": "source"}, node={'align': 'justify'}, filepath='c:\\temp\\sankey.html')
# labels = d3.node_properties

# %% TIMESERIES
from d3blocks import D3Blocks
# Initialize
d3 = D3Blocks(chart='Timeseries', frame=False)
# Import example
df = d3.import_example('climate')
# Node properties
d3.set_node_properties(df.columns)
# d3.node_properties
d3.node_properties.get('wind_speed')['color'] = '#000000'
# d3.node_properties
d3.set_edge_properties(df, datetime='date', dt_format='%Y-%m-%d %H:%M:%S')
# d3.edge_properties
# Show
d3.show(title='Timeseries with adjusted configurations.', showfig=True, filepath='c://temp/timeseries.html')

# or

from d3blocks import D3Blocks
# Initialize
d3 = D3Blocks(chart='Timeseries', frame=True)
# Import example
df = d3.import_example('climate')
# Show
d3.timeseries(df, datetime='date', dt_format='%Y-%m-%d %H:%M:%S', fontsize=10, figsize=[850, 500])


# %% Moving bubbles
from d3blocks import D3Blocks
# Initialize
d3 = D3Blocks(chart='movingbubbles', frame=False)
# Import example
df = d3.import_example('random_time', n=1000, c=100, date_start="1-1-2000 00:10:05", date_stop="1-1-2000 23:59:59")
# Node properties
d3.set_node_properties(df['state'])
# d3.node_properties
d3.node_properties.get('Sleeping')['color'] = '#000000'
# d3.node_properties
d3.set_edge_properties(df)
# d3.edge_properties
# Show
d3.show(title='Movingbubbles with adjusted configurations.', showfig=True)

# or

from d3blocks import D3Blocks
# Initialize
d3 = D3Blocks(frame=False)
# Import example
df = d3.import_example('random_time', n=1000, c=100, date_start="1-1-2000 00:10:05", date_stop="1-1-2000 23:59:59")
# Show
d3.movingbubbles(df)
d3.movingbubbles(df, reset_properties=False, cmap='tab20', datetime='datetime', state='state', sample_id='sample_id', speed={"slow": 1000, "medium": 200, "fast": 10}, filepath='c://temp/movingbubbles1.html')


# %% CHORD - EXAMPLE 2
from d3blocks import D3Blocks

# Initialize
d3 = D3Blocks(chart='chord', frame=False)
# Import example
df = d3.import_example('energy')
# Get the node properties by setting them to defaults
d3.set_node_properties(df, opacity=0.8, cmap='Set1')

# Node properties are stored in labels
# d3.node_properties

# Set one specific node to black color
d3.node_properties.get('Bio-conversion')['color']='#000000'

# Color nodes on characteristics
for key in d3.node_properties.keys():
    # GREEN
    if 'bio' in key.lower():
        d3.node_properties.get(key)['color']='#00FF00'
        d3.node_properties.get(key)['opacity']=0.9
    # ORANGE
    elif 'gas' in key.lower():
        d3.node_properties.get(key)['color']='#FFA500'
    # GREY
    elif 'oil' in key.lower():
        d3.node_properties.get(key)['color']='#808080'
        d3.node_properties.get(key)['opacity']=0.1
    # RED
    elif 'thermal' in key.lower() or 'heat' in key.lower():
        d3.node_properties.get(key)['color']='#FF0000'
        d3.node_properties.get(key)['opacity']=0.5
    # BLUE
    elif 'electr' in key.lower() or 'solar' in key.lower() or 'nuclear' in key.lower():
        d3.node_properties.get(key)['color']='#0000FF'
        d3.node_properties.get(key)['opacity']=0.2
    else:
        d3.node_properties.get(key)['color']='#000000'
        d3.node_properties.get(key)['opacity']=0.1

# Chord diagram
d3.set_edge_properties(df, color='source-target', opacity='target', cmap='Set1')
d3.show(showfig=True, filepath='c://temp//chord1.html')

d3.set_edge_properties(df, color='source', opacity='source', cmap='Set1')
d3.show(showfig=True, filepath='c://temp//chord2.html')

d3.set_edge_properties(df, color='source', opacity='target', cmap='Set1')
d3.show(showfig=True, filepath='c://temp//chord3.html')

d3.set_edge_properties(df, color='target', opacity='target', cmap='Set1')
d3.show(showfig=True, filepath='c://temp//chord4.html')

d3.set_edge_properties(df, color='#000000', opacity='target', cmap='Set1')
d3.show(showfig=True, filepath='c://temp//chord5.html')

d3.set_edge_properties(df, color='#000000', opacity=0.1, cmap='Set1')
d3.show(showfig=True, filepath='c://temp//chord6.html')

# d3.chord(df, filepath='c://temp//chord_demo1.html', color=df['color'].values, opacity=df['opacity'].values, showfig=True)
# d3.chord(df, filepath='c://temp//chord_demo1.html', color=df['color'].values, showfig=True)

# %% Violin plot
import numpy as np
from d3blocks import D3Blocks

# Initialize
d3 = D3Blocks()

# import example
df = d3.import_example('cancer')

tooltip=df['labels'].values + ' <br /> Survival: ' + df['survival_months'].astype(str).values

d3.violin(x=df['labels'].values, y=df['age'].values, tooltip=tooltip, bins=50, size=df['survival_months'].values/10, x_order=['acc','kich', 'brca','lgg','blca','coad','ov'], filepath='c://temp//violine_demo6.html', figsize=[900, None])

d3.violin(x=df['labels'].values, y=df['age'].values, filepath='c://temp//violine_demo1.html', figsize=(1600, 400))

d3.violin(x=df['labels'].values, y=df['age'].values, filepath='c://temp//violine_demo2.html', figsize=(1600, 400), cmap='RdYlBu')

d3.violin(x=df['labels'].values, y=df['age'].values, size=df['survival_months'].values/10, filepath='c://temp//violine_demo3.html', figsize=(1600, 400))

d3.violin(x=df['labels'].values, y=df['age'].values, bins=50, size=df['survival_months'].values/10, filepath='c://temp//violine_demo4.html', figsize=(1600, 400))

d3.violin(x=df['labels'].values, y=df['age'].values, tooltip=tooltip, bins=50, size=df['survival_months'].values/10, filepath='c://temp//violine_demo5.html', figsize=(1600, 400))

d3.violin(x=df['labels'].values, y=df['age'].values, tooltip=tooltip, bins=50, size=df['survival_months'].values/10, filepath='c://temp//violine_demo6.html', figsize=(1600, 400))

d3.violin(x=df['labels'].values, y=df['age'].values, opacity=0.5, stroke='#000000', tooltip=tooltip, bins=50, size=df['survival_months'].values/10, filepath='c://temp//violine_demo7.html', figsize=(1600, 400))

# only coordinates
d3.violin(x=df['labels'].values, y=df['age'].values, tooltip=tooltip, x_order=['acc','kich', 'brca','lgg','blca','coad','ov'], bins=50, opacity=0.5, stroke='#ffffff', cmap='inferno', size=df['survival_months'].values/10, filepath='c://temp//violine_demo.html')
# d3.violin(x=df['labels'].values, y=df['age'].values,  bins=50, opacity=0.5, stroke='#000000', cmap='inferno', s=df['survival_months'].values/10, filepath='c://temp//violine_demo.html')

d3.violin(x=df['labels'].values, y=df['age'].values, opacity=0.5, stroke='#000000', tooltip=tooltip, bins=50, size=df['survival_months'].values/10, filepath='c://temp//violine_demo7.html', figsize=[None, None])



# %% Add function move scatter
from d3blocks import D3Blocks

# Initialize
d3 = D3Blocks()

# import example
df = d3.import_example('cancer')

# df = df.loc[(df.index.values=='kich') | (df.index.values=='brca') | (df.index.values=='laml'), :]

size = df['survival_months'].fillna(1).values / 10
tooltip=df['labels'].values + ' <br /> Survival: ' + df['survival_months'].astype(str).str[0:4].values

# No transition
# d3.scatter(df['x'].values, df['y'].values, size=df['survival_months'].values/10, color=df.index.values, tooltip=tooltip, filepath='c://temp//scatter.html')

# Two transitions
# d3.scatter(df['x'].values, df['y'].values, x1=df['PC1'].values, y1=df['PC2'].values, size=size, color=df.index.values, tooltip=tooltip, filepath='c://temp//scatter_transitions2.html')
d3.scatter(df['x'].values, df['y'].values, x1=df['PC1'].values, y1=df['PC2'].values, label_radio=['tSNE','PCA'], size=size, color=df.index.values, tooltip=tooltip, filepath='c://temp//scatter_transitions2.html', scale=True, figsize=[600, 400])

# Three transitions
# d3.scatter(df['x'].values, df['y'].values, x1=df['PC1'].values, y1=df['PC2'].values, x2=df['PC2'].values, y2=df['PC1'].values, size=size, color=df.index.values, tooltip=tooltip, filepath='c://temp//scatter.html')
# d3.scatter(df['x'].values, df['y'].values, x1=df['PC1'].values, y1=df['PC2'].values, x2=df['PC2'].values, y2=df['PC1'].values, label_radio=['tSNE', 'PCA'], size=size, color=df.index.values, tooltip=tooltip, filepath='c://temp//scatter_transitions3.html')
d3.scatter(df['x'].values, df['y'].values, x1=df['PC1'].values, y1=df['PC2'].values, x2=df['PC2'].values, y2=df['PC1'].values, label_radio=['tSNE', 'PCA', 'PCA_reverse'], size=size, color=df.index.values, tooltip=tooltip, filepath='c://temp//scatter_transitions3.html', scale=True, figsize=[600, 400])


# %% SANKEY - EXAMPLE 1
from d3blocks import D3Blocks

# Initialize
d3 = D3Blocks()

# Import example
df = d3.import_example('energy')

# Link settings
d3.sankey(df, link={"color": "target"}, node={'align': 'justify'}, filepath='c:\\temp\\sankey.html')
# d3.sankey(df, link={"color": "source-target"}, node={'align': 'justify'}, filepath='c:\\temp\\sankey.html', figsize=[650, 500])
# labels = d3.node_properties


# %%
from d3blocks import D3Blocks

# Initialize
d3 = D3Blocks()
# import example
df = d3.import_example('cancer')
# Tooltip
tooltip=df['labels'].values + ' <br /> Survival: ' + df['survival_months'].astype(str).values
# Make the plot
d3.violin(x=df['labels'].values, # class labels on the x axis
          y=df['age'].values,    # Age
          tooltip=tooltip,       # Tooltip for hovering
          bins=50,               # Bins used for the histogram
          size=df['survival_months'].values/10, # Dotsize
          x_order=['acc','kich', 'brca','lgg','blca','coad','ov'], # Keep only these classes and plot in this order.
          figsize=[None, None],   # Figure size is automatically determined.
          filepath='violine_demo.html')



# %% CHORD - EXAMPLE 2
from d3blocks import D3Blocks

# Initialize
d3 = D3Blocks()
# Import example
df = d3.import_example('energy')
# Make plot
d3.chord(df, filepath='c://temp//chord_demo1.html', figsize=[900, 900], fontsize=10, cmap='Set1')

# %% IMGE SLIDER
import cv2

from d3blocks import D3Blocks
# Initialize
d3 = D3Blocks()
# Import example
img_before, img_after = d3.import_example('southern_nebula')

# Read the image
# img_before = cv2.imread(img_before, -1)
# img_after = cv2.imread(img_after, -1)

# Make comparison
d3.imageslider(img_before, img_after, showfig=True, filepath='c:/temp/imageslider.html', figsize=[400, 400], scale=True, colorscale=0)
# d3.imageslider(img_before, img_after, showfig=True, figsize=[None, None])


# %% CHORD - EXAMPLE 2
from d3blocks import D3Blocks

# Initialize
d3 = D3Blocks()

# df = d3.import_example('energy')
# df = d3.import_example('bigbang')
# df = d3.import_example('stormofswords')
# adjmat = d3.vec2adjmat(df['source'], df['target'], weight=df['weight'], symmetric=True)

# Chord diagram
df['opacity'] = 0.75
df['opacity'].iloc[0] = 0.1
d3.chord(df, filepath='c://temp//chord_demo.html', figsize=[900, 900], opacity=df['opacity'].values, fontsize=10)


# %% TIMESERIES
import yfinance as yf
df = yf.download(["TSLA", "TWTR", "META", "AMZN", "AAPL"], start="2019-01-01", end="2021-12-31")
df = df[["Adj Close"]].droplevel(0, axis=1).resample("M").last()
df = df.div(df.iloc[0])
df.head()

from d3blocks import D3Blocks
d3 = D3Blocks()
d3.timeseries(df, filepath='c://temp//timeseries.html', fontsize=10, figsize=[850, 500], dt_format='%Y-%m-%d %H:%M:%S', datetime=None)


# %% TIMESERIES
from d3blocks import D3Blocks

# Initialize
d3 = D3Blocks()
df = d3.import_example('climate')
# d3.timeseries(df, datetime='date', filepath='c://temp//timeseries.html', fontsize=10, figsize=[850, 500])
d3.timeseries(df, datetime='date', filepath='c://temp//timeseries.html', fontsize=10, dt_format='%Y-%m-%d %H:%M:%S')


# %% HEATMAP - EXAMPLE 1

from d3blocks import D3Blocks

# Initialize
d3 = D3Blocks()
# Import example
# df = d3.import_example('bigbang')
# df = d3.import_example('stormofswords')
df = d3.import_example('energy')
df = d3.vec2adjmat(df['source'], df['target'], weight=df['weight'], symmetric=True)
# from sklearn.preprocessing import StandardScaler
# X_scaled = StandardScaler(with_mean=True, with_std=False).fit_transform(adjmat)
# X_scaled = pd.DataFrame(data=X_scaled, columns=adjmat.columns, index=adjmat.index.values)

d3.heatmap(df, stroke='red', vmax=10, figsize=(700,700), title='heatmap')


# %%
from d3blocks import D3Blocks
#
# Initialize
d3 = D3Blocks()
#
# Load example data
df = d3.import_example('energy')
#
# Plot
# d3.d3graph(df, showfig=True)
d3.d3graph(df, filepath='c:/temp/d3graph.html', figsize=[700, 700], scaler='minmax', showfig=False)

# Set colors
d3.D3graph.set_node_properties(color='cluster')
d3.D3graph.show()


# %% Particles
from d3blocks import D3Blocks

# Initialize
d3 = D3Blocks()

# Make particles
# d3.particles('D3Blocks', filepath='c://temp//D3Blocks.html', collision=0.05, spacing=7, figsize=[750, 150], fontsize=130, cmap='Turbo', background='#ffffff')
# d3.particles('D3Blocks', filepath='c://temp//D3Blocks.html', background='#ffffff', fontsize=180, figsize=[900, 200], spacing=8)
d3.particles('D3Blocks', filepath='c://temp//D3Blocks.html', color_background='#ffffff')


# %% SANKEY - EXAMPLE 1
from d3blocks import D3Blocks

# Initialize
d3 = D3Blocks(frame=True)

# Import example
df = d3.import_example('energy')

# Link settings
d3.sankey(df, link={"color": "source-target"}, filepath='c:\\temp\\sankey.html')
labels = d3.node_properties
# Link settings
# d3.d3graph(df, filepath='c:\\temp\\network.html', showfig=False)
# d3.D3graph.set_node_properties(color='cluster')
# d3.D3graph.show()


# Network
d3.d3graph(df, showfig=False)
d3.D3graph.set_node_properties()

# # Show the network graph
d3.D3graph.show(filepath='c:\\temp\\d3graph.html')

# %% Issue color match SCATTER
from d3blocks import D3Blocks
import numpy as np

# Initialize
d3 = D3Blocks()

# import example
df = d3.import_example('cancer')

# df = df.loc[(df.index.values=='kich') | (df.index.values=='kirp'), :]
# color on labels
d3.scatter(df['x'].values, df['y'].values, color=df.index.values, tooltip=df.index.values, filepath='c://temp//scatter_demo.html', cmap='tab20')


# %% SCATTER EXAMPLE
from d3blocks import D3Blocks
import numpy as np

# Initialize
d3 = D3Blocks()

# import example
df = d3.import_example('cancer')

# only coordinates
d3.scatter(df['x'].values, df['y'].values, filepath='c://temp//scatter_demo.html')
# color on labels
d3.scatter(df['x'].values, df['y'].values, color=df.index.values, filepath='c://temp//scatter_demo.html', cmap='tab20')
# color on labels + tooltip
d3.scatter(df['x'].values, df['y'].values, color=df.index.values, tooltip=df.index.values, filepath='c://temp//scatter_demo.html', cmap='tab20')
# size constant
d3.scatter(df['x'].values, df['y'].values, color=df.index.values, size=5, tooltip=df.index.values, filepath='c://temp//scatter_demo.html')
# size constant + opacity
d3.scatter(df['x'].values, df['y'].values, size=5, opacity=0.2, tooltip=df.index.values, filepath='c://temp//scatter_demo.html', cmap='tab20')
# size constant + opacity
d3.scatter(df['x'].values, df['y'].values, color=df.index.values, size=5, opacity=0.2, tooltip=df.index.values, filepath='c://temp//scatter_demo.html', cmap='tab20')
# color on labels + cmap
d3.scatter(df['x'].values, df['y'].values, color=df.index.values, tooltip=df.index.values, filepath='c://temp//scatter_demo.html', cmap='tab20c')
# colors + c_gradient
d3.scatter(df['x'].values, df['y'].values, color=df.index.values, c_gradient='#ffffff', tooltip=df.index.values, filepath='c://temp//scatter_demo.html')
# colors + stroke=black
d3.scatter(df['x'].values, df['y'].values, color=df.index.values, stroke='#000000', tooltip=df.index.values, filepath='c://temp//scatter_demo.html')
# colors + stroke with same color
d3.scatter(df['x'].values, df['y'].values, color=df.index.values, stroke=None, c_gradient='#ffffff', tooltip=df.index.values, filepath='c://temp//scatter_demo.html')

# Set the size
s = df['survival_months'].fillna(1).values / 10

tooltip=df['labels'].values + ' <br /> Survival: ' + df['survival_months'].astype(str).str[0:4].values

# Scatter with dynamic size
d3.scatter(df['x'].values, df['y'].values, size=size, tooltip=tooltip, filepath='c://temp//scatter_demo.html', cmap='tab20')
# size + colors
d3.scatter(df['x'].values, df['y'].values, size=size, color=df.index.values, tooltip=tooltip, filepath='c://temp//scatter_demo.html', cmap='tab20')
# size + colors + stroke + opacity
d3.scatter(df['x'].values, df['y'].values, size=size, color=df.index.values, stroke='#000000', opacity=0.4, tooltip=df.index.values, filepath='c://temp//scatter_demo.html', cmap='tab20')
# size + colors + c_gradient
d3.scatter(df['x'].values, df['y'].values, size=size, color=df.index.values, c_gradient='#ffffff', tooltip=tooltip, filepath='c://temp//scatter_demo.html', cmap='tab20')

# size + colors + stroke + opacity
d3.scatter(df['x'].values, df['y'].values, size=size, color=df.index.values, stroke=None, opacity=0.4, tooltip=tooltip, filepath='c://temp//scatter_demo.html', cmap='tab20')



# %%
import pandas as pd

# Create example dataset
df = pd.DataFrame()
df['source']= ['A','A','A', 'A', 'B', 'C', 'D']
df['target']= ['F','F','F', 'C', 'E', 'D', 'E']
df['weight']= [2, 1, 1, 1, 1, 1, 1]

from d3blocks import D3Blocks

# Initialize
d3 = D3Blocks()

# Create the chart
d3.sankey(df, link={"color": "source-target"})


# %% Moving bubbles
from d3blocks import D3Blocks

d3 = D3Blocks()
# Import example

df = d3.import_example('random_time', n=10000, c=500, date_start="01-01-2000 00:10:05", date_stop="01-02-2000 23:59:59")

# df = d3.standardize(df, sample_id='sample_id', datetime='datetime')

# Make the moving bubbles
d3.movingbubbles(df,
                 datetime='datetime',
                 sample_id='sample_id',
                 state='state',
                 center=None,
                 damper=1,
                 standardize=None,
                 timedelta='day',
                 speed={"slow": 500, "medium": 200, "fast": 100},
                 figsize=(780, 800),
                 note=None,
                 title='d3blocks_movingbubbles',
                 filepath='movingbubbles.html',
                 fontsize=14,
                 showfig=True,
                 cmap='Set1',
                 overwrite=True)


#                 datetime sample_id     state
# 0    01-01-2000 00:10:36        61    Eating
# 1    01-01-2000 00:10:51        83      Sick
# 2    01-01-2000 00:11:30        61  Sleeping
# 3    01-01-2000 00:11:37        66  Sleeping
# 4    01-01-2000 00:11:57        94  Sleeping
#                  ...       ...       ...
# 9995 2000-01-02 23:57:12         6      Home
# 9996 2000-01-02 23:57:23        48      Sick
# 9997 2000-01-02 23:57:54        61      Home
# 9998 2000-01-02 23:58:22         4  Sleeping
# 9999 2000-01-02 23:59:34        88  Sleeping

# [10000 rows x 3 columns]

# %% SCATTER EXAMPLE
from d3blocks import D3Blocks

# Initialize
d3 = D3Blocks()

# import example
df = d3.import_example('iris')

# Scatter
d3.scatter(df['x'].values, df['y'].values, filepath='scatter_demo1.html')
# Scatter
d3.scatter(df['x'].values, df['y'].values, color=df.index.values.astype(str), size=5, filepath='scatter_demo2.html')
# Scatter
d3.scatter(df['x'].values, df['y'].values, color=df.index.values.astype(str), size=5, filepath='scatter_demo3.html', xlim=[1, 12], ylim=[])


# %% CHORD - EXAMPLE 1
from d3blocks import D3Blocks
import numpy as np
import pandas as pd

# Initialize
d3 = D3Blocks(frame=False, chart='chord')
# Import example
# df = d3.import_example('bigbang')
# df = d3.import_example('stormofswords')
# df = d3.import_example('energy')
# df = d3.vec2adjmat(df['source'], df['target'], weight=df['weight'])
# df = d3.adjmat2vec(df)

data = np.array([
    [0, 4, 3, 2, 5, 2], # "Black Widow"
    [4, 0, 3, 2, 4, 3], # Captain Americ
    [3, 3, 0, 2, 3, 3], # Hawkeye
    [2, 2, 2, 0, 3, 3], #The Hulk
    [5, 4, 3, 3, 0, 2], #Iron Man
    [2, 3, 3, 3, 2, 0], #Thor
    ])

df = pd.DataFrame(data=data, columns=["Black Widow", "Captain America", "Hawkeye", "the Hulk", "Iron Man", "Thor"], index=["Black Widow", "Captain America", "Hawkeye", "the Hulk", "Iron Man", "Thor"])
df = d3.adjmat2vec(df)

# Retrieve default label properties
d3.set_node_properties(df, cmap='Set2')

# Make some changes
d3.node_properties["Black Widow"]['color'] = "#301E1E"
d3.node_properties["Captain America"]['color'] = "#083E77"
d3.node_properties["Hawkeye"]['color'] = "#342350"
d3.node_properties["the Hulk"]['color'] = "#567235"
d3.node_properties["Iron Man"]['color'] = "#8B161C"
d3.node_properties["Thor"]['color'] = "#DF7C00"

# Chord diagram
d3.chord(df, filepath='chord_demo.html')


# %% IMGE SLIDER

from d3blocks import D3Blocks
# Initialize
d3 = D3Blocks()
# Import example
img_before, img_after = d3.import_example('unsplash')
# Make comparison
d3.imageslider(img_before, img_after, showfig=True, filepath='c:/temp/imageslider_unsplash.html', figsize=[800, None],)


# %% NETWORK - EXAMPLE 1

from d3blocks import D3Blocks

# Initialize
d3 = D3Blocks()
# Import example
# df = d3.import_example('bigbang')
# df = d3.import_example('stormofswords')
df = d3.import_example('energy')
# df = d3.vec2adjmat(df['source'], df['target'], weight=df['weight'])
# df = d3.adjmat2vec(df)

# Network diagram
d3.d3graph(df, showfig=False)
d3.D3graph.set_node_properties(color='cluster')
d3.D3graph.show()

# Make adjustments to the node: Thermal_generation
d3.D3graph.node_properties['Thermal_generation']['size']=20
d3.D3graph.node_properties['Thermal_generation']['edge_color']='#000fff' # Blue node edge
d3.D3graph.node_properties['Thermal_generation']['edge_size']=3 # Node-edge Size

# Make adjustments to the edge: 'Solar', 'Solar_Thermal'
d3.D3graph.edge_properties['Solar', 'Solar_Thermal']['color']='#000fff'
d3.D3graph.edge_properties['Solar', 'Solar_Thermal']['weight_scaled']=10

# Show the network graph
d3.D3graph.show()


# %% SANKEY - EXAMPLE 2

from d3blocks import D3Blocks

# Initialize
d3 = D3Blocks()

df = d3.import_example('stormofswords')

# Link settings
d3.sankey(df, filepath='sankey_ex1.html', figsize=(1000, 800), link={"color": "source", 'stroke_opacity': 0.2})
d3.sankey(df, filepath='sankey_ex2.html', figsize=(1800, 900), node={"width": 10}, margin={"top": 25, "left": 25}, link={"color": "source", 'stroke_opacity': 0.2})
d3.sankey(df, filepath='sankey_ex3.html', figsize=(1800, 900), node={"align": "left", "padding": 50, "width": 15}, margin={"top": 25, "left": 25}, link={"color": "source", 'stroke_opacity': 0.25})



# %% Timeseries - Example 2 - Set colors manually
# import pandas as pd
# from d3blocks import D3Blocks
# d3 = D3Blocks(cmap='Set1')

# # Import example dataset
# df = d3.import_example('timeseries', n=1000)

# # Collect label properties
# colors = d3.node_properties(df.columns.values)
# colors['A']['color'] = '#000000'
# colors['C']['color'] = '#000000'
# colors['E']['color'] = '#000000'
# # Set the label properties
# d3.node_properties(colors)
# # Check
# print(d3.node_properties)

# # Make timeseries graph where the label properties will be used
# d3.timeseries(df, datetime='datetime', filepath='timeseries.html', fontsize=10)


# %%
# from d3blocks import d3blocks
# d3 = d3blocks()
# X = d3.import_example('movingbubbles')
# d3.movingbubbles(X, filepath='c://temp/movingbubbles_original.html', center='Traveling')

# %% Movingbubbles - Make manual dataset to test the working

# This is an example to demonstrate standardize='samplewise'.
# 

import pandas as pd
from d3blocks import D3Blocks
d3 = D3Blocks()

df1 = pd.DataFrame(columns=['datetime', 'sample_id', 'state'])
df1['datetime'] = ['01-01-2000 00:00:00',
                   '01-01-2000 00:05:00',
                   '01-01-2000 00:10:00',
                   '01-01-2000 00:15:00',
                   '01-01-2000 00:20:00',
                   '01-01-2000 00:25:00']
df1['sample_id'] = [1, 1, 1, 1, 1, 1]
df1['state'] = ['home', 'school', 'work', 'eating', 'coffee', 'sleeping']

df2 = pd.DataFrame(columns=['datetime', 'sample_id', 'state'])
df2['datetime'] = ['01-01-2000 00:00:00',
                   '01-01-2000 00:10:00',
                   '01-01-2000 00:15:00',
                   '01-01-2000 00:20:00',
                   '01-01-2000 00:25:00',
                   '01-01-2000 00:30:00']
df2['sample_id'] = [2, 2, 2, 2, 2, 2]
df2['state'] = ['home', 'school', 'work', 'eating', 'coffee', 'sleeping']

df3 = pd.DataFrame(columns=['datetime', 'sample_id', 'state'])
df3['datetime'] = ['12-12-2000 00:00:00',
                   '12-12-2000 00:15:00',
                   '12-12-2000 00:20:00',
                   '12-12-2000 00:25:00',
                   '12-12-2000 00:30:00',
                   '12-12-2000 00:35:00']
df3['sample_id'] = [3, 3, 3, 3, 3, 3]
df3['state'] = ['home', 'school', 'work', 'eating', 'coffee', 'sleeping']

# Concatenate the dataframes
df = pd.concat([df1, df2, df3], axis=0)

print(df)
#               datetime  sample_id     state
# 0  01-01-2000 00:00:00          1      home
# 1  01-01-2000 00:05:00          1    school
# 2  01-01-2000 00:10:00          1      work
# 3  01-01-2000 00:15:00          1    eating
# 4  01-01-2000 00:20:00          1    coffee
# 5  01-01-2000 00:25:00          1  sleeping
# 0  01-01-2000 00:00:00          2      home
# 1  01-01-2000 00:10:00          2    school
# 2  01-01-2000 00:15:00          2      work
# 3  01-01-2000 00:20:00          2    eating
# 4  01-01-2000 00:25:00          2    coffee
# 5  01-01-2000 00:30:00          2  sleeping
# 0  12-12-2000 00:00:00          3      home
# 1  12-12-2000 00:15:00          3    school
# 2  12-12-2000 00:20:00          3      work
# 3  12-12-2000 00:25:00          3    eating
# 4  12-12-2000 00:30:00          3    coffee
# 5  12-12-2000 00:35:00          3  sleeping

# standardize the time per sample id and make the starting-point the same
# df = d3.standardize(df, sample_id='sample_id', datetime='datetime')

# # Compute delta (this is automatically done if not seen in datafame available)
# df = d3.compute_time_delta(df, sample_id='sample_id', datetime='datetime', state='state')

# Notes that are shown between two time points.
time_notes = [{"start_minute": 1, "stop_minute": 5, "note": "In the first 5 minutes, nothing will happen and every entity is waiting in it's current state."}]
time_notes.append({"start_minute": 6, "stop_minute": 10, "note": "The first entity will move to school. The rest is still at home."})
time_notes.append({"start_minute": 11, "stop_minute": 15, "note": "The first entity will move to work and the second entity to school. There is still one at home."})
time_notes.append({"start_minute": 16, "stop_minute": 40, "note": "From this point, the entities will move behind each other towards threir final destination: sleeping."})


# df['size']=4
# df['size'][df['sample_id']==1]=10
# df['size'][df['sample_id']==3]=40
size = {1: 10, 2: 5, 3: 20}
color = {1: '#000000', 2: '#000FFF', 3: '#FFF000'}

# Make the moving bubbles
d3.movingbubbles(df, 
                 datetime='datetime',
                 state='state',
                 sample_id='sample_id',
                 size=size,
                 color=color,
                 color_method='node',
                 timedelta='minutes',
                 speed={"slow": 1000, "medium": 200, "fast": 10},
                 time_notes=time_notes,
                 filepath=r'c:\temp\movingbubbles.html',
                 cmap='Set2',
                 standardize='samplewise',
                 )

df1=d3.edge_properties

# %% Movingbubbles - Create random dataset
from d3blocks import D3Blocks
d3 = D3Blocks()

df = d3.import_example('random_time', n=10000, c=100, date_start="1-1-2000 00:10:05", date_stop="1-2-2000 23:59:59")

# # Compute delta (this is automatically done if not available)
# df = d3.compute_time_delta(df, sample_id='sample_id', datetime='datetime', state='state')
# d3.node_properties

# Make the moving bubbles
d3.movingbubbles(df, center='Travel', datetime='datetime', state='state', sample_id='sample_id', speed={"slow": 1000, "medium": 200, "fast": 10}, cmap='Set1', filepath='movingbubbles.html')


# %% Moving bubbles
d3 = D3Blocks()
# Import example
df = d3.import_example('random_time', n=10000, c=300, date_start="1-1-2000 00:10:05", date_stop="1-1-2000 23:59:59")
# standardize the time per sample id.
# df = d3.standardize(df, sample_id='sample_id', datetime='datetime')
# Make the moving bubbles
d3.movingbubbles(df, datetime='datetime', state='state', sample_id='sample_id', center='Travel', speed={"slow": 1000, "medium": 200, "fast": 10}, filepath='c://temp/movingbubbles.html', cmap='Set1')
# d3.movingbubbles(df, datetime='datetime_norm', state='state', sample_id='sample_id', center='Travel', speed={"slow": 1000, "medium": 200, "fast": 10}, filepath='c://temp/movingbubbles.html')


# %% Movingbubbles - Create random dataset
from d3blocks import D3Blocks
d3 = D3Blocks()

df = d3.import_example('random_time', n=10000, c=100, date_start="1-1-2000 00:10:05", date_stop="1-2-2000 23:59:59")

# # Compute delta (this is automatically done if not available)
# df = d3.compute_time_delta(df, sample_id='sample_id', datetime='datetime', state='state')
# d3.node_properties

# Make the moving bubbles
d3.movingbubbles(df, center='Travel', datetime='datetime', state='state', sample_id='sample_id', speed={"slow": 1000, "medium": 200, "fast": 10}, filepath='movingbubbles.html', cmap='Set1')


# %% Moving bubbles
from d3blocks import D3Blocks

d3 = D3Blocks()
# Import example
# df = d3.import_example('movingbubbles')
df = d3.import_example('random_time', n=10000, c=300, date_start="1-1-2000 00:10:05", date_stop="1-1-2000 23:59:59")
# standardize the time per sample id.
# df = d3.standardize(df, sample_id='sample_id', datetime='datetime')

# Make the moving bubbles
d3.movingbubbles(df, speed={"slow": 1000, "medium": 200, "fast": 10}, filepath='c://temp/movingbubbles.html')

states = "{'index': '0', 'short': 'Sleeping', 'desc': 'Sleeping'}, {'index': '1', 'short': 'Personal Care', 'desc': 'Personal Care'}, {'index': '2', 'short': 'Eating & Drinking', 'desc': 'Eating and Drinking'}, {'index': '3', 'short': 'Education', 'desc': 'Education'}, {'index': '4', 'short': 'Work', 'desc': 'Work and Work-Related Activities'}, {'index': '5', 'short': 'Housework', 'desc': 'Household Activities'}, {'index': '6', 'short': 'Household Care', 'desc': 'Caring for and Helping Household Members'}, {'index': '7', 'short': 'Non-Household Care', 'desc': 'Caring for and Helping Non-Household Members'}, {'index': '8', 'short': 'Shopping', 'desc': 'Consumer Purchases'}, {'index': '9', 'short': 'Pro. Care Services', 'desc': 'Professional and Personal Care Services'}, {'index': '10', 'short': 'Leisure', 'desc': 'Socializing, Relaxing, and Leisure'}, {'index': '11', 'short': 'Sports', 'desc': 'Sports, Exercise, and Recreation'}, {'index': '12', 'short': 'Religion', 'desc': 'Religious and Spiritual Activities'}, {'index': '13', 'short': 'Volunteering', 'desc': 'Volunteer Activities'}, {'index': '14', 'short': 'Phone Calls', 'desc': 'Telephone Calls'}, {'index': '15', 'short': 'Misc.', 'desc': 'Other'}, {'index': '16', 'short': 'Traveling', 'desc': 'Traveling'}"

# %%
