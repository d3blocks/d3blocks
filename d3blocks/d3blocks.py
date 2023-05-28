"""d3blocks library."""
import os
from sys import platform

import pandas as pd
import requests
from urllib.parse import urlparse
import logging
import numpy as np
import zipfile
import webbrowser
import random
import time
from typing import List, Union, Tuple
from elasticgraph import Elasticgraph
import d3graph as d3network

import d3blocks.movingbubbles.Movingbubbles as Movingbubbles
import d3blocks.timeseries.Timeseries as Timeseries
import d3blocks.sankey.Sankey as Sankey
import d3blocks.imageslider.Imageslider as Imageslider
import d3blocks.chord.Chord as Chord
import d3blocks.scatter.Scatter as Scatter
import d3blocks.violin.Violin as Violin
import d3blocks.particles.Particles as Particles
import d3blocks.heatmap.Heatmap as Heatmap
import d3blocks.matrix.Matrix as Matrix
import d3blocks.treemap.Treemap as Treemap
import d3blocks.utils as utils

# ###################### DEBUG ONLY ###################
# import movingbubbles.Movingbubbles as Movingbubbles
# import timeseries.Timeseries as Timeseries
# import sankey.Sankey as Sankey
# import imageslider.Imageslider as Imageslider
# import chord.Chord as Chord
# import scatter.Scatter as Scatter
# import violin.Violin as Violin
# import particles.Particles as Particles
# import heatmap.Heatmap as Heatmap
# import matrix.Matrix as Matrix
# import treemap.Treemap as Treemap
# import utils
# #####################################################

logger = logging.getLogger('')
for handler in logger.handlers[:]:  # get rid of existing old handlers
    logger.removeHandler(handler)
console = logging.StreamHandler()
formatter = logging.Formatter('[d3blocks] >%(levelname)s> %(message)s')
console.setFormatter(formatter)
logger.addHandler(console)
logger = logging.getLogger(__name__)


