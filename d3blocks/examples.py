# %%
# import d3blocks
# print(dir(d3blocks))
# print(d3blocks.__version__)

# %%
from d3blocks import d3blocks
d3 = d3blocks()
X = d3.import_example(data='movingbubbles')
d3.movingbubbles(X, filepath='c://temp/movingbubbles.html')

# %%
