#!/usr/bin/env python3
"""
Comprehensive test file for d3blocks functionality.
This file contains all examples extracted from d3blocks.py for iterative testing.
"""

import sys
import os
import pandas as pd
import numpy as np
import pytest
from d3blocks import D3Blocks

# Add the d3blocks directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def test_particles():
    """Test particles functionality."""
    print("=== Testing Particles ===")
    print("📊 Initializing D3Blocks...")
    try:
        from d3blocks import D3Blocks
        
        # Initialize
        d3 = D3Blocks()
        print("✅ D3Blocks initialized successfully")
        
        # Create chart with defaults
        print("🎨 Creating default particles chart...")
        d3.particles('D3blocks')
        print("✅ Default particles chart created")
        
        # Create customized chart
        print("🎨 Creating customized particles chart...")
        d3.particles('D3Blocks',
                     filepath='D3Blocks.html',
                     collision=0.05,
                     spacing=7,
                     figsize=[750, 150],
                     fontsize=130,
                     cmap='Turbo',
                     color_background='#ffffff')
        print("✅ Customized particles chart created")
        print("📁 Chart saved as 'D3Blocks.html'")
        print("✅ Particles test completed successfully")
        assert True
    except Exception as e:
        print(f"❌ Particles test failed: {e}")
        print(f"🔍 Error details: {type(e).__name__}: {str(e)}")
        assert False

def test_violin():
    """Test violin functionality."""
    print("=== Testing Violin ===")
    print("📊 Initializing D3Blocks...")
    try:
        from d3blocks import D3Blocks
        
        # Initialize
        d3 = D3Blocks()
        print("✅ D3Blocks initialized successfully")
        
        # Import example dataset
        print("📥 Importing cancer dataset...")
        df = d3.import_example('cancer')
        assert df is not None
        print(f"✅ Cancer dataset loaded successfully - {len(df)} rows, {len(df.columns)} columns")
        print(f"📊 Dataset columns: {list(df.columns)}")
        
        # Set some input variables.
        print("🔧 Preparing chart parameters...")
        tooltip = df['labx'].values + ' <br /> Survival: ' + df['survival_months'].astype(str).values
        fontsize = df['age'].values
        print(f"✅ Tooltip and fontsize prepared for {len(tooltip)} data points")
        
        # Create the chart
        print("🎨 Creating violin chart...")
        d3.violin(x=df['labx'].values, 
                  y=df['age'].values, 
                  fontsize=fontsize, 
                  tooltip=tooltip, 
                  bins=50, 
                  size=df['survival_months'].values/10, 
                  x_order=['acc','kich', 'brca','lgg','blca','coad','ov'], 
                  filepath='violine.html', 
                  figsize=[900, None])
        print("✅ Violin chart created successfully")
        print("📁 Chart saved as 'violine.html'")
        print("✅ Violin test completed successfully")
        assert True
    except Exception as e:
        print(f"❌ Violin test failed: {e}")
        print(f"🔍 Error details: {type(e).__name__}: {str(e)}")
        assert False

def test_violin_advanced():
    """Test violin advanced functionality."""
    print("=== Testing Violin Advanced ===")
    try:
        from d3blocks import D3Blocks
        
        # Initialize for the Violin chart and set output to Frame.
        d3 = D3Blocks(chart='Violin', frame=True)
        
        # Import example dataset
        df = d3.import_example('cancer')
        assert df is not None
        
        # Set the properties by providing the labels
        d3.set_edge_properties(x=df['labx'].values, 
                              y=df['age'].values, 
                              size=df['survival_months'].values/10, 
                              x_order=['acc','kich', 'brca','lgg','blca','coad','ov'])
        
        # Set specific node properties.
        if d3.edge_properties is not None:
            d3.edge_properties.loc[0,'size']=50
            d3.edge_properties.loc[0,'color']='#000000'
            d3.edge_properties.loc[0,'tooltip']='I am adjusted!'
            d3.edge_properties.loc[0,'fontsize']=30
        
        # Show the chart
        d3.show(showfig=False)
        print("✅ Violin advanced test completed")
        assert True
    except Exception as e:
        print(f"❌ Violin advanced test failed: {e}")
        assert False