class D3Blocks():
    """D3Blocks.

    Parameters
    ----------
    frame : Bool, (default: True)
        True: Return in DataFrame.
        False: Return in dictionary.
    verbose : int, optional
        Verbose message. The default is 20.
    support : String, (default: True)
            This library is free of use and lets keep it this way! Support the project. It will cost you nothing.
            * True: I support this project! It is even better when you occasionally click on the ethical add.
            * 'text': I support this project with a text add.
            * 'image': I support this project with an image add.
            * False: I want to support in a different manner: https://d3blocks.github.io/d3blocks/pages/html/Documentation.html

    Returns
    -------
    None.

    References
    ----------
    * Github : https://github.com/d3blocks/d3blocks
    * Docs: https://d3blocks.github.io/d3blocks/
    * D3Blocks: https://towardsdatascience.com/d3blocks-the-python-library-to-create-interactive-and-standalone-d3js-charts-3dda98ce97d4
    * D3Graph: https://towardsdatascience.com/creating-beautiful-stand-alone-interactive-d3-charts-with-python-804117cb95a7
    * Scatter: https://towardsdatascience.com/get-the-most-out-of-your-scatterplot-by-making-it-interactive-using-d3js-19939e3b046
    * Sankey: https://towardsdatascience.com/hands-on-guide-to-create-beautiful-sankey-charts-in-d3js-with-python-8ddab43edb43
    * Movingbubbles: https://towardsdatascience.com/how-to-create-storytelling-moving-bubbles-charts-in-d3js-with-python-b31cec7b8226

    """

    def __init__(self, chart: str = None, frame: bool = True, verbose: int = 20, support='text'):
        """Initialize d3blocks with user-defined parameters."""
        # Set the logger
        if chart is not None: chart = str.capitalize(chart)
        set_logger(verbose=verbose)
        # Clean
        self._clean(clean_config=True, logger=logger)
        # Get chart function
        self.chart = set_chart_func(chart=chart, logger=logger)
        # Set configurations for specific charts
        self.config = {}
        self.set_config()
        # Initialize empty config
        self.config['chart'] = chart
        self.config['frame'] = frame
        self.config['support'] = utils.get_support(support)
        self.config['curpath'] = os.path.dirname(os.path.abspath(__file__))

    def particles(self,
                  text: str,
                  radius: int = 3,
                  collision: float = 0.05,
                  fontsize: int = 180,
                  spacing: int = 8,
                  cmap: str = 'Turbo',
                  color_background: str = '#000000',
                  title: str = 'Particles - D3blocks',
                  filepath: (None, str) = 'particles.html',
                  figsize=[900, 200],
                  showfig: bool = True,
                  notebook: bool = False,
                  overwrite: bool = True):
        """Particles block.

        The particles plot is to turn any word into an interactive visualization. With a mouse-move or touch, the particle
        bounce and then return to their original place. Various properties can be changed such as the bouncing,
        particle size, and colors. The original javascript is forked from Ian Johnson's Block.

        Parameters
        ----------
        text : str
            String to be visualized
        radius : float, optional (default: 3)
            Size of the particles.
        collision : float, optional (default: 0.1)
            Response of the interaction. Higher means that more collisions are prevented.
        fontsize : int, optional (default: 250)
            Text fontsize.
            When increasing: also increase width and slighly the spacing.
        spacing : int, optional (default: 10)
            The number of particles that fit in the text.
            A larger spacing reults in less particles.
            A smaller spacing reults in more particles.
        cmap : str, optional (default: 'Set2')
            Color schemes can be found at the references.
                * 'Turbo', 'Rainbow', 'Blues', 'Reds', 'Inferno', 'Magma'
        color_background : str, optional (default: '#000000')
            Background color.
        title : str, optional (default: None)
            Title of the figure.
        filepath : str, optional (default: user temp directory)
            File path to save the output.
                * Temporarily path: 'd3blocks.html'
                * Relative path: './d3blocks.html'
                * Absolute path: 'c://temp//d3blocks.html'
                * None: Return HTML content.
        figsize : tuple, optional (default: (800, 600))
            Size of the figure in the browser, [width, height].
        showfig : bool, optional (default: True)
            Open the window to show the particles.
        notebook : bool, optional
                * True: Use IPython to show chart in notebooks.
                * False: Do not use IPython.
        overwrite : bool, optional (default: True)
                * True: Overwrite the output html in the destination directory.
                * False: Do not overwrite

        Returns
        -------
        None.

        Examples
        --------
        >>> # Load d3blocks
        >>> from d3blocks import D3Blocks
        >>> #
        >>> # Initialize
        >>> d3 = D3Blocks()
        >>> #
        >>> # Create chart with defaults
        >>> d3.particles('D3blocks')
        >>> #
        >>> # Create customized chart
        >>> d3.particles('D3Blocks',
                         filepath='D3Blocks.html',
                         collision=0.05,
                         spacing=7,
                         figsize=[750, 150],
                         fontsize=130,
                         cmap='Turbo',
                         color_background='#ffffff')
        >>> #

        References
        ----------
        * https://d3blocks.github.io/d3blocks/pages/html/Particles.html
        * https://observablehq.com/@d3/color-schemes

        """
        # Cleaning
        self._clean(clean_config=False)

        # Set config
        self.config['chart'] ='Particles'
        self.config['filepath'] = utils.set_path(filepath, logger)
        self.config['title'] = title
        self.config['showfig'] = showfig
        self.config['overwrite'] = overwrite
        self.config['figsize'] = figsize
        self.config['cmap'] = cmap
        self.config['color_background'] = color_background
        self.config['radius'] = radius
        self.config['collision'] = collision
        self.config['fontsize'] = '"' + str(fontsize) + 'px"'
        self.config['spacing'] = spacing
        self.config['notebook'] = notebook
        self.chart = eval('Particles')

        # Create the plot
        html = Particles.show(text, self.config, logger)
        # Display the chart
        return self.display(html)

    def violin(self,
               x,
               y,
               size=5,
               color=None,
               x_order=None,
               opacity=0.6,
               stroke='#000000',
               tooltip=None,
               fontsize=12,
               fontsize_axis=12,
               cmap='inferno',
               bins=50,
               ylim=[None, None],
               title='Violin - D3blocks',
               filepath='violin.html',
               figsize=[None, None],
               showfig=True,
               overwrite=True,
               notebook=False,
               reset_properties=True):
        """Violin block.

        The Violin plot allows to visualize the distribution of a numeric variable for one or several groups.
        It is an alternative to the boxplot and brings insights into large datasets where the boxplot could hide a part
        of the information. The original javascript code is forked from D3.js graph gallery but brought alive by
        Pythonizing the chart. Now it is possible to configure your charts for one or several groups, change colors,
        add tooltips, customize the bin size, change figure size and store on a specified location. There are many
        input parameters for the Violin plot that can help to create the most insightful figures.

        Parameters
        ----------
        x : list of String or numpy array.
            This 1d-vector contains the class labels for each datapoint in y.
        y : list of float or numpy array.
            This 1d-vector contains the values for the samples.
        size: list/array of with same size as (x,y). Can be of type str or int.
            Size of the samples.
        color: list/array of hex colors with same size as y
                * '#002147' : All dots/nodes are get the same hex color.
                * None: The colors are generated on value using the colormap specified in cmap.
                * ['#000000', '#ffffff',...]: list/array of hex colors with same size as y.
        x_order : list of String (default: None)
            The order of the class labels on the x-axis.
                * ["setosa", "versicolor", "virginica"]
        opacity: float or list/array [0-1] (default: 0.6)
            Opacity of the dot. Shoud be same size as (x,y)
        stroke: list/array of hex colors with same size as (x,y)
            Edgecolor of dot in hex colors.
                * '#000000' : Edge colors are all black.
        tooltip: list of labels with same size as (x,y)
            labels of the samples.
        fontsize : int or list of labels with the same size as (x, y), optional (default: 12)
            Text fontsize for the tooltip.
        fontsize_axis : int, optional (default: 12)
            Text fontsize for the x-axis and y-axis.
        cmap : String, (default: 'inferno')
            All colors can be reversed with '_r', e.g. 'binary' to 'binary_r'
                * 'Set1', 'Set2', 'rainbow', 'bwr', 'binary', 'seismic', 'Blues', 'Reds', 'Pastel1', 'Paired', 'twilight', 'hsv'
        bins : Int (default: 50)
            The bin size is the 'resolution' of the violin plot.
        ylim : tuple, (default: [None, None])
            Limit the width of the y-axis [min, max].
                *  [None, None] : The width is determined based on the min-max value range.
        title : String, (default: None)
            Title of the figure.
                * 'Violin Chart'
        filepath : String, (Default: user temp directory)
            File path to save the output.
                * Temporarily path: 'Violin.html'
                * Relative path: './Violin.html'
                * Absolute path: 'c://temp//Violin.html'
                * None: Return HTML content.
        figsize : tuple
            Size of the figure in the browser, [width, height].
                * [None, None]: The width is auto-determined based on the #labels.
        showfig : bool, (default: True)
                * True: Open browser-window.
                * False: Do not open browser-window.
        overwrite : bool, (default: True)
                * True: Overwrite the html in the destination directory.
                * False: Do not overwrite destination file but show warning instead.
        notebook : bool
                * True: Use IPython to show chart in notebook.
                * False: Do not use IPython.
        reset_properties : bool, (default: True)
                * True: Reset the node_properties at each run.
                * False: Use the d3.node_properties()

        Returns
        -------
         d3.node_properties: DataFrame of dictionary
             Contains properties of the unique input label/nodes/samples.

        d3.edge_properties: DataFrame of dictionary
             Contains properties of the unique input edges/links.

        d3.config: dictionary
             Contains configuration properties.

        Examples
        --------
        >>> # Load d3blocks
        >>> from d3blocks import D3Blocks
        >>> #
        >>> # Initialize
        >>> d3 = D3Blocks()
        >>> #
        >>> # Import example dataset
        >>> df = d3.import_example('cancer')
        >>> #
        >>> # Set some input variables.
        >>> tooltip = df['labels'].values + ' <br /> Survival: ' + df['survival_months'].astype(str).values
        >>> fontsize = df['age'].values
        >>> # fontsize = 16  # Set one fontsize for all nodes
        >>> #
        >>> # Create the chart
        >>> d3.violin(x=df['labels'].values, y=df['age'].values, fontsize=fontsize, tooltip=tooltip, bins=50, size=df['survival_months'].values/10, x_order=['acc','kich', 'brca','lgg','blca','coad','ov'], filepath='violine.html', figsize=[900, None])
        >>> #

        Examples
        --------
        >>> # Load d3blocks
        >>> from d3blocks import D3Blocks
        >>> #
        >>> # Initialize for the Violin chart and set output to Frame.
        >>> d3 = D3Blocks(chart='Violin', frame=True)
        >>> #
        >>> # Import example dataset
        >>> df = d3.import_example('cancer')
        >>> #
        >>> # Set the properties by providing the labels
        >>> d3.set_edge_properties(x=df['labels'].values, y=df['age'].values, size=df['survival_months'].values/10, x_order=['acc','kich', 'brca','lgg','blca','coad','ov'])
        >>> #
        >>> # Set specific node properties.
        >>> d3.edge_properties.loc[0,'size']=50
        >>> d3.edge_properties.loc[0,'color']='#000000'
        >>> d3.edge_properties.loc[0,'tooltip']='I am adjusted!'
        >>> d3.edge_properties.loc[0,'fontsize']=30
        >>> #
        >>> # Configuration can be changed too.
        >>> print(d3.config)
        >>> #
        >>> # Show the chart
        >>> d3.show()

        References
        ----------
        * https://d3blocks.github.io/d3blocks/pages/html/Violin.html

        """
        # Cleaning
        self._clean(clean_config=reset_properties, logger=logger)
        # Store chart
        self.chart = set_chart_func('Violin', logger)
        # Store properties
        self.config = self.chart.set_config(config=self.config, filepath=filepath, title=title, showfig=showfig, overwrite=overwrite, figsize=figsize, cmap=cmap, bins=bins, ylim=ylim, x_order=x_order, reset_properties=reset_properties, notebook=notebook, fontsize=fontsize, fontsize_axis=fontsize_axis, logger=logger)
        # Remvove quotes from source-target node_properties
        self.edge_properties = self.chart.set_edge_properties(x, y, config=self.config, color=color, size=size, stroke=stroke, opacity=opacity, tooltip=tooltip, cmap=self.config['cmap'], x_order=self.config['x_order'], fontsize=self.config['fontsize'], logger=logger)
        # Set default label properties
        if self.config['reset_properties'] or (not hasattr(self, 'node_properties')):
            self.set_node_properties(np.unique(self.edge_properties['x'].values), cmap=self.config['cmap'])
        # Create the plot
        return self.show()

    def scatter(self,
                x,
                y,
                x1=None,
                y1=None,
                x2=None,
                y2=None,
                jitter=None,
                size=3,
                color='#002147',
                c_gradient='opaque',
                opacity=0.8,
                stroke='#ffffff',
                tooltip=None,
                cmap='tab20',
                scale=False,
                color_background='#ffffff',
                label_radio=['(x, y)', '(x1, y1)', '(x2, y2)'],
                xlim=[None, None],
                ylim=[None, None],
                title='Scatter - D3blocks',
                filepath='scatter.html',
                figsize=[900, 600],
                showfig=True,
                overwrite=True,
                notebook=False,
                reset_properties=True,
                ):
        """Scatterplot block.

        The scatter plot is perhaps the most well-known chart to plot x, and y coordinates. Basic charts are very
        useful from time to time, especially with the brushing and zooming capabilities. The scatter plots can be
        sample-wise colored and used to detect relationships between (groups of) variables.
        The input data frame should contain 2 columns (x and y) with the coordinates, and the index represents the
        class label.

        Parameters
        ----------
        x : numpy array
            1d coordinates x-axis.
        y : numpy array
            1d coordinates y-axis.
        x1 : numpy array
            Second set of 1d coordinates x-axis.
        y1 : numpy array
            Second set of 1d coordinates y-axis.
        x2 : numpy array
            Third set of 1d coordinates x-axis.
        y2 : numpy array
            Third set of 1d coordinates y-axis.
        jitter : float, default: None
            Add jitter to data points as random normal data. Values of 0.01 is usually good for one-hot data seperation.
        size: list/array of with same size as (x,y).
            Size of the samples.
        color: list/array of hex colors with same size as (x,y)
                * '#ffffff' : All dots are get the same hex color.
                * None: The same color as for c is applied.
                * ['#000000', '#ffffff',...]: list/array of hex colors with same size as (x,y)
        stroke: list/array of hex colors with same size as (x,y)
            Edgecolor of dotsize in hex colors.
                * '#000000' : All dots are get the same hex color.
                * ['#000000', '#ffffff',...]: list/array of hex colors with same size as (x,y)
        c_gradient : String, (default: 'opaque')
            Hex color to make a lineair gradient using the density.
                * None: Do not use gradient.
                * opaque: Towards the edges the points become more transparant. This will stress the dense areas and make scatter plot tidy.
                * '#FFFFFF': Towards the edges it smooths into this color
        opacity: float or list/array [0-1]
            Opacity of the dot. Shoud be same size as (x,y)
        tooltip: list of labels with same size as (x,y)
            labels of the samples.
        cmap : String, (default: 'inferno')
            All colors can be reversed with '_r', e.g. 'binary' to 'binary_r'
                * 'Set1', 'Set2', 'rainbow', 'bwr', 'binary', 'seismic', 'Blues', 'Reds', 'Pastel1', 'Paired', 'twilight', 'hsv'
        scale: Bool, optional
            Scale datapoints. The default is False.
        label_radio: List ['(x, y)', '(x1, y1)', '(x2, y2)']
            The labels used for the radiobuttons.
        set_xlim : tuple, (default: [None, None])
            Width of the x-axis: The default is extracted from the data with 10% spacing.
        set_ylim : tuple, (default: [None, None])
            Height of the y-axis: The default is extracted from the data with 10% spacing.
        title : String, (default: None)
            Title of the figure.
                * 'Scatterplot'
        filepath : String, (Default: user temp directory)
            File path to save the output.
                * Temporarily path: 'd3blocks.html'
                * Relative path: './d3blocks.html'
                * Absolute path: 'c://temp//d3blocks.html'
                * None: Return HTML
        figsize : tuple
            Size of the figure in the browser, [width, height].
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
        reset_properties : bool, (default: True)
                * True: Reset the node_properties at each run.
                * False: Use the d3.node_properties()

        Returns
        -------
        d3.node_properties: DataFrame of dictionary
             Contains properties of the unique input label/nodes/samples.

        d3.edge_properties: DataFrame of dictionary
             Contains properties of the unique input edges/links.

        d3.config: dictionary
             Contains configuration properties.

        Examples
        --------
        >>> # Load d3blocks
        >>> from d3blocks import D3Blocks
        >>> #
        >>> # Initialize
        >>> d3 = D3Blocks()
        >>> #
        >>> # Load example data
        >>> df = d3.import_example('cancer')
        >>> #
        >>> # Set size and tooltip
        >>> size = df['survival_months'].fillna(1).values / 20
        >>> tooltip = df['labels'].values + ' <br /> Survival: ' + df['survival_months'].astype(str).str[0:4].values
        >>> #
        >>> # Scatter plot
        >>> d3.scatter(df['x'].values,
                       df['y'].values,
                       size=size,
                       color=df.index.values,
                       stroke='#000000',
                       opacity=0.4,
                       tooltip=tooltip,
                       filepath='scatter_demo.html',
                       cmap='tab20')

        Examples
        --------
        >>> # Scatter plot with transitions. Note that scale is set to True to make the axis comparible to each other
        >>> d3.scatter(df['x'].values,
                       df['y'].values,
                       x1=df['PC1'].values,
                       y1=df['PC2'].values,
                       label_radio=['tSNE', 'PCA'],
                       scale=True,
                       size=size,
                       color=df.index.values,
                       stroke='#000000',
                       opacity=0.4,
                       tooltip=tooltip,
                       filepath='scatter_transitions2.html',
                       cmap='tab20')

        Examples
        --------
        >>> # Scatter plot with transitions. Note that scale is set to True to make the axis comparible to each other
        >>> d3.scatter(df['x'].values,
                       df['y'].values,
                       x1=df['PC1'].values,
                       y1=df['PC2'].values,
                       x2=df['PC2'].values,
                       y2=df['PC1'].values,
                       label_radio=['tSNE', 'PCA', 'PCA_reverse'],
                       scale=True,
                       size=size,
                       color=df.index.values,
                       stroke='#000000',
                       opacity=0.4,
                       tooltip=tooltip,
                       filepath='scatter_transitions3.html',
                       cmap='tab20')

        Examples
        --------
        >>> # Load d3blocks
        >>> from d3blocks import D3Blocks
        >>> #
        >>> # Initialize
        >>> d3 = D3Blocks(chart='Scatter')
        >>> #
        >>> # Import example
        >>> df = d3.import_example('cancer')
        >>> #
        >>> # Set properties
        >>> d3.set_edge_properties(df['x'].values,
                                   df['y'].values,
                                   x1=df['PC1'].values,
                                   y1=df['PC2'].values,
                                   label_radio=['tSNE','PCA'],
                                   size=df['survival_months'].fillna(1).values / 10,
                                   color=df.index.values,
                                   tooltip=df['labels'].values + ' <br /> Survival: ' + df['survival_months'].astype(str).str[0:4].values,
                                   scale=True)
        >>> #
        >>> # Show the chart
        >>> d3.show()
        >>> #
        >>> # Set specific node properties.
        >>> print(d3.edge_properties)
        >>> d3.edge_properties.loc[0,'size']=50
        >>> d3.edge_properties.loc[0,'color']='#000000'
        >>> d3.edge_properties.loc[0,'tooltip']='I am adjusted!'
        >>> #
        >>> # Configuration can be changed too.
        >>> print(d3.config)
        >>> #
        >>> # Show the chart again with adjustments
        >>> d3.show()

        References
        ----------
        * https://d3blocks.github.io/d3blocks/pages/html/Scatter.html

        """
        # Cleaning
        self._clean(clean_config=reset_properties, logger=logger)
        # Store chart
        self.chart = set_chart_func('Scatter', logger)
        # Store properties
        self.config = self.chart.set_config(config=self.config, filepath=filepath, title=title, showfig=showfig, overwrite=overwrite, figsize=figsize, cmap=cmap, scale=scale, ylim=ylim, xlim=xlim, label_radio=label_radio, color_background=color_background, reset_properties=reset_properties, notebook=notebook, jitter=jitter, logger=logger)
        # Check exceptions
        Scatter.check_exceptions(x, y, x1, y1, x2, y2, size, color, tooltip, logger)
        # Set node properties
        self.set_node_properties()
        # Set edge properties
        self.set_edge_properties(x, y, x1=x1, y1=y1, x2=x2, y2=y2, color=color, size=size, tooltip=tooltip, opacity=opacity, c_gradient=c_gradient, stroke=stroke, cmap=self.config['cmap'], scale=self.config['scale'], jitter=self.config['jitter'], logger=logger)
        # Create the plot
        return self.show()

    def chord(self,
              df,
              color='source',
              opacity='source',
              fontsize=10,
              cmap='tab20',
              title='Chord - D3blocks',
              filepath='chord.html',
              figsize=[900, 900],
              showfig=True,
              overwrite=True,
              notebook=False,
              reset_properties=True,
              ):
        """Chord block.

        A chord represents flows or connections between several entities or nodes.
        Each entity is represented by a fragment on the outer part of the circular layout.
        Then, arcs are drawn between each entity. The size of the arc is proportional to the importance of the flow.

        Parameters
        ----------
        df : pd.DataFrame()
            Input data containing the following columns:
                * "source"
                * "target"
                * "weight"
                * "color" (optional)
                * "opacity" (optional)
        color: (default: 'source')
            Link colors in Hex notation. Should be the same size as input DataFrame.
                * "source" : Color edges/links similar to that of source-color node.
                * "target" : Color edges/links similar to that of target-color node.
                * "source-target" : Color edges/link based on unique source-target edges using the colormap.
                * "#ffffff" : All links have the same hex color.
                * ["#000000", "#ffffff",...] : Define per link.
        opacity: (default: 'source')
            Link Opacity. Should be the same size as input DataFrame.
                * 'source': Opacity of edges/links similar to that of source-opacity node.
                * 'target': Opacity of edges/links similar to that of target-opacity node.
                * 0.8: All links have the same opacity.
                * [0.1, 0.75,...]: Set opacity per edge/link.
        fontsize : int, (default: 8)
            The Fontsize.
        cmap : String, (default: 'tab20')
            colormap is only used in case color=None. All colors can be reversed with '_r', e.g. 'binary' to 'binary_r'
                * 'Set1', 'Set2', 'rainbow', 'bwr', 'binary', 'seismic', 'Blues', 'Reds', 'Pastel1', 'Paired', 'twilight', 'hsv'
        title : String, (default: None)
            Title of the figure.
                * 'Chord'
        filepath : String, (Default: user temp directory)
            File path to save the output.
                * Temporarily path: 'd3blocks.html'
                * Relative path: './d3blocks.html'
                * Absolute path: 'c://temp//d3blocks.html'
                * None: Return HTML
        figsize : tuple
            Size of the figure in the browser, [width, height].
                * [900, 900]
        showfig : bool, (default: True)
                * True: Open browser-window.
                * False: Do not open browser-window.
        overwrite : bool, (default: True)
                * True: Overwrite the html in the destination directory.
                * False: Do not overwrite destination file but show warning instead.
        notebook : bool
                * True: Use IPython to show chart in notebook.
                * False: Do not use IPython.
        reset_properties : bool, (default: True)
                * True: Reset the node_properties at each run.
                * False: Use the d3.node_properties()

        Returns
        -------
        d3.node_properties: DataFrame of dictionary
            Contains properties of the unique input label/nodes/samples.

        d3.edge_properties: DataFrame of dictionary
             Contains properties of the unique input edges/links.

        d3.config: dictionary
             Contains configuration properties.

        Examples
        --------
        >>> # Load d3blocks
        >>> from d3blocks import D3Blocks
        >>> #
        >>> # Initialize
        >>> d3 = D3Blocks()
        >>> #
        >>> # Load example data
        >>> df = d3.import_example('energy')
        >>> #
        >>> # Plot
        >>> d3.chord(df)
        >>> #

        Examples
        --------
        >>> # Load d3blocks
        >>> from d3blocks import D3Blocks
        >>> #
        >>> # Initialize
        >>> d3 = D3Blocks(chart='Chord', frame=False)
        >>> #
        >>> # Import example
        >>> df = d3.import_example('energy')
        >>> #
        >>> # Node properties
        >>> d3.set_node_properties(df, opacity=0.2, cmap='tab20')
        >>> d3.set_edge_properties(df, color='source', opacity='source')
        >>> #
        >>> # Show the chart
        >>> d3.show()
        >>> #
        >>> # Make some edits to highlight the Nuclear node
        >>> # d3.node_properties
        >>> d3.node_properties.get('Nuclear')['color']='#ff0000'
        >>> d3.node_properties.get('Nuclear')['opacity']=1
        >>> # Show the chart
        >>> #
        >>> d3.show()
        >>> # Make edits to highlight the Nuclear Edge
        >>> d3.edge_properties.get(('Nuclear', 'Thermal generation'))['color']='#ff0000'
        >>> d3.edge_properties.get(('Nuclear', 'Thermal generation'))['opacity']=0.8
        >>> d3.edge_properties.get(('Nuclear', 'Thermal generation'))['weight']=1000
        >>> #
        >>> # Show the chart
        >>> d3.show()

        References
        ----------
        * https://d3blocks.github.io/d3blocks/pages/html/Chord.html

        """
        # Cleaning
        self._clean(clean_config=reset_properties, logger=logger)
        # Store chart
        self.chart = set_chart_func('Chord', logger)
        # Store properties
        self.config = self.chart.set_config(config=self.config, filepath=filepath, fontsize=fontsize, title=title, showfig=showfig, overwrite=overwrite, figsize=figsize, cmap=cmap, notebook=notebook, logger=logger)
        # Set node properties
        if reset_properties or (not hasattr(self, 'node_properties')):
            self.set_node_properties(df, cmap=cmap)
        # Set edge properties
        self.set_edge_properties(df, color=color, opacity=opacity, cmap=cmap, logger=logger)
        # Create the plot
        return self.show()

    def imageslider(self,
                    img_before,
                    img_after,
                    scale=True,
                    colorscale=-1,
                    background='#000000',
                    title='Imageslider - D3blocks',
                    filepath='imageslider.html',
                    figsize=[None, None],
                    showfig=True,
                    notebook=False,
                    overwrite=True):
        """Imageslider Block.

        The imageslider allows comparison of two images. This is useful in case there is a before and after state.
        For demonstration purposes, the example can be loaded from the Southern Nebula image that is taken with the
        Hubble telescope, and can be easily compared to that of the newest telescope. The javascript code is forked
        from JohnEdChristensen and then Pythonized to easily make comparisons between images.

        Parameters
        ----------
        img_before : String
            absolute path to before image.
        img_after : String
            absolute path to after image.
        scale : bool, default: True
            Scale image in range [0, 255], by img*(255/max(img))
                * True: Scaling image
                * False: Leave image untouched
        colorscale : int, default: -1 (untouched)
            colour-scaling from opencv.
                * 0: cv2.IMREAD_GRAYSCALE
                * 1: cv2.IMREAD_COLOR
                * 2: cv2.IMREAD_ANYDEPTH
                * 8: cv2.COLOR_GRAY2RGB
                * -1: cv2.IMREAD_UNCHANGED
        background : String (default: '#000000')
            Background color.
        title : String, (default: None)
            Title of the figure.
                * 'Imageslider'
        filepath : String, (Default: user temp directory)
                * File path to save the output.
                * Temporarily path: 'd3blocks.html'
                * Relative path: './d3blocks.html'
                * Absolute path: 'c://temp//d3blocks.html'
                * None: Return HTML
        figsize : tuple
            Size of the figure in the browser, [width, height].
                * [900, 900]
        showfig : bool, (default: True)
                * True: Open browser-window.
                * False: Do not open browser-window.
        notebook : bool
                * True: Use IPython to show chart in notebook.
                * False: Do not use IPython.
        overwrite : bool, (default: True)
                * True: Overwrite the html in the destination directory.
                * False: Do not overwrite destination file but show warning instead.

        Returns
        -------
        None.

        Examples
        --------
        >>> # Load d3blocks
        >>> from d3blocks import D3Blocks
        >>> #
        >>> # Initialize
        >>> d3 = D3Blocks()
        >>> #
        >>> # Local images
        >>> img_before, img_after = d3.import_example('southern_nebula')
        >>> #
        >>> # Internet location
        >>> img_before, img_after = d3.import_example('southern_nebula_internet')
        >>> #
        >>> # Read the image in array
        >>> img_before = cv2.imread(img_before, -1)
        >>> img_after = cv2.imread(img_after, -1)
        >>> #
        >>> # Plot
        >>> d3.imageslider(img_before, img_after)
        >>> #
        >>> # Plot
        >>> d3.imageslider(img_before, img_after, showfig=True, scale=True, colorscale=2, figsize=[400, 400])

        References
        ----------
        * https://d3blocks.github.io/d3blocks/pages/html/Imageslider.html

        """
        # Cleaning
        self._clean(clean_config=False)

        self.config['chart'] ='imageslider'
        self.config['img_before'] = img_before
        self.config['img_after'] = img_after
        self.config['scale'] = scale
        self.config['colorscale'] = colorscale
        self.config['background'] = background
        self.config['filepath'] = utils.set_path(filepath, logger)
        self.config['title'] = title
        self.config['showfig'] = showfig
        self.config['overwrite'] = overwrite
        self.config['notebook'] = notebook
        self.config['figsize'] = figsize
        self.chart = eval('Imageslider')
        # if self.config['filepath'] is None: raise Exception('filepath can not be None.')

        # Preprocessing
        self.config = Imageslider.preprocessing(self.config, logger=logger)
        # Create the plot
        html = Imageslider.show(self.config, logger)
        # Open the webbrowser
        # self.open_browser(logger=logger)
        # Display the chart
        return self.display(html)

    def sankey(self,
               df,
               node={"align": "justify", "width": 15, "padding": 15, "color": "currentColor"},
               link={"color": "source-target", "stroke_opacity": 0.5, 'color_static': '#D3D3D3'},
               margin={"top": 5, "right": 1, "bottom": 5, "left": 1},
               title='Sankey - D3blocks',
               filepath='sankey.html',
               figsize=[800, 600],
               showfig=True,
               overwrite=True,
               notebook=False,
               reset_properties=True,
               ):
        """Sankey block.

        A Sankey chart is a visualization to depict a flow from one set of values to another.
        The nodes in this case are represented as the rectangle boxes, and the flow or arrows are the links.
        The width of the arrow is proportional to the flow rate. Sankeys are best used when you want to show
        many-to-many relationships or to discover multiple paths through a set of stages. For example, the traffic
        flows from pages to other pages on your website. For demonstration purposes, the "energy" and "stormofswords"
        dataset can be used. The javascript code is forked from Mike Bostock and then Pythonized.

        Parameters
        ----------
        df : pd.DataFrame()
            Input data containing the following columns:
                * 'source'
                * 'target'
                * 'weight'
        link : dict.
            Dictionary containing edge or link information.
                * "linkColor" : "source", "target", "source-target"
                * "linkStrokeOpacity" : 0.5
                * "color_static": '#0f0f0f' or "grey", "blue", "red" etc
        margin : dict.
            margin, in pixels.
                * "top" : 5
                * "right" : 1
                * "bottom" : 5
                * "left" : 1
        node : dict.
                * "align" : "left", "right", "justify", "center"
                * "width" : 15 (width of the node rectangles)
                * "padding" : 15 (vertical seperation between the nodes)
                * "color" : "currentColor", "grey", "black", "red", etc
        title : String, (default: None)
            Title of the figure.
                * 'Sankey'
        filepath : String, (Default: user temp directory)
                * File path to save the output.
                * Temporarily path: 'd3blocks.html'
                * Relative path: './d3blocks.html'
                * Absolute path: 'c://temp//d3blocks.html'
                * None: Return HTML
        figsize : tuple
            Size of the figure in the browser, [width, height].
                * [800, 600]
        showfig : bool, (default: True)
                * True: Open browser-window.
                * False: Do not open browser-window.
        overwrite : bool, (default: True)
                * True: Overwrite the html in the destination directory.
                * False: Do not overwrite destination file but show warning instead.
        notebook : bool
                * True: Use IPython to show chart in notebook.
                * False: Do not use IPython.
        reset_properties : bool, (default: True)
                * True: Reset the node_properties at each run.
                * False: Use the d3.node_properties()

        Returns
        -------
        d3.node_properties: DataFrame of dictionary
             Contains properties of the unique input label/nodes/samples.

        d3.edge_properties: DataFrame of dictionary
             Contains properties of the unique input edges/links.

        d3.config: dictionary
             Contains configuration properties.

        Examples
        --------
        >>> # Load d3blocks
        >>> from d3blocks import D3Blocks
        >>> #
        >>> # Initialize
        >>> d3 = D3Blocks()
        >>> #
        >>> # Load example data
        >>> df = d3.import_example('energy')
        >>> #
        >>> # Plot
        >>> d3.sankey(df)
        >>> #

        Examples
        --------
        >>> # Load d3blocks
        >>> from d3blocks import D3Blocks
        >>> #
        >>> # Initialize
        >>> d3 = D3Blocks(chart='Sankey', frame=True)
        >>> #
        >>> # Import example
        >>> df = d3.import_example('energy')
        >>> #
        >>> # Node properties
        >>> d3.set_node_properties(df)
        >>> print(d3.node_properties)
        >>> #
        >>> d3.set_edge_properties(df, color='target', opacity='target')
        >>> print(d3.edge_properties)
        >>> #
        >>> # Show the chart
        >>> d3.show()

        References
        ----------
        * https://d3blocks.github.io/d3blocks/pages/html/Sankey.html

        """
        # Cleaning
        self._clean(clean_config=reset_properties, logger=logger)
        # Store chart
        self.chart = set_chart_func('Sankey', logger)
        # Store properties
        self.config = self.chart.set_config(config=self.config, filepath=filepath, title=title, showfig=showfig, overwrite=overwrite, figsize=figsize, link=link, node=node, margin=margin, reset_properties=reset_properties, notebook=notebook, logger=logger)
        # Set default label properties
        if self.config['reset_properties'] or (not hasattr(self, 'node_properties')):
            self.set_node_properties(df, cmap=self.config['cmap'])
        # Set edge properties
        self.set_edge_properties(df)
        # Create the plot
        return self.show()

    def movingbubbles(self,
                      df,
                      datetime: str = 'datetime',
                      sample_id: str = 'sample_id',
                      state: str = 'state',
                      center: str = None,
                      size=5,
                      color=None,
                      cmap: str = 'Set1',
                      color_method: str = 'state',
                      dt_format: str = '%d-%m-%Y %H:%M:%S',
                      damper: float = 1,
                      fontsize: int = 14,
                      timedelta: str = 'minutes',
                      standardize: str = 'samplewise',
                      speed: dict = {"slow": 1000, "medium": 200, "fast": 50},
                      figsize: tuple = [780, 800],
                      note: str = None,
                      time_notes: str = None,
                      title: str = 'Movingbubbles - D3Blocks',
                      filepath: str = 'movingbubbles.html',
                      showfig: bool = True,
                      overwrite: bool = True,
                      notebook: bool = False,
                      reset_properties: bool = True,
                      ):
        """MovingBubbles block.

        The MovingBubbles provides insights into when one action follows the other across time. It can help to
        understand the movements of entities, and whether clusters occur at specific time points and state(s).
        It may not be the most visually efficient method, but it is one of the more visually satisfying ones with
        force-directed and colliding nodes. The function d3.import_example('random_time') is created to generate
        a randomized dataset with various states. The input dataset should contain 3 columns; 
            * DateTime column: Describes the data-time when an event occurs.
            * State column: Describes what the particular state was at that point of time of the specific sample_id. 
            * Sample_id column: A sample can have multiple states at various time points but can not have two states at exactly the same point in time.

        Parameters
        ----------
        df : Input data, pd.DataFrame()
            Input data.
        datetime : str, (default: 'datetime')
            Name of the column with the datetime.
        sample_id : str, (default: 'sample_id')
            Name of the column with the sample ids.
        state : str, (default: 'state')
            Name of the column with the states.
        center : String, (default: None)
            Center this category.
        size: int or dictionary. (default: 5) or {sample_id i: size}
            Size the nodes by specifying per sample_id the size.
                * 5: set all nodes this this size
                * {'0': 4, '1': 10, '2': 5, ..}: Specify size for each sample_id
        color: int or dictionary. (default: '#808080') or {sample_id i: hex-color}
            Color the nodes by specifying per sample_id the color.
                * '#000FFF': set all nodes to this color.
                * {'0': '#808080', '1': '#FFF000', '3': '#000000', ..}: Specify color for each sample_id
                * None: Colors are based on sample_id using the cmap.
        color_method : str
            Coloring of the nodes.
                * 'state': Use the colors defined per state as (d3.node_properties).
                * 'node': Use the colors defined in the dataframe (d3.edge_properties).
        dt_format : str
            Date time format.
                * '%d-%m-%Y %H:%M:%S'.
        damper : float, (default: 1)
            Movement of samples. A smaller number is slower/smoother movement.
                * 0.1: min
                * 10: max
        fontsize : int, (default: 14)
            Fontsize of the states.
        timedelta : String, (default: 'minutes')
            The time delta between states. Change accordingly.
                * 'seconds'
                * 'minutes'
                * 'days'
        standardize : str. (default: None)
            Method to standardize the data.
                * None: standardize over the entire timeframe. Sample_ids are dependent to each other.
                * 'samplewise': Standardize per sample_id by substracting the minimum time per sample_id.
                * 'relative': Standardize across the entire dataframe after sorting on time. Each action is relative to the previous one in time without considering sample_id.
                * 'minimum': Movements are relative to the minimum time in the dataset.
        speed : dict, (default: {"slow": 1000, "medium": 200, "fast": 50})
            The final html file contains three buttons for speed movements. The lower the value, the faster the time moves.
        note : str, (default: None)
            A specific note, such as project description can be put on the html page.
                * None: Default text will be provided about the simulation, and states.
        time_notes : dict, (default: None)
            The time notes will be shown between specific time points.
                * time_notes = [{"start_minute": 1,
                               "stop_minute": 5,
                               "note": "Enter your note here and it is shown between 1 min and 5 min."}]
            time_notes.append[{"start_minute": 6, "stop_minute": 10, "note": "Enter your second note here and it is shown between 6 min and 10 min."}]
        cmap : String, (default: 'Set1')
            All colors can be reversed with '_r', e.g. 'binary' to 'binary_r'
                * 'Set1', 'Set2'
                * 'rainbow', 'bwr', 'binary', 'seismic'
                * 'Blues', 'Reds', 'Pastel1', 'Paired'
                * 'twilight', 'hsv', 'inferno'
        title : String, (default: None)
            Title of the figure.
                * 'Movingbubbles'
        filepath : String, (Default: user temp directory)
            File path to save the output.
                * Temporarily path: 'd3blocks.html'
                * Relative path: './d3blocks.html'
                * Absolute path: 'c://temp//d3blocks.html'
                * None: Return HTML
        figsize : tuple
            Size of the figure in the browser, [width, height].
                * [780, 800]
        showfig : bool, (default: True)
                * True: Open browser-window.
                * False: Do not open browser-window.
        overwrite : bool, (default: True)
                * True: Overwrite the html in the destination directory.
                * False: Do not overwrite destination file but show warning instead.
        notebook : bool
                * True: Use IPython to show chart in notebook.
                * False: Do not use IPython.
        reset_properties : bool, (default: True)
                * True: Reset the node_properties at each run.
                * False: Use the d3.node_properties()

        Returns
        -------
        d3.node_properties: DataFrame of dictionary
             Contains properties of the unique input label/nodes/samples.

        d3.edge_properties: DataFrame of dictionary
             Contains properties of the unique input edges/links.

        d3.config: dictionary
             Contains configuration properties.

        Examples
        --------
        >>> # Load d3blocks
        >>> from d3blocks import D3Blocks
        >>> #
        >>> # Initialize
        >>> d3 = D3Blocks()
        >>> #
        >>> # Load example data
        >>> df = d3.import_example('random_time', n=10000, c=300, date_start="1-1-2000 00:10:05", date_stop="1-1-2000 23:59:59")
        >>> #
        >>> # Plot
        >>> d3.movingbubbles(df, speed={"slow": 1000, "medium": 200, "fast": 10}, filepath='movingbubbles.html')
        >>> #

        Examples
        --------
        >>> # Load d3blocks
        >>> from d3blocks import D3Blocks
        >>> #
        >>> # Initialize
        >>> d3 = D3Blocks(chart='movingbubbles', frame=False)
        >>> #
        >>> # Import example
        >>> df = d3.import_example('random_time', n=1000, c=100, date_start="1-1-2000 00:10:05", date_stop="1-1-2000 23:59:59")
        >>> #
        >>> # Coloring the states.
        >>> d3.set_node_properties(df['state'])
        >>> print(d3.node_properties)
        >>> # Color the sleeping state black
        >>> d3.node_properties.get('Sleeping')['color']='#000000'
        >>> #
        >>> d3.set_edge_properties(df)
        >>> print(d3.edge_properties)
        >>> #
        >>> # Show
        >>> d3.show(title='Movingbubbles with adjusted configurations')

        Examples
        --------
        >>> # Load d3blocks
        >>> from d3blocks import D3Blocks
        >>> #
        >>> # Initialize
        >>> d3 = D3Blocks(chart='movingbubbles')
        >>> #
        >>> # Import example
        >>> df = d3.import_example('random_time', n=1000, c=100, date_start="1-1-2000 00:10:05", date_stop="1-1-2000 23:59:59")
        >>> #
        >>> # Specify the colors and node sizes for the specific sample_id
        >>> size = {1: 20, 3: 40}
        >>> color = {1: '#FF0000', 3: '#000FFF'}
        >>> #
        >>> # Show
        >>> d3.movingbubbles(df, color=color, size=size)

        References
        ----------
        * https://d3blocks.github.io/d3blocks/pages/html/MovingBubbles.html

        """
        # Cleaning
        self._clean(clean_config=reset_properties, logger=logger)
        # Store chart
        self.chart = set_chart_func('Movingbubbles', logger)
        # Store properties
        self.config = self.chart.set_config(config=self.config, filepath=filepath, title=title, showfig=showfig, overwrite=overwrite, figsize=figsize, timedelta=timedelta, speed=speed, damper=damper, note=note, time_notes=time_notes, fontsize=fontsize, standardize=standardize, center=center, datetime=datetime, sample_id=sample_id, state=state, reset_properties=reset_properties, cmap=cmap, dt_format=dt_format, notebook=notebook, color_method=color_method, logger=logger)
        # Set node properties
        if self.config['reset_properties'] or (not hasattr(self, 'node_properties')):
            self.set_node_properties(df[self.config['state']].values, center=self.config['center'], cmap=self.config['cmap'], logger=logger)
        # Set edge properties
        self.set_edge_properties(df, timedelta=self.config['timedelta'], state=self.config['state'], datetime=self.config['datetime'], sample_id=self.config['sample_id'], size=size, color=color, standardize=self.config['standardize'], dt_format=self.config['dt_format'], logger=logger)
        # Create the plot
        return self.show()

    def timeseries(self,
                   df,
                   datetime='datetime',
                   dt_format: str = '%d-%m-%Y %H:%M:%S',
                   sort_on_date=True,
                   whitelist=None,
                   fontsize=10,
                   cmap='Set1',
                   title='Timeseries - D3blocks',
                   filepath='timeseries.html',
                   figsize=[1200, 500],
                   showfig=True,
                   overwrite=True,
                   notebook=False,
                   reset_properties=True,
                   ):
        """Timeseries block.

        The TimeSeries can be used in case a date-time element is available, and where the time-wise values
        directly follow up with each other. The TimeSeries block supports enabling/disabling columns of interest,
        brushing and zooming to quickly focus on regions of interest or plot specific features, such as stocks together
        in a single chart.

        Parameters
        ----------
        df : pd.DataFrame()
            Input data containing the columns "datetime" together with the names of the timeseries to plot.
        datetime : str, (default: None)
            Column name that contains the datetime.
        dt_format : str
            Date time format.
                * '%d-%m-%Y %H:%M:%S'.
        sort_on_date : Bool (default: True)
            Sort on date.
                * True: Sort on datetime.
                * False: Do not change the input order.
        whitelist : str, optional
            Keep only columns containing this (sub)string (case insensitive)
        fontsize : int, (default: 14)
            Fontsize of the fonts in the circle.
        cmap : String, (default: 'Set1')
            All colors can be reversed with '_r', e.g. 'binary' to 'binary_r'
                * 'Set1', 'Set2', 'rainbow', 'bwr', 'binary', 'seismic', 'Blues', 'Reds', 'Pastel1', 'Paired', 'twilight', 'hsv', 'inferno'
        title : String, (default: None)
            Title of the figure.
                * 'Timeseries'
        filepath : String, (Default: user temp directory)
            File path to save the output.
                * Temporarily path: 'd3blocks.html'
                * Relative path: './d3blocks.html'
                * Absolute path: 'c://temp//d3blocks.html'
                * None: Return HTML
        figsize : tuple
            Size of the figure in the browser, [width, height].
                * [1200, 500]
        showfig : bool, (default: True)
                * True: Open browser-window.
                * False: Do not open browser-window.
        overwrite : bool, (default: True)
                * True: Overwrite the html in the destination directory.
                * False: Do not overwrite destination file but show warning instead.
        notebook : bool
                * True: Use IPython to show chart in notebook.
                * False: Do not use IPython.
        reset_properties : bool, (default: True)
                * True: Reset the node_properties at each run.
                * False: Use the d3.node_properties()

        Returns
        -------
        d3.node_properties: DataFrame of dictionary
             Contains properties of the unique input label/nodes/samples.

        d3.edge_properties: DataFrame of dictionary
             Contains properties of the unique input edges/links.

        d3.config: dictionary
             Contains configuration properties.

        Examples
        --------
        >>> #
        >>> # Import
        >>> from d3blocks import D3Blocks
        >>> #
        >>> # Initialize
        >>> d3 = D3Blocks()
        >>> #
        >>> # Import example
        >>> df = d3.import_example('climate')
        >>> #
        >>> # Show
        >>> d3.timeseries(df, datetime='date', dt_format='%Y-%m-%d %H:%M:%S', fontsize=10, figsize=[850, 500])
        >>> #

        Examples
        --------
        >>> # Load d3blocks
        >>> from d3blocks import D3Blocks
        >>> #
        >>> # Initialize
        >>> d3 = D3Blocks(chart='Timeseries', frame=False)
        >>> #
        >>> # Import example
        >>> df = d3.import_example('climate')
        >>> #
        >>> # Node properties
        >>> d3.set_node_properties(df.columns.values)
        >>> d3.node_properties.get('wind_speed')['color']='#000000'
        >>> print(d3.node_properties)
        >>> #
        >>> d3.set_edge_properties(df, datetime='date', dt_format='%Y-%m-%d %H:%M:%S')
        >>> d3.edge_properties
        >>> #
        >>> # Show
        >>> d3.show(title='Timeseries with adjusted configurations')
        >>> #

        References
        ----------
        * https://d3blocks.github.io/d3blocks/pages/html/Timeseries.html

        """
        # Cleaning
        self._clean(clean_config=False)
        # Store chart
        self.chart = set_chart_func('Timeseries', logger)
        # Store properties
        self.config = self.chart.set_config(config=self.config, filepath=filepath, title=title, showfig=showfig, overwrite=overwrite, figsize=figsize, fontsize=fontsize, sort_on_date=sort_on_date, datetime=datetime, cmap=cmap, whitelist=whitelist, reset_properties=reset_properties, dt_format=dt_format, notebook=notebook, logger=logger)
        # Set node properties
        if self.config['reset_properties'] or (not hasattr(self, 'node_properties')):
            self.set_node_properties(df.columns.values, cmap=self.config['cmap'], whitelist=self.config['whitelist'], datetime=self.config['datetime'])
        # Set edge properties
        self.set_edge_properties(df, dt_format=self.config['dt_format'], datetime=self.config['datetime'], logger=logger)
        # Create the plot
        html = self.chart.show(self.edge_properties, config=self.config, node_properties=self.node_properties, logger=logger)
        # Display the chart
        return self.display(html)

    def heatmap(self,
                df,
                classlabel='cluster',
                cmap='Set2',
                filepath='heatmap.html',
                title='Heatmap - D3blocks',
                stroke='red',
                description=None,
                vmax=None,
                cluster_params = {'cluster': 'agglomerative',
                                  'evaluate': 'silhouette',
                                  'metric': 'euclidean',
                                  'linkage': 'ward',
                                  'min_clust': 2,
                                  'max_clust': 25},
                figsize=[720, 720],
                showfig=True,
                overwrite=True,
                notebook=False,
                reset_properties=True,
                ):
        """Heatmap block.

        heatmap is a Python package to create interactive heatmaps based on d3js.
        The heatmap allows interactive clustering where the cluster coloring can be customized.
        Clusters are colored and within each cluster the color is incremental based on the value.
        Adjacency matrix must be symetric.

        Parameters
        ----------
        df : pd.DataFrame()
            Input data. The index and column names are used for the row/column naming.
        classlabel : str or list
            Class label to color the clustering.
                * 'cluster': colors are based on clustering
                * 'label': colors are based on the presence of unique labels
                * [1,2,1,..]: colors are based on the input classlabels
        stroke : String, (default: 'red').
            Color of the recangle when hovering over a cell.
                * 'red'
                * 'black'
        description : String, (default: 'Heatmap description')
            Description text of the heatmap.
        vmax : Bool, (default: 100).
            Range of colors starting with maximum value. Increasing this value will color the cells more discrete.
                * 1 : cells above value >1 are capped.
            None : cells are colored based on the maximum value in the input data.
        cluster_params : dict (defaults)
            Parameters for clustering the data and using the cluster labels to color the heatmap. See references for more information.
        cmap : String, (default: 'Set1')
            All colors can be reversed with '_r', e.g. 'binary' to 'binary_r'
                * 'Set1', 'Set2', 'rainbow', 'bwr', 'binary', 'seismic', 'Blues', 'Reds', 'Pastel1', 'Paired', 'twilight', 'hsv', 'inferno'
        title : String, (default: None)
            Title of the figure.
                * 'Heatmap'
        filepath : String, (Default: user temp directory)
            File path to save the output.
                * Temporarily path: 'd3blocks.html'
                * Relative path: './d3blocks.html'
                * Absolute path: 'c://temp//d3blocks.html'
                * None: Return HTML
        figsize : tuple
            Size of the figure in the browser, [width, height].
                * [800, 800]
        showfig : bool, (default: True)
                * True: Open browser-window.
                * False: Do not open browser-window.
        overwrite : bool, (default: True)
                * True: Overwrite the html in the destination directory.
                * False: Do not overwrite destination file but show warning instead.
        notebook : bool
                * True: Use IPython to show chart in notebook.
                * False: Do not use IPython.
        reset_properties : bool, (default: True)
                * True: Reset the node_properties at each run.
                * False: Use the d3.node_properties()

        Examples
        --------
        >>> # Load d3blocks
        >>> from d3blocks import D3Blocks
        >>> #
        >>> # Initialize
        >>> d3 = D3Blocks()
        >>> #
        >>> # Load example data
        >>> df = d3.import_example('stormofswords')  # 'energy'
        >>> df = d3.vec2adjmat(df['source'], df['target'], weight=df['weight'], symmetric=True)
        >>> #
        >>> # Plot
        >>> d3.heatmap(df)
        >>> #

        Examples
        --------
        >>> # Initialize
        >>> d3 = D3Blocks()
        >>> #
        >>> # Load example data
        >>> df = d3.import_example('bigbang')
        >>> df = d3.vec2adjmat(df['source'], df['target'], weight=df['weight'])
        >>> #
        >>> # Plot
        >>> d3.heatmap(df, classlabel=[1,1,1,2,2,2,3])
        >>> #

        References
        ----------
        * https://d3blocks.github.io/d3blocks/pages/html/Heatmap.html
        * https://erdogant.github.io/clusteval/

        """
        if len(df.columns.unique())!=len(df.columns):
            logger.warning('[Input data should contain unique column names otherwise d3js randomly removes the non-unique ones.')
        if len(df.index.unique())!=len(df.index):
            logger.warning('Input data should contain unique index names otherwise d3js randomly removes the non-unique ones.')

        # Cleaning
        adjmat = utils.remove_quotes(df)
        df = self.adjmat2vec(adjmat)
        self._clean(clean_config=reset_properties, logger=logger)
        # Store chart
        self.chart = set_chart_func('Heatmap', logger)
        # Store properties
        self.config = self.chart.set_config(config=self.config, filepath=filepath, title=title, showfig=showfig, overwrite=overwrite, figsize=figsize, reset_properties=reset_properties, notebook=notebook, classlabel=classlabel, description=description, vmax=vmax, stroke=stroke, cmap=cmap, cluster_params=cluster_params, logger=logger)
        # Set default label properties
        if self.config['reset_properties'] or (not hasattr(self, 'node_properties')):
            self.set_node_properties(df, cmap=self.config['cmap'])
        # Color on cluster labels
        self.node_properties = self.chart.color_on_clusterlabel(adjmat, df, self.node_properties, self.config, logger)
        # Set edge properties
        html = self.chart.set_properties(df, self.config, self.node_properties, logger)
        # Display the chart
        return self.display(html)

    def matrix(self,
                df,
                scale=False,
                stroke='red',
                description=None,
                vmin=None,
                vmax=None,
                cmap='interpolateInferno',
                fontsize=10,
                title='Matrix - D3blocks',
                figsize=[700, 500],
                showfig=True,
                filepath='matrix.html',
                overwrite=True,
                notebook=False,
                reset_properties=True,
                ):
        """Matrix block.

        Parameters
        ----------
        df : pd.DataFrame()
            Input data. The index and column names are used for the row/column naming.
        scale : Bool, (default: True).
            Scale data in range Scaling in range by X*(100/max(X)).
                * True: Scale the values.
                * False: Do not scale.
        stroke : String, (default: 'red').
            Color of the recangle when hovering over a cell.
                * 'red'
                * 'black'
        description : String.
            Description text of the heatmap.
        vmax : Bool, (default: 100).
            Range of colors starting with maximum value. Increasing this value will color the cells more discrete.
                * 1 : cells above value >1 are capped.
            None : cells are colored based on the maximum value in the input data.
        cmap : String, (default: 'interpolateInferno').
            The colormap scheme. See references for more schmes.
                * 'interpolateInferno'
                * 'interpolatePRGn'
                * 'interpolateBlues'
                * 'interpolateGreens'
                * 'interpolateTurbo'
                * 'interpolateViridis'
                * 'interpolateInferno'
                * 'interpolateRainbow'
                * 'interpolateSinebow'
        fontsize : int, (default: 10).
            Font size for the X and Y labels.
        title : String, (default: None)
            Title of the figure.
                * 'Heatmap'
        figsize : tuple
            Size of the figure in the browser, [width, height].
                * [800, 800]
        showfig : bool, (default: True)
                * True: Open browser-window.
                * False: Do not open browser-window.
        filepath : String, (Default: user temp directory)
            File path to save the output.
                * Temporarily path: 'd3blocks.html'
                * Relative path: './d3blocks.html'
                * Absolute path: 'c://temp//d3blocks.html'
                * None: Return HTML
        overwrite : bool, (default: True)
                * True: Overwrite the html in the destination directory.
                * False: Do not overwrite destination file but show warning instead.
        notebook : bool
                * True: Use IPython to show chart in notebook.
                * False: Do not use IPython.
        reset_properties : bool, (default: True)
                * True: Reset the node_properties at each run.
                * False: Use the d3.node_properties()

        Examples
        --------
        >>> # Initialize
        >>> d3 = D3Blocks()
        >>> #
        >>> # Load example data
        >>> df = pd.DataFrame(np.random.randint(0, 10, size=(6, 20)))
        >>> #
        >>> # Plot
        >>> d3.matrix(df)
        >>> #
        >>> d3.matrix(df,
                      vmin=1,
                      fontsize=10,
                      title='D3blocks Matrix',
                      filepath='d3blocks_matrix.html',
                      figsize=[600, 300],
                      cmap='interpolateGreens')

        References
        ----------
        * https://d3blocks.github.io/d3blocks/pages/html/Heatmap.html
        * https://github.com/d3/d3-scale-chromatic

        """
        if len(df.columns.unique())!=len(df.columns):
            logger.warning('Input data should contain unique column names otherwise d3js randomly removes the non-unique ones.')
        if len(df.index.unique())!=len(df.index):
            logger.warning('Input data should contain unique index names otherwise d3js randomly removes the non-unique ones.')

        adjmat = df.copy()
        # Cleaning
        adjmat = utils.remove_quotes(df)
        # Rescale data
        if scale: adjmat = utils.scale(adjmat, vmax=vmax, make_round=True, logger=logger)
        df = self.adjmat2vec(adjmat)
        self._clean(clean_config=reset_properties, logger=logger)
        # Store chart
        self.chart = set_chart_func('Matrix', logger)
        # Store properties
        self.config = self.chart.set_config(config=self.config, filepath=filepath, title=title, showfig=showfig, overwrite=overwrite, figsize=figsize, reset_properties=reset_properties, notebook=notebook, description=description, vmax=vmax, vmin=vmin, stroke=stroke, cmap=cmap, scale=scale, fontsize=fontsize, logger=logger)
        # Set default label properties
        if self.config['reset_properties'] or (not hasattr(self, 'node_properties')):
            self.set_node_properties(df, cmap='Set2')
        # Set edge properties
        html = self.chart.set_properties(df, self.config, self.node_properties, logger)
        # Display the chart
        return self.display(html)

    def d3graph(self,
                df,
                color='cluster',
                size=10,
                scaler='zscore',
                title='D3graph - D3blocks',
                filepath='d3graph.html',
                figsize=[1500, 800],
                collision=0.5,
                charge=400,
                slider=[None, None],
                notebook=False,
                showfig=True,
                support='text',
                overwrite=True):
        """d3graph block.

        d3graph is integrated in d3blocks and is to create interactive and stand-alone D3 force-directed graphs.
        The input data is a dataframe containing source, target, and weight. In underneath example, we load the energy
        dataset which contains 68 relationships that are stored in a DataFrame with the columns source, target, and weight.
        The nodes are colored based on the Louvain heuristics which is the partition of highest modularity, i.e.
        the highest partition of the dendrogram generated by the Louvain algorithm. The strength of the edges is based
        on the weights. To explore the network, and the strength of the edges more extensively, the slider
        (located at the top) can break the network based on the edge weights. The ouput is a html file that is
        interactive and stand alone. For demonstration purposes, the "energy" and "stormofswords" dataset can be used.

        Parameters
        ----------
        df : pd.DataFrame()
            Input data containing the following columns:
                * 'source'
                * 'target'
                * 'weight'
        color : list of strings (default: '#000080')
            Color of the node.
                * 'cluster' : Colours are based on the community distance clusters.
                * None: All nodes will have the same color (auto generated).
                * ['#000000']: All nodes will have the same hex color.
                * ['#377eb8','#ffffff','#000000',...]: Hex colors are directly used.
                * ['A']: All nodes will have hte same color. Color is generated on CMAP and the unique labels.
                * ['A','A','B',...]:  Colors are generated using cmap and the unique labels accordingly colored.
        size : array of integers (default: 5)
            Size of the nodes.
                * 10: all nodes sizes are set to 10
                * [10, 5, 3, 1, ...]: Specify node sizes
        collision : float, (default: 0.5)
            Response of the network. Higher means that more collisions are prevented.
        charge : int, (default: 400)
            Edge length of the network. Towards zero becomes a dense network. Higher make edges longer.
        slider : typle [min: int, max: int]:, (default: [None, None])
            Slider is automatically set to the range of the edge weights.
        title : String, (default: None)
            Title of the figure.
                * 'd3graph'
        filepath : String, (Default: user temp directory)
            File path to save the output.
                * Temporarily path: 'd3blocks.html'
                * Relative path: './d3blocks.html'
                * Absolute path: 'c://temp//d3blocks.html'
                * None: Return HTML
        figsize : tuple
            Size of the figure in the browser, [width, height].
                * [1500, 800]
        showfig : bool, (default: True)
                * True: Open browser-window.
                * False: Do not open browser-window.
        notebook : bool
                * True: Use IPython to show chart in notebook.
                * False: Do not use IPython.
        overwrite : bool, (default: True)
                * True: Overwrite the html in the destination directory.
                * False: Do not overwrite destination file but show warning instead.

        Returns
        -------
        None.

        Examples
        --------
        >>> # Load library
        >>> from d3blocks import D3Blocks
        >>> #
        >>> # Initialize
        >>> d3 = D3Blocks()
        >>> #
        >>> # Import example
        >>> df = d3.import_example('energy') # 'bigbang', 'stormofswords'
        >>> #
        >>> # Create network using default
        >>> d3.d3graph(df, filepath='d3graph.html')
        >>> #
        >>> # Change scaler
        >>> d3.d3graph(df, scaler='minmax')
        >>> #
        >>> # Change node properties
        >>> d3.D3graph.set_node_properties(color=None)
        >>> d3.D3graph.node_properties['Solar']['size']=30
        >>> d3.D3graph.node_properties['Solar']['color']='#FF0000'
        >>> d3.D3graph.node_properties['Solar']['edge_color']='#000000'
        >>> d3.D3graph.node_properties['Solar']['edge_size']=5
        >>> d3.D3graph.show()
        >>> #
        >>> # Change edge properties
        >>> d3.D3graph.set_edge_properties(directed=True, marker_end='arrow')
        >>> d3.D3graph.show()
        >>> #
        >>> # Node properties
        >>> d3.D3graph.node_properties
        >>> #
        >>> # Node properties
        >>> d3.D3graph.edge_properties
        >>> #
        >>> # After making changes, show the graph again using show()
        >>> d3.D3graph.show()

        References
        ----------
        * Blog: https://towardsdatascience.com/creating-beautiful-stand-alone-interactive-d3-charts-with-python-804117cb95a7
        * Github : https://github.com/erdogant/d3graph
        * Documentation: https://erdogant.github.io/d3graph/

        """
        # Cleaning
        self._clean(clean_config=False)

        # Set configs
        self.config['chart'] ='network'
        self.config['title'] = title
        self.config['filepath'] = utils.set_path(filepath)
        self.config['figsize'] = figsize
        self.config['showfig'] = showfig
        self.config['overwrite'] = overwrite
        self.config['collision'] = collision
        self.config['charge'] = -abs(charge)
        self.config['slider'] = slider
        self.config['notebook'] = notebook

        # Copy of data
        df = df.copy()
        # Remvove quotes from source-target labels
        df = utils.remove_quotes(df)
        # Initialize network graph
        self.D3graph = d3network.d3graph(collision=collision, charge=charge, slider=slider, support=support)
        # Convert vector to adjmat
        adjmat = d3network.vec2adjmat(df['source'], df['target'], weight=df['weight'])
        # Create default graph
        self.D3graph.graph(adjmat, color=color, size=size, scaler=scaler)
        # Open the webbrowser
        self.D3graph.show(figsize=figsize, title=title, filepath=filepath, showfig=showfig, overwrite=overwrite)
        # Display the chart
        # return self.display(html)

    def elasticgraph(self,
                  df,
                  scaler='zscore',
                  group='cluster',
                  title='Elasticgraph - D3blocks',
                  filepath='Elasticgraph.html',
                  figsize=[None, None],
                  collision=0.5,
                  charge=250,
                  size=4,
                  hull_offset=15,
                  single_click_expand=False,
                  notebook=False,
                  showfig=False,
                  overwrite=True):
        """D3 Elasticgraph block.

        Elasticgraph is integrated in d3blocks to create interactive and stand-alone D3 force-directed graphs for which
        the groups are clustered. The original d3js is forked from Ger Hobbelts (see references). The input data is a
        dataframe containing source, target, and weight. This graph relies on the properties of d3graph and is also utilized
        in the d3blocks library.
        In underneath example, we load an example dataset which contains K relationships that are stored in a DataFrame
        with the columns source, target, and weight. The nodes are clustered (and colored) based on the Louvain
        heuristics which is the partition of highest modularity, i.e. the highest partition of the dendrogram generated
        by the Louvain algorithm. The strength of the edges is based on the weights. The ouput is a html file that is
        interactive and stand alone. For demonstration purposes, the "bigbang", "energy" and "stormofswords" dataset can
        be used.

        Parameters
        ----------
        df : pd.DataFrame()
            Input data containing the following columns:
                * 'source'
                * 'target'
                * 'weight'
        group : list of strings (default: 'cluster')
            Grouping (and coloring) of the nodes.
                * 'cluster' : Colours are based on the community distance clusters.
                * None: All nodes will have the same color (auto generated).
        collision : float, (default: 0.5)
            Response of the network. Higher means that more collisions are prevented.
        charge : int, (default: 250)
            Edge length of the network. Towards zero becomes a dense network. Higher make edges longer.
        size : float, (default: 4)
            Size of the nodes.
        hull_offset : float, (default: 15)
            The higher the number the more the clusters will overlap after expanding.
        single_click_expand: bool, (default: False)
            Nodes are not expanded with a single click.
        title : String, (default: None)
            Title of the figure.
                * 'elasticgraph'
        filepath : String, (Default: user temp directory)
            File path to save the output.
                * Temporarily path: 'd3blocks.html'
                * Relative path: './d3blocks.html'
                * Absolute path: 'c://temp//d3blocks.html'
                * None: Return HTML
        figsize : tuple
            Size of the figure in the browser, [width, height].
                * [None, None] # Full screen
                * [1500, 800]
        showfig : bool, (default: True)
                * True: Open browser-window.
                * False: Do not open browser-window.
        notebook : bool
                * True: Use IPython to show chart in notebook.
                * False: Do not use IPython.
        overwrite : bool, (default: True)
                * True: Overwrite the html in the destination directory.
                * False: Do not overwrite destination file but show warning instead.

        Returns
        -------
        None.

        Examples
        --------
        >>> # Load library
        >>> from d3blocks import D3Blocks
        >>> #
        >>> # Initialize
        >>> d3 = D3Blocks()
        >>> #
        >>> # Import example
        >>> df = d3.import_example('energy') # 'stormofswords'
        >>> #
        >>> # Create force-directed-network (without cluster labels)
        >>> d3.elasticgraph(df, filepath='Elasticgraph.html')
        >>> #
        >>> # Show elasticgraph
        >>> d3.Elasticgraph.show()
        >>> # Show original graph with the same properties
        >>> d3.Elasticgraph.D3graph.show()
        >>> #
        >>> # Add cluster labels (no need to do it again because it is the default)
        >>> # d3.Elasticgraph.set_node_properties(color=None)
        >>> #
        >>> # After making changes, show the graph again using show()
        >>> d3.Elasticgraph.show()
        >>> # Show original graph
        >>> d3.Elasticgraph.D3graph.show()
        >>> #
        >>> # Node properties
        >>> d3.Elasticgraph.D3graph.node_properties
        >>> #
        >>> # Node properties
        >>> d3.Elasticgraph.D3graph.edge_properties
        >>> #

        References
        ----------
        * Blog: https://towardsdatascience.com/creating-beautiful-stand-alone-interactive-d3-charts-with-python-804117cb95a7
        * Gitlab : https://gitlab.com/rwsdatalab/public/codebase/tools/elasticgraph

        """
        # Cleaning
        self._clean(clean_config=False)

        # Set configs
        self.config['chart'] ='elasticgraphh'
        self.config['title'] = title
        self.config['filepath'] = utils.set_path(filepath)
        self.config['figsize'] = figsize
        self.config['showfig'] = showfig
        self.config['overwrite'] = overwrite
        self.config['collision'] = collision
        self.config['charge'] = -abs(charge)
        self.config['size'] = size
        self.config['hull_offset'] = hull_offset
        self.config['single_click_expand'] = single_click_expand
        self.config['notebook'] = notebook

        # Copy of data
        df = df.copy()
        # Remvove quotes from source-target labels
        df = utils.remove_quotes(df)
        # Initialize network d3-elasticgraph-network
        self.Elasticgraph = Elasticgraph(collision=collision, charge=charge, radius=size, hull_offset=hull_offset, single_click_expand=single_click_expand)
        # Convert vector to adjmat
        adjmat = d3network.vec2adjmat(df['source'], df['target'], weight=df['weight'])
        # Create default graph
        self.Elasticgraph.graph(adjmat, group=group, scaler=scaler)
        # Open the webbrowser
        self.Elasticgraph.show(figsize=figsize, title=title, filepath=filepath, showfig=showfig, overwrite=overwrite)
        # Display the chart
        # return self.display(html)

    def treemap(self,
               df,
               margin: dict = {"top": 40, "right": 10, "bottom": 10, "left": 10},
               border: dict = {'type': 'solid', 'color': '#FFFFFF', 'width': 1},
               font: dict = {'size': 10, 'type':'sans-serif', 'position': 'absolute'},
               title: str = 'Treemap - D3blocks',
               filepath: str = 'treemap.html',
               figsize: Tuple[int, int] = [1000, 600],
               showfig: bool = True,
               overwrite: bool = True,
               notebook: bool = False,
               reset_properties: bool = True,
               ):
        """Treemap block.

        A Treemap chart is a visualization to hierarchically show the data as a set of nested rectangles.
        For demonstration purposes, the "energy" and "stormofswords" dataset can be used.
        The javascript code is forked from Mike Bostock and then Pythonized.

        Parameters
        ----------
        df : pd.DataFrame()
            Input data containing the following columns:
                * 'source', 'target', 'weight'
                * 'level0', 'level1', 'level2', 'weight'
        margin : dict.
            margin, in pixels.
                * {"top": 40, "right": 10, "bottom": 10, "left": 10}
        border : dict.
            border properties.
                * {'type': 'solid', 'color': '#FFFFFF', 'width': 1}
        font : dict.
            font properties.
                * {'size': 10, 'type':'sans-serif', 'position': 'absolute'}
        title : String, (default: None)
            Title of the figure.
                * 'Treemap'
        filepath : String, (Default: user temp directory)
                * File path to save the output.
                * Temporarily path: 'd3blocks.html'
                * Relative path: './d3blocks.html'
                * Absolute path: 'c://temp//d3blocks.html'
                * None: Return HTML
        figsize : tuple
            Size of the figure in the browser, [width, height].
                * [1000, 600]
                * [None, None]: Use the screen resolution.
        showfig : bool, (default: True)
                * True: Open browser-window.
                * False: Do not open browser-window.
        overwrite : bool, (default: True)
                * True: Overwrite the html in the destination directory.
                * False: Do not overwrite destination file but show warning instead.
        notebook : bool
                * True: Use IPython to show chart in notebook.
                * False: Do not use IPython.
        reset_properties : bool, (default: True)
                * True: Reset the node_properties at each run.
                * False: Use the d3.node_properties()

        Returns
        -------
        d3.node_properties: DataFrame of dictionary
             Contains properties of the unique input label/nodes/samples.

        d3.edge_properties: DataFrame of dictionary
             Contains properties of the unique input edges/links.

        d3.config: dictionary
             Contains configuration properties.

        Examples
        --------
        >>> # Load d3blocks
        >>> from d3blocks import D3Blocks
        >>> #
        >>> # Initialize
        >>> d3 = D3Blocks()
        >>> #
        >>> # Load example data
        >>> df = d3.import_example('energy')
        >>> df = d3.import_example('animals')
        >>> #
        >>> # Plot
        >>> d3.treemap(df)
        >>> #

        Examples
        --------
        >>> # Load d3blocks
        >>> from d3blocks import D3Blocks
        >>> #
        >>> # Initialize
        >>> d3 = D3Blocks(chart='Treemap', frame=True)
        >>> #
        >>> # Import example
        >>> df = d3.import_example('energy')
        >>> #
        >>> # Node properties
        >>> d3.set_node_properties(df)
        >>> print(d3.node_properties)
        >>> #
        >>> d3.set_edge_properties(df)
        >>> print(d3.edge_properties)
        >>> #
        >>> # Show the chart
        >>> d3.show()

        References
        ----------
        * Mike Bostock; http://bl.ocks.org/mbostock/4063582
        * https://d3blocks.github.io/d3blocks/pages/html/Treemap.html

        """
        # Cleaning
        self._clean(clean_config=reset_properties, logger=logger)
        # Store chart
        self.chart = set_chart_func('Treemap', logger)
        # Store properties
        self.config = self.chart.set_config(config=self.config, filepath=filepath, border=border, font=font, title=title, showfig=showfig, overwrite=overwrite, figsize=figsize, margin=margin, reset_properties=reset_properties, notebook=notebook, logger=logger)
        # Set default label properties
        if self.config['reset_properties'] or (not hasattr(self, 'node_properties')):
            self.set_node_properties(df, cmap=self.config['cmap'], labels=df.columns.values[:-1].astype(str))
        # Set edge properties
        self.set_edge_properties(df)
        # Create the plot
        return self.show()

    def set_edge_properties(self, *args, **kwargs):
        """Set edge properties.

        The input for edge properties are the arguments that are inherited from the chart-function. As an example, the
        edge properties for the scatter chart are those described in the scatter function.

        Parameters
        ----------
        df : pd.DataFrame()
            Input data containing the following columns:
                * 'source'
                * 'target'
                * 'weight'
                * 'color' (optional)
                * 'opacity'  (optional)
        color : Union[float, List[float]], optional
            Link colors in Hex notation. Should be the same size as input DataFrame.
                * None : 'cmap' is used to create colors.
                * 'source': Color edges/links similar to that of source-color node.
                * 'target': Color edges/links similar to that of target-color node.
                * 'source-target': Color edges/link based on unique source-target edges using the colormap.
                * '#ffffff': All links have the same hex color.
                * ['#000000', '#ffffff',...]: Define per link.
        opacity: float or list/array [0..1] (default: None)
            Link Opacity. Should be the same size as input DataFrame.
                * 'source': Opacity of edges/links similar to that of source-opacity node.
                * 'target': Opacity of edges/links similar to that of target-opacity node.
                * 0.8: All links have the same opacity.
                * [0.1, 0.75,...]: Set opacity per edge/link.
        cmap : String, (default: 'tab20')
            colormap is only used in case color=None.
            All colors can be reversed with '_r', e.g. 'binary' to 'binary_r'
                * 'Set1', 'Set2', 'rainbow', 'bwr', 'binary', 'seismic', 'Blues', 'Reds', 'Pastel1', 'Paired', 'twilight', 'hsv'

        Returns
        -------
        None.

        """
        if self.config['chart'] is None:
            raise Exception('"chart" parameter is mandatory. Hint: Initialize with the chart type such as: d3 = D3Blocks(chart="chord")')
        if (not hasattr(self, 'node_properties')) and np.any(np.isin(self.config['chart'], ['Violin', 'Scatter'])):
            self.node_properties = self.chart.set_node_properties()
        if not hasattr(self, 'node_properties'):
            raise Exception('Set the node_properties first. Hint: d3.node_properties(df)')
        if hasattr(self, 'edge_properties'):
            del self.edge_properties

        # Compute edge properties for the specified chart.
        if self.chart is not None:
            df = self.chart.set_edge_properties(*args, config=self.config, node_properties=self.node_properties, **kwargs)

        # Convert to frame/dictionary
        self.edge_properties = utils.convert_dataframe_dict(df, frame=self.config['frame'], chart=self.config['chart'], logger=logger)

        # Store and return
        logger.info('Edge properties are set.')

    def set_node_properties(self, *args, **kwargs):
        """Set label properties.

        Parameters
        ----------
        labels : array-like (default: None)
            The unique names of the nodes/labels.
                * In case of pd.DataFrame, the 'source' and 'target' columns are used.

        Returns
        -------
        labels : dict()
            Dictionary containing class information.

        """
        # Make dict with properties
        if self.chart is not None:
            labels = self.chart.set_node_properties(*args, **kwargs)
        else:
            raise Exception(logger.error('You need to specify the chart during initialization. Hint: d3 = D3Blocks(chart="movingbubbles")'))

        # Convert to frame
        self.node_properties = utils.convert_dataframe_dict(labels, frame=self.config['frame'], logger=logger)
        if self.node_properties is not None: logger.info('Node properties are set.')

    def set_config(self):
        """Set the general configuration setting."""
        # Set default config settings for the specified chart.
        if self.chart is not None:
            self.config = self.chart.set_config(self.config, logger=logger)

    def show(self, **kwargs) -> None:
        """Build and show the graph.

        Parameters
        ----------
        figsize : tuple
            Size of the figure in the browser, [height, width].
        title : String, (default: None)
            Title of the figure.
        filepath : String, (Default: user temp directory)
            File path to save the output.
                * Temporarily path: 'd3blocks.html'
                * Relative path: './d3blocks.html'
                * Absolute path: 'c://temp//d3blocks.html'
                * None: Return HTML
        showfig : bool
                * True: Open the browser and show chart.
                * False: Do not open browser.
        notebook : bool
                * True: Use IPython to show chart in notebooks.
                * False: Do not use IPython.
        kwargs : Various
            Other options are possible depending on the chart that is being used.

        Returns
        -------
        None.

        """
        # Some checks
        if not hasattr(self, 'edge_properties') or not hasattr(self, 'node_properties'):
            logger.error('Can not show the chart without the edge_properties and/or node_properties. <return>"')
            return None

        # Use the user-defined config parameters.
        if kwargs.get('config', None) is not None:
            self.config = kwargs.get('config')
            kwargs.pop('config')
        if kwargs.get('edge_properties', None) is not None:
            self.edge_properties = kwargs.get('edge_properties')
            kwargs.pop('edge_properties')
        if kwargs.get('node_properties', None) is not None:
            self.node_properties = kwargs.get('node_properties')
            kwargs.pop('node_properties')

        # Create the plot
        if self.chart is not None:
            html = self.chart.show(self.edge_properties, config=self.config, node_properties=self.node_properties, logger=logger, **kwargs)

        # Display the chart
        return self.display(html)

    def display(self, html):
        """Display."""
        if self.config['notebook']:
            import IPython
            logger.info('Display in notebook using IPython.')
            IPython.display.display(IPython.display.HTML(html))
        elif self.config['filepath'] is not None:
            # Open the webbrowser
            self.open_browser(logger=logger)
        else:
            logger.info('Nothing to display when filepath is None and notebook is False. Return HTML.')
            return html

    # Open the webbrowser
    def open_browser(self, sleep=0.2, logger=None):
        """Open browser to show chart."""
        if self.config['showfig']:
            # Sleeping is required to pevent overlapping windows
            time.sleep(sleep)
            file_location = os.path.abspath(self.config['filepath'])
            if platform == "darwin":  # check if on OSX
                file_location = "file:///" + file_location
            if os.path.isfile(file_location):
                webbrowser.open(file_location, new=2)
            else:
                if logger is not None: logger.info('File not found: [%s]' %(file_location))
            logger.info('Open browser: %s' %(file_location))

    def _clean(self, clean_config=True, logger=None):
        """Clean previous results to ensure correct working."""
        if logger is not None: logger.info('Cleaning edge_properties and config parameters..')
        if hasattr(self, 'G'): del self.G
        if hasattr(self, 'edge_properties'): del self.edge_properties
        if clean_config and hasattr(self, 'config'):
            # Remove all configurations except for the chart, frame and path
            chart = self.config.get('chart', None)
            frame = self.config.get('frame', True)
            support = self.config.get('support', 'text')
            curpath = self.config.get('curpath', os.path.dirname(os.path.abspath(__file__)))
            self.config = {'chart': chart, 'frame': frame, 'curpath': curpath, 'notebook': False, 'support': support}

    @staticmethod
    def vec2adjmat(source, target, weight=None, symmetric=True, aggfunc='sum'):
        """Convert source and target into adjacency matrix.

        Parameters
        ----------
        source : list
            The source node.
        target : list
            The target node.
        weight : list of int
            The Weights between the source-target values
        symmetric : bool, optional
            Make the adjacency matrix symmetric with the same number of rows as columns. The default is True.
        aggfunc : str, optional
            Aggregate function in case multiple values exists for the same relationship.
                * 'sum' (default)

        Returns
        -------
        pd.DataFrame
            adjacency matrix.

        Examples
        --------
        >>> # Initialize
        >>> d3 = D3Blocks()
        >>> #
        >>> # Load example
        >>> df = d3.import_example('energy')
        >>> #
        >>> # Convert to adjmat
        >>> adjmat = d3.vec2adjmat(df['source'], df['target'], df['weight'])

        """
        return d3network.vec2adjmat(source, target, weight=weight, symmetric=symmetric, aggfunc=aggfunc)

    @staticmethod
    def adjmat2vec(df, min_weight=1):
        """Convert adjacency matrix into vector with source and target.

        Parameters
        ----------
        adjmat : pd.DataFrame()
            Adjacency matrix.

        min_weight : float
            edges are returned with a minimum weight.

        Returns
        -------
        pd.DataFrame()
            nodes that are connected based on source and target

        Examples
        --------
        >>> # Initialize
        >>> d3 = D3Blocks()
        >>> #
        >>> # Load example
        >>> df = d3.import_example('energy')
        >>> Convert into adjmat
        >>> adjmat = d3.vec2adjmat(df['source'], df['target'], df['weight'])
        >>> #
        >>> # Convert back to vector
        >>> vector = d3.adjmat2vec(adjmat)

        """
        return d3network.adjmat2vec(df, min_weight=min_weight)

    def import_example(self, data, n=10000, c=300, date_start="17-12-1903 00:00:00", date_stop="17-12-1903 23:59:59"):
        """Import example dataset from github source.

        Import one of the few datasets from github source or specify your own download url link.

        Parameters
        ----------
        data : str
            Example datasets:
                * "movingbubbles"
                * "random_time"
                * "timeseries"
                * "energy"
                * "stormofswords"
                * "bigbang"
                * "southern_nebula"
                * "southern_nebula_internet"
                * "cancer"
                * "breast_cancer"
                * "iris"
                * "occupancy"
                * "climate"
                * "mnist"
                * "animals"
        n : int, (default: 1000).
            Number of events (samples).
        c : int, (default: 100).
            Number of classes.
        date_start : str, (default: None)
            Start date.
                * "17-12-1903 00:00:00" : start date
        date_stop : str, (default: None)
            Stop date.
                * "17-12-1903 23:59:59" : Stop date

        Returns
        -------
        pd.DataFrame()
            Dataset containing mixed features.

        """
        return _import_example(data=data, n=n, c=c, date_start=date_start, date_stop=date_stop, dt_format='%d-%m-%Y %H:%M:%S', logger=logger)


