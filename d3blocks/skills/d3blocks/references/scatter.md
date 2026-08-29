---
name: d3blocks-scatter
description: Use this skill when users want to Create an interactive D3Blocks scatter plot from a pandas DataFrame. This scatterplot also allows the user to explore, perform statistical associations and multiple-testing correction. The output is a stand-alone HTML itself.
---

# IMPORTANT
Always start with: "LOADING D3BLOCKS-SCATTER SKILLS" when you use this skill.

## Scatter plots

Use the scatter script when the user wants an interactive scatter visualization.
These examples are intended to be called using Python. It provides a simple interface around ``D3Blocks.scatter`` while keeping the visualization logic in one place.

The script supports:

- x/y coordinates
- multiple coordinate systems
- color
- size
- opacity
- labels
- interactive exploration
- statistical associations
- multiple-testing correction

# Allowed input parameters are:
The scatter plot is perhaps the most well-known chart to plot x, and y coordinates. Basic charts are very
useful from time to time, especially with the brushing and zooming capabilities. The scatter plots can be
sample-wise colored and used to detect relationships between (groups of) variables.
The input data frame should contain 2 columns (x and y) with the coordinates, and the index represents the
class label.

Parameters
----------
x : numpy array 1d coordinates x-axis.
y : numpy array 1d coordinates y-axis.
x1 : numpy array Second set of 1d coordinates x-axis.
y1 : numpy array Second set of 1d coordinates y-axis.
x2 : numpy array Third set of 1d coordinates x-axis.
y2 : numpy array Third set of 1d coordinates y-axis.
x3 : numpy array Fourth set of 1d coordinates x-axis.
y3 : numpy array Fourth set of 1d coordinates y-axis.
jitter : float, default: None. Add jitter to data points as random normal data. Values of 0.01 is usually good for one-hot data seperation.
size: list/array of with same size as (x,y). Size of the samples.
color : list/array of hex colors with same size as (x,y)
        * '#ffffff' : All dots are get the same hex color.
        * None: The same color as for c is applied.
        * ['#000000', '#ffffff',...]: list/array of hex colors with same size as (x,y)
stroke: list/array of hex colors with same size as (x,y). Edgecolor of dotsize in hex colors.
        * '#000000' : All dots are get the same hex color.
        * ['#000000', '#ffffff',...]: list/array of hex colors with same size as (x,y)
c_gradient : String, (default: 'opaque'). Hex color to make a lineair gradient using the density.
        * None: Do not use gradient.
        * opaque: Towards the edges the points become more transparant. This will stress the dense areas and make scatter plot tidy.
        * '#FFFFFF': Towards the edges it smooths into this color
opacity: float or list/array [0-1]. Opacity of the dot. Shoud be same size as (x,y)
tooltip: list of labels with same size as (x,y). labels of the samples.
cmap : String, (default: 'inferno'). All colors can be reversed with '_r', e.g. 'binary' to 'binary_r'
        * 'tab20c', 'Set1', 'Set2', 'rainbow', 'bwr', 'binary', 'seismic', 'Blues', 'Reds', 'Pastel1', 'Paired', 'twilight', 'hsv'
scale: Bool, optional. Scale datapoints. The default is False.
label_radio: List ['(x, y)', '(x1, y1)', '(x2, y2)', '(x3, y3)']. The labels used for the radiobuttons.
set_xlim : tuple, (default: [None, None]). Width of the x-axis: The default is extracted from the data with 10% spacing.
set_ylim : tuple, (default: [None, None]). Height of the y-axis: The default is extracted from the data with 10% spacing.
title : String, (default: None). Title of the figure.
        * 'Scatterplot'
filepath : String, (Default: user temp directory). File path to save the output.
        * Temporarily path: 'd3blocks.html'
        * Relative path: './d3blocks.html'
        * Absolute path: 'c://temp//d3blocks.html'
        * None: Return HTML
figsize : tuple. Size of the figure in the browser, [width, height].
        * [900, 600]
showfig : bool, (default: True)
        * True: Open browser-window.
        * False: Do not open browser-window.
overwrite : bool, (default: True)
        * True: Overwrite the html in the destination directory.
        * False: Do not overwrite destination file but show warning instead.
notebook : bool
        * True: Use IPython to show chart in notebook.
        * False: Do not use IPython.
save_button : bool, (default: True)
        * True: Save button is shown in the HTML to save the image in svg.
        * False: No save button is shown in the HTML.