def test_scatter():
    """Test scatter functionality."""
    print("=== Testing Scatter ===")
    try:
        from d3blocks import D3Blocks
        
        # Initialize
        d3 = D3Blocks()
        
        # Load example data
        df = d3.import_example('cancer')
        assert df is not None
        
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
        print("✅ Scatter test completed")
        assert True
    except Exception as e:
        print(f"❌ Scatter test failed: {e}")
        assert False

def test_scatter_transitions():
    """Test scatter with transitions."""
    print("=== Testing Scatter Transitions ===")
    try:
        from d3blocks import D3Blocks
        
        # Initialize
        d3 = D3Blocks()
        
        # Load example data
        df = d3.import_example('cancer')
        assert df is not None
        
        # Set size and tooltip
        size = df['survival_months'].fillna(1).values / 20
        tooltip = df['labx'].values + ' <br /> Survival: ' + df['survival_months'].astype(str).str[0:4].values
        
        # Scatter plot with transitions
        d3.scatter(df['tsneX'].values,
                   df['tsneY'].values,
                   x1=df['PC1'].values,
                   y1=df['PC2'].values,
                   label_radio=['tSNE', 'PCA'],
                   scale=True,
                   size=size,
                   color=df['labx'].values,
                   stroke='#000000',
                   opacity=0.4,
                   tooltip=tooltip,
                   filepath='scatter_transitions2.html',
                   cmap='tab20')
        print("✅ Scatter transitions test completed")
        assert True
    except Exception as e:
        print(f"❌ Scatter transitions test failed: {e}")
        assert False

def test_scatter_advanced():
    """Test scatter advanced functionality."""
    print("=== Testing Scatter Advanced ===")
    try:
        from d3blocks import D3Blocks
        
        # Initialize
        d3 = D3Blocks(chart='Scatter')
        
        # Import example
        df = d3.import_example('cancer')
        assert df is not None
        
        # Set properties
        d3.set_edge_properties(df['tsneX'].values,
                               df['tsneY'].values,
                               x1=df['PC1'].values,
                               y1=df['PC2'].values,
                               label_radio=['tSNE','PCA'],
                               size=df['survival_months'].fillna(1).values / 10,
                               color=df['labx'].values,
                               tooltip=df['labx'].values + ' <br /> Survival: ' + df['survival_months'].astype(str).str[0:4].values,
                               scale=True)
        
        # Show the chart
        d3.show(showfig=False)
        
        # Set specific node properties.
        if d3.edge_properties is not None:
            d3.edge_properties.loc[0,'size']=50
            d3.edge_properties.loc[0,'color']='#000000'
            d3.edge_properties.loc[0,'tooltip']='I am adjusted!'
        
        # Show the chart again with adjustments
        d3.show(showfig=False)
        print("✅ Scatter advanced test completed")
        assert True
    except Exception as e:
        print(f"❌ Scatter advanced test failed: {e}")
        assert False

def test_chord():
    """Test chord functionality."""
    print("=== Testing Chord ===")
    try:
        from d3blocks import D3Blocks
        
        # Initialize
        d3 = D3Blocks()
        
        # Load example data
        df = d3.import_example('energy')
        assert df is not None
        
        # Plot
        d3.chord(df)
        print("✅ Chord test completed")
        assert True
    except Exception as e:
        print(f"❌ Chord test failed: {e}")
        assert False

