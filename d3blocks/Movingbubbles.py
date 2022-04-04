"""Moving bubble graph"""

import pandas as pd
import re
from tqdm import tqdm
import os
from jinja2 import Environment, PackageLoader
from pathlib import Path

def show(X, config):
    """Build and show the graph.

    Parameters
    ----------
    X : Input data
        Input data.

    Returns
    -------
    None.

    """
    print('Moving bubbles')
    write_html(X, config)


def write_html(X, config, overwrite=True):
    """Write html.

    Parameters
    ----------
    X : data file

    Returns
    -------
    None.

    """
    content = {
        'json_data': X,
        'title': config['title'],
        'center': '"' + config['center'] + '"',
        'width': config['figsize'][0],
        'height': config['figsize'][1],
    }

    jinja_env = Environment(loader=PackageLoader(package_name=__name__, package_path='d3js'))
    index_template = jinja_env.get_template('movingbubbles.html.j2')
    index_file = Path(config['filepath'])
    print('Write to path: [%s]' % index_file.absolute())
    # index_file.write_text(index_template.render(content))
    if os.path.isfile(index_file):
        if overwrite:
            print('File already exists and will be overwritten: [%s]' %(index_file))
            os.remove(index_file)
    with open(index_file, "w", encoding="utf-8") as f:
        f.write(index_template.render(content))


def import_example(filepath):
    print('Reading %s' %(filepath))
    lines = []
    with open(filepath) as f:
        for line in tqdm(f):
            # Remove patterns
            line = re.sub('[\n]', '', line)
            # Replace multiple spaces with a single one
            line = re.sub(' +', ' ', line)
            # Strip
            line = line.strip()
            lines.append(line)
    return lines
