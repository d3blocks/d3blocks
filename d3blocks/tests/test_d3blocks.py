import unittest
from d3blocks import D3Blocks


class Testd3blocks(unittest.TestCase):

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
        
        # Show the input data
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
        
        # Print
        df.head()
        
        #            date   meantemp   humidity  wind_speed  meanpressure
        #     2017-01-01  15.913043  85.869565    2.743478     59.000000
        #     2017-01-02  18.500000  77.222222    2.894444   1018.277778
        #     2017-01-03  17.111111  81.888889    4.016667   1018.333333
        #     2017-01-04  18.700000  70.050000    4.545000   1015.700000
        #     2017-01-05  18.388889  74.944444    3.300000   1014.333333
        #           ...        ...        ...         ...           ...
        #     2017-04-20  34.500000  27.500000    5.562500    998.625000
        #     2017-04-21  34.250000  39.375000    6.962500    999.875000
        #     2017-04-22  32.900000  40.900000    8.890000   1001.600000
        #     2017-04-23  32.875000  27.500000    9.962500   1002.125000
        #     2017-04-24  32.000000  27.142857   12.157143   1004.142857
        
        # [114 rows x 5 columns]
        
        # Create the timeseries chart.
        d3.timeseries(df, datetime='date', fontsize=10)

    def test_movingbubbles(self):
        # Import library
        from d3blocks import D3Blocks
        
        # Set color scheme
        d3 = D3Blocks(cmap='Set1')
        
        # Generate random data with various states
        df = d3.import_example('random_time', n=10000, c=500, date_start="1-1-2000 00:10:05", date_stop="1-1-2001 23:59:59")
        
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
        
        # Make the moving bubbles chart.
        d3.movingbubbles(df, datetime='datetime', state='state', sample_id='sample_id', standardize=None, speed={"slow": 1000, "medium": 200, "fast": 10}, filepath='movingbubbles.html')

    def test_imageslider(self):
        # Initialize
        d3 = D3Blocks()
        
        # Import example
        img_before, img_after = d3.import_example('unsplash')
        
        print(img_before)
        'C:\\unsplash_before.jpg'
        
        print(img_after)
        'C:\\unsplash_after.jpg'
        
        # Make image slider graph
        d3.imageslider(img_before, img_after)
        
    
    def test_scatter(self):
        # Initialize
        d3 = D3Blocks()
        
        # import example
        df = d3.import_example('cancer')
        
        #          x          y   age  ... labels 
        #                              ...        
        #  37.204296  24.162813  58.0  ...    acc 
        #  37.093090  23.423557  44.0  ...    acc 
        #  36.806297  23.444910  23.0  ...    acc 
        #  38.067886  24.411770  30.0  ...    acc 
        #  36.791195  21.715324  29.0  ...    acc 
        #    ...        ...   ...  ...    ...     
        #   0.839383  -8.870781   NaN  ...   brca 
        #  -5.842904   2.877595   NaN  ...   brca 
        #  -9.392038   1.663352  71.0  ...   brca 
        #  -4.016389   6.260741   NaN  ...   brca 
        #   0.229801  -8.227086   NaN  ...   brca 
        
        # [4674 rows x 9 columns]
        
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
