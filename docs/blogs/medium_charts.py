# Load library
from d3blocks import D3Blocks

# Initialize
d3 = D3Blocks()
# Import example
df = d3.import_example('energy')
# Create network using default
d3.d3graph(df, filepath='d3graph.html', color='cluster', showfig=True)

#%%
# Customize the chart

# Node properties are stored here:
d3.D3graph.node_properties
# Node properties are stored here:
d3.D3graph.edge_properties

# Change the node properties like this:
d3.D3graph.set_node_properties(color=None)
d3.D3graph.node_properties['Solar']['size']=30
d3.D3graph.node_properties['Solar']['color']='#FF0000'
d3.D3graph.node_properties['Solar']['edge_color']='#000000'
d3.D3graph.node_properties['Solar']['edge_size']=5

# After making changes, show the graph again using show()
d3.D3graph.show()

# Change edge properties like this:
d3.D3graph.set_edge_properties(directed=True, marker_end='arrow')

# After making changes, show the graph again using show()
d3.D3graph.show()

#%%
# Load library
from d3blocks import D3Blocks

# Initialize
d3 = D3Blocks()
# Import example
df = d3.import_example('energy')
# Create Chart
d3.elasticgraph(df, filepath='elastic.html')

#%%
# Load library
from d3blocks import D3Blocks

# Initialize
d3 = D3Blocks()
# Import example
df = d3.import_example('energy')
# Create Chart
d3.sankey(df, filepath='sankey.html')

#%%
# Load library
from d3blocks import D3Blocks

# Initialize
d3 = D3Blocks()
# Import example
df = d3.import_example('energy')
# Create Chart
d3.chord(df, filepath='chord.html')

#%%
# Load library
from d3blocks import D3Blocks

# Initialize
d3 = D3Blocks()

# Import example
df = d3.import_example('stormofswords')

# Create Chart
d3.heatmap(df, filepath='heatmap.html')

#%%
# Load library
from d3blocks import D3Blocks

# Initialize
d3 = D3Blocks()

# Import example
df = d3.import_example('energy')

# Create Chart
d3.tree(df, filepath='tree.html')

#%%
# Load library
from d3blocks import D3Blocks

# Initialize
d3 = D3Blocks()

# Import example
df = d3.import_example('energy')

# Create Chart
d3.treemap(df, filepath=r'C:/temp/treemap.html')

#%%
# Load library
from d3blocks import D3Blocks

# Initialize
d3 = D3Blocks()

# Import example
df = d3.import_example('energy')

# Create Chart
d3.circlepacking(df, filepath=r'C:/temp/circlepacking.html')

#%%
# Import
from d3blocks import D3Blocks

# Initialize
d3 = D3Blocks()

# Import example
df = d3.import_example('climate')

"""
+------------+------------+-----------+-------------+---------------+
|    Date    | Mean Temp  | Humidity  | Wind Speed  | Mean Pressure |
+------------+------------+-----------+-------------+---------------+
| 2017-01-01 |   15.913   |   85.870  |     2.743   |      59.000   |
| 2017-01-02 |   18.500   |   77.222  |     2.894   |    1018.278   |
| 2017-01-03 |   17.111   |   81.889  |     4.017   |    1018.333   |
| 2017-01-04 |   18.700   |   70.050  |     4.545   |    1015.700   |
| 2017-01-05 |   18.389   |   74.944  |     3.300   |    1014.333   |
|    ...     |    ...     |    ...    |     ...     |      ...      |
| 2017-04-20 |   34.500   |   27.500  |     5.563   |     998.625   |
| 2017-04-21 |   34.250   |   39.375  |     6.963   |     999.875   |
| 2017-04-22 |   32.900   |   40.900  |     8.890   |    1001.600   |
| 2017-04-23 |   32.875   |   27.500  |     9.963   |    1002.125   |
| 2017-04-24 |   32.000   |   27.143  |    12.157   |    1004.143   |
+------------+------------+-----------+-------------+---------------+
"""

