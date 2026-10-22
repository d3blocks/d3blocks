# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Setup

To work with this codebase, you'll need to:

1. Install dependencies: `pip install -r requirements.txt` or `pip install -e .`
2. Run tests: `pytest` or `python -m pytest`
3. Build documentation: `make docs` (if applicable)
4. Lint code: `flake8` or `pylint`

## Common Commands

- `python -m pytest tests/` - Run all tests
- `python -m pytest tests/test_something.py::test_function` - Run a specific test
- `python -c "from d3blocks import D3Blocks; d3 = D3Blocks(); df = d3.import_example('energy'); d3.treemap(df)"` - Quick test example

## Code Architecture

The d3blocks library is organized as:

1. **Main module** (`d3blocks.py`) - Contains the core `D3Blocks` class and all charting methods
2. **Chart implementations** - Individual chart types are implemented in separate classes (e.g., Radialgraph, Chord, etc.)
3. **Utilities** (`utils.py`) - Helper functions for data processing, JSON serialization, etc.
4. **Data handling** - Example datasets are available via `import_example()` method
5. **Configuration management** - Chart-specific configuration and properties

The library provides a unified interface for creating various D3.js visualizations with a consistent API.

## Key Components

### Main Class: `D3Blocks`
- Provides the primary interface for all chart types
- Handles configuration, data processing, and HTML generation
- Manages node and edge properties for charts
- Contains chart-specific methods (treemap, chord, etc.)

### Chart Types
- RadialGraph, Chord, Sankey, Timeseries, Violin, Movingbubbles, Scatter, Heatmap, Matrix, Treemap, Tree, Circlepacking, Maps
- Each chart type has its own implementation class with specific parameters and rendering logic

### Data Processing
- Uses `utils.pre_processing()` for data conversion to Python types
- Handles node and edge property setting via `set_node_properties()` and `set_edge_properties()`
- Provides example datasets through `import_example()` method

### Key Methods
- `treemap(df)`, `chord(df)`, etc. - Main charting methods
- `set_node_properties(df)` - Set node properties for charts
- `set_edge_properties(df)` - Set edge/relationship properties
- `show()` - Display the chart in browser or return HTML
- `import_example(data)` - Load example datasets

### Example Usage Pattern
```python
from d3blocks import D3Blocks

# Initialize with chart type
d3 = D3Blocks(chart='Treemap')

# Load data
df = d3.import_example('energy')

# Set properties
d3.set_node_properties(df)
d3.set_edge_properties(df)

# Show chart
d3.show()
```

## Testing Strategy

Tests are located in the `tests/` directory and cover:
- Core functionality of all chart types
- Data processing and conversion
- Configuration handling
- Example dataset loading