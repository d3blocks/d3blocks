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

import movingbubbles.Movingbubbles as Movingbubbles
import timeseries.Timeseries as Timeseries
import sankey.Sankey as Sankey
import imageslider.Imageslider as Imageslider
from d3graph import d3graph
import d3graph as d3ng
from d3heatmap import d3heatmap
import chord.Chord as Chord
import scatter.Scatter as Scatter


logger = logging.getLogger('')
for handler in logger.handlers[:]: #get rid of existing old handlers
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
        return d3ng.vec2adjmat(source, target, weight=weight, symmetric=symmetric, aggfunc=aggfunc)

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
        return d3ng.adjmat2vec(df, min_weight=min_weight)

    def scatter(self,
              df,
              title='Scatter - d3blocks',
              filepath='scatter.html',
              figsize=(900, 600),
              xlim = [None, None],
              ylim = [None, None],
              showfig=True,
              overwrite=True):
        """Create of chord graph.

        Parameters
        ----------
        df : pd.DataFrame()
            Input data containing the following columns:
            'x'
            'y'
            'index' : class labels
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
            Open the window to show the network.
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
        df = df.copy()
        self.config['chart'] ='scatter'
        self.config['filepath'] = self.set_path(filepath)
        self.config['title'] = title
        self.config['xlim'] = xlim
        self.config['ylim'] = ylim
        self.config['showfig'] = showfig
        self.config['overwrite'] = overwrite
        self.config['figsize'] = figsize
        # self.config['margin'] = {**{"top": 5, "right": 1, "bottom": 5, "left": 1}, **margin}

        # Set default label properties
        if not hasattr(self, 'labels'):
            labels = self.get_label_properties(np.unique(df.index.values), cmap=self.config['cmap'])
            self.set_label_properties(labels)

        # Create the plot
        self.config = Scatter.show(df, self.config, labels=self.labels)
        # Open the webbrowser
        if self.config['showfig']:
            _showfig(self.config['filepath'])

    def chord(self,
              df,
              title='Chord - d3blocks',
              filepath='chord.html',
              figsize=(1200, 1200),
              showfig=True,
              overwrite=True):
        """Create of chord graph.

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
            Open the window to show the network.
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
        >>> d3.chord(df, filepath='chord_demo.html')

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
        df = remove_quotes(df)

        # Set default label properties
        if not hasattr(self, 'labels'):
            labels = self.get_label_properties(np.unique(df[['source', 'target']].values.ravel()), cmap=self.config['cmap'])
            self.set_label_properties(labels)

        # Create the plot
        self.config = Chord.show(df, self.config, labels=self.labels)
        # Open the webbrowser
        if self.config['showfig']:
            _showfig(self.config['filepath'])

    def imageslider(self,
                    img_before,
                    img_after,
                    title='Image slider - d3blocks',
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
            Open the window to show the network.
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

    def heatmap(self, df, vmax=None, stroke='red', title='Heatmap - d3blocks', filepath='heatmap.html', figsize=(720, 720), showfig=True, overwrite=True):
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
            Open the window to show the network.
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

        # Set default label properties
        # if not hasattr(self, 'labels'):
            # Create labels
            # labels = self.get_label_properties(np.unique(df.columns.values), cmap=self.config['cmap'])
            # Store in object
            # self.set_label_properties(labels)

        # Create heatmap graph
        d3heatmap.heatmap(df, vmax=self.config['vmax'], stroke=self.config['stroke'], width=self.config['figsize'][0], height=self.config['figsize'][1], path=self.config['filepath'], title=title, description='', showfig=self.config['showfig'])

    def network(self, df, title='Network - d3blocks', filepath='network.html', figsize=(1500, 800), showfig=True, overwrite=True, collision=0.5, charge=400, slider=[None, None]):
        """Network graph.

        Description
        -----------
        Network is a module of d3blocks that is build on d3js and creates interactive and stand-alone networks.
        The input data is a adjacency matrix for which the columns and indexes are the nodes and elements>0 the edges.
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
            Open the window to show the network.
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
        >>>
        >>> # Import example
        >>> df = d3.import_example('energy') # 'bigbang', 'stormofswords'
        >>>
        >>> d3.network(df, showfig=False)
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
        self.config['chart'] ='network'
        self.config['title'] = title
        self.config['filepath'] = self.set_path(filepath)
        self.config['figsize'] = figsize
        self.config['showfig'] = showfig
        self.config['overwrite'] = overwrite
        self.config['collision'] = collision
        self.config['charge'] = charge * -1
        self.config['slider'] = slider

        # Initialize network graph
        self.Network = d3graph(collision=collision, charge=charge, slider=slider)
        # Convert vector to adjmat
        df = d3ng.vec2adjmat(df['source'], df['target'], weight=df['weight'])
        # Create graph
        self.Network.graph(df)
        # Open the webbrowser
        self.Network.show(figsize=figsize, title=title, filepath=filepath, showfig=showfig, overwrite=overwrite)

    def sankey(self,
               df,
               title='Sankey - d3blocks',
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
            Open the window to show the network.
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
        df = remove_quotes(df)

        # Set default label properties
        if not hasattr(self, 'labels'):
            labels = self.get_label_properties(np.unique(df[['source', 'target']].values.ravel()), cmap=self.config['cmap'])
            self.set_label_properties(labels)

        # Create the plot
        self.config = Sankey.show(df, self.config, labels=self.labels)
        # Open the webbrowser
        if self.config['showfig']:
            _showfig(self.config['filepath'])

    def movingbubbles(self, df, datetime='datetime', sample_id='sample_id', state='state', dt_format='%Y-%m-%d %H:%M:%S', center=None, damper=1, reset_time='day', speed={"slow": 1000, "medium": 200, "fast": 50}, figsize=(780, 800), note=None, title='d3blocks_movingbubbles', filepath='movingbubbles.html', fontsize=14, showfig=True, overwrite=True):
        """Creation of moving bubble graph.

        Parameters
        ----------
        df : Input data
            Input data.
        center : String, (default: None)
            Center this category.
        dampler : float, (default: 1)
            Movement of sample: [0.1 - 10]. A smaller number is slower/smoother movement.
        reset_time : String, (default: 'day')
            'day'  : Every 24h de the day start over again.
            'year' : Every 365 days the year starts over again.
        figsize : tuple, (default: (1500, 800))
            Size of the figure in the browser, [width, height].
        title : String, (default: None)
            Title of the figure.
        filepath : String, (Default: user temp directory)
            File path to save the output
        showfig : bool, (default: True)
            Open the window to show the network.
        fontsize : int, (default: 14)
            Fontsize of the fonts in the circle.
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
        if note is None: note=("This is a simulation of [%s] unique classes across time. <a href='https://github.com/d3blocks/d3blocks'>d3blocks movingbubbles</a>." %(len(df)))
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
        self.config['fontsize'] = fontsize
        self.config['columns'] = {'datetime': datetime, 'sample_id': sample_id, 'state': state}
        self.config['dt_format'] = dt_format

        # Compute delta
        if ~np.any(df.columns=='delta') and isinstance(df, pd.DataFrame) and np.any(df.columns==state) and np.any(df.columns==datetime) and np.any(df.columns==sample_id):
            df = self.compute_time_delta(df, sample_id=sample_id, datetime=datetime, state=state, dt_format=dt_format)
        # Set label properties
        if isinstance(df, pd.DataFrame) and not hasattr(self, 'labels') and np.any(df.columns==state):
            self.labels = self.get_label_properties(df[state], cmap=self.config['cmap'])
        if not isinstance(df, pd.DataFrame):
            self.labels=None
        if not hasattr(self, 'labels'):
            raise Exception('Set labels is required or specify the category.')

        # Create the plot
        self.config = Movingbubbles.show(df, self.config, self.labels)

        # Open the webbrowser
        if self.config['showfig']:
            _showfig(self.config['filepath'])

        # Return
        return df

    def timeseries(self, df, datetime=None, sort_on_date=True, title='Timeseries - d3blocks', filepath='timeseries.html', fontsize=10, showfig=True, overwrite=True):
        """Create of Timeseries graph.

        Parameters
        ----------
        df : pd.DataFrame()
            Input data.
        title : String, (default: None)
            Title of the figure.
        filepath : String, (Default: user temp directory)
            File path to save the output
        showfig : bool, (default: True)
            Open the window to show the network.
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
        >>> df = yf.download(["TSLA", "TWTR", "FB", "AMZN", "AAPL"], start="2019-01-01", end="2021-12-31")
        >>> d = df[["Adj Close"]].droplevel(0, axis=1).resample("M").last()
        >>> df = df.div(df.iloc[0])
        >>> df.head()
        >>>
        >>> # Load d3blocks
        >>> from d3blocks import D3Blocks
        >>>
        >>> # Initialize with filtering on close columns
        >>> d3 = D3Blocks(whitelist='close')
        >>>
        >>> # Plot
        >>> d3.timeseries(df, filepath='timeseries.html', fontsize=10)

        """
        df = df.copy()
        self.config['chart'] ='timeseries'
        self.config['filepath'] = self.set_path(filepath)
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
            labels = self.get_label_properties(df.columns.values, cmap=self.config['cmap'])
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

    def get_label_properties(self, y, cmap='Set1'):
        """Get label properties.

        Parameters
        ----------
        y : classes
            Class or column names.
        cmap : str, (default: 'Set1')
            Colormap.

        Returns
        -------
        labels : dict()
            Dictionary containing class information.

        """
        logger.info('Create label properties based on [%s].' %(cmap))
        # Get unique categories
        uiy = np.unique(y)
        # Create unique colors
        hexcolors = colourmap.generate(len(uiy), cmap=cmap, scheme='hex')
        # Make dict with properties
        labels = {}
        for i, cat in enumerate(uiy):
            labels[cat] = {'id': i, 'color': hexcolors[i], 'desc': cat, 'short': cat}
        return labels

    def compute_time_delta(self, df, sample_id='sample_id', datetime='datetime', state='state', dt_format='%Y-%m-%d %H:%M:%S'):
        """Compute delta between two time-points that follow-up.

        Parameters
        ----------
        df : Input DataFrame
            Input data.
        sample_id : str.
            Column name of the sample identifier.
        datetime : datetime
            Column name of the date time.
        state : str
            Column name that describes the state.
        cmap : str, (default: 'Set1')
            The name of the colormap.
            'Set1'.
        dt_format : str
            '%Y-%m-%d %H:%M:%S'.

        Returns
        -------
        df : pd.DataFrame()
            DataFrame.

        """
        logger.info('Compute time delta.')
        # Compute delta
        df = Movingbubbles.compute_time_delta(df, sample_id, datetime, state, cmap=self.config['cmap'])
        # Return
        return df

    def standardize(self, df, sample_id='sample_id', datetime='datetime', dt_format='%Y-%m-%d %H:%M:%S'):
        """Normalize time per sample_id.

        Parameters
        ----------
        df : Input DataFrame
            Input data.
        sample_id : str.
            Column name of the sample identifier.
        datetime : datetime
            Column name of the date time.
        dt_format : str, optional
            '%Y-%m-%d %H:%M:%S'.

        Returns
        -------
        df : DataFrame
            Dataframe with the input columns with an extra column with normalized time.
            'datetime_norm'

        """
        return Movingbubbles.standardize(df, sample_id=sample_id, datetime=datetime, dt_format=dt_format)

    def _clean(self, clean_config=True):
        """Clean previous results to ensure correct working."""
        if hasattr(self, 'G'): del self.G
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

    def import_example(self, graph='movingbubbles', n=10000, c=1000, date_start="2000-1-1 00:00:00", date_stop="2010-1-1 23:59:59"):
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
            "1-1-2000 00:00:00" : start date
        date_stop : str, (default: None)
            "1-1-2010 23:59:59" : Stop date

        Returns
        -------
        pd.DataFrame()
            Dataset containing mixed features.

        """
        return _import_example(graph=graph, n=n, c=c, date_start=date_start, date_stop=date_stop, dt_format=self.config['dt_format'])


# %% Import example dataset from github.
def _import_example(graph='movingbubbles', n=10000, c=1000, date_start=None, date_stop=None, dt_format='%Y-%m-%d %H:%M:%S'):
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
        "1-1-2000 00:00:00" : start date
    date_stop : str, (default: None)
        "1-1-2010 23:59:59" : Stop date

    Returns
    -------
    pd.DataFrame()
        Dataset containing mixed features.

    """
    ext = '.csv'
    if graph=='movingbubbles':
        url='https://erdogant.github.io/datasets/movingbubbles.zip'
    elif graph=='random_time':
        return generate_data_with_random_datetime(n, c=c, date_start=date_start, date_stop=date_stop)
    elif graph=='timeseries':
        df = pd.DataFrame(np.random.randint(0, n, size=(n, 6)), columns=list('ABCDEF'))
        df['datetime'] = list(map(lambda x: random_date(date_start, date_stop, random.random(), dt_format=dt_format), range(0, n)))
        return df
    elif graph=='energy':
        # Sankey demo
        url='https://erdogant.github.io/datasets/energy_source_target_value.zip'
    elif graph=='stormofswords':
        # Sankey demo
        url='https://erdogant.github.io/datasets/stormofswords.zip'
    elif graph=='bigbang':
        # Initialize
        d3model = d3graph()
        df = d3model.import_example('bigbang')
        return d3ng.adjmat2vec(df)
    elif graph=='southern_nebula':
        # Image slider demo
        url='https://erdogant.github.io/datasets/southern_nebula.zip'
        ext='.jpg'
    elif graph=='iris':
        from sklearn import datasets
        iris = datasets.load_iris()
        X = iris.data[:, :2]  # we only take the first two features.
        labels = iris.target
        df = pd.DataFrame(data=X, index=labels, columns=['x','y'])
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
        df = Movingbubbles.import_example(csvfile)
    if graph=='energy':
        df = pd.read_csv(csvfile)
        df.rename(columns={'value': 'weight'}, inplace=True)
        df[['source', 'target']] = df[['source', 'target']].astype(str)
    if graph=='stormofswords':
        df = pd.read_csv(csvfile)
        # df.rename(columns={'weight':'value'}, inplace=True)
    if graph=='southern_nebula':
        img_before = os.path.join(os.path.split(csvfile)[0], 'southern_nebula_before.jpg')
        img_after = os.path.join(os.path.split(csvfile)[0], 'southern_nebula_after.jpg')
        return img_before, img_after

    # Return
    return df


# %%
def generate_data_with_random_datetime(n=10000, c=1000, date_start=None, date_stop=None):
    """Generate random time data.

    Parameters
    ----------
    n : int, (default: 10000).
        Number of events or data points.
    c : int, (default: 1000).
        Number of unique classes.
    date_start : str, (default: None)
        "1-1-2000 00:00:00" : start date
    date_stop : str, (default: None)
        1-1-2010 23:59:59" : Stop date

    Returns
    -------
    df : DataFrame
        Example dataset with datetime.

    """
    if date_start is None:
        date_start="1-1-2000 00:00:00"
        logger.info('Date start is set to %s' %(date_start))
    if date_stop is None:
        date_stop="1-1-2010 23:59:59"
        logger.info('Date start is set to %s' %(date_stop))

    # Create empty dataframe
    df = pd.DataFrame(columns=['datetime', 'sample_id', 'state'], data=np.array([[None, None, None]] * n))
    location_types = ['Home', 'Hospital', 'Bed', 'Sport', 'Sleeping', 'Sick', 'Work', 'Eating', 'Bored']
    # Take random few columns
    location_types = location_types[0:random.randint(2, len(location_types))]
    # Always add the column Travel
    location_types = location_types + ['Travel']

    # Generate random timestamps with catagories and sample ids
    for i in tqdm(range(0, df.shape[0])):
        df['sample_id'].iloc[i] = random.randint(0, c)
        # df['sample_id'].iloc[i] = int(np.floor(np.absolute(np.random.normal(0, c))))
        df['state'].iloc[i] = location_types[random.randint(0, len(location_types) - 1)]
        df['datetime'].iloc[i] = random_date(date_start, date_stop, random.random())
    df['datetime'] = pd.to_datetime(df['datetime'])
    df = df.sort_values(by="datetime")
    df.reset_index(inplace=True, drop=True)
    return df


def str_time_prop(start, end, dt_format, prop):
    """Get a time at a proportion of a range of two formatted times.

    start and end should be strings specifying times formatted in the
    given format (strftime-style), giving an interval [start, end].
    prop specifies how a proportion of the interval to be taken after
    start.  The returned time will be in the specified format.
    """

    stime = time.mktime(time.strptime(start, dt_format))
    etime = time.mktime(time.strptime(end, dt_format))
    ptime = stime + prop * (etime - stime)
    return time.strftime(dt_format, time.localtime(ptime))


def random_date(start, end, prop, dt_format='%d-%m-%Y %H:%M:%S'):
    return str_time_prop(start, end, dt_format, prop)


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
            # if not os.path.isfile(getpath):
                # logger.error('Extraction failed.')
                # getpath = None
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
def _showfig(filepath: str):
    file_location = os.path.abspath(filepath)
    if platform == "darwin":  # check if on OSX
        file_location = "file:///" + file_location
    webbrowser.open(file_location, new=2)


def remove_quotes(df):
    df.loc[:, df.dtypes==object].apply(lambda s: s.str.replace("'", ""))
    return df

# %% Do checks
def library_compatibility_checks():
    """Library compatibiliy checks.

    Returns
    -------
    None.

    """
    # if not version.parse(nx.__version__) >= version.parse("2.5"):
        # logger.error('Networkx version should be >= 2.5')
        # logger.info('Hint: pip install -U networkx')
    pass


# %% Main
# if __name__ == "__main__":
#     import d3blocks as d3blocks
#     df = d3blocks.import_example()
#     out = d3blocks.fit(df)
#     fig,ax = d3blocks.plot(out)
