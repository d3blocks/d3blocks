# %%
import d3blocks
print(dir(d3blocks))
print(d3blocks.__version__)

# %%
from d3blocks import d3blocks
model = d3blocks(verbose=10)
model.fit_transform()

# %%
