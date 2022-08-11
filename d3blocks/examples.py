# %%
# import d3blocks
# print(dir(d3blocks))
# print(d3blocks.__version__)

# %% Moving bubbles
from d3blocks import D3Blocks

d3 = D3Blocks(cmap='Set1', dt_format='%Y-%m-%d %H:%M:%S')
# Import example
# df = d3.import_example(graph='movingbubbles')
# Normalize the time per sample id.
# df = d3.standardize(df, sample_id='sample_id', datetime='datetime')

df = d3.import_example(graph='random_time', n=10000, c=1000, date_start="2000-01-01 00:10:05", date_stop="2000-01-02 23:59:59")
# df = d3.standardize(df, sample_id='sample_id', datetime='datetime')

# Make the moving bubbles
d3.movingbubbles(df, datetime='datetime', center='Travel', speed={"slow": 1000, "medium": 200, "fast": 1}, filepath='c://temp/movingbubbles.html')

# %% SCATTER EXAMPLE
from d3blocks import D3Blocks

# Initialize
d3 = D3Blocks()

# import example
df = d3.import_example('iris')

# Scatter
d3.scatter(df, filepath='scatter_demo.html')

# Scatter
d3.scatter(df, filepath='scatter_demo_1.html', xlim=[1, 12], ylim=[])


# %% CHORD - EXAMPLE 2
from d3blocks import D3Blocks

# Initialize
d3 = D3Blocks()

df = d3.import_example('energy')
# df = d3.import_example('bigbang')
# df = d3.import_example('stormofswords')
# adjmat = d3.vec2adjmat(df['source'], df['target'], weight=df['weight'], symmetric=True)

# Chord diagram
d3.chord(df, filepath='chord_demo.html', figsize=[900, 900])

# %% CHORD - EXAMPLE 1
from d3blocks import D3Blocks
import numpy as np
import pandas as pd

# Initialize
d3 = D3Blocks()
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
labels = d3.get_label_properties(df['source'].unique(), cmap='Set2')

# Make some changes
labels["Black Widow"]['color'] = "#301E1E"
labels["Captain America"]['color'] = "#083E77"
labels["Hawkeye"]['color'] = "#342350"
labels["the Hulk"]['color'] = "#567235"
labels["Iron Man"]['color'] = "#8B161C"
labels["Thor"]['color'] = "#DF7C00"

d3.set_label_properties(labels)

# Chord diagram
d3.chord(df, filepath='chord_demo.html')


# %% IMGE SLIDER

from d3blocks import D3Blocks
# Initialize
d3 = D3Blocks()
# Import example
img_before, img_after = d3.import_example('southern_nebula')
# Make comparison
d3.imageslider(img_before, img_after, showfig=True)


# %% HEATMAP - EXAMPLE 1

from d3blocks import D3Blocks

# Initialize
d3 = D3Blocks()
# Import example
# df = d3.import_example('bigbang')
# df = d3.import_example('stormofswords')
df = d3.import_example('energy')
adjmat = d3.vec2adjmat(df['source'], df['target'], weight=df['weight'], symmetric=True)
# df = d3.adjmat2vec(df)
# from sklearn.preprocessing import StandardScaler
# X_scaled = StandardScaler(with_mean=True, with_std=False).fit_transform(adjmat)
# X_scaled = pd.DataFrame(data=X_scaled, columns=adjmat.columns, index=adjmat.index.values)

d3.heatmap(adjmat, showfig=True, stroke='red', vmax=10, figsize=(700,700))


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
d3.network(df, showfig=False)
d3.Network.set_node_properties(color='cluster')

# Make adjustments to the node: Thermal_generation
d3.Network.node_properties['Thermal_generation']['size']=20
d3.Network.node_properties['Thermal_generation']['edge_color']='#000fff' # Blue node edge
d3.Network.node_properties['Thermal_generation']['edge_size']=3 # Node-edge Size

# Make adjustments to the edge: 'Solar', 'Solar_Thermal'
d3.Network.edge_properties['Solar', 'Solar_Thermal']['color']='#000fff'
d3.Network.edge_properties['Solar', 'Solar_Thermal']['weight_scaled']=10

# Show the network graph
d3.Network.show()



# %% SANKEY - EXAMPLE 1

