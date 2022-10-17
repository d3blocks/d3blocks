"""d3blocks library."""
import os
from sys import platform

import pandas as pd
import requests
from urllib.parse import urlparse
import logging
import numpy as np
import zipfile
import tempfile
import webbrowser
import random
import time
import colourmap
from typing import List, Union, Tuple
from ismember import ismember

import d3blocks.movingbubbles.Movingbubbles as Movingbubbles
import d3blocks.timeseries.Timeseries as Timeseries
import d3blocks.sankey.Sankey as Sankey
import d3blocks.imageslider.Imageslider as Imageslider
import d3blocks.chord.Chord as Chord
import d3blocks.scatter.Scatter as Scatter
import d3blocks.violin.Violin as Violin
import d3blocks.particles.Particles as Particles
from d3blocks.utils import pre_processing, remove_quotes, convert_dataframe_dict

# ###################### DEBUG ONLY ###################
# import movingbubbles.Movingbubbles as Movingbubbles
# import timeseries.Timeseries as Timeseries
# import sankey.Sankey as Sankey
# import imageslider.Imageslider as Imageslider
# import chord.Chord as Chord
# import scatter.Scatter as Scatter
# import violin.Violin as Violin
# import particles.Particles as Particles
# from utils import pre_processing, remove_quotes, convert_dataframe_dict
# #####################################################

import d3graph as d3network
from d3heatmap import d3heatmap

logger = logging.getLogger('')
for handler in logger.handlers[:]:  # get rid of existing old handlers
    logger.removeHandler(handler)
console = logging.StreamHandler()
formatter = logging.Formatter('[d3blocks] >%(levelname)s> %(message)s')
console.setFormatter(formatter)
logger.addHandler(console)
logger = logging.getLogger()