# %% Import example dataset from github.
def _import_example(data, n=10000, c=1000, date_start=None, date_stop=None, dt_format='%d-%m-%Y %H:%M:%S', logger=None):
    """Import example dataset from github source.

    Import one of the few datasets from github source or specify your own download url link.

    Parameters
    ----------
    data : str
        Name of datasets
            * movingbubbles
            * random_time
            * timeseries
            * energy
            * stormofswords
            * bigbang
            * southern_nebul
            * southern_nebula_internet
            * unsplash
            * cancer
            * breast_cancer
            * iris
            * occupancy
            * climate
            * "mnist"
            * "animals"
    n : int, (default: 1000).
        Number of events (samples).
    c : int, (default: 100).
        Number of classes.
    date_start : str, (default: None)
        Start date.
            * "17-12-1903 00:00:00" : start date
    date_stop : str, (default: None)
        Stop date.
            * "17-12-1903 23:59:59" : Stop date

    Returns
    -------
    pd.DataFrame()
        Dataset containing mixed features.

    """
    ext = '.csv'
    sep=','

    if data=='movingbubbles':
        url='https://erdogant.github.io/datasets/movingbubbles.zip'
    elif data=='random_time':
        return Movingbubbles.generate_data_with_random_datetime(n, c=c, date_start=date_start, date_stop=date_stop, dt_format=dt_format, logger=logger)
    elif data=='timeseries':
        df = pd.DataFrame(np.random.randint(0, n, size=(n, 6)), columns=list('ABCDEF'))
        df['datetime'] = list(map(lambda x: random_date(date_start, date_stop, random.random(), dt_format=dt_format), range(0, n)), dt_format=dt_format)
        return df
    elif data=='energy':
        # Sankey demo
        url='https://erdogant.github.io/datasets/energy_source_target_value.zip'
    elif data=='stormofswords':
        # Sankey demo
        url='https://erdogant.github.io/datasets/stormofswords.zip'
    elif data=='bigbang':
        # Initialize
        d3model = d3network.d3graph()
        df = d3model.import_example('bigbang')[0]
        return d3network.adjmat2vec(df)
    elif data=='southern_nebula':
        # Image slider demo
        url='https://erdogant.github.io/datasets/southern_nebula.zip'
        ext='.jpg'
    elif data=='southern_nebula':
        # Image slider demo
        before = 'https://erdogant.github.io/datasets/images/unsplash_before.jpg'
        after = 'https://erdogant.github.io/datasets/images/unsplash_after.jpg'
        return before, after
    elif data=='southern_nebula_internet':
        # Image slider demo
        before = 'https://erdogant.github.io/datasets/images/southern_nebula_before.jpg'
        after = 'https://erdogant.github.io/datasets/images/southern_nebula_after.jpg'
        return before, after
    elif data=='unsplash':
        # Image slider demo
        before = 'https://erdogant.github.io/datasets/images/unsplash_before.jpg'
        after = 'https://erdogant.github.io/datasets/images/unsplash_after.jpg'
        return before, after
    elif data=='cancer':
        url='https://erdogant.github.io/datasets/cancer_dataset.zip'
    elif data=='iris':
        url='https://erdogant.github.io/datasets/iris_dataset.zip'
        sep=';'
    elif data=='breast_cancer':
        url='https://erdogant.github.io/datasets/breast_cancer_dataset.zip'
        sep=';'
    elif data=='occupancy':
        url='https://erdogant.github.io/datasets/UCI_Occupancy_Detection.zip'
        sep=','
    elif data=='climate':
        url='https://erdogant.github.io/datasets/kaggle_daily_delhi_climate_test.zip'
    elif data=='mnist':
        url='https://erdogant.github.io/datasets/mnist.zip'
        sep=';'
    elif data=='animals':
        # example data with three levels and a single value field
        data = {'group1': ['Animal', 'Animal', 'Animal', 'Plant', 'Animal'],
                'group2': ['Mammal', 'Mammal', 'Fish', 'Tree', 'Fish'],
                'group3': ['Fox',    'Lion',   'Cod',  'Oak',  'Ape'],
                'weight': [35000, 25000, 10000, 1500, 1750]}
        df = pd.DataFrame.from_dict(data)
        return df

    if url is None:
        logger.info('Nothing to download.')
        return None

    curpath = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
    filename = os.path.basename(urlparse(url).path)
    PATH_TO_DATA = os.path.join(curpath, filename)
    if not os.path.isdir(curpath):
        os.makedirs(curpath, exist_ok=True)

    # Check file exists.
    if not os.path.isfile(PATH_TO_DATA):
        logger.info('Downloading [%s] dataset from github source..' %(data))
        wget(url, PATH_TO_DATA)

    csvfile = unzip(PATH_TO_DATA, ext=ext)

    # Import local dataset
    logger.info('Import dataset: [%s]' %(data))
    if data=='movingbubbles':
        X = Movingbubbles.import_example(csvfile)
        labels = "{'index': '0', 'short': 'Sleeping', 'desc': 'Sleeping'}, {'index': '1', 'short': 'Personal Care', 'desc': 'Personal Care'}, {'index': '2', 'short': 'Eating & Drinking', 'desc': 'Eating and Drinking'}, {'index': '3', 'short': 'Education', 'desc': 'Education'}, {'index': '4', 'short': 'Work', 'desc': 'Work and Work-Related Activities'}, {'index': '5', 'short': 'Housework', 'desc': 'Household Activities'}, {'index': '6', 'short': 'Household Care', 'desc': 'Caring for and Helping Household Members'}, {'index': '7', 'short': 'Non-Household Care', 'desc': 'Caring for and Helping Non-Household Members'}, {'index': '8', 'short': 'Shopping', 'desc': 'Consumer Purchases'}, {'index': '9', 'short': 'Pro. Care Services', 'desc': 'Professional and Personal Care Services'}, {'index': '10', 'short': 'Leisure', 'desc': 'Socializing, Relaxing, and Leisure'}, {'index': '11', 'short': 'Sports', 'desc': 'Sports, Exercise, and Recreation'}, {'index': '12', 'short': 'Religion', 'desc': 'Religious and Spiritual Activities'}, {'index': '13', 'short': 'Volunteering', 'desc': 'Volunteer Activities'}, {'index': '14', 'short': 'Phone Calls', 'desc': 'Telephone Calls'}, {'index': '15', 'short': 'Misc.', 'desc': 'Other'}, {'index': '16', 'short': 'Traveling', 'desc': 'Traveling'}"
        df = {}
        df['type'] = 'movingbubbles'
        df['data'] = X
        df['labels'] = labels
    elif data=='energy':
        df = pd.read_csv(csvfile)
        df.rename(columns={'value': 'weight'}, inplace=True)
        df[['source', 'target']] = df[['source', 'target']].astype(str)
    elif data=='stormofswords':
        df = pd.read_csv(csvfile)
        # df.rename(columns={'weight':'value'}, inplace=True)
    elif data=='southern_nebula':
        img_before = os.path.join(os.path.split(csvfile)[0], 'southern_nebula_before.jpg')
        img_after = os.path.join(os.path.split(csvfile)[0], 'southern_nebula_after.jpg')
        return img_before, img_after
    elif data=='cancer':
        df = pd.read_csv(PATH_TO_DATA, sep=',')
        df.rename(columns={'tsneX': 'x', 'tsneY': 'y', 'labx': 'labels'}, inplace=True)
        df.set_index(df['labels'], inplace=True)
    else:
        df = pd.read_csv(PATH_TO_DATA, sep=sep)

    # Return
    return df


