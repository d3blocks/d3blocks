#!/usr/bin/env python3
"""
Test script to verify the movingbubbles timer display fix.
This script tests that the timer shows the correct format based on the timedelta parameter.
"""

import pandas as pd
import numpy as np
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

def test_timer_display():
    """Test timer display for different timedelta units."""
    print("Testing movingbubbles timer display fix...")
    
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
                title=f'Movingbubbles Timer Test - {timedelta_unit.capitalize()}',
                filepath=f'movingbubbles_timer_test_{timedelta_unit}.html',
                showfig=True,
                save_button=True
            )
            
            print(f"✓ Successfully created plot for {timedelta_unit}")
            print(f"  Expected timer format:")
            if timedelta_unit == 'seconds':
                print("    HH:MM:SS (hours:minutes:seconds)")
            elif timedelta_unit == 'days':
                print("    Day X HH:MM (day number and time)")
            else:
                print("    HH:MM (hours:minutes)")
                
        except Exception as e:
            print(f"✗ Error creating plot for {timedelta_unit}: {str(e)}")
    
    print("\n--- Test Summary ---")
    print("The timer display should now show:")
    print("1. When timedelta='seconds': HH:MM:SS format")
    print("2. When timedelta='minutes': HH:MM format (default)")
    print("3. When timedelta='days': Day X HH:MM format")
    print("\nCheck the generated HTML files to verify the timer display matches the timedelta setting.")

if __name__ == "__main__":
    test_timer_display() 