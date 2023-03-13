<p align="center">
  <a href="https://d3blocks.github.io/d3blocks/pages/html/index.html">
  <img src="https://github.com/d3blocks/d3blocks/blob/main/logo.png" align="center" width="600" /> 
  </a>
</p>


[![Python](https://img.shields.io/pypi/pyversions/d3blocks)](https://img.shields.io/pypi/pyversions/d3blocks)
[![Pypi](https://img.shields.io/pypi/v/d3blocks)](https://pypi.org/project/d3blocks/)
[![Docs](https://img.shields.io/badge/Sphinx-Docs-blue)](https://d3blocks.github.io/d3blocks/)
[![LOC](https://sloc.xyz/github/d3blocks/d3blocks/?category=code)](https://github.com/d3blocks/d3blocks/)
[![Downloads](https://static.pepy.tech/personalized-badge/d3blocks?period=month&units=international_system&left_color=grey&right_color=brightgreen&left_text=PyPI%20downloads/month)](https://pepy.tech/project/d3blocks)
[![Downloads](https://static.pepy.tech/personalized-badge/d3blocks?period=total&units=international_system&left_color=grey&right_color=brightgreen&left_text=Downloads)](https://pepy.tech/project/d3blocks)
[![License](https://img.shields.io/badge/license-GPL3-green.svg)](https://github.com/d3blocks/d3blocks/blob/master/LICENSE)
[![Forks](https://img.shields.io/github/forks/d3blocks/d3blocks.svg)](https://github.com/d3blocks/d3blocks/network)
[![Open Issues](https://img.shields.io/github/issues/d3blocks/d3blocks.svg)](https://github.com/d3blocks/d3blocks/issues)
[![Project Status](http://www.repostatus.org/badges/latest/active.svg)](http://www.repostatus.org/#active)
[![Medium](https://img.shields.io/badge/Medium-Blog-black)](https://d3blocks.github.io/d3blocks/pages/html/Documentation.html#medium-blog)
![GitHub Repo stars](https://img.shields.io/github/stars/d3blocks/d3blocks)
![GitHub repo size](https://img.shields.io/github/repo-size/d3blocks/d3blocks)
[![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://d3blocks.github.io/d3blocks/pages/html/Documentation.html#colab-notebook)
[![Donate](https://img.shields.io/badge/Support%20this%20project-grey.svg?logo=github%20sponsors)](https://d3blocks.github.io/d3blocks/pages/html/Documentation.html#)

-------------------------------------------------------------------------

D3Blocks builts on the graphics of d3 javascript (d3js) to create the most visually attractive and useful charts with only a few lines of Python code!
The [documentation pages](https://d3blocks.github.io/d3blocks/) contains detailed information about the working of the blocks with many examples. 

<p align="center">
  <a href="https://d3blocks.github.io/d3blocks/pages/html/index.html">
  <img src="https://github.com/d3blocks/d3blocks/blob/main/docs/figs/summary.png" width="600" />
  </a>
</p>

-------------------------------------------------------------------------

#### Installation (Pypi)
```bash
pip install d3blocks     # Normal installation
pip install -U d3blocks  # Force update
```

#### Installation (clone)
```bash
git clone https://github.com/d3blocks/d3blocks.git
cd d3blocks
pip install -U .
```  

#### Import d3blocks package
```python
from d3blocks import d3blocks
# Initialize
d3 = D3Blocks()
```

-------------------------------------------------------------------------
### [Supported charts](https://d3blocks.github.io/d3blocks/)


|  Block                                                                             |    Function                  |    Blog                                                                                                                              |
|------------------------------------------------------------------------------------|------------------------------|--------------------------------------------------------------------------------------------------------------------------------------|
| [D3graph](https://erdogant.github.io/d3graph/pages/html/index.html)                | ``` d3.d3graph() ```         | [D3graph](https://towardsdatascience.com/creating-beautiful-stand-alone-interactive-d3-charts-with-python-804117cb95a7)              |
| [Elasticgraph](https://d3blocks.github.io/d3blocks/pages/html/elasticgraph.html)   | ``` d3.elasticgraph() ```    | [Elasticgraph](https://towardsdatascience.com/creating-beautiful-stand-alone-interactive-d3-charts-with-python-804117cb95a7)         |
| [Sankey](https://d3blocks.github.io/d3blocks/pages/html/Sankey.html)               | ``` d3.sankey()  ```         | [Sankey](https://towardsdatascience.com/hands-on-guide-to-create-beautiful-sankey-charts-in-d3js-with-python-8ddab43edb43)           |
| [Movingbubbles](https://d3blocks.github.io/d3blocks/pages/html/MovingBubbles.html) | ``` d3.movingbubbles()  ```  | [Movingbubbles](https://towardsdatascience.com/how-to-create-storytelling-moving-bubbles-charts-in-d3js-with-python-b31cec7b8226)    |
| [Scatter](https://d3blocks.github.io/d3blocks/pages/html/Scatter.html)             | ``` d3.scatter()  ```        | [Scatter](https://towardsdatascience.com/get-the-most-out-of-your-scatterplot-by-making-it-interactive-using-d3js-19939e3b046)       |
| [Heatmap](https://d3blocks.github.io/d3blocks/pages/html/Heatmap.html)             | ``` d3.heatmap()  ```        | [D3Blocks](https://towardsdatascience.com/d3blocks-the-python-library-to-create-interactive-and-standalone-d3js-charts-3dda98ce97d4) |
| [Chord diagram](https://d3blocks.github.io/d3blocks/pages/html/Chord.html)         | ``` d3.chord()  ```          | [D3Blocks](https://towardsdatascience.com/d3blocks-the-python-library-to-create-interactive-and-standalone-d3js-charts-3dda98ce97d4) |
| [Timeseries](https://d3blocks.github.io/d3blocks/pages/html/Timeseries.html)       | ``` d3.timeseries()  ```     | [D3Blocks](https://towardsdatascience.com/d3blocks-the-python-library-to-create-interactive-and-standalone-d3js-charts-3dda98ce97d4) |
| [Image slider](https://d3blocks.github.io/d3blocks/pages/html/Imageslider.html)    | ``` d3.imageslider()  ```    | [D3Blocks](https://towardsdatascience.com/d3blocks-the-python-library-to-create-interactive-and-standalone-d3js-charts-3dda98ce97d4) |
| [Violin plot](https://d3blocks.github.io/d3blocks/pages/html/Violin.html)          | ``` d3.violin()  ```         | [D3Blocks](https://towardsdatascience.com/d3blocks-the-python-library-to-create-interactive-and-standalone-d3js-charts-3dda98ce97d4) |
| [Particles](https://d3blocks.github.io/d3blocks/pages/html/Particles.html)         | ``` d3.particles()  ```      | [D3Blocks](https://towardsdatascience.com/d3blocks-the-python-library-to-create-interactive-and-standalone-d3js-charts-3dda98ce97d4) |
| [Treemap](https://d3blocks.github.io/d3blocks/pages/html/Treemap.html)             | ``` d3.treemap()  ```        | [D3Blocks](https://towardsdatascience.com/d3blocks-the-python-library-to-create-interactive-and-standalone-d3js-charts-3dda98ce97d4) |
|                                                                                    |                              |                                                                                                                                      |

-------------------------------------------------------------------------

#### References
* [bl.ocks](https://bl.ocks.org/)
* [observablehq](https://observablehq.com/top)
