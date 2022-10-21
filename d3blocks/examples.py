# %%
# import d3blocks
# print(dir(d3blocks))
# print(d3blocks.__version__)
# Initialize

from d3blocks import D3Blocks

# Initialize
d3 = D3Blocks()

# Make particles
# d3.particles('D3Blocks', filepath='c://temp//D3Blocks.html', collision=0.05, spacing=7, figsize=[750, 150], fontsize=130, cmap='Turbo', background='#ffffff')
# d3.particles('D3Blocks', filepath='c://temp//D3Blocks.html', background='#ffffff', fontsize=180, figsize=[900, 200], spacing=8)
d3.particles('D3Blocks', filepath='c://temp//D3Blocks.html', color_background='#ffffff')


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
           figsize=[600, 400],
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
d3.show(title='Timeseries with adjusted configurations.', showfig=True)

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
# adjmat = d3.vec2adjmat(df['source'], df['target'], weight=df['weight'], symmetric=True)
# df = d3.adjmat2vec(df)
# from sklearn.preprocessing import StandardScaler
# X_scaled = StandardScaler(with_mean=True, with_std=False).fit_transform(adjmat)
# X_scaled = pd.DataFrame(data=X_scaled, columns=adjmat.columns, index=adjmat.index.values)

d3.heatmap(df, showfig=True, stroke='red', vmax=10, figsize=(700,700), title='d3heatmap')


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
                 reset_time='day',
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
