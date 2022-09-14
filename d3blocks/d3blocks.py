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
import unicodedata

import d3blocks.movingbubbles.Movingbubbles as Movingbubbles
import d3blocks.timeseries.Timeseries as Timeseries
import d3blocks.sankey.Sankey as Sankey
import d3blocks.imageslider.Imageslider as Imageslider
import d3blocks.chord.Chord as Chord
import d3blocks.scatter.Scatter as Scatter
import d3blocks.violin.Violin as Violin
import d3blocks.particles.Particles as Particles

# import movingbubbles.Movingbubbles as Movingbubbles
# import timeseries.Timeseries as Timeseries
# import sankey.Sankey as Sankey
# import imageslider.Imageslider as Imageslider
# import chord.Chord as Chord
# import scatter.Scatter as Scatter
# import violin.Violin as Violin
# import particles.Particles as Particles


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
    """D3Blocks."""

    def __init__(self, cmap='Set1', dt_format='%Y-%m-%d %H:%M:%S', whitelist=None, verbose=20):
        """Initialize d3blocks with user-defined parameters.

        Parameters
        ----------
        cmap : String, optional
            'Set1'       (default)
            'Set2'
            'rainbow'
            'bwr'        Blue-white-red
            'binary' or 'binary_r'
            'seismic'    Blue-white-red
            'Blues'      white-to-blue
            'Reds'       white-to-red
            'Pastel1'    Discrete colors
            'Paired'     Discrete colors
            'Set1'       Discrete colors
        dt_format : str
            '%Y-%m-%d %H:%M:%S'.
        whitelist : str, optional
            Keep only columns containing this (sub)string (case insensitive)
        verbose : int, optional
            Verbose message. The default is 20.

        Returns
        -------
        None.

        """
        # Clean
        self._clean(clean_config=True)
        # Some library compatibily checks
        library_compatibility_checks()
        # Initialize empty config
        self.config = {}
        self.config['cmap'] = cmap
        self.config['whitelist'] = whitelist
        self.config['dt_format'] = dt_format
        self.config['curpath'] = os.path.dirname(os.path.abspath(__file__))
        # Set the logger
        set_logger(verbose=verbose)

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
        >>>
        >>> # Convert back to vector
        >>> vector = d3.adjmat2vec(adjmat)

        """
        return d3network.adjmat2vec(df, min_weight=min_weight)

    def particles(self,
                  text,
                  radius=3,
                  collision=0.05,
                  fontsize=250,
                  spacing=10,
                  cmap='Turbo',
                  background='#000000',
                  title='Particles - D3blocks',
                  filepath='particles.html',
                  figsize=[900, 500],
                  showfig=True,
                  overwrite=True):
        """Create of chord graph.

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
            Color scheme for that is used for c(olor) in case list of string is used. All color schemes can be reversed with "_r".
            'tab20', 'tab20b', 'tab20c'
            'Set1', 'Set2'
            'seismic'    Blue-white-red
            'Blues'      white-to-blue
            'Reds'       white-to-red
            'Pastel1'    Discrete colors
            'Paired'     Discrete colors
            'Set1'       Discrete colors
        background : String (default: '#000000')
            Background color.
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
        >>> # Plot
        >>> d3.particles('D3blocks')

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
        if self.config['showfig']:
            _showfig(self.config['filepath'])

    def violin(self,
               x,
               y,
               s=5,
               c=None,
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
        """Create of violin graph.

        Parameters
        ----------
        x : list of String or numpy array.
            This 1d-vector contains the class labels for each datapoint in y.
        y : list of float or numpy array.
            This 1d-vector contains the values for the samples.
        s: list/array of with same size as (x,y). Can be of type str or int.
            Size of the samples.
        c: list/array of hex colors with same size as y
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
        cmap : String (default: 'inferno')
            Color scheme for that is used for the scatterplot. All color schemes can be reversed with "_r".
            Sequential : 'viridis', 'plasma', 'inferno', 'magma', 'cividis'
            Sequential (white-to) : 'Greys', 'Purples', 'Blues', 'Greens', 'Oranges', 'Reds', 'YlOrBr', 'YlOrRd', 'OrRd', 'PuRd', 'RdPu', 'BuPu', 'GnBu', 'PuBu', 'YlGnBu', 'PuBuGn', 'BuGn', 'YlGn'
            Sequential2 (to-white) : 'binary', 'gist_yarg', 'gist_gray', 'gray', 'bone', 'pink', 'spring', 'summer', 'autumn', 'winter', 'cool', 'Wistia', 'hot', 'afmhot', 'gist_heat', 'copper'
            Diverging (from-white-to): 'PiYG', 'PRGn', 'BrBG', 'PuOr', 'RdGy', 'RdBu', 'RdYlBu', 'RdYlGn', 'Spectral', 'coolwarm', 'bwr', 'seismic'
            Cyclic : 'twilight', 'twilight_shifted', 'hsv'
        title : String, (default: None)
            Title of the figure.
        filepath : String, (Default: user temp directory)
            File path to save the output
        figsize : tuple, (default: (None, 500))
            Size of the figure in the browser, [width, height].
            The width is determined based on the number of class labels x.
        showfig : bool, (default: True)
            Open the window to show the graph.
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
        >>>
        >>> # Initialize
        >>> d3 = D3Blocks()
        >>>
        >>> # Load example data
        >>> df = d3.import_example('stormofswords')
        >>>
        >>> # Plot
        >>> d3.violin(df, filepath='chord_demo.html')

        """
        if len(x)!=len(y): raise Exception(logger.error('input parameter "x" should be of size of "y".'))
        if s is None: raise Exception(logger.error('input parameter "s" should have value >0.'))
        if isinstance(s, (list, np.ndarray)) and (len(s)!=len(x)): raise Exception(logger.error('input parameter "s" should be of same size of (x, y).'))
        if stroke is None: raise Exception(logger.error('input parameter "stroke" should have hex value.'))
        if isinstance(stroke, (list, np.ndarray)) and (len(stroke)!=len(x)): raise Exception(logger.error('input parameter "stroke" should be of same size of (x, y).'))
        if opacity is None: raise Exception(logger.error('input parameter "opacity" should have value in range [0..1].'))
        if isinstance(opacity, (list, np.ndarray)) and (len(opacity)!=len(x)): raise Exception(logger.error('input parameter "opacity" should be of same size of (x, y).'))

        # Cleaning
        self._clean(clean_config=False)

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
        df = Violin.preprocessing(x, y, config=self.config, c=c, s=s, stroke=stroke, opacity=opacity, tooltip=tooltip, logger=logger)

        # Set default label properties
        if not hasattr(self, 'labels'):
            labels = self.get_label_properties(labels=np.unique(df['x'].values), cmap=self.config['cmap'])
            self.set_label_properties(labels)

        # Create the plot
        self.config = Violin.show(df, config=self.config, labels=self.labels)
        # Open the webbrowser
        if self.config['showfig']:
            _showfig(self.config['filepath'])

    def scatter(self,
                x,
                y,
                s=3,
                c='#002147',
                c_gradient=None,
                opacity=0.8,
                stroke='#ffffff',
                tooltip=None,
                cmap='tab20',
                normalize=False,
                title='Scatter - D3blocks',
                filepath='scatter.html',
                figsize=[900, 600],
                xlim=[None, None],
                ylim=[None, None],
                showfig=True,
                overwrite=True):
        """Create of chord graph.

        Parameters
        ----------
        x : numpy array
            1d coordinates x-axis.
        y : numpy array
            1d coordinates y-axis.
        s: list/array of with same size as (x,y). Can be of type str or int.
            Size of the samples.
        c: list/array of hex colors with same size as (x,y)
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
        cmap : String (default: 'Set2')
            Color scheme for that is used for c(olor) in case list of string is used. All color schemes can be reversed with "_r".
            'tab20', 'tab20b', 'tab20c'
            'Set1', 'Set2'
            'seismic'    Blue-white-red
            'Blues'      white-to-blue
            'Reds'       white-to-red
            'Pastel1'    Discrete colors
            'Paired'     Discrete colors
            'Set1'       Discrete colors
        normalize: Bool, optional
            Normalize datapoints. The default is False.
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
            Open the window to show the graph.
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
        >>>
        >>> # Initialize
        >>> d3 = D3Blocks()
        >>>
        >>> # Load example data
        >>> df = d3.import_example('iris')
        >>>
        >>> # Plot
        >>> d3.scatter(df)

        """
        if len(x)!=len(y): raise Exception(logger.error('input parameter [x] should be of size of (x, y).'))
        if s is None: raise Exception(logger.error('input parameter [s] should have value >0.'))
        if c is None: raise Exception(logger.error('input parameter [c] should be of a list of string with hex color, such as "#000000".'))
        if isinstance(s, (list, np.ndarray)) and (len(s)!=len(x)): raise Exception(logger.error('input parameter [s] should be of same size of (x, y).'))
        if (tooltip is not None) and len(tooltip)!=len(x): raise Exception(logger.error('input parameter [tooltip] should be of size (x, y) and not None.'))

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
        self.config['normalize'] = normalize
        self.config['cmap'] = cmap

        # Preprocessing
        # Remvove quotes from source-target labels
        labels = Scatter.preprocessing(x, y, c, s, tooltip, opacity, c_gradient, stroke, self.config['cmap'], self.config['normalize'], logger=logger)
        # Set default label properties
        if not hasattr(self, 'labels'):
            self.set_label_properties(labels)

        # Create the plot
        df = pd.DataFrame(self.labels).T
        self.config = Scatter.show(df, self.config)
        # Open the webbrowser
        if self.config['showfig']:
            _showfig(self.config['filepath'])

    def chord(self,
              df,
              title='Chord - D3blocks',
              filepath='chord.html',
              figsize=[1200, 1200],
              showfig=True,
              overwrite=True):
        """Chord graph.

        Description
        -----------
        A chord graph represents flows or connections between several entities or nodes.
        Each entity is represented by a fragment on the outer part of the circular layout.
        Then, arcs are drawn between each entity. The size of the arc is proportional to the importance of the flow.

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

        """
        df = df.copy()
        self.config['chart'] ='chord'
        self.config['filepath'] = self.set_path(filepath)
        self.config['title'] = title
        self.config['showfig'] = showfig
        self.config['overwrite'] = overwrite
        self.config['figsize'] = figsize
        # self.config['margin'] = {**{"top": 5, "right": 1, "bottom": 5, "left": 1}, **margin}

        # Remvove quotes from source-target labels
        df = pre_processing(df)

        # Set default label properties
        if not hasattr(self, 'labels'):
            labels = self.get_label_properties(labels=np.unique(df[['source', 'target']].values.ravel()), cmap=self.config['cmap'])
            self.set_label_properties(labels)

        # Create the plot
        self.config = Chord.show(df, self.config, labels=self.labels)
        # Open the webbrowser
        if self.config['showfig']:
            _showfig(self.config['filepath'])

    def imageslider(self,
                    img_before,
                    img_after,
                    title='Image slider - D3blocks',
                    filepath='imageslider.html',
                    figsize=(800, 600),
                    showfig=True,
                    overwrite=True):
        """Create image slider.

        Parameters
        ----------
        img_before : String
            absolute path to before image.
        img_after : String
            absolute path to after image.
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
        >>> # Load example data
        >>> img_before, img_after = d3.import_example('southern_nebula')
        >>>
        >>> # Plot
        >>> d3.imageslider(img_before, img_after, showfig=True)

        """
        self.config['chart'] ='imageslider'
        self.config['img_before'] = os.path.abspath(img_before)
        self.config['img_after'] = os.path.abspath(img_after)
        self.config['filepath'] = self.set_path(filepath)
        self.config['title'] = title
        self.config['alt_before'] = os.path.basename(img_before)
        self.config['alt_after'] = os.path.basename(img_after)
        self.config['showfig'] = showfig
        self.config['overwrite'] = overwrite
        self.config['figsize'] = figsize

        # Create the plot
        self.config = Imageslider.show(self.config)
        # Open the webbrowser
        if self.config['showfig']:
            _showfig(self.config['filepath'])

    def heatmap(self, df, vmax=None, stroke='red', title='Heatmap - D3blocks', filepath='heatmap.html', figsize=(720, 720), showfig=True, overwrite=True):
        """Heatmap graph.

        Description
        -----------
        heatmap is a module in d3blocks to create interactive heatmaps.

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

        Returns
        -------
        None.

        Examples
        --------
        >>> # Initialize
        >>> d3 = D3Blocks()
        >>>
        >>> # Import example
        >>> df = d3.import_example('energy') # 'bigbang', 'stormofswords'
        >>> df_adjmat = d3.vec2adjmat(df['source'], df['target'], weight=df['weight'])
        >>>
        >>> d3.heatmap(df_adjmat, showfig=False)
        >>> d3.Network.show()
        >>>
        >>> d3.Network.set_node_properties(color='cluster')
        >>> d3.Network.show()
        >>>
        >>> # Node and edge properties
        >>> d3.Network.node_properties
        >>> d3.Network.edge_properties

        """
        # Copy of data
        df = df.copy()

        # Set configs
        self.config['chart'] ='heatmap'
        self.config['title'] = title
        self.config['filepath'] = self.set_path(filepath)
        self.config['figsize'] = figsize
        self.config['showfig'] = showfig
        self.config['overwrite'] = overwrite
        self.config['vmax'] = vmax
        self.config['stroke'] = stroke

        # Create heatmap graph
        d3heatmap.heatmap(df, vmax=self.config['vmax'], stroke=self.config['stroke'], width=self.config['figsize'][0], height=self.config['figsize'][1], path=self.config['filepath'], title=title, description='', showfig=self.config['showfig'])

    def d3graph(self, df, title='D3graph - D3blocks', filepath='d3graph.html', figsize=[1500, 800], showfig=True, overwrite=True, collision=0.5, charge=400, slider=[None, None], scaler='zscore'):
        """d3graph graph.

        Description
        -----------
        d3graph is a integrated in d3blocks and is to create interactive and stand-alone D3 force-directed graphs.
        The input data is a dataframe containing source, target, and weight. In underneath example, we load the energy
        dataset which contains 68 relationships that are stored in a DataFrame with the columns source, target, and weight.
        The nodes are colored based on the Louvain heuristics which is the partition of highest modularity, i.e.
        the highest partition of the dendrogram generated by the Louvain algorithm.
        The strength of the edges is based on the weights. To explore the network, and the strength of the edges more
        extensively, the slider (located at the top) can break the network based on the edge weights.
        The ouput is a html file that is interactive and stand alone.

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
        >>> d3.d3graph(df)
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

        """
        # Copy of data
        df = df.copy()

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
               figsize=(800, 600),
               node={"align": "justify", "width": 15, "padding": 15, "color": "currentColor"},
               link={"color": "source-target", "stroke_opacity": 0.5},
               margin={"top": 5, "right": 1, "bottom": 5, "left": 1},
               showfig=True,
               overwrite=True):
        """Create of sankey graph.

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
            "linkColor" : "source", "target", "source-target", or a static olor such as "grey", "blue", "red" etc
            "linkStrokeOpacity" : 0.5
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
            Open the window to show the graph.
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
        >>>
        >>> # Initialize
        >>> d3 = D3Blocks()
        >>>
        >>> # Load example data
        >>> df = d3.import_example('sankey')  # 'stormofswords'
        >>>
        >>> # Plot
        >>> d3.sankey(df, filepath='sankey_demo.html', fontsize=10)

        """
        df = df.copy()
        self.config['chart'] ='sankey'
        self.config['filepath'] = self.set_path(filepath)
        self.config['title'] = title
        self.config['showfig'] = showfig
        self.config['overwrite'] = overwrite
        self.config['figsize'] = figsize
        self.config['link'] = {**{"color": "source-target", "stroke_opacity": 0.5}, **link}
        self.config['node'] = {**{"align": "justify", "width": 15, "padding": 15, "color": "currentColor"}, **node}
        self.config['margin'] = {**{"top": 5, "right": 1, "bottom": 5, "left": 1}, **margin}

        # Remvove quotes from source-target labels
        df = pre_processing(df)

        # Set default label properties
        if not hasattr(self, 'labels'):
            labels = self.get_label_properties(labels=np.unique(df[['source', 'target']].values.ravel()), cmap=self.config['cmap'])
            self.set_label_properties(labels)

        # Create the plot
        self.config = Sankey.show(df, self.config, labels=self.labels)
        # Open the webbrowser
        if self.config['showfig']:
            _showfig(self.config['filepath'])
        # Return config
        # return self.config

    def movingbubbles(self, df, datetime='datetime', sample_id='sample_id', state='state', center=None, damper=1, fontsize=14, reset_time='day', standardize=None, speed={"slow": 1000, "medium": 200, "fast": 50}, figsize=(780, 800), note=None, time_notes=None, title='d3blocks_movingbubbles', filepath='movingbubbles.html', showfig=True, overwrite=True):
        """Creation of moving bubble graph.

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
        >>> from d3blocks import D3Blocks
        >>> d3 = D3Blocks()
        >>> df = d3.import_example(data='random_time')
        >>> d3.movingbubbles(df)

        """
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
            self.labels = self.get_label_properties(labels=labels, cmap=self.config['cmap'])
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
        if self.config['showfig']:
            _showfig(self.config['filepath'])

        # Return
        return df

    def timeseries(self, df, datetime=None, sort_on_date=True, title='Timeseries - D3blocks', filepath='timeseries.html', fontsize=10, figsize=[1000, 500], showfig=True, overwrite=True):
        """Timeseries graph.

        Description
        -----------
        The TimeSeries graph can be used in case a date-time element is available, and where the time-wise values
        directly follow up with each other. The TimeSeries graph supports now enabling/disabling columns of interest,
        brushing and zooming to quickly focus on regions of interest or plot specific features, such as stocks together
        in a single graph.

        Parameters
        ----------
        df : pd.DataFrame()
            Input data.
        title : String, (default: None)
            Title of the figure.
        filepath : String, (Default: user temp directory)
            File path to save the output
        showfig : bool, (default: True)
            Open the window to show the graph.
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
        >>> d = df[["Adj Close"]].droplevel(0, axis=1).resample("M").last()
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

        """
        df = df.copy()
        self.config['chart'] ='timeseries'
        self.config['filepath'] = self.set_path(filepath)
        self.config['figsize'] = figsize
        self.config['title'] = title
        self.config['showfig'] = showfig
        self.config['overwrite'] = overwrite
        self.config['fontsize'] = fontsize
        self.config['sort_on_date'] = sort_on_date
        self.config['columns'] = {'datetime': datetime}

        # Convert to datetime
        if datetime is not None:
            df.index = pd.to_datetime(df[self.config['columns']['datetime']].values, format=self.config['dt_format'])
            df.drop(labels=self.config['columns']['datetime'], axis=1, inplace=True)
        else:
            logger.info('Taking the index for datetime.')
            df.index = pd.to_datetime(df.index.values, format=self.config['dt_format'])
        # Check multi-line columns and merge those that are multi-line
        df.columns = list(map(lambda x: '_'.join('_'.join(x).split()), df.columns))
        # Check whitelist
        if self.config['whitelist'] is not None:
            logger.info('Filtering columns on [%s]' %(self.config['whitelist']))
            Ikeep = list(map(lambda x: self.config['whitelist'].lower() in x.lower(), df.columns.values))
            df = df.iloc[:, Ikeep]

        # Set default label properties
        if not hasattr(self, 'labels'):
            labels = self.get_label_properties(labels=df.columns.values, cmap=self.config['cmap'])
            self.set_label_properties(labels)
        # Create the plot
        self.config = Timeseries.show(df, self.config, labels=self.labels)
        # Open the webbrowser
        if self.config['showfig']:
            _showfig(self.config['filepath'])

    def set_label_properties(self, labels):
        """Set the label properties.

        Parameters
        ----------
        labels : dict()
            Dictionary containing class information.

        Returns
        -------
        None.

        """
        self.labels = labels
        logger.info('Labels are set')

    def get_label_properties(self, labels=None, cmap='Set1'):
        """Get label properties.

        Parameters
        ----------
        labels : classes
            Class or column names.
        cmap : str, (default: 'Set1')
            Colormap.

        Returns
        -------
        labels : dict()
            Dictionary containing class information.

        """
        if hasattr(self, 'labels'):
            labels = [*self.labels.keys()]
        if (labels is None):
            logger.warning('Input parameter labels is not specified. Provide it manually. <return>')
            return None

        logger.info('Create label properties based on [%s].' %(cmap))
        # Get unique categories without sort
        indexes = np.unique(labels, return_index=True)[1]
        uil = [labels[index] for index in sorted(indexes)]

        # Create unique colors
        hexcolors = colourmap.generate(len(uil), cmap=cmap, scheme='hex')
        # Make dict with properties
        labels = make_dict_label_properties(uil, hexcolors)
        for i, cat in enumerate(uil):
            labels[cat] = {'id': i, 'color': hexcolors[i], 'desc': cat, 'short': cat}
        return labels

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

    def import_example(self, graph='movingbubbles', n=10000, c=100, date_start="2000-01-01 00:00:00", date_stop="2001-01-01 23:59:59"):
        """Import example dataset from github source.

        Description
        -----------
        Import one of the few datasets from github source or specify your own download url link.

        Parameters
        ----------
        graph : str
            Name of datasets
            'movingbubbles', 'random_time'
        n : int, (default: 1000).
            Number of events.
        date_start : str, (default: None)
            "2000-01-01 00:00:00" : start date
        date_stop : str, (default: None)
            "2010-01-01 23:59:59" : Stop date

        Returns
        -------
        pd.DataFrame()
            Dataset containing mixed features.

        """
        return _import_example(graph=graph, n=n, c=c, date_start=date_start, date_stop=date_stop, dt_format=self.config['dt_format'], logger=logger)