# Create Chart
d3.timeseries(df, datetime='date', dt_format='%Y-%m-%d', fontsize=10, figsize=[850, 500])


#%%
# Import
from d3blocks import D3Blocks
import random

# Initialize
d3 = D3Blocks(chart='movingbubbles')

# Import example
df = d3.import_example('random_time', n=10000, c=300, date_start="1-1-2000 00:10:05", date_stop="1-1-2000 23:59:59")

"""
+---------------------+-----------+-----------+
|      Datetime       | Sample ID |   State   |
+---------------------+-----------+-----------+
| 2000-01-01 00:10:07 |     187   |   Sick    |
| 2000-01-01 00:10:14 |      59   |   Sick    |
| 2000-01-01 00:10:46 |     122   |   Sick    |
| 2000-01-01 00:10:57 |     112   |   Sick    |
| 2000-01-01 00:11:12 |     174   |   Work    |
|         ...         |    ...    |   ...     |
| 2000-01-01 23:59:56 |     183   |  Sport    |
| 2000-01-01 23:59:57 |       9   | Sleeping  |
| 2000-01-01 23:59:58 |     297   |  Travel   |
| 2000-01-01 23:59:58 |     297   | Sleeping  |
| 2000-01-01 23:59:58 |     261   | Sleeping  |
+---------------------+-----------+-----------+
"""

# Customize states with color and size:
color = {1: '#FF0000', 3: '#000FFF'}
size = {i: random.randint(5, 20) for i in range(1, 50)}

d3.movingbubbles(df, color=color, size=size, figsize=[775, 800])

#%%
# Load d3blocks
from d3blocks import D3Blocks

# Initialize
d3 = D3Blocks()

# Load example data
df = d3.import_example('cancer')

"""
+-----------+-----------+------+--------+------------+------------+
|  tsneX    |  tsneY    | Age  | Labx   |    PC1     |    PC2     |
+-----------+-----------+------+--------+------------+------------+
|  37.20430 |  24.16281 | 58.0 |  acc   |  49.23346  |  14.49651  |
|  37.09309 |  23.42356 | 44.0 |  acc   |  46.32799  |  14.46447  |
|  36.80630 |  23.44491 | 23.0 |  acc   |  46.56793  |  13.48013  |
|  38.06789 |  24.41177 | 30.0 |  acc   |  63.62468  |   1.87406  |
|  36.79120 |  21.71532 | 29.0 |  acc   |  41.74671  |  37.53362  |
|   ...     |    ...    | ...  |  ...   |    ...     |    ...     |
|   0.83938 |  -8.87078 | NaN  |  brca  | -15.38129  |  -8.25454  |
|  -5.84290 |   2.87760 | NaN  |  brca  | -19.16332  |  -6.42407  |
|  -9.39204 |   1.66335 | 71.0 |  brca  | -21.79413  |  -6.19291  |
|  -4.01639 |   6.26074 | NaN  |  brca  | -24.53614  |  -1.17167  |
|   0.22980 |  -8.22709 | NaN  |  brca  | -28.16274  |  -5.29207  |
+-----------+-----------+------+--------+------------+------------+
"""

# Set size and tooltip
size = df['survival_months'].fillna(1).values / 20
tooltip = df['labx'].values + ' <br /> Survival: ' + df['survival_months'].astype(str).str[0:4].values

# Scatter plot
d3.scatter(df['tsneX'].values,
                       df['tsneY'].values,
                       size=size,
                       color=df['labx'].values,
                       stroke='#000000',
                       opacity=0.4,
                       tooltip=tooltip,
                       filepath='scatter_demo.html',
                       cmap='tab20')

#%%
# Load d3blocks
from d3blocks import D3Blocks

# Initialize
d3 = D3Blocks()

# Import example data set
df = d3.import_example('cancer')

