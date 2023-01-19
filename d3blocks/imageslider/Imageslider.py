"""Imageslider block.

Library     : d3blocks
Author      : E.Taskesen
Mail        : erdogant@gmail.com
Github      : https://github.com/d3blocks/d3blocks
License     : GPL3
"""

import numpy as np
from jinja2 import Environment, PackageLoader
from pathlib import Path
import os
import time
import re
try:
    from .. utils import set_path, write_html_file
except:
    from utils import set_path, write_html_file


# %% Set configuration properties
# def set_config(config, logger=None):
#     """Set the general configuration setting."""
#     config['chart'] ='imageslider'
#     config['title']='Imageslider - D3blocks',
#     config['filepath'] = set_path('imageslider.html')
#     config['showfig']=True
#     config['overwrite']=True
#     config['figsize']=[None, None]
#     config['scale']=True
#     config['colorscale']=-1
#     config['background']='#000000'
#     config['notebook'] = True
#     return config


# %% Preprocessing
def preprocessing(config, logger=None):
    """Preprocessing."""
    filepath_was_None = False
    if config['filepath'] is None:
        config['filepath'] = set_path('imageslider.html')
        filepath_was_None = True

    dirname, _ = os.path.split(config['filepath'])
    # Only load cv2 if requied
    # if (config['colorscale']>=0) and config['scale'] and (config['figsize'] is not None) and (config['figsize'][1] is not None):
    cv2 = _import_cv2(logger)

    imgs = ['img_before', 'img_after']
    # Check whether url
    for img in imgs:
        is_url, is_path, is_array = False, False, False
        if isinstance(config[img], str) and check_url(config[img]):
            logger.info('%s: %s' %(img, config[img]))
            is_url=True
        if isinstance(config[img], str) and os.path.isfile(config[img]):
            X = os.path.abspath(config[img])
            is_path=True
        if isinstance(config[img], (np.ndarray, np.generic)):
            X = config[img]
            is_array=True
        if is_path or is_array:
            # Preprocessing
            X = imread(cv2, X, is_path, colorscale=config['colorscale'], scale=config['scale'], dim=config['figsize'], logger=logger)
            # Save image
            filename = img + '.png'
            config[img] = filename
            cv2.imwrite(os.path.join(dirname, filename), X)

    config['alt_before'] = os.path.basename(config['img_before'])
    config['alt_after'] = os.path.basename(config['img_after'])
    
    if filepath_was_None: config['filepath']=None
    return config

# %% Check url
def check_url(url):
    regex = re.compile(
            r'^(?:http|ftp)s?://' # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
            r'localhost|' #localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
            r'(?::\d+)?' # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    
    isvalid = re.match(regex, url) is not None
    # Return
    return isvalid


def show(config, logger):
    """Build and show the graph.

    config : dict
        Dictionary containing configuration keys.

    Returns
    -------
    config : dict
        Dictionary containing updated configuration keys.

    """
    # Do stuff like rescale image if required to the same size.
    img_before = config['img_before']
    img_after = config['img_after']
    # Write to HTML
    return write_html(img_before, img_after, config, logger)


def write_html(img_before, img_after, config, logger):
    """Write html.

    Parameters
    ----------
    img_before : String
        absolute path to before image.
    img_after : String
        absolute path to after image.
    config : dict
        Dictionary containing configuration keys.
    overwrite : bool (default: True)
        True: Overwrite current exiting html file.
        False: Do not overwrite existing html file.

    Returns
    -------
    None.

    """
    content = {
        'TITLE': config['title'],
        'WIDTH': config['figsize'][0],
        'HEIGHT': config['figsize'][1],
        'IMG_BEFORE': img_before,
        'IMG_AFTER': img_after,
        'ALT_BEFORE': config['alt_before'],
        'ALT_AFTER': config['alt_after'],
        'BACKGROUND': config['background'],
    }

    try:
        jinja_env = Environment(loader=PackageLoader(package_name=__name__, package_path='d3js'))
    except:
        jinja_env = Environment(loader=PackageLoader(package_name='d3blocks.imageslider', package_path='d3js'))

    index_template = jinja_env.get_template('imageslider.html.j2')

    # Generate html content
    html = index_template.render(content)
    write_html_file(config, html, logger)
    # Return html
    return html


# %% Scaling
def imscale(img, cv2, logger=None):
    """Normalize image by scaling.

    Description
    -----------
    Scaling in range [0-255] by img*(255/max(img))

    Parameters
    ----------
    img : array-like
        Input image data.

    Returns
    -------
    img : array-like
        Scaled image.

    """
    try:
        # Normalizing between 0-255
        img = img - img.min()
        img = img / img.max()
        img = img * 255
        # Downscale typing
        img = np.uint8(img)
    except:
        logger.warning('Scaling not possible.')
    return img


# %% Resize image
def imresize(img, cv2, dim=(128, 128)):
    """Resize image."""

    if dim is not None:
        img = cv2.resize(img, dim, interpolation=cv2.INTER_AREA)
    return img


def imread(cv2, X, is_path, colorscale=1, scale=True, dim=[None, None], logger=None):
    """Read and pre-processing of images.

    Description
    -----------
    The pre-processing has 4 steps and are exectued in this order.
        * 1. Import data.
        * 2. Conversion to gray-scale (user defined)
        * 3. Scaling color pixels between [0-255]
        * 4. Resizing

    Parameters
    ----------
    filepath : str
        Full path to the image that needs to be imported.
    colorscale : int, default: 1 (gray)
        colour-scaling from opencv.
        * 0: cv2.IMREAD_GRAYSCALE
        * 1: cv2.IMREAD_COLOR
        * 2: cv2.IMREAD_ANYDEPTH
        * 8: cv2.COLOR_GRAY2RGB
        * -1: cv2.IMREAD_UNCHANGED
    dim : tuple, (default: (128,128))
        Rescale images. This is required because the feature-space need to be the same across samples.

    Returns
    -------
    img : array-like
        Imported and processed image.

    Examples
    --------
    >>> # Import libraries
    >>> from clustimage import Clustimage
    >>> import matplotlib.pyplot as plt
    >>>
    >>> # Init
    >>> cl = Clustimage()
    >>>
    >>> # Load example dataset
    >>> pathnames = cl.import_example(data='flowers')
    >>> # Preprocessing of the first image
    >>> img = cl.imread(pathnames[0], dim=(128,128), colorscale=1)
    >>>
    >>> # Plot
    >>> fig, axs = plt.subplots(1,2, figsize=(15,10))
    >>> axs[0].imshow(cv2.imread(pathnames[0])); plt.axis('off')
    >>> axs[1].imshow(img.reshape(128,128,3)); plt.axis('off')
    >>> fig
    >>>

    """
    img=[]
    readOK = False
    try:
        # Read the image
        if is_path:
            img = cv2.imread(X, colorscale)
            logger.info('Reading %s' %(X))
        else:
            img = X
        # Scale the image
        if scale:
            logger.info('Scaling image in range [0, 255]')
            img = imscale(img, cv2)
        # Resize the image
        if (dim[0] is not None) and (dim[1] is not None):
            logger.info('Resizing image towards: %s' %(dim))
            img = imresize(img, cv2, dim=dim)
        readOK = True
    except:
        logger.warning('Could not read: [%s]' %(X))

    if not readOK:
        raise Exception('Could not read image')
    # Return
    return img


def _import_cv2(logger):
    # Only required in case to adjust the images
    try:
        import cv2
        return cv2
    except:
        raise ImportError('cv2 must be installed manually. Try to: <pip install opencv-python>')
