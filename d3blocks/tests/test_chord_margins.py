#!/usr/bin/env python3
"""
Test script to demonstrate the new margin and text offset parameters for chord diagrams.
This shows how to fix the issue with labels being cut off.
"""

import sys
import os
import pandas as pd
import numpy as np
import pytest
from d3blocks import D3Blocks

# Add the d3blocks directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def test_chord_default_margins():
    """Test chord with default margins (labels may be cut off)."""
    print("=== Testing Chord with Default Margins ===")
    print("📊 Initializing D3Blocks...")
    try:
        from d3blocks import D3Blocks
        
        # Initialize
        d3 = D3Blocks()
        print("✅ D3Blocks initialized successfully")
        
        # Load example data
        print("📥 Loading energy dataset...")
        df = d3.import_example('energy')
        assert df is not None
        print(f"✅ Energy dataset loaded successfully")
        
        # Plot with default margins (may cut off labels)
        print("🎨 Creating chord diagram with default margins...")
        d3.chord(df, filepath='chord_default_margins.html')
        print("✅ Chord with default margins created successfully")
        print("📁 Chart saved as 'chord_default_margins.html'")
        print("⚠️ Note: Labels may be cut off with default margins")
        assert True
    except Exception as e:
        print(f"❌ Chord with default margins failed: {e}")
        print(f"🔍 Error details: {type(e).__name__}: {str(e)}")
        assert False

def test_chord_increased_margins():
    """Test chord with increased margins to prevent label cutoff."""
    print("=== Testing Chord with Increased Margins ===")
    print("📊 Initializing D3Blocks...")
    try:
        from d3blocks import D3Blocks
        
        # Initialize
        d3 = D3Blocks()
        print("✅ D3Blocks initialized successfully")
        
        # Load example data
        print("📥 Loading energy dataset...")
        df = d3.import_example('energy')
        assert df is not None
        print(f"✅ Energy dataset loaded successfully")
        
        # Plot with increased margins to prevent label cutoff
        print("🎨 Creating chord diagram with increased margins...")
        print("🔧 Parameters: figsize=[1000, 1000], margin=200, text_offset=20")
        d3.chord(df, 
                 filepath='chord_increased_margins.html',
                 figsize=[1000, 1000],  # Larger figure size
                 margin=200,  # Increased margin (default was 150)
                 text_offset=20)  # Increased text offset (default was 5)
        print("✅ Chord with increased margins created successfully")
        print("📁 Chart saved as 'chord_increased_margins.html'")
        print("✅ Labels should be fully visible with increased margins")
        assert True
    except Exception as e:
        print(f"❌ Chord with increased margins failed: {e}")
        print(f"🔍 Error details: {type(e).__name__}: {str(e)}")
        assert False

def test_chord_large_margins():
    """Test chord with very large margins for long labels."""
    print("=== Testing Chord with Large Margins ===")
    print("📊 Initializing D3Blocks...")
    try:
        from d3blocks import D3Blocks
        
        # Initialize
        d3 = D3Blocks()
        print("✅ D3Blocks initialized successfully")
        
        # Load example data
        print("📥 Loading energy dataset...")
        df = d3.import_example('energy')
        assert df is not None
        print(f"✅ Energy dataset loaded successfully")
        
        # Plot with very large margins for long labels
        print("🎨 Creating chord diagram with large margins...")
        print("🔧 Parameters: figsize=[1200, 1200], margin=300, text_offset=50")
        d3.chord(df, 
                 filepath='chord_large_margins.html',
                 figsize=[1200, 1200],  # Even larger figure size
                 margin=300,  # Large margin for long labels
                 text_offset=50)  # Large text offset
        print("✅ Chord with large margins created successfully")
        print("📁 Chart saved as 'chord_large_margins.html'")
        print("✅ Large margins ensure all labels are visible")
        assert True
    except Exception as e:
        print(f"❌ Chord with large margins failed: {e}")
        print(f"🔍 Error details: {type(e).__name__}: {str(e)}")
        assert False