"""
+-----------+-----------+------+--------+------------+------------+
|  tsneX    |  tsneY    | Age  | Labx   |    PC1     |    PC2     |
+-----------+-----------+------+--------+------------+------------+
|  37.20430 |  24.16281 | 58.0 |  acc   |  49.23346  |  14.49651  |
|  37.09309 |  23.42356 | 44.0 |  acc   |  46.32799  |  14.46447  |
|  36.80630 |  23.44491 | 23.0 |  acc   |  46.56793  |  13.48013  |
|  38.06789 |  24.41177 | 30.0 |  acc   |  63.62468  |   1.87406  |
|  36.79120 |  21.71532 | 29.0 |  acc   |  41.74671  |  37.53362  |
|   ...     |    ...    | ...  |  ...   |    ...     |    ...     |
|   0.83938 |  -8.87078 | NaN  |  brca  | -15.38129  |  -8.25454  |
|  -5.84290 |   2.87760 | NaN  |  brca  | -19.16332  |  -6.42407  |
|  -9.39204 |   1.66335 | 71.0 |  brca  | -21.79413  |  -6.19291  |
|  -4.01639 |   6.26074 | NaN  |  brca  | -24.53614  |  -1.17167  |
|   0.22980 |  -8.22709 | NaN  |  brca  | -28.16274  |  -5.29207  |
+-----------+-----------+------+--------+------------+------------+
"""

# Set some input variables.
tooltip = df['labx'].values + ' <br /> Survival: ' + df['survival_months'].astype(str).values

# Create the chart
d3.violin(x=df['labx'].values, y=df['age'].values, tooltip=tooltip, bins=50, size=df['survival_months'].values/10, x_order=['acc','kich', 'brca','lgg','blca','coad','ov'], filepath='violine.html', figsize=[900, None])


#%%
# Load d3blocks
from d3blocks import D3Blocks

# Initialize
d3 = D3Blocks()

# Load example data
df = d3.import_example('surfspots')

"""
+--------+--------+----------------+------+
|  Lat   |  Lon   |     Label      | Size |
+--------+--------+----------------+------+
| -82.9  | 135.0  |  Antarctica    |   4  |
| -54.8  | -68.3  | South America  |   4  |
| -53.8  | -67.7  | South America  |   1  |
| -53.2  | -70.9  |      NaN       |   2  |
| -52.4  | -71.0  | South America  |   2  |
|  ...   |  ...   |      ...       |  ... |
|  69.6  |  19.0  |      NaN       |   1  |
|  70.0  |  23.3  |    Europe      |   1  |
|  70.4  |  29.5  |    Europe      |  13  |
|  76.3  | -100.1 | North America  |   1  |
|  78.2  |  15.6  |    Europe      |   3  |
+--------+--------+----------------+------+
"""

# Plot
d3.maps(df)

#%%
# Load d3blocks
from d3blocks import D3Blocks
import cv2
import requests
import numpy as np

# Initialize
d3 = D3Blocks()
# Load local images
img_before, img_after = d3.import_example('southern_nebula')
# Read the image in array
img_before = cv2.imread(img_before, -1)
img_after = cv2.imread(img_after, -1)
# Create the Slider
d3.imageslider(img_before, img_after)

# Internet images
url_before, url_after = d3.import_example('southern_nebula_internet')
# Import image from the internet
resp = requests.get(url_before)
image_data = np.asarray(bytearray(resp.content), dtype=np.uint8)
img_before = cv2.imdecode(image_data, cv2.IMREAD_UNCHANGED)
# Import image from the internet
resp = requests.get(url_after)
image_data = np.asarray(bytearray(resp.content), dtype=np.uint8)
img_after = cv2.imdecode(image_data, cv2.IMREAD_UNCHANGED)
# Create the Slider
d3.imageslider(img_before, img_after)

#%%
# Load d3blocks
from d3blocks import D3Blocks

# Initialize
d3 = D3Blocks()

# Create chart with defaults
d3.particles('D3blocks')

# Create customized chart
d3.particles('D3Blocks',
             filepath='D3Blocks.html',
             collision=0.05,
             spacing=7,
             figsize=[750, 150],
             fontsize=130,
             cmap='Turbo',
             color_background='#ffffff')
