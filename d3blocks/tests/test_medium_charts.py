import pytest
from d3blocks import D3Blocks

def test_d3graph_basic():
    """Test basic d3graph functionality."""
    print("=== Testing D3Graph Basic ===")
    print("📊 Initializing D3Blocks...")
    try:
        # Initialize
        d3 = D3Blocks()
        print("✅ D3Blocks initialized successfully")
        
        # Import example
        print("📥 Importing energy dataset...")
        df = d3.import_example('energy')
        print(f"✅ Energy dataset loaded successfully")
        
        # Create network using default
        print("🎨 Creating d3graph chart...")
        d3.d3graph(df, filepath='d3graph.html', color='cluster', showfig=False)
        print("✅ D3Graph chart created successfully")
        print("📁 Chart saved as 'd3graph.html'")
        assert True
    except Exception as e:
        print(f"❌ D3Graph basic test failed: {e}")
        print(f"🔍 Error details: {type(e).__name__}: {str(e)}")
        assert False

def test_d3graph_customization():
    """Test d3graph customization functionality."""
    print("=== Testing D3Graph Customization ===")
    print("📊 Initializing D3Blocks...")
    try:
        # Initialize
        d3 = D3Blocks()
        print("✅ D3Blocks initialized successfully")
        
        # Import example
        print("📥 Importing energy dataset...")
        df = d3.import_example('energy')
        print(f"✅ Energy dataset loaded successfully")
        
        # Create network using default
        print("🎨 Creating d3graph chart...")
        d3.d3graph(df, filepath='d3graph_custom.html', color='cluster', showfig=False)
        print("✅ D3Graph chart created successfully")
        
        # Node properties are stored here:
        print("🔧 Accessing node properties...")
        node_props = d3.D3graph.node_properties
        print(f"✅ Node properties accessed: {len(node_props) if node_props else 0} nodes")
        
        # Edge properties are stored here:
        print("🔧 Accessing edge properties...")
        edge_props = d3.D3graph.edge_properties
        print(f"✅ Edge properties accessed: {len(edge_props) if edge_props else 0} edges")

        # Change the node properties like this:
        print("🔧 Customizing node properties...")
        d3.D3graph.set_node_properties(color='cluster')
        if d3.D3graph.node_properties is not None and 'Solar' in d3.D3graph.node_properties:
            d3.D3graph.node_properties['Solar']['size']=30
            d3.D3graph.node_properties['Solar']['color']='#FF0000'
            d3.D3graph.node_properties['Solar']['edge_color']='#000000'
            d3.D3graph.node_properties['Solar']['edge_size']=5
            print("✅ Solar node properties customized")

        # After making changes, show the graph again using show()
        print("🎨 Showing updated graph...")
        d3.D3graph.show(showfig=False)
        print("✅ Updated graph displayed successfully")

        # Change edge properties like this:
        print("🔧 Customizing edge properties...")
        d3.D3graph.set_edge_properties(directed=True, marker_end='arrow')
        print("✅ Edge properties customized")

        # After making changes, show the graph again using show()
        print("🎨 Showing final graph...")
        d3.D3graph.show(showfig=False)
        print("✅ Final graph displayed successfully")
        print("📁 Chart saved as 'd3graph_custom.html'")
        assert True
    except Exception as e:
        print(f"❌ D3Graph customization test failed: {e}")
        print(f"🔍 Error details: {type(e).__name__}: {str(e)}")
        assert False

def test_elasticgraph():
    """Test elasticgraph functionality."""
    print("=== Testing ElasticGraph ===")
    print("📊 Initializing D3Blocks...")
    try:
        # Initialize
        d3 = D3Blocks()
        print("✅ D3Blocks initialized successfully")
        
        # Import example
        print("📥 Importing energy dataset...")
        df = d3.import_example('energy')
        print(f"✅ Energy dataset loaded successfully")
        
        # Create Chart
        print("🎨 Creating elasticgraph chart...")
        d3.elasticgraph(df, filepath='elastic.html')
        print("✅ ElasticGraph chart created successfully")
        print("📁 Chart saved as 'elastic.html'")
        assert True
    except Exception as e:
        print(f"❌ ElasticGraph test failed: {e}")
        print(f"🔍 Error details: {type(e).__name__}: {str(e)}")
        assert False

