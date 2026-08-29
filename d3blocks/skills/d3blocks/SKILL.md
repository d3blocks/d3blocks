---
name: d3blocks
description: Use this skill when users want to create data visualizations using D3Blocks from a pandas DataFrame. This skill helps users create scatterplots, sankey diagrams, network graphs, chord diagrams, heatmaps, treemaps, circle packing, tree diagrams, moving bubbles, time series, violin plots, particles, maps, and
other D3Blocks visualizations. Trigger when users mention having a dataframe/data and wanting to create specific visualizations like scatter plots, sankey diagrams, network analysis, etc. The skill guides users through selecting the appropriate visualization type, configuring parameters, and generating interactive HTML outputs.
---

# D3Blocks

D3Blocks is a Python library for creating interactive visualizations
using D3.js. It provides high-level Python APIs for visualizing
networks, scatter plots, heatmaps, treemaps, timelines, and other
data structures.

## When to use D3Blocks

Use D3Blocks when the user wants to:

- Create an interactive visualization from Python data.
- Explore relationships between data points.
- Visualize networks or graphs.
- Create interactive scatter plots.
- Create heatmaps or clustered visualizations.
- Export or embed D3 visualizations.
- Customize an existing D3Blocks visualization.
- Add interactivity to a visualization.


## Choosing a visualization

When the user asks about networks or relationships between entities, prefer `d3graph`.
When the user asks about networks or relationships but entities are hierarchical, prefer `radialgraph`.
When the user asks about automatic clustering of networks or relationships between entities, prefer `elasticgraph`.
When the user wants to understand the relationship between two continuous variables, prefer `scatter`.
When the user wants to compare values across two categorical dimensions, prefer `heatmap`.
When the user wants to visualize relationships between multiple categories in a circular layout, prefer `chord`.
When the user wants to visualize hierarchical data as nested circles, prefer `circlepacking`.
When the user wants to interactively compare or browse multiple images, prefer `imageslider`.
When the user wants to visualize data geographically or on a map, prefer `maps`.
When the user wants to visualize relationships or values between rows and columns as a matrix, prefer `matrix`.
When the user wants to visualize changing values or entities as animated bubbles over time, prefer `movingbubbles`.
When the user wants to visualize particles, movement, or dynamic particle-based patterns, prefer `particles`.
When the user wants to visualize flows between different entities, stages, or categories, prefer `sankey`.
When the user wants to visualize how one or more variables change over time, prefer `timeseries`.
When the user wants to visualize hierarchical data using nested rectangles sized by value, prefer `treemap`.
When the user wants to compare the distributions of continuous variables across groups, prefer `violin`.
Use `matrix` primarily when the user wants to inspect pairwise relationships, similarities, distances, or connections between rows and columns.
Use `circlepacking` when the hierarchical structure and relative containment of groups are important.
Use `treemap` when comparing the relative size of hierarchical categories is the primary goal.


## Installation

```bash
pip install d3blocks
```

## References

For detailed information about individual visualizations:

- Scatter plots: `references/scatter.md`
- radialgraph: `references/radialgraph.md`
- sankey: `references/sankey.md`
- d3graph: `references/d3graph.md`
- chord: `references/chord.md`
- circlepacking: `references/circlepacking.md`
- elasticgraph: `references/elasticgraph.md`
- heatmap: `references/heatmap.md`
- imageslider: `references/imageslider.md`
- maps: `references/maps.md`
- matrix: `references/matrix.md`
- movingbubbles: `references/movingbubbles.md`
- particles: `references/particles.md`
- timeseries: `references/timeseries.md`
- tree: `references/tree.md`
- treemap: `references/treemap.md`
- violin: `references/violin.md`