# %% Import example dataset from github.
def _import_example(graph='movingbubbles', n=10000, c=1000, date_start=None, date_stop=None, dt_format='%Y-%m-%d %H:%M:%S', logger=None):
    """Import example dataset from github source.

    Description
    -----------
    Import one of the few datasets from github source or specify your own download url link.

    Parameters
    ----------
    graph : str
        Name of datasets
        'movingbubbles', 'random_time'
    n : int, (default: 1000).
        Number of events.
    date_start : str, (default: None)
        "2000-01-01 00:00:00" : start date
    date_stop : str, (default: None)
        "2010-01-01 23:59:59" : Stop date

    Returns
    -------
    pd.DataFrame()
        Dataset containing mixed features.

    """
    ext = '.csv'
    if graph=='movingbubbles':
        url='https://erdogant.github.io/datasets/movingbubbles.zip'
    elif graph=='random_time':
        return Movingbubbles.generate_data_with_random_datetime(n, c=c, date_start=date_start, date_stop=date_stop, dt_format=dt_format, logger=logger)
    elif graph=='timeseries':
        df = pd.DataFrame(np.random.randint(0, n, size=(n, 6)), columns=list('ABCDEF'))
        df['datetime'] = list(map(lambda x: random_date(date_start, date_stop, random.random(), dt_format=dt_format), range(0, n)), dt_format=dt_format)
        return df
    elif graph=='energy':
        # Sankey demo
        url='https://erdogant.github.io/datasets/energy_source_target_value.zip'
    elif graph=='stormofswords':
        # Sankey demo
        url='https://erdogant.github.io/datasets/stormofswords.zip'
    elif graph=='bigbang':
        # Initialize
        d3model = d3network.d3graph()
        df = d3model.import_example('bigbang')
        return d3network.adjmat2vec(df)
    elif graph=='southern_nebula':
        # Image slider demo
        url='https://erdogant.github.io/datasets/southern_nebula.zip'
        ext='.jpg'
    elif graph=='cancer':
        url='https://erdogant.github.io/datasets/cancer_dataset.zip'
    elif graph=='iris':
        from sklearn import datasets
        iris = datasets.load_iris()
        X = iris.data[:, :2]  # we only take the first two features.
        labels = iris.target
        df = pd.DataFrame(data=X, index=labels, columns=['x', 'y'])
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
        logger.info('Downloading [%s] dataset from github source..' %(graph))
        wget(url, PATH_TO_DATA)

    csvfile = unzip(PATH_TO_DATA, ext=ext)

    # Import local dataset
    logger.info('Import demo dataset for [%s] graph' %(graph))
    if graph=='movingbubbles':
        X = Movingbubbles.import_example(csvfile)
        labels = "{'index': '0', 'short': 'Sleeping', 'desc': 'Sleeping'}, {'index': '1', 'short': 'Personal Care', 'desc': 'Personal Care'}, {'index': '2', 'short': 'Eating & Drinking', 'desc': 'Eating and Drinking'}, {'index': '3', 'short': 'Education', 'desc': 'Education'}, {'index': '4', 'short': 'Work', 'desc': 'Work and Work-Related Activities'}, {'index': '5', 'short': 'Housework', 'desc': 'Household Activities'}, {'index': '6', 'short': 'Household Care', 'desc': 'Caring for and Helping Household Members'}, {'index': '7', 'short': 'Non-Household Care', 'desc': 'Caring for and Helping Non-Household Members'}, {'index': '8', 'short': 'Shopping', 'desc': 'Consumer Purchases'}, {'index': '9', 'short': 'Pro. Care Services', 'desc': 'Professional and Personal Care Services'}, {'index': '10', 'short': 'Leisure', 'desc': 'Socializing, Relaxing, and Leisure'}, {'index': '11', 'short': 'Sports', 'desc': 'Sports, Exercise, and Recreation'}, {'index': '12', 'short': 'Religion', 'desc': 'Religious and Spiritual Activities'}, {'index': '13', 'short': 'Volunteering', 'desc': 'Volunteer Activities'}, {'index': '14', 'short': 'Phone Calls', 'desc': 'Telephone Calls'}, {'index': '15', 'short': 'Misc.', 'desc': 'Other'}, {'index': '16', 'short': 'Traveling', 'desc': 'Traveling'}"
        df = {}
        df['type'] = 'movingbubbles'
        df['data'] = X
        df['labels'] = labels
    elif graph=='energy':
        df = pd.read_csv(csvfile)
        df.rename(columns={'value': 'weight'}, inplace=True)
        df[['source', 'target']] = df[['source', 'target']].astype(str)
    elif graph=='stormofswords':
        df = pd.read_csv(csvfile)
        # df.rename(columns={'weight':'value'}, inplace=True)
    elif graph=='southern_nebula':
        img_before = os.path.join(os.path.split(csvfile)[0], 'southern_nebula_before.jpg')
        img_after = os.path.join(os.path.split(csvfile)[0], 'southern_nebula_after.jpg')
        return img_before, img_after
    elif graph=='cancer':
        df = pd.read_csv(PATH_TO_DATA, sep=',')
        df.rename(columns={'tsneX': 'x', 'tsneY': 'y', 'labx': 'labels'}, inplace=True)
        df.set_index(df['labels'], inplace=True)

    # Return
    return df


