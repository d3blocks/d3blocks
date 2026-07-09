# -*- coding: utf-8 -*-
"""Elasticgraph"""

import logging

try:
    from d3blocks.elasticgraph.elasticgraph import Elasticgraph
except:
    from elasticgraph.elasticgraph import Elasticgraph

logging.getLogger(__name__).addHandler(logging.NullHandler())

