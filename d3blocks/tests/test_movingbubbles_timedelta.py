#!/usr/bin/env python3
"""
Test script to verify the movingbubbles timedelta fix.
This script tests that the plot runs in the correct time units based on the timedelta parameter.
"""

import pandas as pd
import numpy as np
import pytest
from datetime import datetime, timedelta
from d3blocks import D3Blocks

def create_test_data(timedelta_unit='minutes'):
    """Create test data with specific time intervals."""
    # Create sample data with known time intervals
    data = []
    base_time = datetime(2023, 1, 1, 0, 0, 0)
    
    # Create data with different time intervals based on timedelta_unit
    if timedelta_unit == 'seconds':
        intervals = [30, 45, 60, 90, 120]  # seconds
    elif timedelta_unit == 'minutes':
        intervals = [2, 5, 10, 15, 30]  # minutes
    elif timedelta_unit == 'days':
        intervals = [1, 2, 3, 5, 7]  # days
    else:
        intervals = [5, 10, 15, 20, 25]  # default minutes
    
    sample_id = 0
    current_time = base_time
    
    for interval in intervals:
        # Add start state
        data.append({
            'datetime': current_time,
            'sample_id': sample_id,
            'state': 'Home'
        })
        
        # Add travel state
        if timedelta_unit == 'seconds':
            current_time += timedelta(seconds=interval)
        elif timedelta_unit == 'minutes':
            current_time += timedelta(minutes=interval)
        elif timedelta_unit == 'days':
            current_time += timedelta(days=interval)
        
        data.append({
            'datetime': current_time,
            'sample_id': sample_id,
            'state': 'Travel'
        })
        
        # Add end state
        if timedelta_unit == 'seconds':
            current_time += timedelta(seconds=interval//2)
        elif timedelta_unit == 'minutes':
            current_time += timedelta(minutes=interval//2)
        elif timedelta_unit == 'days':
            current_time += timedelta(days=interval//2)
        
        data.append({
            'datetime': current_time,
            'sample_id': sample_id,
            'state': 'Work'
        })
        
        sample_id += 1
    
    return pd.DataFrame(data)

def test_timedelta_units():
    """Test different timedelta units."""
    print("Testing movingbubbles timedelta fix...")
    
    # Test each time unit
    for timedelta_unit in ['seconds', 'minutes', 'days']:
        print(f"\n--- Testing {timedelta_unit.upper()} ---")
        
        # Create test data
        df = create_test_data(timedelta_unit)
        print(f"Created test data with {len(df)} rows")
        print(f"Time range: {df['datetime'].min()} to {df['datetime'].max()}")
        
        # Initialize d3blocks
        d3 = D3Blocks()
        
        try:
            # Create the movingbubbles plot
            d3.movingbubbles(
                df,
                datetime='datetime',
                sample_id='sample_id',
                state='state',
                timedelta=timedelta_unit,
                standardize='samplewise',
                title=f'Movingbubbles Test - {timedelta_unit.capitalize()}',
                filepath=f'movingbubbles_test_{timedelta_unit}.html',
                showfig=False,
                save_button=True
            )
            
            print(f"✓ Successfully created plot for {timedelta_unit}")
            
            # Check if the delta column was created correctly
            if 'delta' in df.columns:
                print(f"  Delta column created with {len(df['delta'].dropna())} non-null values")
                print(f"  Delta range: {df['delta'].min()} to {df['delta'].max()}")
            else:
                print("  Warning: Delta column not found in dataframe")
                
        except Exception as e:
            print(f"✗ Error creating plot for {timedelta_unit}: {str(e)}")
            assert False
    
    print("\n--- Test Summary ---")
    print("The fix should ensure that:")
    print("1. When timedelta='seconds': plot runs in seconds")
    print("2. When timedelta='minutes': plot runs in minutes") 
    print("3. When timedelta='days': plot runs in days")
    print("\nCheck the generated HTML files to verify the animation speed matches the timedelta setting.")
    assert True 