from d3blocks import D3Blocks

# Initialize
d3 = D3Blocks()

# Import example
df = d3.import_example('energy')

# Link settings
d3.sankey(df, link={"color": "source-target"})


# %% SANKEY - EXAMPLE 2

from d3blocks import D3Blocks

# Initialize
d3 = D3Blocks()

df = d3.import_example('stormofswords')

# Link settings
d3.sankey(df, filepath='sankey_ex1.html', figsize=(1000, 800), link={"color": "source", 'stroke_opacity': 0.2})
d3.sankey(df, filepath='sankey_ex2.html', figsize=(1800, 900), node={"width": 10}, margin={"top": 25, "left": 25}, link={"color": "source", 'stroke_opacity': 0.2})
d3.sankey(df, filepath='sankey_ex3.html', figsize=(1800, 900), node={"align": "left", "padding": 50, "width": 15}, margin={"top": 25, "left": 25}, link={"color": "source", 'stroke_opacity': 0.25})

# %% TIMESERIES
import yfinance as yf
df = yf.download(["TSLA", "TWTR", "FB", "AMZN", "AAPL"], start="2019-01-01", end="2021-12-31")
d = df[["Adj Close"]].droplevel(0, axis=1).resample("M").last()
df = df.div(df.iloc[0])
df.head()

from d3blocks import D3Blocks
d3 = D3Blocks(whitelist='close')
d3.timeseries(df, filepath='timeseries.html', fontsize=10)


# %% Timeseries - Example 1
import pandas as pd
from d3blocks import D3Blocks
d3 = D3Blocks(cmap='Set1')

# Import example dataset
df = d3.import_example('timeseries', n=1000)
df.iloc[:, 0] = df.iloc[:, 0] * 0.001
# Make the timeseries graph
d3.timeseries(df, datetime='datetime', filepath='timeseries.html', fontsize=10)


# %% Timeseries - Example 2 - Set colors manually
import pandas as pd
from d3blocks import D3Blocks
d3 = D3Blocks(cmap='Set1')

# Import example dataset
df = d3.import_example('timeseries', n=1000)

# Collect label properties
colors = d3.get_label_properties(df.columns.values)
colors['A']['color'] = '#000000'
colors['C']['color'] = '#000000'
colors['E']['color'] = '#000000'
# Set the label properties
d3.set_label_properties(colors)
# Check
print(d3.labels)

# Make timeseries graph where the label properties will be used
d3.timeseries(df, datetime='datetime', filepath='timeseries.html', fontsize=10)


# %%
# from d3blocks import d3blocks
# d3 = d3blocks()
# X = d3.import_example(data='movingbubbles')
# d3.movingbubbles(X, filepath='c://temp/movingbubbles_original.html', center='Traveling')

# %% Movingbubbles - Make manual dataset to test the working
import pandas as pd
from d3blocks import D3Blocks
d3 = D3Blocks(cmap='Set2_r')

df1 = pd.DataFrame(columns=['datetime', 'sample_id', 'state'])
df1['datetime'] = ['2000-01-01 00:00:00', '2000-01-01 00:00:05', '2000-01-01 00:00:10', '2000-01-01 00:00:15', '2000-01-01 00:00:20', '2000-01-01 00:00:25']
df1['sample_id'] = [1, 1, 1, 1, 1, 1]
df1['state'] = ['home', 'school', 'work', 'eating', 'coffee', 'sleeping']

df2 = pd.DataFrame(columns=['datetime', 'sample_id', 'state'])
df2['datetime'] = ['2000-01-01 00:00:00', '2000-01-01 00:00:10', '2000-01-01 00:00:15', '2000-01-01 00:00:20', '2000-01-01 00:00:25', '2000-01-01 00:00:30']
df2['sample_id'] = [2, 2, 2, 2, 2, 2]
df2['state'] = ['home', 'school', 'work', 'eating', 'coffee', 'sleeping']

df3 = pd.DataFrame(columns=['datetime', 'sample_id', 'state'])
df3['datetime'] = ['2000-12-12 00:00:00', '2000-12-12 00:00:15', '2000-12-12 00:00:20', '2000-12-12 00:00:25', '2000-12-12 00:00:30', '2000-12-12 00:00:35']
df3['sample_id'] = [3, 3, 3, 3, 3, 3]
df3['state'] = ['home', 'school', 'work', 'eating', 'coffee', 'sleeping']

