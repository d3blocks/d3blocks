from d3blocks.d3blocks import D3Blocks
from datazets import get as import_example
from d3blocks.utils import (
    normalize,
    scale,
    adjmat2vec,
    vec2adjmat,
    convert_flare2source_target,
    )

__author__ = 'Erdogan Taskesen'
__email__ = 'erdogant@gmail.com'
__version__ = '1.5.2'

# Setup root logger
import logging

_logger = logging.getLogger('D3Blocks')
_log_handler = logging.StreamHandler()
_fmt = '[{asctime}] [{name}] [{levelname}] {msg}'
_formatter = logging.Formatter(fmt=_fmt, style='{', datefmt='%d-%m-%Y %H:%M:%S')
_log_handler.setFormatter(_formatter)
_log_handler.setLevel(logging.DEBUG)
_logger.addHandler(_log_handler)
_logger.propagate = False


# module level doc-string
__doc__ = """
D3Blocks
=====================================================================

d3blocks is for the creation of stand-alone and interactive d3 graphs.
Create interactive, stand-alone, and visually attractive charts that are built on the graphics of d3 javascript (d3js)
but configurable with Python.

References
----------
* Github : https://github.com/d3blocks/d3blocks
* Docs: https://d3blocks.github.io/d3blocks/
* Blog: https://erdogant.medium.com

"""