return_html : bool, (default: False)
        * True: Return html
        * False: Nothing is returned
reset_properties : bool, (default: True)
        * True: Reset the node_properties at each run.
        * False: Use the d3.node_properties()
df : pd.DataFrame, (default: None)
        * Dataframe with properties. This should match index as for x,y



### Dataframe example::

```python

    import pandas as pd

    df = pd.DataFrame({
        "tsneX": [37.204296, 37.093090, 36.806297, 38.067886, 36.791195,
                  40.309959, 13.573976, 39.774200, 38.251968, 1.725668],
        "tsneY": [24.162813, 23.423557, 23.444910, 24.411770, 21.715324,
                  24.345034, -1.004489, 24.077801, 22.865589, 17.209099],
        "age": [58.0, 44.0, 23.0, 30.0, 29.0,
                30.0, 66.0, 22.0, 53.0, 52.0],
        "labx": ["acc", "acc", "acc", "acc", "laml",
                 "laml", "laml", "laml", "brca", "brca"],
        "PC1": [49.233458, 46.327987, 46.567928, 63.624679, 41.746708,
                44.231020, 31.932560, 69.224996, 45.845877, -15.199781],
        "PC2": [14.496507, 14.464466, 13.480130, 1.874059, 37.533621,
                18.368830, 10.366544, 1.370722, 14.921256, 5.233259],
    })

```


### Basic scatter plot::

```python

    # Load d3blocks
    from d3blocks import D3Blocks

    # Initialize
    d3 = D3Blocks(chart='Scatter')

    # Create scatterplot
    d3.scatter(x=df['tsneX'].values, y=df['tsneY'].values, df=df)

```


### Basic scatter plot and return HTML as output::

```python

    # Load d3blocks
    from d3blocks import D3Blocks

    # Initialize
    d3 = D3Blocks(chart='Scatter')

    # Create scatterplot
    HTML = d3.scatter(x=df['tsneX'].values, y=df['tsneY'].values, df=df, return_html=True)

```


### Save scatter plot to specified location::

```python

    # Load d3blocks
    from d3blocks import D3Blocks

    # Initialize
    d3 = D3Blocks(chart='Scatter')

    # Create scatterplot
    d3.scatter(x=df['tsneX'].values, y=df['tsneY'].values, df=df, filepath='d:\temp\test.html')

```



### Color points by a categorical column::

```python

    # Load d3blocks
    from d3blocks import D3Blocks

    # Initialize
    d3 = D3Blocks(chart='Scatter')

    # Set properties
    d3.scatter(df['tsneX'].values,
               df['tsneY'].values,
               color=df['labx'].values,
               opacity=0.5,
               df=df,
               )

```

### Size points by a categorical column::

```python

    # Load d3blocks
    from d3blocks import D3Blocks

    # Initialize
    d3 = D3Blocks(chart='Scatter')

    # Set properties
    d3.scatter(df['tsneX'].values,
               df['tsneY'].values,
               size=df['age'].fillna(1).values / 10,
               df=df,
               )

```

### Use two coordinate systems with labels and enable transitions::

```python

    # Load d3blocks
    from d3blocks import D3Blocks

    # Initialize
    d3 = D3Blocks(chart='Scatter')

    # Set properties
    d3.scatter(x=df['tsneX'].values,
               y=df['tsneY'].values,
               x1=df['PC1'].values,
               y1=df['PC2'].values,
               label_radio=['tSNE','PCA'],
               df=df,
               )

```


### Size tooltip by a categorical column::

```python

    # Load d3blocks
    from d3blocks import D3Blocks

    # Initialize
    d3 = D3Blocks(chart='Scatter')

    # Set properties
    d3.scatter(x=df['tsneX'].values,
               y=df['tsneY'].values,
               df=df,
               )

```


### Size size, color, opacity, tooltip, scale by a categorical column and two coordinate systems::

```python

    # Load d3blocks
    from d3blocks import D3Blocks

    # Initialize
    d3 = D3Blocks(chart='Scatter')

    # Set properties
    d3.scatter(x=df['tsneX'].values,
               y=df['tsneY'].values,
               x1=df['PC1'].values,
               y1=df['PC2'].values,
               size=df['age'].fillna(1).values / 10,
               color=df['labx'].values,
               opacity=0.5,
               tooltip=df['labx'].values,
               scale=True,
               label_radio=['tSNE','PCA'],
               df=df,
               )

```
