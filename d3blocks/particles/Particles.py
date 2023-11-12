"""Particles block.

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
try:
    from .. utils import set_path, write_html_file, include_save_to_svg_script
except:
    from utils import set_path, write_html_file, include_save_to_svg_script


def show(text, config, logger):
    """Build and show the graph.

    Parameters
    ----------
    text : string
        String to be visualized
    config : dict
        Dictionary containing configuration keys.

    Returns
    -------
    config : dict
        Dictionary containing updated configuration keys.

    """
    # Write to HTML
    return write_html(text, config, logger)


def write_html(X, config, logger):
    """Write html.

    Parameters
    ----------
    X : list of str
        Input data for javascript.
    config : dict
        Dictionary containing configuration keys.

    Returns
    -------
    None.

    """
    # Save button
    save_script, show_save_button = include_save_to_svg_script(config['save_button'], title=config['title'])

    content = {
        'json_data': X,
        'TITLE': config['title'],
        'WIDTH': config['figsize'][0],
        'HEIGHT': config['figsize'][1],
        'COLOR_BACKGROUND': config['color_background'],
        'RADIUS': config['radius'],
        'COLLISION': config['collision'],
        'FONTSIZE': config['fontsize'],
        'SPACING': config['spacing'],
        'CMAP': config['cmap'],
        'SUPPORT': config['support'],
        'SAVE_TO_SVG_SCRIPT': save_script,
        'SAVE_BUTTON_START': show_save_button[0],
        'SAVE_BUTTON_STOP': show_save_button[1],
    }

    try:
        jinja_env = Environment(loader=PackageLoader(package_name=__name__, package_path='d3js'))
    except:
        jinja_env = Environment(loader=PackageLoader(package_name='d3blocks.particles', package_path='d3js'))

    index_template = jinja_env.get_template('particles.html.j2')

    # Generate html content
    html = index_template.render(content)
    write_html_file(config, html, logger)
    # Return html
    return html
