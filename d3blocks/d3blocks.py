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
import Movingbubbles as Movingbubbles
import random
import time
import colourmap

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

    def __init__(self, cmap='Set1', verbose=20):
        """Initialize d3blocks with user-defined parameters."""
        # Clean
        self._clean(clean_config=True)
        # Some library compatibily checks
        library_compatibility_checks()
        # Initialize empty config
        self.config = {}
        self.config['cmap'] = cmap
        self.config['curpath'] = os.path.dirname(os.path.abspath(__file__))
        # Set the logger
        set_logger(verbose=verbose)

    def movingbubbles(self, df, datetime='datetime', sample_id='sample_id', state='state', center=None, reset_time='day', speed={"slow": 1000, "medium": 200, "fast": 50}, figsize=(780, 800), note=None, title='movingbubbles', filepath='movingbubbles.html', showfig=True, overwrite=True):
        """Creation of moving bubble graph.

        Parameters
        ----------
        df : Input data
            Input data.
        center : String, (default: None)
            Center this category.
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
        overwrite : bool, (default: True)
            Overwrite the existing html file.

        Returns
        -------
        None.

        """
        if note is None: note=("This is a simulation of %s groups across time. <a href='https://github.com/d3blocks/d3blocks'>d3blocks movingbubbles</a>." %(df.shape[0]))
        self.config['chart'] ='movingbubbles'
        self.config['filepath'] = self.set_path(filepath)
        self.config['title'] = title
        self.config['figsize'] = figsize
        self.config['showfig'] = showfig
        self.config['overwrite'] = overwrite
        self.config['center'] = center
        self.config['reset_time'] = reset_time
        self.config['speed'] = speed
        self.config['note'] = note
        self.config['columns'] = {'datetime': datetime, 'sample_id': sample_id, 'state': state}

        # Compute delta
        if isinstance(df, pd.DataFrame) and np.any(df.columns==state) and np.any(df.columns==datetime) and np.any(df.columns==sample_id):
            df = self.compute_delta(df, sample_id=sample_id, datetime=datetime, state=state)
        # Set label properties
        if isinstance(df, pd.DataFrame) and not hasattr(self, 'labels') and np.any(df.columns==state):
            self.set_label_properties(df[state])
        if not isinstance(df, pd.DataFrame):
            self.labels=None
        if not hasattr(self, 'labels'):
            raise Exception('Set labels is required first or specify the category.')

        # Create the plot
        self.config = Movingbubbles.show(df, self.config, self.labels)

        # Open the webbrowser
        if self.config['showfig']:
            # Sleeping is required to pevent overlapping windows
            webbrowser.open(os.path.abspath(self.config['filepath']), new=2)

    def compute_delta(self, df, sample_id, datetime, state):
        logger.info('Compute time delta.')
        # Compute delta
        df = Movingbubbles.compute_delta(df, sample_id, datetime)
        # Set default label properties
        self.set_label_properties(df[state].values)
        # Return
        return df

    def set_label_properties(self, y):
        logger.info('Extracting label properties')
        # Get unique categories
        uiy = np.unique(y)
        # Create unique colors
        hexcolors = colourmap.generate(len(uiy), cmap=self.config['cmap'], scheme='hex')
        # Make dict with properties
        labels = {}
        for i, cat in enumerate(uiy):
            labels[cat] = {'id': i, 'color': hexcolors[i], 'desc': cat, 'short': cat}
        self.labels = labels

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

    def import_example(self, data='movingbubbles', n=1000, groups=100, date_start=None, date_stop=None):
        """Import example dataset from github source.

        Description
        -----------
        Import one of the few datasets from github source or specify your own download url link.

        Parameters
        ----------
        data : str
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
        return _import_example(data=data, n=n, groups=groups, date_start=date_start, date_stop=date_stop)


# %% Import example dataset from github.
def _import_example(data='movingbubbles', n=1000, groups=100, date_start=None, date_stop=None):
    """Import example dataset from github source.

    Description
    -----------
    Import one of the few datasets from github source or specify your own download url link.

    Parameters
    ----------
    data : str
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
    if data=='movingbubbles':
        url='https://erdogant.github.io/datasets/movingbubbles.zip'
    if data=='random_time':
        return generate_data_with_random_datetime(n, groups=groups, date_start=date_start, date_stop=date_stop)

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


# %%
def generate_data_with_random_datetime(n=1000, groups=100, date_start=None, date_stop=None):
    """Generate random time data.

    Parameters
    ----------
    n : int, (default: 1000).
        Number of events or data points.
    groups : int, (default: 1000).
        Number of unique groups.
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
    location_types = ['Home', 'Hospital', 'Bed', 'Sport', 'Sleeping', 'Sick', 'Travel']

    # Generate random timestamps with catagories and sample ids
    for i in range(0, df.shape[0]):
        # df['sample_id'].iloc[i] = random.randint(0, groups)
        df['sample_id'].iloc[i] = int(np.floor(np.absolute(np.random.normal(0, groups))))
        df['state'].iloc[i] = location_types[random.randint(0, len(location_types) - 1)]
        df['datetime'].iloc[i] = random_date(date_start, date_stop, random.random())
    df['datetime'] = pd.to_datetime(df['datetime'])
    df = df.sort_values(by="datetime")
    df.reset_index(inplace=True, drop=True)
    return df

def str_time_prop(start, end, time_format, prop):
    """Get a time at a proportion of a range of two formatted times.

    start and end should be strings specifying times formatted in the
    given format (strftime-style), giving an interval [start, end].
    prop specifies how a proportion of the interval to be taken after
    start.  The returned time will be in the specified format.
    """

    stime = time.mktime(time.strptime(start, time_format))
    etime = time.mktime(time.strptime(end, time_format))
    ptime = stime + prop * (etime - stime)
    return time.strftime(time_format, time.localtime(ptime))


def random_date(start, end, prop):
    return str_time_prop(start, end, '%d-%m-%Y %H:%M:%S', prop)


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