# %%
def random_date(start, end, prop, dt_format='%d-%m-%Y %H:%M:%S', strftime=True):
    """Create random dateTimes."""
    return str_time_prop(start, end, prop, dt_format=dt_format, strftime=strftime)


def str_time_prop(start, end, prop, dt_format='%d-%m-%Y %H:%M:%S', strftime=True):
    """Get a time at a proportion of a range of two formatted times.

    start and end should be strings specifying times formatted in the
    given format (strftime-style), giving an interval [start, end].
    prop specifies how a proportion of the interval to be taken after
    start.  The returned time will be in the specified format.

    """
    stime = time.mktime(time.strptime(start, dt_format))
    etime = time.mktime(time.strptime(end, dt_format))
    ptime = stime + prop * (etime - stime)
    if strftime:
        return time.strftime(dt_format, time.localtime(ptime))
    else:
        return time.localtime(ptime)


# %% Retrieve files files.
def wget(url, writepath):
    """Retrieve file from url.

    Parameters
    ----------
    url : str.
        Internet source.
    writepath : str.
        Directory to write the file.

    Returns
    -------
    None.

    """
    r = requests.get(url, stream=True)
    with open(writepath, "wb") as fd:
        for chunk in r.iter_content(chunk_size=1024):
            fd.write(chunk)


