from copy import deepcopy
import unittest
from d3blocks import D3Blocks
import pandas as pd
import numpy as np
try:
    import cv2
except:
    raise ImportError('cv2 must be installed manually. Try to: <pip install opencv-python>')

class Testd3blocks(unittest.TestCase):

    def test_instantiate_d3blocks_no_args() -> None:
        """Test instantiation works with defaults"""
        # Initialize
        d3 = D3Blocks()
        assert isinstance(d3, type(D3Blocks()))

    def test_heatmap(self):
        # Initialize
        d3 = D3Blocks()
        # Import example
        df = d3.import_example('energy')
        # Create the heatmap
        d3.heatmap(df, showfig=True, stroke='red', vmax=10, figsize=(700,700))


    def test_sankey(self):
        # Initialize
        d3 = D3Blocks()
        # Import example
        df = d3.import_example('energy')
        # Link settings
        d3.sankey(df, link={"color": "source-target"})

        d3 = D3Blocks()
        d = [{'source':1, 'target':2, 'weight':10}, {'source':2, 'target':3, 'weight':100}, {'source':3,'target':4, 'weight':160}, {'source':4, 'target':1, 'weight':108}]
        df = pd.DataFrame(d)
        d3.sankey(df, showfig=False)

    def test_d3graph(self):
        # Initialize
        d3 = D3Blocks()
        # Import example
        df = d3.import_example('energy')
        # Initialize Network chart but do not yet show the chart.
        d3.d3graph(df, showfig=False)
        # Color node on clustering
        d3.D3graph.set_node_properties(color='cluster')
        # Make adjustments to the node: Thermal_generation
        d3.D3graph.node_properties['Thermal_generation']['size']=20
        d3.D3graph.node_properties['Thermal_generation']['edge_color']='#000fff' # Blue node edge
        d3.D3graph.node_properties['Thermal_generation']['edge_size']=3 # Node-edge Size
        # Make adjustments to the edge: 'Solar', 'Solar_Thermal'
        d3.D3graph.edge_properties['Solar', 'Solar_Thermal']['color']='#000fff'
        d3.D3graph.edge_properties['Solar', 'Solar_Thermal']['weight_scaled']=10
        # Show the network graph
        d3.D3graph.show()

        d3 = D3Blocks()
        d = [{'source':1, 'target':2, 'weight':10}, {'source':2, 'target':3, 'weight':100}, {'source':3,'target':4, 'weight':160}, {'source':4, 'target':1, 'weight':108}]
        df = pd.DataFrame(d)
        d3.d3graph(df, showfig=True)

    def test_chord(self):
        # Initialize
        d3 = D3Blocks()
        # Import example
        df = d3.import_example('energy')
        # Link settings
        d3.chord(df, filepath='c://temp//chord_demo1.html', color='target')
        d3.chord(df, filepath='c://temp//chord_demo2.html', color='source')
        d3.chord(df, filepath='c://temp//chord_demo3.html', color='source-target')

        d3 = D3Blocks()
        df = pd.DataFrame([{'source':1, 'target':2, 'weight':10}, {'source':2, 'target':3, 'weight':100}, {'source':3,'target':4, 'weight':160}, {'source':4, 'target':1, 'weight':108}])
        # Get the node properties by setting them to defaults
        d3.set_node_properties(df, opacity=0.8, cmap='tab20')
        d3.chord(df, showfig=False)
        
        #### TEST USING NODE AND EDGE PROPERTIES
        # Initialize
        d3 = D3Blocks(chart='Chord', frame=True)
        # Import example
        df = d3.import_example('energy')
        # Node properties
        d3.set_node_properties(df, opacity=0.6, cmap='Set1')
        assert np.all(d3.node_properties['opacity']==0.6)
        assert np.all(d3.node_properties['color'].iloc[[0,2,5,9,22]]==['#e41a1c','#e41a1c','#e41a1c','#377eb8','#ff7f00'])
        ### CHECK COLORS
        d3.set_edge_properties(df, color='target')
        assert np.all(d3.edge_properties['color'].iloc[[0,2,5,9,22]]==['#e41a1c','#ff7f00','#ff7f00','#999999','#ff7f00'])
        d3.set_edge_properties(df, color='source')
        assert np.all(d3.edge_properties['color'].iloc[[0,2,5,9,22]]==['#e41a1c','#e41a1c','#e41a1c','#e41a1c','#377eb8'])
        d3.set_edge_properties(df, color='source-target')
        assert np.all(d3.edge_properties['color'].iloc[[0,2,5,9,22]]==['#1f77b4','#d62728','#f7b6d2','#9edae5','#ff7f0e'])
        d3.set_edge_properties(df, color='#f0f0f0')
        assert np.all(d3.edge_properties['color']=='#f0f0f0')
        ### CHECK OPACITY
        d3.set_edge_properties(df, color='target', opacity=0.2)
        assert np.all(d3.edge_properties['opacity']==0.2)

        # d3.edge_properties
        # Show the chord diagram
        d3.show(showfig=True, filepath='chord.html')

    def test_timeseries(self):
        # Import library.
        from d3blocks import D3Blocks
        # Initialize and set the datetime format
        d3 = D3Blocks(dt_format='%Y-%m-%d %H:%M:%S')
        # Import climate dataset
        df = d3.import_example('climate')
        # Create the timeseries chart.
        d3.timeseries(df, datetime='date', fontsize=10)

    def test_imageslider(self):
        # Initialize
        d3 = D3Blocks()
        # Import example
        img_before_path, img_after_path = d3.import_example('southern_nebula')
        img_before_url, img_after_url = d3.import_example('southern_nebula_internet')
        # Read the image
        img_before_X = cv2.imread(img_before_path, -1)
        img_after_X = cv2.imread(img_after_path, -1)

        # Make image slider graph
        d3.imageslider(img_before_url, img_after_url, showfig=False, scale=False)
        d3.imageslider(img_before_X, img_after_X, showfig=False)
        d3.imageslider(img_before_path, img_after_path, showfig=True, scale=True, colorscale=2, figsize=[400, 400])

        d3.imageslider(img_before_path, img_after_url, showfig=False)
        d3.imageslider(img_before_url, img_after_X, showfig=False)
        d3.imageslider(img_before_X, img_after_path, showfig=False)

        d3.imageslider(img_before_url, img_after_path, showfig=False)
        d3.imageslider(img_before_X, img_before_url, showfig=False)
        d3.imageslider(img_before_path, img_after_X, showfig=False)


    def test_scatter(self):
        # Initialize
        d3 = D3Blocks()
        # import example
        df = d3.import_example('cancer')
        # Setup the tooltip
        tooltip=df['labels'].values + ' <br /> Survival: ' + df['survival_months'].astype(str).str[0:4].values
        # Set the size
        size = df['survival_months'].fillna(1).values / 10
        # Scatter
        d3.scatter(df['x'].values,        # tSNE x-coordinates
                   df['y'].values,        # tSNE y-coordinates
                   x1=df['PC1'].values,   # PC1 x-coordinates
                   y1=df['PC2'].values,   # PC2 y-coordinates
                   scale=True,            # Scale the 
                   label_radio=['tSNE', 'PCA'],
                   size=size,             # Size
                   color=df['labels'].values, # List with hex colors or strings
                   stroke='#000000',      # Edge color
                   opacity=0.4,           # Opacity
                   tooltip=tooltip,       # Tooltip
                   cmap='tab20',          # Colormap in case strings are given for "c" as input
                   filepath='scatter_demo.html')
    

    def test_violin(self):
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

    def test_particles(self):
        # Initialize
        d3 = D3Blocks()
        # Make particles
        d3.particles('D3Blocks', collision=0.05, spacing=10, figsize=[1200, 500])

    def test_movingbubbles(self):
        # Set color scheme
        d3 = D3Blocks(cmap='Set1')
        # Generate random data with various states
        df = d3.import_example('random_time', n=10000, c=500, date_start="1-1-2000 00:10:05", date_stop="1-1-2001 23:59:59")
        # Make the moving bubbles chart.
        d3.movingbubbles(df, datetime='datetime', state='state', sample_id='sample_id', standardize=None, speed={"slow": 1000, "medium": 200, "fast": 10}, filepath='movingbubbles.html')
