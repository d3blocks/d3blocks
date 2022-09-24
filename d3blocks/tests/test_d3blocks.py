from copy import deepcopy
import unittest
from d3blocks import D3Blocks


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

    def test_chord(self):
        # Initialize
        d3 = D3Blocks()
        # Import example
        df = d3.import_example('energy')
        # Link settings
        d3.chord(df, filepath='chord_demo.html')

    def test_timeseries(self):
        # Import library.
        from d3blocks import D3Blocks
        # Initialize and set the datetime format
        d3 = D3Blocks(dt_format='%Y-%m-%d %H:%M:%S')
        # Import climate dataset
        df = d3.import_example('climate')
        # Create the timeseries chart.
        d3.timeseries(df, datetime='date', fontsize=10)

    def test_movingbubbles(self):
        # Import library
        from d3blocks import D3Blocks
        # Set color scheme
        d3 = D3Blocks(cmap='Set1')
        # Generate random data with various states
        df = d3.import_example('random_time', n=10000, c=500, date_start="1-1-2000 00:10:05", date_stop="1-1-2001 23:59:59")
        # Make the moving bubbles chart.
        d3.movingbubbles(df, datetime='datetime', state='state', sample_id='sample_id', standardize=None, speed={"slow": 1000, "medium": 200, "fast": 10}, filepath='movingbubbles.html')

    def test_imageslider(self):
        # Initialize
        d3 = D3Blocks()
        # Import example
        img_before, img_after = d3.import_example('unsplash')
        # Make image slider graph
        d3.imageslider(img_before, img_after)
        
    
    def test_scatter(self):
        # Initialize
        d3 = D3Blocks()
        # import example
        df = d3.import_example('cancer')
        # Setup the tooltip
        tooltip=df['labels'].values + ' <br /> Survival: ' + df['survival_months'].astype(str).str[0:4].values
        # Set the size
        s = df['survival_months'].fillna(1).values / 10
        # Scatter
        d3.scatter(df['x'].values,        # tSNE x-coordinates
                   df['y'].values,        # tSNE y-coordinates
                   x1=df['PC1'].values,   # PC1 x-coordinates
                   y1=df['PC2'].values,   # PC2 y-coordinates
                   scale=True,            # Scale the 
                   label_radio=['tSNE', 'PCA'],
                   s=s,                   # Size
                   c=df['labels'].values, # List with hex colors or strings
                   stroke='#000000',      # Edge color
                   opacity=0.4,           # Opacity
                   tooltip=tooltip,       # Tooltip
                   cmap='tab20',          # Colormap in case strings are given for "c" as input
                   filepath='c://temp//scatter_demo.html')
    

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
                  s=df['survival_months'].values/10, # Dotsize
                  x_order=['acc','kich', 'brca','lgg','blca','coad','ov'], # Keep only these classes and plot in this order.
                  figsize=[None, None],   # Figure size is automatically determined.
                  filepath='c://temp//violine_demo.html')

    def test_particles(self):
        # Initialize
        d3 = D3Blocks()
        # Make particles
        d3.particles('D3Blocks', collision=0.05, spacing=10, figsize=[1200, 500])