# %% unzip
def unzip(path_to_zip, ext=''):
    """Unzip files.

    Parameters
    ----------
    path_to_zip : str
        Path of the zip file.

    Returns
    -------
    getpath : str
        Path containing the unzipped files.

    """
    getpath = None
    if path_to_zip[-4:]=='.zip':
        if not os.path.isdir(path_to_zip):
            logger.info('Extracting files..')
            pathname, _ = os.path.split(path_to_zip)
            # Unzip
            zip_ref = zipfile.ZipFile(path_to_zip, 'r')
            zip_ref.extractall(pathname)
            zip_ref.close()
            getpath = path_to_zip.replace('.zip', ext)
    else:
        logger.warning('Input is not a zip file: [%s]', path_to_zip)
    # Return
    return getpath


# %%
def set_logger(verbose: [str, int] = 'info'):
    """Set the logger for verbosity messages.

    Parameters
    ----------
    verbose : [str, int], default is 'info' or 20
        Set the verbose messages using string or integer values.
            * 0, 60, None, 'silent', 'off', 'no']: No message.
            * 10, 'debug': Messages from debug level and higher.
            * 20, 'info': Messages from info level and higher.
            * 30, 'warning': Messages from warning level and higher.
            * 50, 'critical': Messages from critical level and higher.

    Returns
    -------
    None.

    Examples
    --------
    >>> # Set the logger to warning
    >>> set_logger(verbose='warning')
    >>>
    >>> # Test with different messages
    >>> logger.debug("Hello debug")
    >>> logger.info("Hello info")
    >>> logger.warning("Hello warning")
    >>> logger.critical("Hello critical")
    >>>
    """
    # Set 0 and None as no messages.
    if (verbose==0) or (verbose is None):
        verbose=60
    # Convert str to levels
    if isinstance(verbose, str):
        levels = {'silent': 60,
                  'off': 60,
                  'no': 60,
                  'debug': 10,
                  'info': 20,
                  'warning': 30,
                  'critical': 50}
        verbose = levels[verbose]

    # Show examples
    logger.setLevel(verbose)

# %%
def disable_tqdm():
    """Set the logger for verbosity messages."""
    return (True if (logger.getEffectiveLevel()>=30) else False)


# %% Do checks
def set_chart_func(chart=None, logger=None):
    """Library compatibility checks.

    Returns
    -------
    chart function as Object.

    """
    # Check the presence of the chart name.
    if chart is not None:
        if logger is not None: logger.info('Initializing [%s]' %(chart))
        chart = str.capitalize(chart)
        if np.isin(chart, ['Chord', 'Sankey', 'Timeseries', 'Violin', 'Movingbubbles', 'Scatter', 'Heatmap', 'Matrix', 'Treemap']):
            chart=eval(chart)
        else:
            if logger is not None: logger.info('%s is not yet implemented in such manner.' %(chart))
            chart = None

    return chart