def test_chord_advanced():
    """Test chord advanced functionality."""
    print("=== Testing Chord Advanced ===")
    try:
        from d3blocks import D3Blocks
        
        # Initialize
        d3 = D3Blocks(chart='Chord', frame=False)
        
        # Import example
        df = d3.import_example('energy')
        assert df is not None
        
        # Node properties
        d3.set_node_properties(df, opacity=0.2, cmap='tab20')
        d3.set_edge_properties(df, color='source', opacity='source')
        
        # Show the chart
        d3.show(showfig=False)
        
        # Make some edits to highlight the Nuclear node
        if d3.node_properties is not None and 'Nuclear' in d3.node_properties:
            d3.node_properties.get('Nuclear')['color']='#ff0000'
            d3.node_properties.get('Nuclear')['opacity']=1
        
        # Show the chart
        d3.show(showfig=False)
        
        # Make edits to highlight the Nuclear Edge
        if d3.edge_properties is not None:
            mask = (d3.edge_properties['source'] == 'Nuclear') & (d3.edge_properties['target'] == 'Thermal generation')
            d3.edge_properties.loc[mask, 'color'] = '#ff0000'
            d3.edge_properties.loc[mask, 'opacity'] = 0.8
            d3.edge_properties.loc[mask, 'weight'] = 1000
        
        # Show the chart
        d3.show(showfig=False)
        print("✅ Chord advanced test completed")
        assert True
    except Exception as e:
        print(f"❌ Chord advanced test failed: {e}")
        assert False

def test_chord_ordering():
    """Test chord with different ordering."""
    print("=== Testing Chord Ordering ===")
    try:
        from d3blocks import D3Blocks
        
        # Initialize
        d3 = D3Blocks()
        
        # Import example
        df = d3.import_example('energy')
        assert df is not None
        
        # Custom order of the labels
        d3.chord(df, ordering=np.sort(np.unique(df['source'].values)))
        
        # Sort Ascending
        d3.chord(df, ordering='ascending')
        
        # Sort Descending
        d3.chord(df, ordering='descending')
        
        # Do not sort
        d3.chord(df, ordering='')
        print("✅ Chord ordering test completed")
        assert True
    except Exception as e:
        print(f"❌ Chord ordering test failed: {e}")
        assert False

def test_imageslider():
    """Test imageslider functionality."""
    print("=== Testing Imageslider ===")
    try:
        from d3blocks import D3Blocks
        
        # Initialize
        d3 = D3Blocks()
        
        # Local images
        img_before, img_after = d3.import_example('southern_nebula')
        
        # Internet location
        img_before, img_after = d3.import_example('southern_nebula_internet')
        
        # Plot
        d3.imageslider(img_before, img_after)
        
        # Plot with custom settings
        d3.imageslider(img_before, img_after, showfig=False, scale=True, colorscale=2, figsize=[400, 400])
        print("✅ Imageslider test completed")
        assert True
    except Exception as e:
        print(f"❌ Imageslider test failed: {e}")
        assert False

def test_sankey():
    """Test sankey functionality."""
    print("=== Testing Sankey ===")
    try:
        from d3blocks import D3Blocks
        
        # Initialize
        d3 = D3Blocks()
        
        # Load example data
        df = d3.import_example('energy')
        assert df is not None
        
        # Plot
        d3.sankey(df)
        print("✅ Sankey test completed")
        assert True
    except Exception as e:
        print(f"❌ Sankey test failed: {e}")
        assert False

def test_sankey_advanced():
    """Test sankey advanced functionality."""
    print("=== Testing Sankey Advanced ===")
    try:
        from d3blocks import D3Blocks
        
        # Initialize
        d3 = D3Blocks(chart='Sankey', frame=True)
        
        # Import example
        df = d3.import_example('energy')
        assert df is not None
        
        # Node properties
        d3.set_node_properties(df)
        d3.set_edge_properties(df, color='target', opacity='target')
        
        # Show the chart
        d3.show(showfig=False)
        print("✅ Sankey advanced test completed")
        assert True
    except Exception as e:
        print(f"❌ Sankey advanced test failed: {e}")
        assert False

