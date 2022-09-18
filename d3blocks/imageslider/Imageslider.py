"""Imageslider block.

Library     : d3blocks
Author      : E.Taskesen
Mail        : erdogant@gmail.com
Github      : https://github.com/d3blocks/d3blocks
License     : GPL3
"""

from jinja2 import Environment, PackageLoader
from pathlib import Path
import os
import time


def show(config):
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
    write_html(img_before, img_after, config)
    # Return config
    return config


def write_html(img_before, img_after, config):
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

    jinja_env = Environment(loader=PackageLoader(package_name=__name__, package_path='d3js'))
    index_template = jinja_env.get_template('imageslider.html.j2')
    index_file = Path(config['filepath'])
    # index_file.write_text(index_template.render(content))
    if config['overwrite'] and os.path.isfile(index_file):
        print('File already exists and will be overwritten: [%s]' %(index_file))
        os.remove(index_file)
        time.sleep(0.5)
    with open(index_file, "w", encoding="utf-8") as f:
        f.write(index_template.render(content))
