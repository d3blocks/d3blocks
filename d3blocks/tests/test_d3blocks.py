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
    def test_medium_blog_chart_comparison(self) -> None:
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

        # Initialize
        d3 = D3Blocks()
        # Load stormofswords data sets
        df = d3.import_example(data='stormofswords')

        # Create network graph
        # Initialize
        d3 = D3Blocks()
        # Network graph
        d3.d3graph(df, charge=800, collision=2, showfig=True)
        # d3.elasticgraph(df, charge=800, collision=2, scaler='zscore')
        # Extract the node colors from the network graph.
        node_colors = d3.D3graph.node_properties

        # Heatmap
        # Initialize
        d3 = D3Blocks()
        # Create the heatmap but do not show it yet because we first need to adjust the colors
        d3.heatmap(df, showfig=False)
        # Update the colors of the network graph to be consistent with the colors
        d3.node_properties

        for i, label in enumerate(d3.node_properties['label']):
            if node_colors.get(label) is not None:
                d3.node_properties['color'].iloc[i] = node_colors.get(label)['color']

        d3.show(showfig=True, figsize=[600, 600], fontsize=8, scaler='zscore')

        # Initialize
        d3 = D3Blocks()
        # Create sankey graph
        d3.sankey(df, showfig=True)
        
        d3 = D3Blocks(chart='Sankey', frame=True)
        # Load data set
        df = d3.import_example(data='energy')
        
        # Set default node properties
        d3.set_node_properties(df)
        
        # Update the colors of the network graph to be consistent with the colors
        for i, label in enumerate(d3.node_properties['label']):
            if node_colors.get(label) is not None:
                d3.node_properties['color'].iloc[i] = node_colors.get(label)['color']
        
        # The colors in the dataframe are used in the chart.
        print(d3.node_properties)
        # Create edge properties
        d3.set_edge_properties(df, color='target', opacity='target')
        # Show the chart
        d3.show()
        

    def test_instantiate_d3blocks_no_args(self) -> None:
        """Test instantiation works with defaults"""
        # Initialize
        d3 = D3Blocks()
        assert isinstance(d3, type(D3Blocks()))

    def test_heatmap(self):
        # Initialize
        d3 = D3Blocks()
        # Import example
        df = d3.import_example('energy')
        df = d3.vec2adjmat(df['source'], df['target'], weight=df['weight'], symmetric=True)
        # Create the heatmap
        d3.heatmap(df, stroke='red', figsize=(700, 700))

    def test_matrix(self):
        # Initialize
        d3 = D3Blocks()
        # Import example
        df = d3.import_example('energy')
        df = d3.vec2adjmat(df['source'], df['target'], weight=df['weight'], symmetric=True)
        # Create the heatmap
        d3.matrix(df, stroke='red', vmax=10, figsize=(700, 700), cmap='interpolateGreens')

    def test_sankey(self):
        # Initialize
        d3 = D3Blocks()
        d = [{'source':1, 'target':2, 'weight':10}, {'source':2, 'target':3, 'weight':100}, {'source':3,'target':4, 'weight':160}, {'source':4, 'target':1, 'weight':108}]
        df = pd.DataFrame(d)
        d3.sankey(df, showfig=False)

        # Initialize
        d3 = D3Blocks()
        # Import example
        df = d3.import_example('energy')
        # Link settings
        d3.sankey(df, link={"color": "source-target"})

        # Initialize
        d3 = D3Blocks()
        df = d3.import_example('energy')
        html = d3.sankey(df, filepath=None, notebook=False)
        assert html is not None
        html = d3.sankey(df, filepath=None, notebook=True)
        assert html is None
        html = d3.sankey(df, filepath='./test.html', notebook=False)
        assert html is None


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
        d3.chord(df, filepath='chord_demo1.html', color='target')
        d3.chord(df, filepath='chord_demo2.html', color='source')
        d3.chord(df, filepath='chord_demo3.html', color='source-target')

        d3 = D3Blocks(chart='chord')
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
        d3.set_edge_properties(df, color='target', cmap='Set1')
        assert np.all(d3.edge_properties['color'].iloc[[0,2,5,9,22]]==['#e41a1c','#e41a1c','#e41a1c','#377eb8','#984ea3'])
        d3.set_edge_properties(df, color='source', cmap='Set1')
        assert np.all(d3.edge_properties['color'].iloc[[0,2,5,9,22]]==['#e41a1c','#e41a1c','#377eb8','#377eb8','#4daf4a'])
        d3.set_edge_properties(df, color='source-target')
        assert np.all(d3.edge_properties['color'].iloc[[0,2,5,9,22]]==['#1f77b4','#ffbb78','#f7b6d2','#9edae5','#2ca02c'])
        ### CHECK OPACITY
        d3.set_edge_properties(df, color='target', opacity=0.3)
        assert np.all(d3.edge_properties['opacity']==0.3)

        # d3.edge_properties
        # Show the chord diagram
        d3.set_edge_properties(df, color='#f0f0f0')
        assert np.all(d3.edge_properties['color']=='#f0f0f0')
        d3.show(showfig=True, filepath='chord.html')

        d3 = D3Blocks()
        df = d3.import_example('energy')
        html = d3.chord(df, filepath=None, notebook=False)
        assert html is not None
        html = d3.chord(df, filepath=None, notebook=True)
        assert html is None
        html = d3.chord(df, filepath='test.html', notebook=False)
        assert html is None

    def test_timeseries(self):
        # Import library.
        # Initialize and set the datetime format
        d3 = D3Blocks()
        # Import climate dataset
        df = d3.import_example('climate')
        # Create the timeseries chart.
        d3.timeseries(df, datetime='date', fontsize=10, dt_format='%Y-%m-%d')

        d3 = D3Blocks()
        df = d3.import_example('climate')
        html = d3.timeseries(df, datetime='date', dt_format='%Y-%m-%d', filepath=None, notebook=False)
        assert html is not None
        html = d3.timeseries(df, datetime='date', dt_format='%Y-%m-%d', filepath=None, notebook=True)
        assert html is None
        html = d3.timeseries(df, datetime='date', dt_format='%Y-%m-%d', filepath='./test.html', notebook=False)
        assert html is None
        

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

        # Initialize
        d3 = D3Blocks()
        img_before, img_after = d3.import_example('southern_nebula_internet')
        html = d3.imageslider(img_before, img_after, filepath=None, notebook=False)
        assert html is not None
        html = d3.imageslider(img_before, img_after, filepath=None, notebook=True)
        assert html is None
        html = d3.imageslider(img_before, img_after, filepath='test.html', notebook=False)
        assert html is None


    def test_scatter(self):
        # Initialize
        d3 = D3Blocks()
        # import example
        df = d3.import_example('cancer')
        # Setup the tooltip
        tooltip=df['labx'].values + ' <br /> Survival: ' + df['survival_months'].astype(str).str[0:4].values
        # Set the size
        size = df['survival_months'].fillna(1).values / 10
        # Scatter
        d3.scatter(df['tsneX'].values,        # tSNE x-coordinates
                   df['tsneY'].values,        # tSNE y-coordinates
                   x1=df['PC1'].values,   # PC1 x-coordinates
                   y1=df['PC2'].values,   # PC2 y-coordinates
                   scale=True,            # Scale the 
                   label_radio=['tSNE', 'PCA'],
                   size=size,             # Size
                   color=df['labx'].values, # List with hex colors or strings
                   stroke='#000000',      # Edge color
                   opacity=0.4,           # Opacity
                   tooltip=tooltip,       # Tooltip
                   cmap='tab20',          # Colormap in case strings are given for "c" as input
                   filepath='scatter_demo.html')

        d3 = D3Blocks()
        df = d3.import_example('cancer')
        html = d3.scatter(df['tsneX'].values, df['tsneY'].values, filepath=None, notebook=False)
        assert html is not None
        html = d3.scatter(df['tsneX'].values, df['tsneY'].values, filepath=None, notebook=True)
        assert html is None
        html = d3.scatter(df['tsneX'].values, df['tsneY'].values, filepath='./test.html', notebook=False)
        assert html is None


    def test_violin(self):
        # Initialize
        d3 = D3Blocks()
        # import example
        df = d3.import_example('cancer')
        # Tooltip
        tooltip=df['labx'].values + ' <br /> Survival: ' + df['survival_months'].astype(str).values
        # Make the plot
        d3.violin(x=df['labx'].values, # class labels on the x axis
                  y=df['age'].values,    # Age
                  tooltip=tooltip,       # Tooltip for hovering
                  bins=50,               # Bins used for the histogram
                  size=df['survival_months'].values/10, # Dotsize
                  x_order=['acc','kich', 'brca','lgg','blca','coad','ov'], # Keep only these classes and plot in this order.
                  figsize=[None, None],   # Figure size is automatically determined.
                  filepath='violine_demo.html')

        # Violin
        d3 = D3Blocks()
        df = d3.import_example('cancer')
        html = d3.violin(x=df['labx'].values, y=df['age'].values, filepath=None, notebook=False)
        assert html is not None
        html = d3.violin(x=df['labx'].values, y=df['age'].values, filepath=None, notebook=True)
        assert html is None
        html = d3.violin(x=df['labx'].values, y=df['age'].values, filepath='./test.html', notebook=False)
        assert html is None

    def test_particles(self):
        # Initialize
        d3 = D3Blocks()
        # Make particles
        d3.particles('D3Blocks', collision=0.05, spacing=10, figsize=[1200, 500])

        # Initialize
        d3 = D3Blocks()
        df = d3.import_example('energy')
        html = d3.particles('D3blocks', filepath=None, notebook=False)
        assert html is not None
        html = d3.particles('D3blocks', filepath=None, notebook=True)
        assert html is None
        html = d3.particles('D3blocks', filepath='test.html', notebook=False)
        assert html is None

    def test_treemap(self):
        # Load d3blocks
        from d3blocks import D3Blocks
        # Initialize
        d3 = D3Blocks()
        # Load example data
        df = d3.import_example('energy')
        # df = d3.import_example('animals')
        # Plot
        d3.treemap(df)

        # Load d3blocks
        from d3blocks import D3Blocks
        # Initialize
        d3 = D3Blocks(chart='Treemap', frame=True)
        # Import example
        df = d3.import_example('energy')
        # Node properties
        d3.set_node_properties(df)
        d3.set_edge_properties(df)
        # Show the chart
        d3.show()

    def test_tree(self):
        # Load d3blocks
        from d3blocks import D3Blocks
        # Initialize
        d3 = D3Blocks()
        # Load example data
        df = d3.import_example('energy')
        # Plot
        d3.tree(df)

        # Load library
        from d3blocks import D3Blocks
        # Initialize
        d3 = D3Blocks(verbose='info', chart='tree', frame=False)
        # Import example
        df = d3.import_example('energy')
        # Set node properties
        d3.set_node_properties(df)
        # Set specific properties
        d3.node_properties.get('Bio-conversion')['size'] = 30
        d3.node_properties.get('Bio-conversion')['color'] = '#000000'
        d3.node_properties.get('Bio-conversion')['tooltip'] = 'Title: P Operations<br><img src="https://source.unsplash.com/collection/385548/150x100">'
        d3.node_properties.get('Bio-conversion')['edge_color'] = '#00FFFF'
        d3.node_properties.get('Bio-conversion')['edge_size'] = 5
        d3.node_properties.get('Bio-conversion')['opacity'] = 0.4
        # Set properties for Losses
        d3.node_properties.get('Losses')['color'] = '#FF0000'
        d3.node_properties.get('Losses')['size'] = 15
        d3.node_properties.get('Losses')['tooltip'] = ''
        # Set properties for Agriculture
        d3.node_properties.get('Agriculture')['color'] = '#00FFFF'
        d3.node_properties.get('Agriculture')['size'] = 5
        d3.node_properties.get('Agriculture')['edge_color'] = '#89CFF0'
        d3.node_properties.get('Agriculture')['edge_size'] = 3
        d3.node_properties.get('Agriculture')['opacity'] = 0.7
        # Set edge properties
        d3.set_edge_properties(df)
        # Show chart
        d3.show(hierarchy=[1, 2, 3, 4, 5, 6, 7, 8], filepath=r'c:\temp\tree.html')

        # Load d3blocks
        from d3blocks import D3Blocks
        # Initialize
        d3 = D3Blocks(chart='tree', frame=True)
        # Import example
        df = d3.import_example('energy')
        # Node properties
        d3.set_node_properties(df)
        d3.set_edge_properties(df)
        # Show the chart
        d3.show()

    def test_movingbubbles(self):
        # Set color scheme
        d3 = D3Blocks()
        # Generate random data with various states
        df = d3.import_example('random_time', n=10000, c=500, date_start="01-01-2000 00:10:05", date_stop="01-01-2001 23:59:59")
        # Make the moving bubbles chart.
        d3.movingbubbles(df, datetime='datetime', state='state', sample_id='sample_id', standardize=None, speed={"slow": 1000, "medium": 200, "fast": 10}, filepath='movingbubbles.html')

        d3 = D3Blocks()
        df = d3.import_example('random_time', n=10000, c=300, date_start="01-01-2000 00:10:05", date_stop="01-01-2000 23:59:59")
        html = d3.movingbubbles(df, speed={"slow": 1000, "medium": 200, "fast": 10}, filepath=None, notebook=False)
        assert html is not None
        html = d3.movingbubbles(df, speed={"slow": 1000, "medium": 200, "fast": 10}, filepath=None, notebook=True)
        assert html is None
        html = d3.movingbubbles(df, speed={"slow": 1000, "medium": 200, "fast": 10}, filepath='test.html', notebook=False)
        assert html is None

    def test_html(self):
        # Violin
        from d3blocks import D3Blocks
        d3 = D3Blocks()
        df = d3.import_example('cancer')
        html = d3.violin(x=df['labx'].values, y=df['age'].values, filepath=None, notebook=False)
        assert html is not None
        html = d3.violin(x=df['labx'].values, y=df['age'].values, filepath=None, notebook=True)
        assert html is None
        html = d3.violin(x=df['labx'].values, y=df['age'].values, filepath='./test.html', notebook=False, showfig=False)
        assert html is None

        # Timeseries
        from d3blocks import D3Blocks
        d3 = D3Blocks()
        df = d3.import_example('climate')
        html = d3.timeseries(df, datetime='date', dt_format='%Y-%m-%d', filepath=None, notebook=False)
        assert html is not None
        html = d3.timeseries(df, datetime='date', dt_format='%Y-%m-%d', filepath=None, notebook=True)
        assert html is None
        html = d3.timeseries(df, datetime='date', dt_format='%Y-%m-%d', filepath='./test.html', notebook=False, showfig=False)
        assert html is None

        # Scatter
        from d3blocks import D3Blocks
        d3 = D3Blocks()
        df = d3.import_example('cancer')
        html = d3.scatter(df['tsneX'].values, df['tsneY'].values, filepath=None, notebook=False)
        assert html is not None
        html = d3.scatter(df['tsneX'].values, df['tsneY'].values, filepath=None, notebook=True)
        assert html is None
        html = d3.scatter(df['tsneX'].values, df['tsneY'].values, filepath='./test.html', notebook=False, showfig=False)
        assert html is None

        # Sankey
        from d3blocks import D3Blocks
        d3 = D3Blocks()
        df = d3.import_example('energy')
        html = d3.sankey(df, filepath=None, notebook=False)
        assert html is not None
        html = d3.sankey(df, filepath=None, notebook=True)
        assert html is None
        html = d3.sankey(df, filepath='./test.html', notebook=False, showfig=False)
        assert html is None

        # Particles
        from d3blocks import D3Blocks
        d3 = D3Blocks()
        df = d3.import_example('energy')
        html = d3.particles('D3blocks', filepath=None, notebook=False)
        assert html is not None
        html = d3.particles('D3blocks', filepath=None, notebook=True)
        assert html is None
        html = d3.particles('D3blocks', filepath='test.html', notebook=False, showfig=False)
        assert html is None

        # Movingbubbles
        from d3blocks import D3Blocks
        d3 = D3Blocks()
        df = d3.import_example('random_time', n=10000, c=100, date_start="01-01-2000 00:10:05", date_stop="01-01-2000 23:59:59")
        html = d3.movingbubbles(df, speed={"slow": 1000, "medium": 200, "fast": 10}, filepath=None, notebook=False)
        assert html is not None
        html = d3.movingbubbles(df, speed={"slow": 1000, "medium": 200, "fast": 10}, filepath=None, notebook=True)
        assert html is None
        html = d3.movingbubbles(df, speed={"slow": 1000, "medium": 200, "fast": 10}, filepath='test.html', notebook=False, showfig=False)
        assert html is None

        from d3blocks import D3Blocks
        d3 = D3Blocks()
        img_before, img_after = d3.import_example('southern_nebula_internet')
        html = d3.imageslider(img_before, img_after, filepath=None, notebook=False)
        assert html is not None
        html = d3.imageslider(img_before, img_after, filepath=None, notebook=True)
        assert html is None
        html = d3.imageslider(img_before, img_after, filepath='test.html', notebook=False, showfig=False)
        assert html is None

        # Chord
        from d3blocks import D3Blocks
        d3 = D3Blocks()
        df = d3.import_example('energy')
        html = d3.chord(df, filepath=None, notebook=False)
        assert html is not None
        html = d3.chord(df, filepath=None, notebook=True)
        assert html is None
        html = d3.chord(df, filepath='test.html', notebook=False, showfig=False)
        assert html is None

        # treemap
        from d3blocks import D3Blocks
        d3 = D3Blocks()
        df = d3.import_example('energy')
        html = d3.treemap(df, filepath=None, notebook=False)
        assert html is not None
        html = d3.treemap(df, filepath=None, notebook=True)
        assert html is None
        html = d3.treemap(df, filepath='test.html', notebook=False, showfig=False)
        assert html is None

        # Tree
        from d3blocks import D3Blocks
        d3 = D3Blocks()
        df = d3.import_example('energy')
        html = d3.tree(df, filepath=None, notebook=False)
        assert html is not None
        html = d3.tree(df, filepath=None, notebook=True)
        assert html is None
        html = d3.tree(df, filepath='test.html', notebook=False, showfig=False)
        assert html is None