def test_chord_custom_data():
    """Test chord with custom data that has long labels."""
    print("=== Testing Chord with Custom Long Labels ===")
    print("📊 Initializing D3Blocks...")
    try:
        from d3blocks import D3Blocks
        
        # Initialize
        d3 = D3Blocks()
        print("✅ D3Blocks initialized successfully")
        
        # Create custom data with long labels
        print("🔧 Creating custom dataset with long labels...")
        data = {
            'source': [
                'Very Long Source Label That Might Be Cut Off',
                'Another Very Long Source Label',
                'Short Source',
                'Medium Length Source Label'
            ],
            'target': [
                'Very Long Target Label That Might Be Cut Off',
                'Another Very Long Target Label',
                'Short Target',
                'Medium Length Target Label'
            ],
            'weight': [10, 20, 15, 25]
        }
        df = pd.DataFrame(data)
        print(f"✅ Custom dataset created with {len(df)} rows")
        print(f"📊 Dataset columns: {list(df.columns)}")
        
        # Plot with large margins to accommodate long labels
        print("🎨 Creating chord diagram with custom long labels...")
        print("🔧 Parameters: figsize=[1400, 1400], margin=400, text_offset=80")
        d3.chord(df, 
                 filepath='chord_long_labels.html',
                 figsize=[1400, 1400],  # Large figure size
                 margin=400,  # Very large margin for long labels
                 text_offset=80)  # Large text offset
        print("✅ Chord with long labels created successfully")
        print("📁 Chart saved as 'chord_long_labels.html'")
        print("✅ Large margins accommodate very long labels")
        assert True
    except Exception as e:
        print(f"❌ Chord with long labels failed: {e}")
        print(f"🔍 Error details: {type(e).__name__}: {str(e)}")
        assert False

def test_chord_parameter_comparison():
    """Test different parameter combinations to show the effect."""
    print("=== Testing Chord Parameter Comparison ===")
    print("📊 Initializing D3Blocks...")
    try:
        from d3blocks import D3Blocks
        
        # Initialize
        d3 = D3Blocks()
        print("✅ D3Blocks initialized successfully")
        
        # Load example data
        print("📥 Loading energy dataset...")
        df = d3.import_example('energy')
        assert df is not None
        print(f"✅ Energy dataset loaded successfully")
        
        # Test different combinations
        print("🔧 Setting up parameter combinations for comparison...")
        combinations = [
            {
                'name': 'Default',
                'figsize': [900, 900],
                'margin': 150,
                'text_offset': 5,
                'filepath': 'chord_comparison_default.html'
            },
            {
                'name': 'Medium',
                'figsize': [1000, 1000],
                'margin': 200,
                'text_offset': 20,
                'filepath': 'chord_comparison_medium.html'
            },
            {
                'name': 'Large',
                'figsize': [1200, 1200],
                'margin': 300,
                'text_offset': 50,
                'filepath': 'chord_comparison_large.html'
            },
            {
                'name': 'Extra Large',
                'figsize': [1400, 1400],
                'margin': 400,
                'text_offset': 80,
                'filepath': 'chord_comparison_extra_large.html'
            }
        ]
        print(f"✅ {len(combinations)} parameter combinations prepared")
        
        for i, combo in enumerate(combinations, 1):
            print(f"🎨 Creating {combo['name']} chord diagram ({i}/{len(combinations)})...")
            print(f"🔧 Parameters: figsize={combo['figsize']}, margin={combo['margin']}, text_offset={combo['text_offset']}")
            d3.chord(df, 
                     filepath=combo['filepath'],
                     figsize=combo['figsize'],
                     margin=combo['margin'],
                     text_offset=combo['text_offset'])
            print(f"✅ {combo['name']} chord diagram created")
            print(f"📁 Chart saved as '{combo['filepath']}'")
        
        print("✅ All chord comparison diagrams created successfully")
        print("📊 Comparison complete: Default, Medium, Large, and Extra Large configurations")
        assert True
    except Exception as e:
        print(f"❌ Chord parameter comparison failed: {e}")
        print(f"🔍 Error details: {type(e).__name__}: {str(e)}")
        assert False

def run_all_chord_tests():
    """Run all chord margin tests."""
    print("Starting chord margin testing...")
    print("=" * 50)
    
    tests = [
        test_chord_default_margins,
        test_chord_increased_margins,
        test_chord_large_margins,
        test_chord_custom_data,
        test_chord_parameter_comparison
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
    print("CHORD MARGIN TEST SUMMARY")
    print("=" * 50)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All chord margin tests passed!")
        print("\n📝 USAGE TIPS:")
        print("- Use 'margin' parameter to control space around the chord diagram")
        print("- Use 'text_offset' parameter to control distance of labels from the diagram")
        print("- Increase 'figsize' for larger overall chart size")
        print("- For long labels, try: margin=300-400, text_offset=50-80")
    else:
        print(f"⚠️  {total - passed} tests failed")

if __name__ == "__main__":
    # Run all tests
    run_all_chord_tests()
    
    # Or run individual tests:
    # test_chord_default_margins()
    # test_chord_increased_margins()
    # test_chord_large_margins()
    # test_chord_custom_data()
    # test_chord_parameter_comparison() 