def test_sankey_custom_colors():
    """Test sankey with custom colors."""
    print("=== Testing Sankey Custom Colors ===")
    try:
        from d3blocks import D3Blocks
        
        # Initialize
        d3 = D3Blocks(chart='Sankey', frame=True)
        
        # Import example
        df = d3.import_example('energy')
        assert df is not None
        
        # Custom color the nodes
        html = d3.sankey(df.copy(), filepath='sankey.html', 
                        color={'Nuclear': '#FF0000', 'Wind':'#000000', 'Electricity grid':'#FF0000'})
        
        # Alternatively:
        d3 = D3Blocks(chart='Sankey', frame=True)
        df = d3.import_example('energy')
        d3.set_node_properties(df, color={'Nuclear': '#FF0000', 'Wind':'#FF0000', 'Electricity grid':'#7FFFD4', 'Bio-conversion':'#000000', 'Industry': '#000000'})
        d3.set_edge_properties(df, color='target', opacity='target')
        d3.show(filepath='sankey.html', showfig=False)
        print("✅ Sankey custom colors test completed")
        assert True
    except Exception as e:
        print(f"❌ Sankey custom colors test failed: {e}")
        assert False

def test_movingbubbles():
    """Test movingbubbles functionality."""
    print("=== Testing Movingbubbles ===")
    try:
        from d3blocks import D3Blocks
        
        # Initialize
        d3 = D3Blocks()
        
        # Load example data
        df = d3.import_example('random_time', n=10000, c=300, date_start="1-1-2000 00:10:05", date_stop="1-1-2000 23:59:59")
        assert df is not None
        
        # Plot
        d3.movingbubbles(df, speed={"stop": 100000, "slow": 1000, "medium": 200, "fast": 10}, filepath='movingbubbles.html')
        print("✅ Movingbubbles test completed")
        assert True
    except Exception as e:
        print(f"❌ Movingbubbles test failed: {e}")
        assert False

def test_movingbubbles_advanced():
    """Test movingbubbles advanced functionality."""
    print("=== Testing Movingbubbles Advanced ===")
    try:
        from d3blocks import D3Blocks
        
        # Initialize
        d3 = D3Blocks(chart='movingbubbles', frame=False)
        
        # Import example
        df = d3.import_example('random_time', n=1000, c=100, date_start="1-1-2000 00:10:05", date_stop="1-1-2000 23:59:59")
        assert df is not None
        
        # Coloring the states.
        d3.set_node_properties(df['state'])
        
        # Color the sleeping state black
        if d3.node_properties is not None and 'Sleeping' in d3.node_properties:
            d3.node_properties.get('Sleeping')['color']='#000000'
        
        d3.set_edge_properties(df)
        
        # Show
        d3.show(title='Movingbubbles with adjusted configurations', showfig=False)
        print("✅ Movingbubbles advanced test completed")
        assert True
    except Exception as e:
        print(f"❌ Movingbubbles advanced test failed: {e}")
        assert False

def test_movingbubbles_custom():
    """Test movingbubbles with custom colors and sizes."""
    print("=== Testing Movingbubbles Custom ===")
    try:
        import random
        from d3blocks import D3Blocks
        
        # Initialize
        d3 = D3Blocks(chart='movingbubbles')
        
        # Import example
        df = d3.import_example('random_time', n=10000, c=300, date_start="1-1-2000 00:10:05", date_stop="1-1-2000 23:59:59")
        assert df is not None
        
        # Specify the colors and node sizes for the specific sample_id or for demonstration, generated randomly
        size = {i: random.randint(2, 15) for i in range(1, 100)}
        color = {1: '#FF0000', 3: '#000FFF'}
        
        # Show
        d3.movingbubbles(df, color=color, size=size)
        print("✅ Movingbubbles custom test completed")
        assert True
    except Exception as e:
        print(f"❌ Movingbubbles custom test failed: {e}")
        assert False