def test_sankey():
    """Test sankey functionality."""
    print("=== Testing Sankey ===")
    print("📊 Initializing D3Blocks...")
    try:
        # Initialize
        d3 = D3Blocks()
        print("✅ D3Blocks initialized successfully")
        
        # Import example
        print("📥 Importing energy dataset...")
        df = d3.import_example('energy')
        print(f"✅ Energy dataset loaded successfully")
        
        # Create Chart
        print("🎨 Creating sankey chart...")
        d3.sankey(df, filepath='sankey.html')
        print("✅ Sankey chart created successfully")
        print("📁 Chart saved as 'sankey.html'")
        assert True
    except Exception as e:
        print(f"❌ Sankey test failed: {e}")
        print(f"🔍 Error details: {type(e).__name__}: {str(e)}")
        assert False

def test_chord():
    """Test chord functionality."""
    print("=== Testing Chord ===")
    print("📊 Initializing D3Blocks...")
    try:
        # Initialize
        d3 = D3Blocks()
        print("✅ D3Blocks initialized successfully")
        
        # Import example
        print("📥 Importing energy dataset...")
        df = d3.import_example('energy')
        print(f"✅ Energy dataset loaded successfully")
        
        # Create Chart
        print("🎨 Creating chord chart...")
        d3.chord(df, filepath='chord.html')
        print("✅ Chord chart created successfully")
        print("📁 Chart saved as 'chord.html'")
        assert True
    except Exception as e:
        print(f"❌ Chord test failed: {e}")
        print(f"🔍 Error details: {type(e).__name__}: {str(e)}")
        assert False

def test_heatmap():
    """Test heatmap functionality."""
    print("=== Testing Heatmap ===")
    print("📊 Initializing D3Blocks...")
    try:
        # Initialize
        d3 = D3Blocks()
        print("✅ D3Blocks initialized successfully")

        # Import example
        print("📥 Importing stormofswords dataset...")
        df = d3.import_example('stormofswords')
        print(f"✅ Stormofswords dataset loaded successfully")

        # Create Chart
        print("🎨 Creating heatmap chart...")
        d3.heatmap(df, filepath='heatmap.html')
        print("✅ Heatmap chart created successfully")
        print("📁 Chart saved as 'heatmap.html'")
        assert True
    except Exception as e:
        print(f"❌ Heatmap test failed: {e}")
        print(f"🔍 Error details: {type(e).__name__}: {str(e)}")
        assert False

def test_tree():
    """Test tree functionality."""
    print("=== Testing Tree ===")
    print("📊 Initializing D3Blocks...")
    try:
        # Initialize
        d3 = D3Blocks()
        print("✅ D3Blocks initialized successfully")

        # Import example
        print("📥 Importing energy dataset...")
        df = d3.import_example('energy')
        print(f"✅ Energy dataset loaded successfully")

        # Create Chart
        if df is not None:
            print("🎨 Creating tree chart...")
            d3.tree(df, filepath='tree.html')
            print("✅ Tree chart created successfully")
            print("📁 Chart saved as 'tree.html'")
        else:
            print("⚠️ Dataset is None, skipping tree chart creation")
        assert True
    except Exception as e:
        print(f"❌ Tree test failed: {e}")
        print(f"🔍 Error details: {type(e).__name__}: {str(e)}")
        assert False

