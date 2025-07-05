#!/usr/bin/env python3
"""
Test script to verify the movingbubbles day-step functionality.
This script tests that the day-step button allows stepping through the animation one day at a time.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from d3blocks import D3Blocks

def create_test_data_with_days():
    """Create test data with day-level intervals."""
    # Create sample data with day-level intervals
    data = []
    base_time = datetime(2023, 1, 1, 0, 0, 0)
    
    # Create data with day intervals
    intervals = [1, 2, 3, 5, 7]  # days
    
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
        current_time += timedelta(days=interval)
        data.append({
            'datetime': current_time,
            'sample_id': sample_id,
            'state': 'Travel'
        })
        
        # Add end state
        current_time += timedelta(days=interval//2)
        data.append({
            'datetime': current_time,
            'sample_id': sample_id,
            'state': 'Work'
        })
        
        sample_id += 1
    
    return pd.DataFrame(data)

def create_multi_day_movements():
    """Create test data with multi-day movements that span several days."""
    data = []
    base_time = datetime(2023, 1, 1, 0, 0, 0)
    
    # Create multiple samples with different day-long activities
    samples = [
        # Sample 0: Business trip pattern
        {
            'Home': 3,      # 3 days at home
            'Travel': 1,    # 1 day traveling
            'Work': 5,      # 5 days at work
            'Travel': 1,    # 1 day traveling back
            'Home': 2       # 2 days at home
        },
        # Sample 1: Vacation pattern
        {
            'Home': 2,      # 2 days at home
            'Travel': 2,    # 2 days traveling
            'Leisure': 7,   # 7 days vacation
            'Travel': 2,    # 2 days traveling back
            'Home': 3       # 3 days at home
        },
        # Sample 2: Conference pattern
        {
            'Home': 1,      # 1 day at home
            'Travel': 1,    # 1 day traveling
            'Work': 3,      # 3 days at conference
            'Travel': 1,    # 1 day traveling back
            'Home': 4       # 4 days at home
        },
        # Sample 3: Extended work pattern
        {
            'Home': 1,      # 1 day at home
            'Work': 10,     # 10 days at work
            'Home': 1       # 1 day at home
        },
        # Sample 4: Short trip pattern
        {
            'Home': 5,      # 5 days at home
            'Travel': 1,    # 1 day traveling
            'Work': 2,      # 2 days at work
            'Travel': 1,    # 1 day traveling back
            'Home': 3       # 3 days at home
        }
    ]
    
    for sample_id, activities in enumerate(samples):
        current_time = base_time + timedelta(days=sample_id * 2)  # Stagger start times
        
        for state, duration in activities.items():
            # Add the state entry
            data.append({
                'datetime': current_time,
                'sample_id': sample_id,
                'state': state
            })
            
            # Move to next state
            current_time += timedelta(days=duration)
    
    return pd.DataFrame(data)

def test_daystep_functionality():
    """Test day-step functionality."""
    print("Testing movingbubbles day-step functionality...")
    
    # Create test data with multi-day movements
    df = create_multi_day_movements()
    print(f"Created test data with {len(df)} rows")
    print(f"Time range: {df['datetime'].min()} to {df['datetime'].max()}")
    print(f"Total time span: {(df['datetime'].max() - df['datetime'].min()).days} days")
    
    # Show the data structure
    print("\n--- Data Preview ---")
    for sample_id in df['sample_id'].unique():
        sample_data = df[df['sample_id'] == sample_id]
        print(f"Sample {sample_id}: {len(sample_data)} states")
        for _, row in sample_data.iterrows():
            dt = pd.to_datetime(row['datetime'])
            print(f"  {row['state']} at {dt.strftime('%Y-%m-%d')}")
    
    # Initialize d3blocks
    d3 = D3Blocks()
    
    try:
        # Create the movingbubbles plot
        d3.movingbubbles(
            df,
            datetime='datetime',
            sample_id='sample_id',
            state='state',
            timedelta='days',
            standardize='samplewise',
            title='Movingbubbles Multi-Day Movements Test',
            filepath='movingbubbles_multiday_test.html',
            showfig=True,
            save_button=True
        )
        
        print("\n✓ Successfully created plot with day-step functionality")
        print("\n--- Day-Step Instructions ---")
        print("1. Open the generated HTML file")
        print("2. Click the 'Day-Step' button to advance one day at a time")
        print("3. Each click will advance the animation by exactly one day")
        print("4. The timer will show 'Day X HH:MM' format")
        print("5. You can switch back to other speeds (Slow/Medium/Fast) for continuous animation")
        print("\n--- Expected Behavior ---")
        print("• Day 1-3: Sample 0 at Home, others at various states")
        print("• Day 4: Sample 0 starts Travel, others continue")
        print("• Day 5: Sample 0 arrives at Work, Sample 1 starts Travel")
        print("• Day 6-7: More samples start their journeys")
        print("• Continue clicking to see the full multi-day patterns")
        
    except Exception as e:
        print(f"✗ Error creating plot: {str(e)}")
    
    print("\n--- Test Summary ---")
    print("The day-step functionality should:")
    print("1. Add a 'Day-Step' button to the speed controls")
    print("2. Allow manual advancement by one day per click")
    print("3. Stop automatic animation when day-step is selected")
    print("4. Display time in 'Day X HH:MM' format")
    print("5. Update node positions and percentages correctly")
    print("6. Show meaningful day-by-day progression of multi-day activities")

if __name__ == "__main__":
    test_daystep_functionality() 