def test_timeseries():
    """Test timeseries functionality."""
    print("=== Testing Timeseries ===")
    try:
        from d3blocks import D3Blocks
        
        # Initialize
        d3 = D3Blocks()
        
        # Import example
        df = d3.import_example('climate')
        assert df is not None
        
        # Show
        d3.timeseries(df, datetime='date', dt_format='%Y-%m-%d', fontsize=10, figsize=[850, 500])
        print("✅ Timeseries test completed")
        assert True
    except Exception as e:
        print(f"❌ Timeseries test failed: {e}")
        assert False

def test_timeseries_advanced():
    """Test timeseries advanced functionality."""
    print("=== Testing Timeseries Advanced ===")
    try:
        from d3blocks import D3Blocks
        
        # Initialize
        d3 = D3Blocks(chart='Timeseries', frame=False)
        
        # Import example
        df = d3.import_example('climate')
        assert df is not None
        
        # Node properties
        d3.set_node_properties(df.columns.values)
        if d3.node_properties is not None and 'wind_speed' in d3.node_properties:
            d3.node_properties.get('wind_speed')['color']='#000000'
        
        d3.set_edge_properties(df, datetime='date', dt_format='%Y-%m-%d')
        
        # Show
        d3.show(title='Timeseries with adjusted configurations', showfig=False)
        print("✅ Timeseries advanced test completed")
        assert True
    except Exception as e:
        print(f"❌ Timeseries advanced test failed: {e}")
        assert False

def test_heatmap():
    """Test heatmap functionality."""
    print("=== Testing Heatmap ===")
    try:
        from d3blocks import D3Blocks
        
        # Initialize
        d3 = D3Blocks()
        
        # Load example data
        df = d3.import_example('stormofswords')  # 'energy'
        assert df is not None
        
        # Plot
        d3.heatmap(df)
        print("✅ Heatmap test completed")
        assert True
    except Exception as e:
        print(f"❌ Heatmap test failed: {e}")
        assert False

def test_heatmap_cluster_params():
    """Test heatmap with cluster parameters."""
    print("=== Testing Heatmap Cluster Parameters ===")
    try:
        from d3blocks import D3Blocks
        
        # Initialize
        d3 = D3Blocks()
        
        # Load example data
        df = d3.import_example('energy')
        assert df is not None
        
        # Change cluster parameters
        d3.heatmap(df, cluster_params={'evaluate':'dbindex',
                                      'metric':'hamming',
                                      'linkage':'complete',
                                      'normalize': False,
                                      'min_clust': 3,
                                      'max_clust': 15})
        print("✅ Heatmap cluster parameters test completed")
        assert True
    except Exception as e:
        print(f"❌ Heatmap cluster parameters test failed: {e}")
        assert False

def test_heatmap_color_labels():
    """Test heatmap with color labels."""
    print("=== Testing Heatmap Color Labels ===")
    try:
        from d3blocks import D3Blocks
        
        # Initialize
        d3 = D3Blocks()
        
        # Load example data
        df = d3.import_example('bigbang')
        assert df is not None
        
        # Plot and color on label
        d3.heatmap(df, color=[1,1,1,2,2,2,3])
        
        # Plot and specify the hex color
        d3.heatmap(df, color=['#FFF000', '#FFF000', '#FFF000', '#000FFF' , '#000FFF', '#000FFF', '#000FFF'])
        print("✅ Heatmap color labels test completed")
        assert True
    except Exception as e:
        print(f"❌ Heatmap color labels test failed: {e}")
        assert False

