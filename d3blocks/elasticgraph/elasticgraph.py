"""Elasticgraph block.

Library     : d3blocks
Author      : E.Taskesen
Github      : https://github.com/d3blocks/d3blocks
License     : GPL3

"""
import logging
import os
from pathlib import Path
from typing import List, Union, Tuple
from d3graph import d3graph, json_create, data_checks, make_graph
from jinja2 import Environment, PackageLoader

# logger = logging.getLogger('')
# for handler in logger.handlers[:]:
#     logger.removeHandler(handler)
# console = logging.StreamHandler()
# formatter = logging.Formatter('[elasticgraph] %(levelname)s> %(message)s')
# console.setFormatter(formatter)
# logger.addHandler(console)
# logger = logging.getLogger()

logger = logging.getLogger(__name__)
if not logger.hasHandlers():
    logging.basicConfig(level=logging.INFO, format='[{asctime}] [{name}] [{levelname}] {msg}', style='{', datefmt='%Y-%m-%d %H:%M:%S')


# %%
class Elasticgraph:
    """Create interactive networks in d3js.

    Description
    -----------
    D3-force-graph is integrated in d3blocks to create interactive and stand-alone D3 force-directed graphs for which
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
    radius : float, (default: 4)
        Size of the nodes.
    hull_offset : float, (default: 15)
        The higher the number the more the clusters will overlap after expanding.
    collision : float, (default: 0.5)
        Response of the network. Higher means that more collisions are prevented.
    charge : int, (default: 250)
        Edge length of the network. Towards zero becomes a dense network. Higher make edges longer.
    single_click_expand : bool, (default: True)
        Nodes are expanded with a single click.
    verbose : int, (default: 20)
        Print progress to screen.
        60: None, 40: Error, 30: Warn, 20: Info, 10: Debug

    Returns
    -------
    None.

    References
    ----------
    * Blog: erdogant.medium.com
    * Fork Ger Hobbelts (Block 3104394): https://bl.ocks.org/GerHobbelt/3104394
    """

    def __init__(self, radius: int = 4, hull_offset: int = 15, collision: float = 0.5, charge: int = 250, verbose: int = 20, single_click_expand: bool = True) -> None:
        """Initialize elasticgraph."""
        self.D3graph = d3graph()
        # Cleaning
        self.D3graph._clean()
        # Set the logger
        set_logger(verbose=verbose)
        # Setup configurations
        self.D3graph.config = {}
        self.D3graph.config['point_radius'] = radius
        self.D3graph.config['hull_offset'] = hull_offset
        self.D3graph.config['debug'] = '0'
        self.D3graph.config['collision'] = collision
        self.D3graph.config['charge'] = -abs(charge)
        self.D3graph.config['single_click_expand'] = single_click_expand
        # Set paths
        self.D3graph.config['curpath'] = os.path.dirname(os.path.abspath(__file__))
        self.D3graph.config['d3_library'] = os.path.abspath(os.path.join(self.D3graph.config['curpath'], 'd3js/d3.v2.js'))
        self.D3graph.config['d3_script'] = os.path.abspath(os.path.join(self.D3graph.config['curpath'], 'd3js/elasticgraph_script.js'))
        self.D3graph.config['css'] = os.path.abspath(os.path.join(self.D3graph.config['curpath'], 'd3js/style.css'))

    def graph(self,
              adjmat,
              group: str = 'cluster',
              scaler: str = 'zscore') -> None:
        """Process the adjacency matrix and set all properties to default.

        Description
        -----------
        This function processes the adjacency matrix. The nodes are the column and index names.
        A connect edge is seen in case vertices have values larger than 0. The strenght of the edge is based on the vertices values.

        Parameters
        ----------
        adjmat : pd.DataFrame()
            Adjacency matrix (symmetric). Values > 0 are edges.
        group : list of strings (default: 'cluster')
            Grouping (and coloring) of the nodes.
            * 'cluster' : Colours are based on the community distance clusters.
            * None: All nodes will have the same color (auto generated).
        scaler : str, (default: 'zscore')
            Scale the edge-width using the following scaler:
            'zscore' : Scale values to Z-scores.
            'minmax' : The sklearn scaler will shrink the distribution between minmax.
            None : No scaler is used.

        Examples
        --------
        >>> from elasticgraph import Elasticgraph
        >>> #
        >>> # Initialize
        >>> d3 = Elasticgraph()
        >>> #
        >>> # Load karate example
        >>> adjmat, _ = d3.import_example('karate')
        >>> #
        >>> # Initialize
        >>> d3.graph(adjmat)
        >>> #
        >>> # Plot
        >>> d3.show()
        >>> #
        >>> # Node properties
        >>> d3.set_node_properties(label=df['label'].values, color=df['label'].values, size=df['degree'].values, edge_size=df['degree'].values, cmap='Set1')
        >>> #
        >>> print(d3.D3graph.edge_properties)
        >>> print(d3.D3graph.node_properties)
        >>> #
        >>> # Plot
        >>> d3.show()
        >>> #
        >>> # Example 2:
        >>> # Initialize
        >>> d3 = Elasticgraph(single_click_expand=True)
        >>> # Load karate example
        >>> adjmat, _ = d3.import_example('karate')
        >>> # Initialize
        >>> d3.graph(adjmat)
        >>> # Plot
        >>> d3.show()

        Returns
        -------
        None

        """
        # Clean readily fitted models to ensure correct results
        self.D3graph._clean(clean_config=False)
        # Checks
        # self.adjmat = data_checks(adjmat.copy())
        self.D3graph.adjmat = data_checks(adjmat.copy())
        # Set default edge properties
        self.D3graph.set_edge_properties(scaler=scaler)
        # Set default node properties
        self.D3graph.set_node_properties(color=group, scaler=scaler)

    def show(self,
             figsize: Tuple[int, int] = (1500, 800),
             title: str = 'elasticgraph',
             filepath: str = 'elasticgraph.html',
             showfig: bool = True,
             overwrite: bool = True,
             notebook: bool = False,
             ) -> None:
        """Build and show the graph.

        Parameters
        ----------
        figsize : tuple, (default: (1500, 800))
            Size of the figure in the browser, [width, height].
        title : String, (default: None)
            Title of the figure.
        filepath : String, (Default: user temp directory)
            File path to save the output.
            Temporarily path: 'elasticgraph.html'
            Relative path: './elasticgraph.html'
            Absolute path: 'c://temp//elasticgraph.html'
            None: Return HTML
        showfig : bool, (default: True)
            Open the window to show the network.
        overwrite : bool, (default: True)
            Overwrite the existing html file.
        notebook : bool
            True: Use IPython to show chart in notebooks.
            False: Do not use IPython.

        Returns
        -------
        None.

        """
        # Some checks
        if not hasattr(self.D3graph, 'edge_properties') or not hasattr(self.D3graph, 'node_properties'):
            logger.warning('No graph detected. <return> Hint: "d3.graph(df)"')
            return None

        self.D3graph.config['figsize'] = figsize
        self.D3graph.config['network_title'] = title
        self.D3graph.config['showfig'] = showfig
        self.D3graph.config['notebook'] = notebook
        self.D3graph.config['filepath'] = self.D3graph.set_path(filepath)

        # Create dataframe from co-occurrence matrix
        self.D3graph.G = make_graph(self.D3graph.node_properties, self.D3graph.edge_properties)
        # Create json
        json_data = json_create(self.D3graph.G)
        # Create html with json file embedded
        html = self.write_html(json_data, overwrite=overwrite)
        # Display the chart
        return self.D3graph.display(html)
        # if self.D3graph.config['showfig']:
        #     self.D3graph.showfig(self.D3graph.config['filepath'])
        # return html

    def set_edge_properties(self,
                            edge_distance: int = None,
                            scaler: str = 'zscore',
                            minmax: List[float] = None,
                            directed: bool = False,
                            marker_start=None,
                            marker_end='arrow',
                            marker_color='#808080') -> dict:
        """Edge properties.

        Parameters
        ----------
        edge_distance : Int (default: 30)
            Distance of nodes on the edges.
            * 0: Weighted approach using edge weights in the adjacency matrix. Weights are normalized between the minmax
            * 80: Constant edge distance
        scaler : str, (default: 'zscore')
            Scale the edge-width using the following scaler:
            'zscore' : Scale values to Z-scores.
            'minmax' : The sklearn scaler will shrink the distribution between minmax.
            None : No scaler is used.
        minmax : tuple(float, float), (default: [0.5, 15.0])
            Weights are normalized between minimum and maximum
            * [0.5, 15]
        directed : Bool, (default: False)
            True: Edges are shown with an marker (e.g. arrow)
            False: Edges do not show markers.
        marker_start : (list of) str, (default: 'arrow')
            The start of the edge can be one of the following markers:
            'arrow','square','circle','stub',None or ''
        marker_end : (list of) str, (default: 'arrow')
            The end of the edge can be one of the following markers:
            'arrow','square','circle','stub',None or ''

        Returns
        -------
        edge_properties: dict
            key: (source, target)
                'weight': weight of the edge
                'weight_scaled': scaled weight of the edge
                'color': color of the edge

        """
        self.D3graph.set_edge_properties(edge_distance=edge_distance, scaler=scaler, minmax=minmax, directed=directed, marker_start=marker_start, marker_end=marker_end, marker_color=marker_color)

    def set_node_properties(self, label: List[str] = None,
                            tooltip: List[str] = None,
                            color: Union[str, List[str]] = '#000080',
                            size=10, edge_color='#000000',
                            edge_size=1,
                            cmap='Set1',
                            scaler='zscore',
                            minmax = [10, 50]):
        """Node properties.

        Parameters
        ----------
        label : list of names (default: None)
            The text that is shown on the Node.
            If not specified, the label text will be inherited from the adjacency matrix column-names.
            * ['label 1','label 2','label 3', ...]
        tooltip : list of names (default: None)
            The text that is shown when hovering over the Node.
            If not specified, the text will inherit from the label.
            * ['tooltip 1','tooltip 2','tooltip 3', ...]
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
        edge_color : list of strings (default: '#000080')
            Edge color of the node.
            * 'cluster' : Colours are based on the community distance clusters.
            * ['#377eb8','#ffffff','#000000',...]: Hex colors are directly used.
            * ['A']: All nodes will have hte same color. Color is generated on CMAP and the unique labels.
            * ['A','A','B',...]:  Colors are generated using cmap and the unique labels recordingly colored.
        edge_size : array of integers (default: 1)
            Size of the node edge. Note that node edge sizes are automatically scaled between [0.1 - 4].
            * 1: All nodes will be set on this size,
            * [2,5,1,...]  Specify per node the edge size.
        cmap : String, (default: 'Set1')
            All colors can be reversed with '_r', e.g. 'binary' to 'binary_r'
            'Set1',  'Set2', 'rainbow', 'bwr', 'binary', 'seismic', 'Blues', 'Reds', 'Pastel1', 'Paired'
        scaler : str, (default: 'zscore')
            Scale the edge-width using the following scaler:
            'zscore' : Scale values to Z-scores.
            'minmax' : The sklearn scaler will shrink the distribution between minmax.
            None : No scaler is used.
        minmax : tuple, (default: [10, 50])
            Scale the node size in the range of a minimum and maximum [5, 50] using the following scaler:
            'zscore' : Scale values to Z-scores.
            'minmax' : The sklearn scaler will shrink the distribution.
            None : No scaler is used.

        Returns
        -------
        node_properties: dict
            key: node_name
                'label': Label of the node
                'color': color of the node
                'size': size of the node
                'edge_size': edge_size of the node
                'edge_color': edge_color of the node

        """
        self.D3graph.set_node_properties(label=label, tooltip=tooltip, color=color, size=size, edge_color=edge_color, edge_size=edge_size, cmap=cmap, scaler=scaler, minmax=minmax)

    def write_html(self, json_data, overwrite: bool = True) -> None:
        """Write html.

        Parameters
        ----------
        json_data : json file

        Returns
        -------
        None.

        """
        content = {
            'json_data': json_data,
            'title': self.D3graph.config['network_title'],
            'width': self.D3graph.config['figsize'][0],
            'height': self.D3graph.config['figsize'][1],
            'point_radius': self.D3graph.config['point_radius'],
            'hull_offset': self.D3graph.config['hull_offset'],
            'debug': self.D3graph.config['debug'],
            'single_click_expand': self.D3graph.config['single_click_expand'],
        }

        try:
            jinja_env = Environment(loader=PackageLoader(package_name=__name__, package_path='d3js'))
        except:
            jinja_env = Environment(loader=PackageLoader(package_name='d3blocks.elasticgraph', package_path='d3js'))
        index_template = jinja_env.get_template('elasticgraph.html.j2')
        html = index_template.render(content)

        index_file = self.D3graph.config['filepath']
        if overwrite and index_file:
            logger.info(f'Write to path: [{index_file.absolute()}]')
            logger.info(f'File already exists and will be overwritten: [{index_file}]')
            if os.path.isfile(index_file): os.remove(index_file)
            with open(index_file, 'w', encoding='utf-8') as f:
                f.write(html)

        # write_html_file(config, html, logger)
        # Return html
        return html

    def import_example(self, network='small'):
        """Import example.

        Parameters
        ----------
        network : str, optional
            Import example adjacency matrix. The default is 'small'.

        Returns
        -------
        adjmat : pd.DataFrame()

        """
        return self.D3graph.import_example(network=network)

# %%
def set_logger(verbose: int = 20) -> None:
    """Set the logger for verbosity messages."""
    logger.setLevel(verbose)