def test_treemap():
    """Test treemap functionality."""
    print("=== Testing Treemap ===")
    print("📊 Initializing D3Blocks...")
    try:
        # Initialize
        d3 = D3Blocks()
        print("✅ D3Blocks initialized successfully")

        # Import example
        print("📥 Importing energy dataset...")
        df = d3.import_example('energy')
        print(f"✅ Energy dataset loaded successfully")

        # Create Chart
        if df is not None:
            print("🎨 Creating treemap chart...")
            d3.treemap(df, filepath='treemap.html')
            print("✅ Treemap chart created successfully")
            print("📁 Chart saved as 'treemap.html'")
        else:
            print("⚠️ Dataset is None, skipping treemap chart creation")
        assert True
    except Exception as e:
        print(f"❌ Treemap test failed: {e}")
        print(f"🔍 Error details: {type(e).__name__}: {str(e)}")
        assert False

def test_circlepacking():
    """Test circlepacking functionality."""
    print("=== Testing Circlepacking ===")
    print("📊 Initializing D3Blocks...")
    try:
        # Initialize
        d3 = D3Blocks()
        print("✅ D3Blocks initialized successfully")

        # Import example
        print("📥 Importing energy dataset...")
        df = d3.import_example('energy')
        print(f"✅ Energy dataset loaded successfully")

        # Create Chart
        print("🎨 Creating circlepacking chart...")
        d3.circlepacking(df, filepath='circlepacking.html')
        print("✅ Circlepacking chart created successfully")
        print("📁 Chart saved as 'circlepacking.html'")
        assert True
    except Exception as e:
        print(f"❌ Circlepacking test failed: {e}")
        print(f"🔍 Error details: {type(e).__name__}: {str(e)}")
        assert False

def test_timeseries():
    """Test timeseries functionality."""
    print("=== Testing Timeseries ===")
    print("📊 Initializing D3Blocks...")
    try:
        # Initialize
        d3 = D3Blocks()
        print("✅ D3Blocks initialized successfully")

        # Import example
        print("📥 Importing climate dataset...")
        df = d3.import_example('climate')
        print(f"✅ Climate dataset loaded successfully")

        # Create Chart
        print("🎨 Creating timeseries chart...")
        d3.timeseries(df, datetime='date', dt_format='%Y-%m-%d', fontsize=10, figsize=[850, 500])
        print("✅ Timeseries chart created successfully")
        assert True
    except Exception as e:
        print(f"❌ Timeseries test failed: {e}")
        print(f"🔍 Error details: {type(e).__name__}: {str(e)}")
        assert False

def test_movingbubbles():
    """Test movingbubbles functionality."""
    print("=== Testing MovingBubbles ===")
    print("📊 Initializing D3Blocks...")
    try:
        # Initialize
        d3 = D3Blocks(chart='movingbubbles')
        print("✅ D3Blocks initialized successfully")

        # Import example
        print("📥 Importing random time dataset...")
        df = d3.import_example('random_time', n=10000, c=300, date_start="1-1-2000 00:10:05", date_stop="1-1-2000 23:59:59")
        print(f"✅ Random time dataset loaded successfully")

        # Customize states with color and size:
        print("🔧 Setting up customization parameters...")
        import random
        color = {1: '#FF0000', 3: '#000FFF'}
        size = {i: random.randint(5, 20) for i in range(1, 50)}
        print(f"✅ Customization parameters prepared: {len(color)} colors, {len(size)} sizes")

        print("🎨 Creating movingbubbles chart...")
        d3.movingbubbles(df, color=color, size=size, figsize=[775, 800])
        print("✅ MovingBubbles chart created successfully")
        assert True
    except Exception as e:
        print(f"❌ MovingBubbles test failed: {e}")
        print(f"🔍 Error details: {type(e).__name__}: {str(e)}")
        assert False

def test_cancer_dataset():
    """Test cancer dataset functionality."""
    print("=== Testing Cancer Dataset ===")
    print("📊 Initializing D3Blocks...")
    try:
        # Initialize
        d3 = D3Blocks()
        print("✅ D3Blocks initialized successfully")

        # Load example data
        print("📥 Loading cancer dataset...")
        df = d3.import_example('cancer')
        print(f"✅ Cancer dataset loaded successfully")
        assert True
    except Exception as e:
        print(f"❌ Cancer dataset test failed: {e}")
        print(f"🔍 Error details: {type(e).__name__}: {str(e)}")
        assert False