def test_matrix():
    """Test matrix functionality."""
    print("=== Testing Matrix ===")
    try:
        from d3blocks import D3Blocks
        
        # Initialize
        d3 = D3Blocks()
        
        # Load example data
        df = pd.DataFrame(np.random.randint(0, 10, size=(6, 20)))
        
        # Plot
        d3.matrix(df)
        
        d3.matrix(df,
                  vmin=1,
                  fontsize=10,
                  title='D3blocks Matrix',
                  figsize=[600, 300],
                  cmap='interpolateGreens',
                  filepath='matrix.html')
        print("✅ Matrix test completed")
        return True
    except Exception as e:
        print(f"❌ Matrix test failed: {e}")
        return False

def test_d3graph():
    """Test d3graph functionality."""
    print("=== Testing D3graph ===")
    try:
        from d3blocks import D3Blocks
        
        # Initialize
        d3 = D3Blocks()
        
        # Import example
        df = d3.import_example('energy') # 'bigbang', 'stormofswords'
        
        # Create network using default
        d3.d3graph(df, filepath='d3graph.html')
        
        # Change scaler
        d3.d3graph(df, scaler='minmax')
        
        # Change node properties
        d3.D3graph.set_node_properties(color=None)
        d3.D3graph.node_properties['Solar']['size']=30
        d3.D3graph.node_properties['Solar']['color']='#FF0000'
        d3.D3graph.node_properties['Solar']['edge_color']='#000000'
        d3.D3graph.node_properties['Solar']['edge_size']=5
        d3.D3graph.show()
        
        # Change edge properties
        d3.D3graph.set_edge_properties(directed=True, marker_end='arrow')
        d3.D3graph.show()
        
        # After making changes, show the graph again using show()
        d3.D3graph.show()
        print("✅ D3graph test completed")
        return True
    except Exception as e:
        print(f"❌ D3graph test failed: {e}")
        return False

def test_elasticgraph():
    """Test elasticgraph functionality."""
    print("=== Testing Elasticgraph ===")
    try:
        from d3blocks import D3Blocks
        
        # Initialize
        d3 = D3Blocks()
        
        # Import example
        df = d3.import_example('energy') # 'stormofswords'
        
        # Create force-directed-network (without cluster labels)
        d3.elasticgraph(df, filepath='Elasticgraph.html')
        
        # Show elasticgraph
        d3.Elasticgraph.show()
        
        # Show original graph with the same properties
        d3.Elasticgraph.D3graph.show()
        
        # After making changes, show the graph again using show()
        d3.Elasticgraph.show()
        
        # Show original graph
        d3.Elasticgraph.D3graph.show()
        print("✅ Elasticgraph test completed")
        return True
    except Exception as e:
        print(f"❌ Elasticgraph test failed: {e}")
        return False

def test_tree():
    """Test tree functionality."""
    print("=== Testing Tree ===")
    try:
        from d3blocks import D3Blocks
        
        # Initialize
        d3 = D3Blocks()
        
        # Load example data
        df = d3.import_example('energy')
        
        # Plot
        d3.tree(df)
        print("✅ Tree test completed")
        return True
    except Exception as e:
        print(f"❌ Tree test failed: {e}")
        return False

def test_tree_advanced():
    """Test tree advanced functionality."""
    print("=== Testing Tree Advanced ===")
    try:
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
        d3.show(hierarchy=[1, 2, 3, 4, 5, 6, 7, 8], filepath='tree_hierarchy.html')
        print("✅ Tree advanced test completed")
        return True
    except Exception as e:
        print(f"❌ Tree advanced test failed: {e}")
        return False

def test_tree_frame():
    """Test tree with frame=True."""
    print("=== Testing Tree Frame ===")
    try:
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
        print("✅ Tree frame test completed")
        return True
    except Exception as e:
        print(f"❌ Tree frame test failed: {e}")
        return False

def test_treemap():
    """Test treemap functionality."""
    print("=== Testing Treemap ===")
    try:
        from d3blocks import D3Blocks
        
        # Initialize
        d3 = D3Blocks()
        
        # Load example data
        df = d3.import_example('energy')
        df = d3.import_example('animals')
        
        # Plot
        d3.treemap(df)
        print("✅ Treemap test completed")
        return True
    except Exception as e:
        print(f"❌ Treemap test failed: {e}")
        return False