df = pd.concat([df1, df2, df3], axis=0)

# Normalize the time per sample id and make the starting-point the same
df = d3.standardize(df, sample_id='sample_id', datetime='datetime')
# # Compute delta (this is automatically done if not available)
df = d3.compute_time_delta(df, sample_id='sample_id', datetime='datetime', state='state')
# Make the moving bubbles
df = d3.movingbubbles(df, datetime='datetime', state='state', sample_id='sample_id', speed={"slow": 1000, "medium": 200, "fast": 10}, filepath='movingbubbles.html')


# %% Movingbubbles - Create random dataset
from d3blocks import D3Blocks
d3 = D3Blocks(cmap='Set1')

df = d3.import_example(graph='random_time', n=10000, c=100, date_start="1-1-2000 00:10:05", date_stop="1-2-2000 23:59:59")

# # Compute delta (this is automatically done if not available)
# df = d3.compute_time_delta(df, sample_id='sample_id', datetime='datetime', state='state')
# d3.labels

# Make the moving bubbles
d3.movingbubbles(df, center='Travel', datetime='datetime', state='state', sample_id='sample_id', speed={"slow": 1000, "medium": 200, "fast": 10}, filepath='movingbubbles.html')


# %% Moving bubbles
d3 = D3Blocks(cmap='Set1')
# Import example
df = d3.import_example(graph='random_time', n=10000, c=100, date_start="1-1-2000 00:10:05", date_stop="1-1-2000 23:59:59")
# Normalize the time per sample id.
# df = d3.standardize(df, sample_id='sample_id', datetime='datetime')
# Make the moving bubbles
d3.movingbubbles(df, datetime='datetime', state='state', sample_id='sample_id', center='Travel', speed={"slow": 1000, "medium": 200, "fast": 10}, filepath='c://temp/movingbubbles.html')
# d3.movingbubbles(df, datetime='datetime_norm', state='state', sample_id='sample_id', center='Travel', speed={"slow": 1000, "medium": 200, "fast": 10}, filepath='c://temp/movingbubbles.html')


# %% Moving bubbles
d3 = D3Blocks(cmap='Set1')
# Import example
df = d3.import_example(graph='movingbubbles')
# Normalize the time per sample id.
# df = d3.standardize(df, sample_id='sample_id', datetime='datetime')
# Make the moving bubbles
d3.movingbubbles(df, datetime='datetime', state='state', sample_id='sample_id', center='Travel', speed={"slow": 1000, "medium": 200, "fast": 10}, filepath='c://temp/movingbubbles.html')


# 	{"index": "0", "short": "Sleeping", "desc": "Sleeping"},
# 	{"index": "1", "short": "Personal Care", "desc": "Personal Care"},
# 	{"index": "2", "short": "Eating & Drinking", "desc": "Eating and Drinking"},
# 	{"index": "3", "short": "Education", "desc": "Education"},
# 	{"index": "4", "short": "Work", "desc": "Work and Work-Related Activities"},
# 	{"index": "5", "short": "Housework", "desc": "Household Activities"},
# 	{"index": "6", "short": "Household Care", "desc": "Caring for and Helping Household Members"},
# 	{"index": "7", "short": "Non-Household Care", "desc": "Caring for and Helping Non-Household Members"},
# 	{"index": "8", "short": "Shopping", "desc": "Consumer Purchases"},
# 	{"index": "9", "short": "Pro. Care Services", "desc": "Professional and Personal Care Services"},
# 	{"index": "10", "short": "Leisure", "desc": "Socializing, Relaxing, and Leisure"},
# 	{"index": "11", "short": "Sports", "desc": "Sports, Exercise, and Recreation"},
# 	{"index": "12", "short": "Religion", "desc": "Religious and Spiritual Activities"},
# 	{"index": "13", "short": "Volunteering", "desc": "Volunteer Activities"},
# 	{"index": "14", "short": "Phone Calls", "desc": "Telephone Calls"},
# 	{"index": "15", "short": "Misc.", "desc": "Other"},
# 	{"index": "16", "short": "Traveling", "desc": "Traveling"},
    