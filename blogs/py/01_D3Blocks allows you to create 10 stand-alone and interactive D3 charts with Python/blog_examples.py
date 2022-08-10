from d3blocks import D3Blocks
# Initialize
d3 = D3Blocks()
# Import example
img_before, img_after = d3.import_example('southern_nebula')

print(img_before)
'C:\\southern_nebula_before.jpg'

print(img_after)
'C:\\southern_nebula_after.jpg'

# Make comparison
d3.imageslider(img_before, img_after, showfig=True)

#%%
from d3blocks import D3Blocks

# Initialize
d3 = D3Blocks()

# import example
df = d3.import_example('iris')

print(df)
#       x    y
# 0   5.1  3.5
# 0   4.9  3.0
# 0   4.7  3.2
# 0   4.6  3.1
# 0   5.0  3.6
# ..  ...  ...
# 2   6.7  3.0
# 2   6.3  2.5
# 2   6.5  3.0
# 2   6.2  3.4
# 2   5.9  3.0

# [150 rows x 2 columns]

# Scatter
d3.scatter(df, filepath='scatter_demo.html')


#%%
from d3blocks import D3Blocks

# Initialize
d3 = D3Blocks()

# Import example
df = d3.import_example('energy')

print(df)
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


# %% Time series example

import yfinance as yf
df = yf.download(["TSLA", "TWTR", "FB", "AMZN", "AAPL"], start="2019-01-01", end="2021-12-31")
d = df[["Adj Close"]].droplevel(0, axis=1).resample("M").last()
df = df.div(df.iloc[0])
df.head()

#            Adj Close                      ...    Volume                    
#                 AAPL      AMZN        FB  ...        FB      TSLA      TWTR
# Date                                      ...                              
# 2018-12-31  1.000000  1.000000  1.000000  ...  1.000000  1.000000  1.000000
# 2019-01-02  1.001141  1.024741  1.035014  ...  1.142978  1.849896  0.942329
# 2019-01-03  0.901420  0.998875  1.004958  ...  0.922545  1.105184  1.192595
# 2019-01-04  0.939901  1.048882  1.052330  ...  1.177734  1.173238  1.465577
# 2019-01-07  0.937809  1.084915  1.053093  ...  0.815800  1.198166  1.246811
#              ...       ...       ...  ...       ...       ...       ...
# 2021-12-23  4.604702  2.277922  2.557327  ...  0.568021  0.980734  0.561978
# 2021-12-27  4.710494  2.259293  2.640781  ...  0.722632  0.752592  0.537696
# 2021-12-28  4.683328  2.272495  2.641086  ...  0.675630  0.638116  0.552801
# 2021-12-29  4.685678  2.253054  2.616065  ...  0.436421  0.594005  0.546660
# 2021-12-30  4.654855  2.245644  2.626898  ...  0.430181  0.497606  0.910241

# [757 rows x 30 columns]

from d3blocks import D3Blocks
d3 = D3Blocks(whitelist='close')
d3.timeseries(df, filepath='timeseries.html', fontsize=10)


# %% moving bubbles

# Import library
from d3blocks import D3Blocks

# Set color scheme
d3 = D3Blocks(cmap='Set1')

# Import example
df = d3.import_example(graph='random_time', n=10000, c=100, date_start="1-1-2000 00:10:05", date_stop="1-1-2000 23:59:59")

#                 datetime sample_id     state
# 0    2000-01-01 00:10:10        54  Hospital
# 1    2000-01-01 00:10:19        28      Home
# 2    2000-01-01 00:10:21        98  Hospital
# 3    2000-01-01 00:10:30        12  Hospital
# 4    2000-01-01 00:10:32        71    Travel
#                  ...       ...       ...
# 9995 2000-01-01 23:59:20         2  Hospital
# 9996 2000-01-01 23:59:24        17      Home
# 9997 2000-01-01 23:59:31        37     Bored
# 9998 2000-01-01 23:59:47        48     Sport
# 9999 2000-01-01 23:59:47        70    Travel

# [10000 rows x 3 columns]

# Make the moving bubbles chart
d3.movingbubbles(df, datetime='datetime', state='state', sample_id='sample_id', center='Travel', speed={"slow": 1000, "medium": 200, "fast": 10}, filepath='./temp/movingbubbles.html')
