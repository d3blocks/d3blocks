#!/usr/bin/env python3
"""
Test script to demonstrate the new margin and text offset parameters for chord diagrams.
This shows how to fix the issue with labels being cut off.
"""

import sys
import os
import pandas as pd
import numpy as np

# Add the d3blocks directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'd3blocks'))

def test_chord_default_margins():
    """Test chord with default margins (labels may be cut off)."""
    print("=== Testing Chord with Default Margins ===")
    try:
        from d3blocks import D3Blocks
        
        # Initialize
        d3 = D3Blocks()
        
        # Load example data
        df = d3.import_example('energy')
        
        # Plot with default margins (may cut off labels)
        d3.chord(df, filepath='chord_default_margins.html')
        print("✅ Chord with default margins created")
        return True
    except Exception as e:
        print(f"❌ Chord with default margins failed: {e}")
        return False

def test_chord_increased_margins():
    """Test chord with increased margins to prevent label cutoff."""
    print("=== Testing Chord with Increased Margins ===")
    try:
        from d3blocks import D3Blocks
        
        # Initialize
        d3 = D3Blocks()
        
        # Load example data
        df = d3.import_example('energy')
        
        # Plot with increased margins to prevent label cutoff
        d3.chord(df, 
                 filepath='chord_increased_margins.html',
                 figsize=[1000, 1000],  # Larger figure size
                 margin=200,  # Increased margin (default was 150)
                 text_offset=20)  # Increased text offset (default was 5)
        print("✅ Chord with increased margins created")
        return True
    except Exception as e:
        print(f"❌ Chord with increased margins failed: {e}")
        return False

def test_chord_large_margins():
    """Test chord with very large margins for long labels."""
    print("=== Testing Chord with Large Margins ===")
    try:
        from d3blocks import D3Blocks
        
        # Initialize
        d3 = D3Blocks()
        
        # Load example data
        df = d3.import_example('energy')
        
        # Plot with very large margins for long labels
        d3.chord(df, 
                 filepath='chord_large_margins.html',
                 figsize=[1200, 1200],  # Even larger figure size
                 margin=300,  # Large margin for long labels
                 text_offset=50)  # Large text offset
        print("✅ Chord with large margins created")
        return True
    except Exception as e:
        print(f"❌ Chord with large margins failed: {e}")
        return False

def test_chord_custom_data():
    """Test chord with custom data that has long labels."""
    print("=== Testing Chord with Custom Long Labels ===")
    try:
        from d3blocks import D3Blocks
        
        # Initialize
        d3 = D3Blocks()
        
        # Create custom data with long labels
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
        
        # Plot with large margins to accommodate long labels
        d3.chord(df, 
                 filepath='chord_long_labels.html',
                 figsize=[1400, 1400],  # Large figure size
                 margin=400,  # Very large margin for long labels
                 text_offset=80)  # Large text offset
        print("✅ Chord with long labels created")
        return True
    except Exception as e:
        print(f"❌ Chord with long labels failed: {e}")
        return False

def test_chord_parameter_comparison():
    """Test different parameter combinations to show the effect."""
    print("=== Testing Chord Parameter Comparison ===")
    try:
        from d3blocks import D3Blocks
        
        # Initialize
        d3 = D3Blocks()
        
        # Load example data
        df = d3.import_example('energy')
        
        # Test different combinations
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
        
        for combo in combinations:
            print(f"Creating {combo['name']} chord diagram...")
            d3.chord(df, 
                     filepath=combo['filepath'],
                     figsize=combo['figsize'],
                     margin=combo['margin'],
                     text_offset=combo['text_offset'])
        
        print("✅ All chord comparison diagrams created")
        return True
    except Exception as e:
        print(f"❌ Chord parameter comparison failed: {e}")
        return False

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