def test_treemap_advanced():
    """Test treemap advanced functionality."""
    print("=== Testing Treemap Advanced ===")
    try:
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
        print("✅ Treemap advanced test completed")
        return True
    except Exception as e:
        print(f"❌ Treemap advanced test failed: {e}")
        return False

def test_treemap_tooltip():
    """Test treemap with tooltips."""
    print("=== Testing Treemap Tooltip ===")
    try:
        from d3blocks import D3Blocks
        
        # Initialize Treemap
        d3 = D3Blocks(chart='treemap', frame=False)
        
        # Import example
        df = d3.import_example('energy')
        
        # Set node properties
        d3.set_node_properties(df)
        
        # Set tooltip for specific nodes
        d3.node_properties['Bio-conversion']['tooltip'] = 'Title: Bio conversion Operations'
        d3.node_properties.get('Losses')['tooltip'] = 'losses tooltip'
        
        # Set edge properties
        d3.set_edge_properties(df)
        
        # Show chart
        d3.show(filepath='treemap_advanced.html')
        print("✅ Treemap tooltip test completed")
        return True
    except Exception as e:
        print(f"❌ Treemap tooltip test failed: {e}")
        return False

def test_circlepacking():
    """Test circlepacking functionality."""
    print("=== Testing Circlepacking ===")
    try:
        from d3blocks import D3Blocks
        
        # Initialize
        d3 = D3Blocks()
        
        # Load example data
        df = d3.import_example('animals')
        df = d3.import_example('energy')
        
        # Plot
        d3.circlepacking(df)
        print("✅ Circlepacking test completed")
        return True
    except Exception as e:
        print(f"❌ Circlepacking test failed: {e}")
        return False

def test_circlepacking_advanced():
    """Test circlepacking advanced functionality."""
    print("=== Testing Circlepacking Advanced ===")
    try:
        from d3blocks import D3Blocks
        
        # Initialize
        d3 = D3Blocks(chart='Circlepacking', frame=True)
        
        # Import example
        df = d3.import_example('energy')
        
        # Node properties
        d3.set_node_properties(df)
        d3.set_edge_properties(df)
        
        # Show the chart
        d3.show()
        print("✅ Circlepacking advanced test completed")
        return True
    except Exception as e:
        print(f"❌ Circlepacking advanced test failed: {e}")
        return False

def test_circlepacking_custom():
    """Test circlepacking with custom settings."""
    print("=== Testing Circlepacking Custom ===")
    try:
        from d3blocks import D3Blocks
        
        # Initialize
        d3 = D3Blocks()
        
        # Import example
        df = d3.import_example('energy')
        
        html = d3.circlepacking(df,
                                speed=1500,
                                zoom='mouseover',
                                filepath='circlepacking_advanced.html',
                                border={'color': '#FFFFFF', 'width': 1.5, 'fill': '#FFFFFF', "padding": 2},
                                overwrite=True)
        
        # Show the chart
        d3.show()
        print("✅ Circlepacking custom test completed")
        return True
    except Exception as e:
        print(f"❌ Circlepacking custom test failed: {e}")
        return False

def test_maps():
    """Test maps functionality."""
    print("=== Testing Maps ===")
    try:
        from d3blocks import D3Blocks
        
        # Initialize
        d3 = D3Blocks()
        
        # Load example data
        df = d3.import_example('surfspots')
        
        # Plot
        d3.maps(df)
        print("✅ Maps test completed")
        return True
    except Exception as e:
        print(f"❌ Maps test failed: {e}")
        return False

