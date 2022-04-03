import os
import pandas as pd
import requests
from urllib.parse import urlparse
import logging
import numpy as np
from tqdm import tqdm
import zipfile
import tempfile
import webbrowser
import d3blocks.Movingbubbles as Movingbubbles


logger = logging.getLogger('')
for handler in logger.handlers[:]: #get rid of existing old handlers
    logger.removeHandler(handler)
console = logging.StreamHandler()
formatter = logging.Formatter('[d3blocks] >%(levelname)s> %(message)s')
console.setFormatter(formatter)
logger.addHandler(console)
logger = logging.getLogger()


class d3blocks():
    """d3blocks."""

    def __init__(self, verbose=20):
        """Initialize d3blocks with user-defined parameters."""
        # Clean
        self._clean(clean_config=True)
        # Some library compatibily checks
        library_compatibility_checks()
        # Initialize empty config
        self.config = {}
        self.config['curpath'] = os.path.dirname(os.path.abspath(__file__))
        # Set the logger
        set_logger(verbose=verbose)

    def movingbubbles(self, X, figsize=(1500, 800), title='movingbubbles', filepath='movingbubbles.html', showfig=True, overwrite=True):
        """Creation of moving bubble graph.

        Parameters
        ----------
        X : Input data
            Input data.
        figsize : tuple, (default: (1500, 800))
            Size of the figure in the browser, [height, width].
        title : String, (default: None)
            Title of the figure.
        filepath : String, (Default: user temp directory)
            File path to save the output
        showfig : bool, (default: True)
            Open the window to show the network.
        overwrite : bool, (default: True)
            Overwrite the existing html file.

        Returns
        -------
        None.

        """
        self.config['chart'] ='movingbubbles'
        self.config['filepath'] = self.set_path(filepath)
        self.config['title'] = title
        self.config['figsize'] = figsize
        self.config['showfig'] = showfig
        self.config['overwrite'] = overwrite
        # Set path locations
        # self.config['d3_library'] = os.path.abspath(os.path.join(self.config['curpath'], 'd3js/d3-3-5-5.min.js'))
        # self.config['d3_script'] = os.path.abspath(os.path.join(self.config['curpath'], 'd3js/movingbubbles.html.j2'))
        # self.config['css'] = os.path.abspath(os.path.join(self.config['curpath'], 'd3js/style.css'))

        # Create the plot
        Movingbubbles.show(X, self.config)

        # Open the webbrowser
        if self.config['showfig']:
            # Sleeping is required to pevent overlapping windows
            webbrowser.open(os.path.abspath(self.config['filepath']), new=2)

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

        if (filename is None) or (filename==''):
            filename = 'd3blocks.html'

        if (dirname is None) or (dirname==''):
            dirname = tempfile.TemporaryDirectory().name

        if not os.path.isdir(dirname):
            logger.info('Create directory: [%s]' %(dirname))
            os.mkdir(dirname)

        filepath = os.path.abspath(os.path.join(dirname, filename))
        logger.debug("filepath is set to [%s]" %(filepath))
        return filepath

    def import_example(self, data='movingbubbles'):
        """Import example dataset from github source.

        Description
        -----------
        Import one of the few datasets from github source or specify your own download url link.

        Parameters
        ----------
        data : str
            Name of datasets: 'movingbubbles'
        url : str
            url link to to dataset.

        Returns
        -------
        pd.DataFrame()
            Dataset containing mixed features.

        """
        return _import_example(data=data)


# %% Import example dataset from github.
def _import_example(data='movingbubbles'):
    """Import example dataset from github source.

    Description
    -----------
    Import one of the few datasets from github source or specify your own download url link.

    Parameters
    ----------
    data : str
            Name of datasets: 'movingbubbles'
    url : str
        url link to to dataset.

    Returns
    -------
    pd.DataFrame()
        Dataset containing mixed features.

    """
    if data=='movingbubbles':
        url='https://erdogant.github.io/datasets/movingbubbles.zip'

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

    csvfile = unzip(PATH_TO_DATA, ext='.csv')

    # Import local dataset
    logger.info('Import dataset [%s]' %(data))
    if data=='movingbubbles':
        df = Movingbubbles.import_example(csvfile)

    # Return
    return df


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
            if not os.path.isfile(getpath):
                logger.error('Extraction failed.')
                getpath = None
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
        # logger.error('Networkx version should be >= 2.5')
        # logger.info('Hint: pip install -U networkx')
    pass

# %% Main
# if __name__ == "__main__":
#     import d3blocks as d3blocks
#     df = d3blocks.import_example()
#     out = d3blocks.fit(df)
#     fig,ax = d3blocks.plot(out)