class D3Blocks():
    """D3Blocks.

    Parameters
    ----------
    cmap : String, (default: 'inferno')
        All colors can be reversed with '_r', e.g. 'binary' to 'binary_r'
        'Set1','Set2','rainbow','bwr','binary','seismic','Blues','Reds','Pastel1','Paired','twilight','hsv'
    dt_format : str
        '%d-%m-%Y %H:%M:%S'.
    whitelist : str, optional
        Keep only columns containing this (sub)string (case insensitive)
    frame : Bool, (default: True)
        True: Return in DataFrame.
        False: Return in dictionary.
    verbose : int, optional
        Verbose message. The default is 20.

    Returns
    -------
    None.

    References
    ----------
    * Blog - D3Blocks: https://towardsdatascience.com/d3blocks-the-python-library-to-create-interactive-and-standalone-d3js-charts-3dda98ce97d4
    * Blog - D3Graph: https://towardsdatascience.com/creating-beautiful-stand-alone-interactive-d3-charts-with-python-804117cb95a7
    * Github: https://github.com/d3blocks/d3blocks
    * Documentation: https://d3blocks.github.io/d3blocks/

    """

    def __init__(self, cmap='Set1', dt_format='%d-%m-%Y %H:%M:%S', whitelist=None, frame=True, verbose=20):
        """Initialize d3blocks with user-defined parameters."""
        # Clean
        self._clean(clean_config=True)
        # Some library compatibily checks
        library_compatibility_checks()
        # Initialize empty config
        self.config = {}
        self.config['cmap'] = cmap
        self.config['frame'] = frame
        self.config['whitelist'] = whitelist
        self.config['dt_format'] = dt_format
        self.config['curpath'] = os.path.dirname(os.path.abspath(__file__))
        # Set the logger
        set_logger(verbose=verbose)

    def particles(self,
                  text,
                  radius=3,
                  collision=0.05,
                  fontsize=180,
                  spacing=8,
                  cmap='Turbo',
                  background='#000000',
                  title='Particles - D3blocks',
                  filepath='particles.html',
                  figsize=[900, 200],
                  showfig=True,
                  overwrite=True):
        """Particles block.

        Description
        -----------
        The particles plot is to turn any word into an interactive visualization. With a mouse-move or touch, the particle
        bounce and then return to their original place. Various properties can be changed such as the bouncing,
        particle size, and colors. The original javascript is forked from Ian Johnson's Block.

        Parameters
        ----------
        text : string
            String to be visualized
        radius : float (Default: 3)
            Size of the particles.
        collision : float, (default: 0.1)
            Response of the interaction. Higher means that more collisions are prevented.
        fontsize : int (Default: 250)
            Text fontsize.
            When increasing: also increase width and slighly the spacing.
        spacing : int (Default: 10)
            The number of particles that fit in the text.
            A larger spacing reults in less particles.
            A smaller spacing reults in more particles.
        cmap : String (default: 'Set2')
            Color schemes can be found here: https://observablehq.com/@d3/color-schemes
            'Turbo', 'Rainbow', 'Blues', 'Reds', 'Inferno', 'Magma'
        background : String (default: '#000000')
            Background color.
        title : String, (default: None)
            Title of the figure.
        filepath : String, (Default: user temp directory)
            File path to save the output
        figsize : tuple, (default: (800, 600))
            Size of the figure in the browser, [width, height].
        showfig : bool, (default: True)
            Open the window to show the particles.
        overwrite : bool, (default: True)
            Overwrite the output html in the destination directory.

        Returns
        -------
        None

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
        >>> d3.particles('D3Blocks', filepath='D3Blocks.html', collision=0.05, spacing=7, figsize=[750, 150], fontsize=130, cmap='Turbo', background='#ffffff')
        >>> #

        References
        ----------
        * https://d3blocks.github.io/d3blocks/pages/html/Particles.html

        """
        # Cleaning
        self._clean(clean_config=False)

        # Set config
        self.config['chart'] ='Particles'
        self.config['filepath'] = self.set_path(filepath)
        self.config['title'] = title
        self.config['showfig'] = showfig
        self.config['overwrite'] = overwrite
        self.config['figsize'] = figsize
        self.config['cmap'] = cmap
        self.config['background'] = background
        self.config['radius'] = radius
        self.config['collision'] = collision
        self.config['fontsize'] = '"' + str(fontsize) + 'px"'
        self.config['spacing'] = spacing

        # Create the plot
        self.config = Particles.show(text, self.config)
        # Open the webbrowser
        if self.config['showfig']: self.showfig(logger=logger)

    def violin(self,
               x,
               y,
               size=5,
               color=None,
               bins=20,
               x_order=None,
               opacity=0.8,
               stroke='#ffffff',
               tooltip=None,
               title='Violin - D3blocks',
               filepath='violin.html',
               figsize=[None, None],
               ylim=[None, None],
               cmap='inferno',
               showfig=True,
               overwrite=True):
        """Violin block.

        Description
        -----------
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
            '#002147' : All dots are get the same hex color.
            None: The colors are generated on value using the colormap specified in cmap.
            ['#000000', '#ffffff',...]: list/array of hex colors with same size as y.
        bins : Int (default: 20)
            The bin size is the 'resolution' of the violin plot.
        x_order : list of String (default: None)
            The order of the class labels (x-axis).
            ["setosa", "versicolor", "virginica"]
        opacity: float or list/array [0-1]
            Opacity of the dot. Shoud be same size as (x,y)
        stroke: list/array of hex colors with same size as (x,y)
            Edgecolor of dot in hex colors.
        tooltip: list of labels with same size as (x,y)
            labels of the samples.
        cmap : String, (default: 'inferno')
            All colors can be reversed with '_r', e.g. 'binary' to 'binary_r'
            'Set1','Set2','rainbow','bwr','binary','seismic','Blues','Reds','Pastel1','Paired','twilight','hsv'
        title : String, (default: None)
            Title of the figure.
        filepath : String, (Default: user temp directory)
            File path to save the output
        figsize : tuple, (default: (None, 500))
            Size of the figure in the browser, [width, height].
            The width is determined based on the number of class labels x.
        showfig : bool, (default: True)
            Open the window to show the chart.
        overwrite : bool, (default: True)
            Overwrite the output html in the destination directory.

        Returns
        -------
        df : pd.DataFrame()
            DataFrame.

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
        >>> # Plot
        >>> d3.violin(x=df['labels'].values, y=df['age'].values, tooltip=tooltip, bins=50, size=df['survival_months'].values/10, x_order=['acc','kich', 'brca','lgg','blca','coad','ov'], filepath='violine.html', figsize=[900, None])
        >>> #

        References
        ----------
        * https://d3blocks.github.io/d3blocks/pages/html/Violin.html

        """
        # Cleaning
        self._clean(clean_config=False)

        if len(x)!=len(y): raise Exception(logger.error('input parameter "x" should be of size of "y".'))
        if size is None: raise Exception(logger.error('input parameter "size" should have value >0.'))
        if isinstance(size, (list, np.ndarray)) and (len(size)!=len(x)): raise Exception(logger.error('input parameter "s" should be of same size of (x, y).'))
        if stroke is None: raise Exception(logger.error('input parameter "stroke" should have hex value.'))
        if isinstance(stroke, (list, np.ndarray)) and (len(stroke)!=len(x)): raise Exception(logger.error('input parameter "stroke" should be of same size of (x, y).'))
        if opacity is None: raise Exception(logger.error('input parameter "opacity" should have value in range [0..1].'))
        if isinstance(opacity, (list, np.ndarray)) and (len(opacity)!=len(x)): raise Exception(logger.error('input parameter "opacity" should be of same size of (x, y).'))

        if bins is None: bins=20
        self.config['bins'] = bins
        self.config['chart'] ='violin'
        self.config['cmap'] = cmap
        self.config['filepath'] = self.set_path(filepath)
        self.config['title'] = title
        self.config['ylim'] = ylim
        self.config['x_order'] = x_order
        self.config['showfig'] = showfig
        self.config['overwrite'] = overwrite
        self.config['figsize'] = figsize

        # Remvove quotes from source-target labels
        df = Violin.label_properties(x, y, config=self.config, color=color, size=size, stroke=stroke, opacity=opacity, tooltip=tooltip, logger=logger)

        # Set default label properties
        if not hasattr(self, 'labels'):
            self.set_node_properties(labels=np.unique(df['x'].values), cmap=self.config['cmap'])

        # Create the plot
        self.config = Violin.show(df, config=self.config, labels=self.labels)
        # Open the webbrowser
        if self.config['showfig']: self.showfig(logger=logger)

    def scatter(self,
                x,
                y,
                x1=None,
                y1=None,
                x2=None,
                y2=None,
                size=3,
                color='#002147',
                c_gradient=None,
                opacity=0.8,
                stroke='#ffffff',
                tooltip=None,
                cmap='tab20',
                scale=False,
                label_radio=['(x, y)', '(x1, y1)', '(x2, y2)'],
                title='Scatter - D3blocks',
                filepath='scatter.html',
                figsize=[900, 600],
                xlim=[None, None],
                ylim=[None, None],
                showfig=True,
                overwrite=True):
        """Scatterplot block.

        Description
        -----------
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
        size: list/array of with same size as (x,y). Can be of type str or int.
            Size of the samples.
        color: list/array of hex colors with same size as (x,y)
            '#ffffff' : All dots are get the same hex color.
            None: The same color as for c is applied.
            ['#000000', '#ffffff',...]: list/array of hex colors with same size as (x,y)
        c_gradient : String, (default: None)
            Make a lineair gradient based on the density for the particular class label.
            '#FFFFFF'
        stroke: list/array of hex colors with same size as (x,y)
            Edgecolor of dotsize in hex colors.
        opacity: float or list/array [0-1]
            Opacity of the dot. Shoud be same size as (x,y)
        tooltip: list of labels with same size as (x,y)
            labels of the samples.
        cmap : String, (default: 'inferno')
            All colors can be reversed with '_r', e.g. 'binary' to 'binary_r'
            'Set1','Set2','rainbow','bwr','binary','seismic','Blues','Reds','Pastel1','Paired','twilight','hsv'
        scale: Bool, optional
            Scale datapoints. The default is False.
        label_radio: List ['(x, y)', '(x1, y1)', '(x2, y2)']
            The labels used for the radiobuttons.
        title : String, (default: None)
            Title of the figure.
        filepath : String, (Default: user temp directory)
            File path to save the output
        figsize : tuple, (default: (800, 600))
            Size of the figure in the browser, [width, height].
        set_xlim : tuple, (default: [None, None])
            Width of the x-axis: The default is extracted from the data with 10% spacing.
        set_ylim : tuple, (default: [None, None])
            Height of the y-axis: The default is extracted from the data with 10% spacing.
        showfig : bool, (default: True)
            Open the window to show the chart.
        overwrite : bool, (default: True)
            Overwrite the output html in the destination directory.

        Returns
        -------
        df : pd.DataFrame()
            DataFrame.

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
        >>> # Example 1: Scatter plot
        >>> d3.scatter(df['x'].values, df['y'].values, size=size, color=df.index.values, stroke='#000000', opacity=0.4, tooltip=tooltip, filepath='scatter_demo.html', cmap='tab20')
        >>> #
        >>> # Example 2: Scatter plot with transitions. Note that scale is set to True to make the axis comparible to each other
        >>> d3.scatter(df['x'].values, df['y'].values, x1=df['PC1'].values, y1=df['PC2'].values, label_radio=['tSNE', 'PCA'], scale=True, size=size, color=df.index.values, stroke='#000000', opacity=0.4, tooltip=tooltip, filepath='scatter_transitions2.html', cmap='tab20')
        >>> #
        >>> # Example 3: Scatter plot with transitions. Note that scale is set to True to make the axis comparible to each other
        >>> d3.scatter(df['x'].values, df['y'].values, x1=df['PC1'].values, y1=df['PC2'].values, x2=df['PC2'].values, y2=df['PC1'].values, label_radio=['tSNE', 'PCA', 'PCA_reverse'], scale=True, size=size, color=df.index.values, stroke='#000000', opacity=0.4, tooltip=tooltip, filepath='scatter_transitions3.html', cmap='tab20')
        >>> #

        References
        ----------
        * https://d3blocks.github.io/d3blocks/pages/html/Scatter.html

        """
        # Cleaning
        self._clean(clean_config=False)

        # Set config
        self.config['chart'] ='scatter'
        self.config['filepath'] = self.set_path(filepath)
        self.config['title'] = title
        self.config['xlim'] = xlim
        self.config['ylim'] = ylim
        self.config['showfig'] = showfig
        self.config['overwrite'] = overwrite
        self.config['figsize'] = figsize
        self.config['scale'] = scale
        self.config['cmap'] = cmap

        # Set the radio button and visibility of the labels
        self.config['radio_button_visible'] = [("display:none;" if (x1 is None) else ""), ("display:none;" if (x1 is None) else ""), ("display:none;" if (x2 is None) else "")]
        self.config['label_radio'] = label_radio
        if ("display:none" in self.config['radio_button_visible'][0]): self.config['label_radio'][0]=""
        if ("display:none" in self.config['radio_button_visible'][1]): self.config['label_radio'][1]=""
        if len(self.config['label_radio'])==3 and ("display:none" in self.config['radio_button_visible'][2]):
            self.config['label_radio'][2]=""
        elif len(self.config['label_radio'])==2:
            self.config['label_radio'].append("")

        # Check exceptions
        Scatter.check_exceptions(x, y, x1, y1, x2, y2, size, color, tooltip, self.config, logger)
        # Preprocessing
        df, labels = Scatter.preprocessing(x, y, x1, y1, x2, y2, color, size, tooltip, opacity, c_gradient, stroke, self.config['cmap'], self.config['scale'], logger=logger)
        # Set default label properties
        if not hasattr(self, 'labels'): self.labels = labels
        # Make het scatterplot
        self.config = Scatter.show(df, self.config)
        # Open the webbrowser
        if self.config['showfig']: self.showfig(logger=logger)

    def chord(self,
              df,
              color=None,
              opacity=None,
              fontsize=10,
              cmap='tab20',
              title='Chord - D3blocks',
              filepath='chord.html',
              figsize=[900, 900],
              showfig=True,
              overwrite=True):
        """Chord block.

        Description
        -----------
        A chord represents flows or connections between several entities or nodes.
        Each entity is represented by a fragment on the outer part of the circular layout.
        Then, arcs are drawn between each entity. The size of the arc is proportional to the importance of the flow.

        Parameters
        ----------
        df : pd.DataFrame()
            Input data containing the following columns:
            'source'
            'target'
            'weight'
            'color' (optional)
            'opacity'  (optional)
        color: list/array of str (default: None)
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
        fontsize : int, (default: 8)
            Fontsize.
        cmap : String, (default: 'tab20')
            colormap is only used in case color=None.
            All colors can be reversed with '_r', e.g. 'binary' to 'binary_r'
            'Set1','Set2','rainbow','bwr','binary','seismic','Blues','Reds','Pastel1','Paired','twilight','hsv'
        title : String, (default: None)
            Title of the figure.
        filepath : String, (Default: user temp directory)
            File path to save the output
        figsize : tuple, (default: (800, 600))
            Size of the figure in the browser, [width, height].
        showfig : bool, (default: True)
            Open the window to show the chart.
        overwrite : bool, (default: True)
            Overwrite the output html in the destination directory.

        Returns
        -------
        df : pd.DataFrame()
            DataFrame.

        Examples
        --------
        >>> # Load d3blocks
        >>> from d3blocks import D3Blocks
        >>> #
        >>> # Initialize
        >>> d3 = D3Blocks()
        >>> #
        >>> # Load example data
        >>> df = d3.import_example('stormofswords')
        >>> #
        >>> # Plot
        >>> d3.chord(df)

        References
        ----------
        * https://d3blocks.github.io/d3blocks/pages/html/Chord.html

        """
        # Cleaning
        self._clean(clean_config=False)

        # Store properties
        self.config['chart'] ='chord'
        self.config['filepath'] = self.set_path(filepath)
        self.config['fontsize'] = fontsize
        self.config['title'] = title
        self.config['showfig'] = showfig
        self.config['overwrite'] = overwrite
        self.config['figsize'] = figsize
        self.config['cmap'] = cmap

        # Convert to Frame
        df = convert_dataframe_dict(df.copy(), frame=True)

        # Set label properties
        if not hasattr(self, 'labels'):
            self.set_node_properties(labels=df[['source', 'target']], cmap=self.config['cmap'])

        # Set edge properties based on input parameters
        self.set_edge_properties(df, color=color, opacity=opacity, cmap=cmap, nodes=self.labels, logger=logger)

        # Create the plot
        self.config = Chord.show(self.edge_properties, self.config, labels=self.labels, logger=logger)
        # Open the webbrowser
        if self.config['showfig']: self.showfig(logger=logger)

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
                    overwrite=True):
        """Imageslider Block.

        Description
        -----------
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
            True: Scaling image
            False: Leave image untouched
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
        filepath : String, (Default: user temp directory)
            File path to save the output
        figsize : tuple, (default: [800, None])
            Size of the figure in the browser, [width, None]. The heigth is changed according to the width.
        showfig : bool, (default: True)
            Open the window to show the chart.
        overwrite : bool, (default: True)
            Overwrite the output html in the destination directory.

        Returns
        -------
        None

        Examples
        --------
        >>> # Load d3blocks
        >>> from d3blocks import D3Blocks
        >>>
        >>> # Initialize
        >>> d3 = D3Blocks()
        >>>
        >>> # Local images
        >>> img_before, img_after = d3.import_example('southern_nebula')
        >>>
        >>> # Internet location
        >>> img_before, img_after = d3.import_example('southern_nebula_internet')
        >>>
        >>> # Read the image in array
        >>> img_before = cv2.imread(img_before, -1)
        >>> img_after = cv2.imread(img_after, -1)
        >>>
        >>> # Plot
        >>> d3.imageslider(img_before, img_after)
        >>>
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
        self.config['filepath'] = self.set_path(filepath)
        self.config['title'] = title
        self.config['showfig'] = showfig
        self.config['overwrite'] = overwrite
        self.config['figsize'] = figsize

        # Preprocessing
        self.config = Imageslider.preprocessing(self.config, logger=logger)
        # Create the plot
        self.config = Imageslider.show(self.config, logger)
        # Open the webbrowser
        if self.config['showfig']: self.showfig(logger=logger)

    def heatmap(self,
                df,
                vmax=None,
                stroke='red',
                fontsize=10,
                title='Heatmap - D3blocks',
                description='',
                filepath='heatmap.html',
                figsize=[720, 720],
                showfig=True,
                overwrite=True):
        """Heatmap block.

        Description
        -----------
        heatmap is a module in d3blocks to create interactive heatmaps.
        The heatmap is utilized from the d3heatmap library which creates heatmaps from an (adjacency) matrix.
        In the following example, we load the energy dataset, reformat the data into an adjacency matrix, and then
        create the heatmap. The heatmap can be clustered interactively. The javascript code is forked from Mike Bostock
        and then Pythonized.

        Parameters
        ----------
        df : pd.DataFrame()
            Input data is an adjacency matrix for which the columns and rows are the names of the variables.
        vmax : Bool, (default: 100).
            Range of colors starting with maximum value. Increasing this value will color the cells more discrete.
                * 1 : cells above value >1 are capped.
                * None : cells are colored based on the maximum value in the input data.
        stroke : String, (default: 'red').
            Color of the recangle when hovering over a cell.
                * 'red'
                * 'black'
        fontsize : int, (default: 14)
            Fontsize of the states.
        title : String, (default: None)
            Title of the figure.
        description : String, (default: 'Heatmap description')
            Description text of the heatmap.
        filepath : String, (Default: user temp directory)
            File path to save the output
        figsize : tuple, (default: (800, 600))
            Size of the figure in the browser, [width, height].
        showfig : bool, (default: True)
            Open the window to show the chart.
        overwrite : bool, (default: True)
            Overwrite the output html in the destination directory.

        Returns
        -------
        None.

        Examples
        --------
        >>> # Initialize
        >>> d3 = D3Blocks()
        >>> #
        >>> # Import example
        >>> df = d3.import_example('energy') # 'bigbang', 'stormofswords'
        >>> #
        >>> d3.heatmap(adjmat, showfig=True, figsize=[400, 400], title='', filepath='heatmap.html')
        >>> #

        References
        ----------
        * Github: https://github.com/erdogant/d3heatmap
        * Documentation: https://d3blocks.github.io/d3blocks/pages/html/Heatmap.html

        """
        # Cleaning
        self._clean(clean_config=False)

        # Set configs
        self.config['chart'] ='heatmap'
        self.config['title'] = title
        self.config['description'] = description
        self.config['filepath'] = self.set_path(filepath)
        self.config['figsize'] = figsize
        self.config['showfig'] = showfig
        self.config['overwrite'] = overwrite
        self.config['vmax'] = vmax
        self.config['stroke'] = stroke

        # Copy of data
        df = df.copy()

        # Convert vector to adjmat
        adjmat = d3network.vec2adjmat(df['source'], df['target'], weight=df['weight'])
        # Create heatmap chart
        d3heatmap.heatmap(adjmat, vmax=self.config['vmax'], stroke=self.config['stroke'], width=self.config['figsize'][0], height=self.config['figsize'][1], path=self.config['filepath'], title=title, description=self.config['description'], showfig=self.config['showfig'])

    def d3graph(self,
                df,
                title='D3graph - D3blocks',
                filepath='d3graph.html',
                figsize=[1500, 800],
                showfig=True,
                overwrite=True,
                collision=0.5,
                charge=400,
                slider=[None, None],
                scaler='zscore'):
        """d3graph block.

        Description
        -----------
        d3graph is a integrated in d3blocks and is to create interactive and stand-alone D3 force-directed graphs.
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
            'source'
            'target'
            'weight'
        title : String, (default: None)
            Title of the figure.
        filepath : String, (Default: user temp directory)
            File path to save the output
        figsize : tuple, (default: (800, 600))
            Size of the figure in the browser, [width, height].
        showfig : bool, (default: True)
            Open the window to show the graph.
        overwrite : bool, (default: True)
            Overwrite the output html in the destination directory.
        collision : float, (default: 0.5)
            Response of the network. Higher means that more collisions are prevented.
        charge : int, (default: 400)
            Edge length of the network. Towards zero becomes a dense network. Higher make edges longer.
        slider : typle [min: int, max: int]:, (default: [None, None])
            Slider is automatically set to the range of the edge weights.

        Returns
        -------
        None.

        Examples
        --------
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
        >>> d3.D3graph.set_node_properties(color='cluster')
        >>> d3.D3graph.node_properties['Solar']['size']=30
        >>> d3.D3graph.node_properties['Solar']['edge_color']='#FF0000'
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
        self.config['filepath'] = self.set_path(filepath)
        self.config['figsize'] = figsize
        self.config['showfig'] = showfig
        self.config['overwrite'] = overwrite
        self.config['collision'] = collision
        self.config['charge'] = charge * -1
        self.config['slider'] = slider

        # Copy of data
        df = df.copy()
        # Remvove quotes from source-target labels
        df = remove_quotes(df)
        # Initialize network graph
        self.D3graph = d3network.d3graph(collision=collision, charge=charge, slider=slider)
        # Convert vector to adjmat
        adjmat = d3network.vec2adjmat(df['source'], df['target'], weight=df['weight'])
        # Create default graph
        self.D3graph.graph(adjmat, scaler=scaler)
        # Open the webbrowser
        self.D3graph.show(figsize=figsize, title=title, filepath=filepath, showfig=showfig, overwrite=overwrite)

    def sankey(self,
               df,
               title='Sankey - D3blocks',
               filepath='sankey.html',
               figsize=[800, 600],
               node={"align": "justify", "width": 15, "padding": 15, "color": "currentColor"},
               link={"color": "source-target", "stroke_opacity": 0.5, 'color_static': '#D3D3D3'},
               margin={"top": 5, "right": 1, "bottom": 5, "left": 1},
               showfig=True,
               overwrite=True):
        """Sankey block.

        Description
        -----------
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
            'source'
            'target'
            'weight'
        title : String, (default: None)
            Title of the figure.
        filepath : String, (Default: user temp directory)
            File path to save the output
        figsize : tuple, (default: (800, 600))
            Size of the figure in the browser, [width, height].
        link : dict.
            "linkColor" : "source", "target", "source-target"
            "linkStrokeOpacity" : 0.5
            "color_static": '#0f0f0f' or "grey", "blue", "red" etc
        margin : dict.
            margin, in pixels
            "top" : 5
            "right" : 1
            "bottom" : 5
            "left" : 1
        node : dict.
            "align" : "left", "right", "justify", "center"
            "width" : 15 (width of the node rectangles)
            "padding" : 15 (vertical seperation between the nodes)
            "color" : "currentColor", "grey", "black", "red", etc
        showfig : bool, (default: True)
            Open the window to show the chart.
        overwrite : bool, (default: True)
            Overwrite the output html in the destination directory.

        Returns
        -------
        df : pd.DataFrame()
            DataFrame.

        Examples
        --------
        >>> # Load d3blocks
        >>> from d3blocks import D3Blocks
        >>> #
        >>> # Initialize
        >>> d3 = D3Blocks()
        >>> #
        >>> # Load example data
        >>> df = d3.import_example('energy')  # 'stormofswords'
        >>> #
        >>> # Plot
        >>> d3.sankey(df, filepath='sankey.html')

        References
        ----------
        * https://d3blocks.github.io/d3blocks/pages/html/Sankey.html

        """
        # Cleaning
        self._clean(clean_config=False)

        # Store paramters
        self.config['chart'] ='sankey'
        self.config['filepath'] = self.set_path(filepath)
        self.config['title'] = title
        self.config['showfig'] = showfig
        self.config['overwrite'] = overwrite
        self.config['figsize'] = figsize
        self.config['link'] = {**{"color": "source-target", "stroke_opacity": 0.5, "color_static": '#D3D3D3'}, **link}
        self.config['node'] = {**{"align": "justify", "width": 15, "padding": 15, "color": "currentColor"}, **node}
        self.config['margin'] = {**{"top": 5, "right": 1, "bottom": 5, "left": 1}, **margin}

        # Convert to Frame
        df = convert_dataframe_dict(df.copy(), frame=True)
        # Remove quotes from source-target labels
        df = pre_processing(df)

        # Set default label properties
        if not hasattr(self, 'labels'):
            self.set_node_properties(labels=np.unique(df[['source', 'target']].values.ravel()), cmap=self.config['cmap'])

        # Set edge properties
        self.set_edge_properties(df)

        # Create the plot
        self.config = Sankey.show(self.edge_properties, self.config, labels=self.labels)
        # Open the webbrowser
        if self.config['showfig']: self.showfig(logger=logger)
        # Return config
        # return self.config

    def movingbubbles(self,
                      df,
                      datetime='datetime',
                      sample_id='sample_id',
                      state='state',
                      center=None,
                      damper=1,
                      fontsize=14,
                      reset_time='day',
                      standardize=None,
                      speed={"slow": 1000, "medium": 200, "fast": 50},
                      figsize=[780, 800],
                      note=None,
                      time_notes=None,
                      title='Movingbubbles - D3Blocks',
                      filepath='movingbubbles.html',
                      showfig=True,
                      overwrite=True):
        """MovingBubbles block.

        Description
        -----------
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
        dampler : float, (default: 1)
            Movement of sample: [0.1 - 10]. A smaller number is slower/smoother movement.
        fontsize : int, (default: 14)
            Fontsize of the states.
        standardize : str. (default: None)
            Method to standardize the data.
            None: standardize over the entire timeframe. Sample_ids are dependent to each other.
            'samplewise': Standardize per sample_id. Thus the sample_ids are independent of each other.
        reset_time : String, (default: 'day')
            'day'  : Every 24h de the day start over again.
            'year' : Every 365 days the year starts over again.
        speed : dict, (default: {"slow": 1000, "medium": 200, "fast": 50})
            The final html file contains three buttons for speed movements. The lower the value, the faster the time moves.
        figsize : tuple, (default: (1500, 800))
            Size of the figure in the browser, [width, height].
        note : str, (default: None)
            A specific note, such as project description can be put on the html page.
        time_notes : dict, (default: None)
            The time notes will be shown between specific time points.
            time_notes = [{"start_minute": 1, "stop_minute": 5, "note": "Enter your note here and it is shown between 1 min and 5 min."}]
            time_notes.append[{"start_minute": 6, "stop_minute": 10, "note": "Enter your second note here and it is shown between 6 min and 10 min."}]
        title : String, (default: None)
            Title of the figure.
        filepath : String, (Default: user temp directory)
            File path to save the output
        showfig : bool, (default: True)
            Open the window to show the chart.
        overwrite : bool, (default: True)
            Overwrite the existing html file.

        Returns
        -------
        pd.DataFrame()

        Examples
        --------
        >>> # Load d3blocks
        >>> from d3blocks import D3Blocks
        >>> #
        >>> # Initialize
        >>> d3 = D3Blocks()
        >>> #
        >>> # Load example data
        >>> df = d3.import_example('random_time', n=10000, c=300, date_start="17-12-1903 00:10:05", date_stop="17-12-1903 23:59:59")
        >>> #
        >>> # Plot
        >>> d3.movingbubbles(df, speed={"slow": 1000, "medium": 200, "fast": 10}, filepath='movingbubbles.html')
        >>> #

        References
        ----------
        * https://d3blocks.github.io/d3blocks/pages/html/MovingBubbles.html

        """
        # Cleaning
        self._clean(clean_config=False)

        # Store parameters
        self.config['chart'] ='movingbubbles'
        self.config['filepath'] = self.set_path(filepath)
        self.config['title'] = title
        self.config['figsize'] = figsize
        self.config['showfig'] = showfig
        self.config['overwrite'] = overwrite
        self.config['center'] = center
        self.config['reset_time'] = reset_time
        self.config['speed'] = speed
        self.config['damper'] = damper
        self.config['note'] = note
        self.config['time_notes'] = time_notes
        self.config['fontsize'] = fontsize
        self.config['standardize'] = standardize
        self.config['columns'] = {'datetime': datetime, 'sample_id': sample_id, 'state': state}

        # Compute delta
        if ~np.any(df.columns=='delta') and isinstance(df, pd.DataFrame) and np.any(df.columns==state) and np.any(df.columns==datetime) and np.any(df.columns==sample_id):
            # df = self.compute_time_delta(df, sample_id=sample_id, datetime=datetime, dt_format=self.config['dt_format'])
            df = Movingbubbles.standardize(df, method=self.config['standardize'], sample_id=sample_id, datetime=datetime, dt_format=self.config['dt_format'])

        # Set label properties
        if isinstance(df, pd.DataFrame) and not hasattr(self, 'labels') and np.any(df.columns==state):
            labels = list(np.unique(df[state]))
            # Center should be at the very end of the list for d3!
            if self.config['center'] is not None:
                center_label = labels.pop(labels.index(self.config['center']))
                labels.append(center_label)

            # Set the label properties
            self.set_node_properties(labels=labels, cmap=self.config['cmap'])

        if not isinstance(df, pd.DataFrame):
            self.labels=None
        if not hasattr(self, 'labels'):
            raise Exception('Set labels is required or specify the category.')
        if time_notes is None:
            self.config['time_notes'] = [{"start_minute": 1, "stop_minute": 2, "note": ""}]
        if note is None:
            self.config['note']=("This is a simulation of [%s] states across [%s] samples. <a href='https://github.com/d3blocks/d3blocks'>d3blocks movingbubbles</a>." %(len(df['state'].unique()), len(df[sample_id].unique())))

        # Create the plot
        self.config = Movingbubbles.show(df, self.config, self.labels)
        # Open the webbrowser
        if self.config['showfig']: self.showfig(logger=logger)

        # Return
        return df

    def timeseries(self,
                   df,
                   datetime=None,
                   sort_on_date=True,
                   title='Timeseries - D3blocks',
                   filepath='timeseries.html',
                   fontsize=10,
                   figsize=[1000, 500],
                   showfig=True,
                   overwrite=True):
        """Timeseries block.

        Description
        -----------
        The TimeSeries can be used in case a date-time element is available, and where the time-wise values
        directly follow up with each other. The TimeSeries block supports enabling/disabling columns of interest,
        brushing and zooming to quickly focus on regions of interest or plot specific features, such as stocks together
        in a single chart.

        Parameters
        ----------
        df : pd.DataFrame()
            Input data. If the index is not datetime, specify the column with 'datetime'
        title : String, (default: None)
            Title of the figure.
        filepath : String, (Default: user temp directory)
            File path to save the output
        showfig : bool, (default: True)
            Open the window to show the chart.
        fontsize : int, (default: 14)
            Fontsize of the fonts in the circle.
        overwrite : bool, (default: True)
            Overwrite the existing html file.

        Returns
        -------
        df : pd.DataFrame()
            DataFrame.

        Examples
        --------
        >>> # Load example data
        >>> import yfinance as yf
        >>> df = yf.download(["TSLA", "TWTR", "META", "AMZN", "AAPL"], start="2019-01-01", end="2021-12-31")
        >>> df = df[["Adj Close"]].droplevel(0, axis=1).resample("M").last()
        >>> df = df.div(df.iloc[0])
        >>> df.head()
        >>> #
        >>> # Load d3blocks
        >>> from d3blocks import D3Blocks
        >>> #
        >>> # Initialize with filtering on close columns
        >>> d3 = D3Blocks(whitelist='close')
        >>> #
        >>> # Plot
        >>> d3.timeseries(df, fontsize=10)

        References
        ----------
        * https://d3blocks.github.io/d3blocks/pages/html/Timeseries.html

        """
        # Cleaning
        self._clean(clean_config=False)

        # Store parameters
        self.config['chart'] ='timeseries'
        self.config['filepath'] = self.set_path(filepath)
        self.config['figsize'] = figsize
        self.config['title'] = title
        self.config['showfig'] = showfig
        self.config['overwrite'] = overwrite
        self.config['fontsize'] = fontsize
        self.config['sort_on_date'] = sort_on_date
        self.config['columns'] = {'datetime': datetime}

        # Make copy
        df = df.copy()
        # Get datetime
        if datetime is None:
            logger.info('Taking the index for datetime.')
            df.index = pd.to_datetime(df.index.values, format=self.config['dt_format'])
        else:
            df.index = pd.to_datetime(df[self.config['columns']['datetime']].values, format=self.config['dt_format'])
            df.drop(labels=self.config['columns']['datetime'], axis=1, inplace=True)
        # Check multi-line columns and merge those that are multi-line
        # df.columns = list(map(lambda x: '_'.join('_'.join(x).split()), df.columns))
        # Check whitelist
        if self.config['whitelist'] is not None:
            logger.info('Filtering columns on [%s]' %(self.config['whitelist']))
            Ikeep = list(map(lambda x: self.config['whitelist'].lower() in x.lower(), df.columns.values))
            df = df.iloc[:, Ikeep]

        if df.shape[1]==0:
            logger.info('All columns are removed. Change whitelist/blacklist setting.')
            return None

        # Set default label properties
        if not hasattr(self, 'labels'):
            self.set_node_properties(labels=df.columns.values, cmap=self.config['cmap'])

        # Create the plot
        self.config = Timeseries.show(df, self.config, labels=self.labels)
        # Open the webbrowser
        if self.config['showfig']: self.showfig(logger=logger)

    def set_edge_properties(self, df, color: Union[float, List[float]] = None, opacity: Union[float, List[float]] = 0.8, cmap: str = 'tab20', chart: str = None, nodes=None, logger=None):
        """Set link/edge properties."""
        # Get or set the chart type
        if hasattr(self, 'config') and (self.config.get('chart', None) is not None):
            chart = self.config['chart']
        if chart is None:
            raise Exception('"chart" parameter is mandatory. Hint: use chart="chord" or chart="sankey" etc')
        
        # Compute edge properties for the specified chart.
        if chart=='chord':
            df = Chord.set_edge_properties(df, color=color, opacity=opacity, cmap=cmap, nodes=nodes, logger=logger)
        if chart=='sankey':
            pass

        # Convert to frame/dictionary
        self.edge_properties = convert_dataframe_dict(df, frame=self.config['frame'])
        # Store and return
        if logger is not None: logger.info('Edge properties are set.')
        return self.edge_properties

    def set_node_properties(self, labels=None, opacity: Union[float, List[float]] = 0.8, cmap: str = 'Set1'):
        """Set label properties.

        Parameters
        ----------
        labels : array-like (default: None)
            The unique names of the nodes/labels.
            * In case of pd.DataFrame, the 'source' and 'target' columns are used.
        cmap : String, (default: 'inferno')
            All colors can be reversed with '_r', e.g. 'binary' to 'binary_r'
            'Set1','Set2','rainbow','bwr','binary','seismic','Blues','Reds','Pastel1','Paired','twilight','hsv'

        Returns
        -------
        labels : dict()
            Dictionary containing class information.

        """
        logger.info('Set node/label properties.')

        if hasattr(self, 'labels'):
            labels = np.array([*self.labels.keys()])
        if isinstance(labels, pd.DataFrame) and np.all(ismember(['source', 'target'], labels.columns.values)[0]):
            labels = np.unique(labels[['source', 'target']].values.flatten())
            logger.info('Collecting labels from DataFrame using the "source" and "target" columns.')

        # Preprocessing
        labels = pre_processing(labels)
        # Count number of labels
        label_count = len(labels)

        # Checks
        if (labels is None) or label_count<1:
            logger.warning('Input parameter labels is not specified. Provide it manually. <return>')
            return None
        if isinstance(opacity, list) and len(opacity) != label_count:
            raise ValueError(f'Input parameter [color] has wrong length. Must be of length: {str(label_count)}')

        # Opacity
        if isinstance(opacity, float):
            opacity = np.repeat(opacity, label_count)

        # Get unique categories without sort
        indexes = np.unique(labels, return_index=True)[1]
        uilabels = [labels[index] for index in sorted(indexes)]

        # Create unique label/node colors
        hexcolors = colourmap.generate(len(uilabels), cmap=cmap, scheme='hex')

        # Make dict with properties
        labels = make_dict(uilabels, colors=hexcolors, opacity=opacity)

        # Convert to frame
        self.labels = convert_dataframe_dict(labels, frame=self.config['frame'])
        logger.info('Node properties are set.')

    def _clean(self, clean_config=True):
        """Clean previous results to ensure correct working."""
        if hasattr(self, 'G'): del self.G
        if hasattr(self, 'labels'): del self.labels
        if clean_config and hasattr(self, 'config'): del self.config

    def set_path(self, filepath='d3blocks.html'):
        """Set the file path.

        Parameters
        ----------
        filepath : str
            filename and or full pathname.
            * 'd3graph.html'
            * 'c://temp/'
            * 'c://temp/d3graph.html'

        Returns
        -------
        filepath : str
            Path to graph.

        """
        dirname, filename = os.path.split(filepath)
        # dirname = os.path.abspath(dirname)

        if (filename is None) or (filename==''):
            filename = 'd3blocks.html'

        if (dirname is None) or (dirname==''):
            # dirname = tempfile.TemporaryDirectory().name
            dirname = os.path.join(tempfile.gettempdir(), 'd3blocks')

        if not os.path.isdir(dirname):
            logger.info('Create directory: [%s]', dirname)
            os.mkdir(dirname)

        filepath = os.path.abspath(os.path.join(dirname, filename))
        logger.debug("filepath is set to [%s]" %(filepath))
        return filepath

    # Open the webbrowser
    def showfig(self, sleep=0.2, logger=None):
        """Open browser to show chart."""
        # Sleeping is required to pevent overlapping windows
        time.sleep(sleep)
        file_location = os.path.abspath(self.config['filepath'])
        if platform == "darwin":  # check if on OSX
            file_location = "file:///" + file_location
        if os.path.isfile(file_location):
            webbrowser.open(file_location, new=2)
        else:
            if logger is not None: logger.info('File not found: [%s]' %(file_location))

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
            'sum' (default)

        Returns
        -------
        pd.DataFrame
            adjacency matrix.

        Examples
        --------
        >>> # Initialize
        >>> d3 = D3Blocks()
        >>>
        >>> # Load example
        >>> df = d3.import_example('energy')
        >>>
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
        >>>
        >>> # Load example
        >>> df = d3.import_example('energy')
        >>> Convert into adjmat
        >>> adjmat = d3.vec2adjmat(df['source'], df['target'], df['weight'])
        >>>
        >>> # Convert back to vector
        >>> vector = d3.adjmat2vec(adjmat)

        """
        return d3network.adjmat2vec(df, min_weight=min_weight)

    def import_example(self, data, n=10000, c=100, date_start="17-12-1903 00:00:00", date_stop="17-12-1903 23:59:59"):
        """Import example dataset from github source.

        Description
        -----------
        Import one of the few datasets from github source or specify your own download url link.

        Parameters
        ----------
        data : str
            "movingbubbles"
            "random_time"
            "timeseries"
            "energy"
            "stormofswords"
            "bigbang"
            "southern_nebula"
            "southern_nebula_internet"
            "cancer"
            "breast_cancer"
            "iris"
            "occupancy"
            "climate"
        n : int, (default: 1000).
            Number of events (samples).
        c : int, (default: 100).
            Number of classes.
        date_start : str, (default: None)
            "17-12-1903 00:00:00" : start date
        date_stop : str, (default: None)
            "17-12-1903 23:59:59" : Stop date

        Returns
        -------
        pd.DataFrame()
            Dataset containing mixed features.

        """
        return _import_example(data=data, n=n, c=c, date_start=date_start, date_stop=date_stop, dt_format=self.config['dt_format'], logger=logger)


# %% Import example dataset from github.
def _import_example(data, n=10000, c=1000, date_start=None, date_stop=None, dt_format='%d-%m-%Y %H:%M:%S', logger=None):
    """Import example dataset from github source.

    Description
    -----------
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
        n : int, (default: 1000).
            Number of events (samples).
        c : int, (default: 100).
            Number of classes.
    date_start : str, (default: None)
        "17-12-1903 00:00:00" : start date
    date_stop : str, (default: None)
        "17-12-1903 23:59:59" : Stop date

    Returns
    -------
    pd.DataFrame()
        Dataset containing mixed features.

    """
    from sklearn import datasets
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
        df = d3model.import_example('bigbang')
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
        iris = datasets.load_iris()
        X = iris.data[:, :2]  # we only take the first two features.
        labels = iris.target
        df = pd.DataFrame(data=X, index=labels, columns=['x', 'y'])
        return df
    elif data=='breast_cancer':
        return datasets.load_breast_cancer(return_X_y=True, as_frame=True)[0]
    elif data=='occupancy':
        url='https://erdogant.github.io/datasets/UCI_Occupancy_Detection.zip'
        sep=','
    elif data=='climate':
        url='https://erdogant.github.io/datasets/kaggle_daily_delhi_climate_test.zip'

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
def make_dict(labels, colors, opacity=0.8):
    """Create dictionary with label properties."""
    dlabel = {}
    for i, cat in enumerate(labels):
        dlabel[cat] = {'id': i, 'desc': cat, 'short': cat, 'color': colors[i], 'opacity': opacity[i]}
    return dlabel


def random_date(start, end, prop, dt_format='%d-%m-%Y %H:%M:%S', strftime=True):
    """Create random dateTimes."""
    return str_time_prop(start, end, prop, dt_format=dt_format, strftime=strftime)


def str_time_prop(start, end, prop, dt_format='%d-%m-%Y %H:%M:%S', strftime=True):
    """Get a time at a proportion of a range of two formatted times.

    Description
    -----------
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
    """ Retrieve file from url.

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
def set_logger(verbose=20):
    """Set the logger for verbosity messages."""
    logger.setLevel(verbose)


# %%
def disable_tqdm():
    """Set the logger for verbosity messages."""
    return (True if (logger.getEffectiveLevel()>=30) else False)


# %% Do checks
def library_compatibility_checks():
    """Library compatibiliy checks.

    Returns
    -------
    None.

    """
    # if not version.parse(nx.__version__) >= version.parse("2.5"):
    #     logger.error('Networkx version should be >= 2.5')
    #     logger.info('Hint: pip install -U networkx')
    pass
