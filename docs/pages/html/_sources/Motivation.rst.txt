Summary
###########
Python has become one the most popular programming languages to analyze and visualize your data. Visualizing can be the key to success in projects because it can reveal hidden insights in the data, and improve understanding. The best way to understand and explain the data is by making it interactive. Despite many visualization packages being available in Python, it remains challenging to create beautiful, stand-alone, and interactive charts that can also work outside your own machine. D3Blocks is a framework to create stand-alone, interactive charts. There is no need to install anything else than Python to create D3 charts, and after creating the chart, you only need a regular (internet) browser to plot the graphs. Sharing and publishing becomes thus super easy.


Why bother using D3.js?
#########################
In recent years, the Python community developed an impressive list of visualization libraries, such as Matplotlib, Seaborn, Bokeh, Plotly, Folium, and many more. Some libraries also allow graphs to be interactive but in such cases, they still require Python or other web services to keep them running. The advantage of D3 is its high performance, deeply customizable charts, and it works with web standards. Read more of the advantages of D3 in this blog. A summary is as follows; D3 is short for Data-Driven Documents, which is a JavaScript library for producing dynamic, interactive data visualizations in web browsers. It makes use of Scalable Vector Graphics (SVG), HTML5, and Cascading Style Sheets (CSS) standards. D3 is also named D3.js or d3js. I will use the names interchangeably.
"D3 helps you bring data to life using HTML, SVG, and CSS. D3's emphasis on web standards gives you the full capabilities of modern browsers without tying yourself to a proprietary framework, combining powerful visualization components and a data-driven approach to DOM manipulation.
You can basically add all your creativity to the charts without limits. However, the disadvantage is that it requires an understanding of the different elements such as SVG, HTML, CSS, and Javascript. We overcome the disadvantages by making it configurable using Python.


D3 Motivation
#########################

D3 is a collection of modules that are designed to work together; you can use the modules independently, or you can use them together as part of the default build. The D3 website provides 168 working charts that allow for performant incremental updates during interaction and supports popular interaction such as dragging, brushing, and zooming. The charts can be used for many purposes, such as quantitative analysis, visualizing hierarchies, creating networks graphs, but also bar plots, line plots, scatter plots, radial plots, geographic projections, and various other interactive visualizations for explorable explanations. 

D3 charts
#########################

By bridging the gap between d3 javascript and Python we combine the advantages of both worlds with the focus on creating charts that are not only beautiful but also practical for usage. The key advantage of D3 is that it works with web standards so you don't need any other technology than a browser to plot the graphs. We created D3Blocks in such a manner that each chart contains its own set of d3 libraries, and as such, it has the advantage of easily adopting new d3 charts.
Each graph created by D3Blocks is entirely encapsulated into a single HTML file which makes it very easy to share or publish on websites.



.. include:: add_bottom.add