# %%
def make_dict_label_properties(labels, colors):
    dlabel = {}
    for i, cat in enumerate(labels):
        dlabel[cat] = {'id': i, 'color': colors[i], 'desc': cat, 'short': cat}
    return dlabel


def random_date(start, end, prop, dt_format='%Y-%m-%d %H:%M:%S', strftime=True):
    return str_time_prop(start, end, prop, dt_format=dt_format, strftime=strftime)


def str_time_prop(start, end, prop, dt_format='%Y-%m-%d %H:%M:%S', strftime=True):
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


# %% Download files from github source
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


# %% Open the webbrowser
def _showfig(filepath: str, sleep=0.5):
    # Sleeping is required to pevent overlapping windows
    # time.sleep(sleep)
    file_location = os.path.abspath(filepath)
    if platform == "darwin":  # check if on OSX
        file_location = "file:///" + file_location
    webbrowser.open(file_location, new=2)


def pre_processing(df):
    """Pre-processing of the input dataframe.

    Parameters
    ----------
    df : pd.DataFrame()

    Returns
    -------
    df : pd.DataFrame()

    """
    df = remove_quotes(df)
    df = remove_special_chars(df)
    return df


def remove_quotes(df):
    """Pre-processing of the input dataframe.

    Parameters
    ----------
    df : pd.DataFrame()

    Returns
    -------
    df : pd.DataFrame()

    """
    Iloc = df.dtypes==object
    df.loc[:, Iloc] = df.loc[:, Iloc].apply(lambda s: s.str.replace("'", ""))
    return df


# %% Remove special characters from column names
def remove_special_chars(df):
    """Remove special characters.

    Parameters
    ----------
    df : pd.DataFrame()

    Returns
    -------
    df : pd.DataFrame()

    """
    df.columns = list(map(lambda x: unicodedata.normalize('NFD', x).encode('ascii', 'ignore').decode("utf-8").replace(' ', '_'), df.columns.values.astype(str)))
    df.index = list(map(lambda x: unicodedata.normalize('NFD', x).encode('ascii', 'ignore').decode("utf-8").replace(' ', '_'), df.index.values.astype(str)))
    return df


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