def test_maps_custom():
    """Test maps with custom colors."""
    print("=== Testing Maps Custom ===")
    try:
        from d3blocks import D3Blocks
        
        # Initialize
        d3 = D3Blocks()
        
        # Load example data
        df = d3.import_example('surfspots')
        
        # Plot
        d3.maps(df, color=df['label'].values, cmap='Set2')
        
        html = d3.maps(df, color=df['label'].values, 
                      countries = {'World': {'color':'#D3D3D3', 'opacity': 0.4, 'line': 'none', 'linewidth': 0.1},
                                  'Netherlands': {'color': '#000FFF', 'opacity': 0.5, 'line': 'none', 'linewidth': 1},
                                  'France': {'color': '#FFA500', 'opacity': 1, 'line': 'dashed', 'linewidth': 2},
                                  'Australia': {'color': '#008000', 'opacity': 0.3, 'line': 'dashed', 'linewidth': 5}})
        print("✅ Maps custom test completed")
        return True
    except Exception as e:
        print(f"❌ Maps custom test failed: {e}")
        return False

def test_maps_advanced():
    """Test maps advanced functionality."""
    print("=== Testing Maps Advanced ===")
    try:
        from d3blocks import D3Blocks
        
        # Initialize
        d3 = D3Blocks(chart='maps', frame=False)
        
        # Import example
        df = d3.import_example('surfspots', overwrite=True)
        
        # Set node properties
        d3.set_node_properties(df)
        
        # Set edge properties
        d3.set_edge_properties({'Australia': {'color': '#008000', 'opacity': 0.3, 'line': 'dashed', 'linewidth': 5},
                                'Netherlands': {'color': '#000FFF', 'line': 'dashed'}})
        
        # Show chart
        d3.show()
        print("✅ Maps advanced test completed")
        return True
    except Exception as e:
        print(f"❌ Maps advanced test failed: {e}")
        return False

def test_utility_functions():
    """Test utility functions."""
    print("=== Testing Utility Functions ===")
    try:
        from d3blocks import D3Blocks
        
        # Initialize
        d3 = D3Blocks()
        
        # Load example
        df = d3.import_example('energy')
        
        # Convert to adjmat
        adjmat = d3.vec2adjmat(df['source'], df['target'], df['weight'])
        
        # Convert back to vector
        vector = d3.adjmat2vec(adjmat)
        
        print("✅ Utility functions test completed")
        return True
    except Exception as e:
        print(f"❌ Utility functions test failed: {e}")
        return False

def run_all_tests():
    """Run all tests."""
    print("Starting comprehensive d3blocks testing...")
    print("=" * 50)
    
    tests = [
        test_particles,
        test_violin,
        test_violin_advanced,
        test_scatter,
        test_scatter_transitions,
        test_scatter_advanced,
        test_chord,
        test_chord_advanced,
        test_chord_ordering,
        test_imageslider,
        test_sankey,
        test_sankey_advanced,
        test_sankey_custom_colors,
        test_movingbubbles,
        test_movingbubbles_advanced,
        test_movingbubbles_custom,
        test_timeseries,
        test_timeseries_advanced,
        test_heatmap,
        test_heatmap_cluster_params,
        test_heatmap_color_labels,
        test_matrix,
        test_d3graph,
        test_elasticgraph,
        test_tree,
        test_tree_advanced,
        test_tree_frame,
        test_treemap,
        test_treemap_advanced,
        test_treemap_tooltip,
        test_circlepacking,
        test_circlepacking_advanced,
        test_circlepacking_custom,
        test_maps,
        test_maps_custom,
        test_maps_advanced,
        test_utility_functions
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append((test.__name__, result))
        except Exception as e:
            print(f"❌ {test.__name__} failed with exception: {e}")
            results.append((test.__name__, False))
    
    print("\n" + "=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed!")
    else:
        print(f"⚠️  {total - passed} tests failed")

if __name__ == "__main__":
    # You can run individual tests or all tests
    # For example:
    # test_particles()
    # test_violin()
    # etc.
    
    # Or run all tests:
    run_all_tests() 