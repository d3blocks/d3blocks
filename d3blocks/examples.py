# %%
# import d3blocks
# print(dir(d3blocks))
# print(d3blocks.__version__)

# %%
# from d3blocks import d3blocks
# d3 = d3blocks()
# X = d3.import_example(data='movingbubbles')
# d3.movingbubbles(X, filepath='c://temp/movingbubbles_original.html', center='Traveling')

# %% Create random dataset
from d3blocks import d3blocks
d3 = d3blocks(cmap='Set1')

df = d3.import_example(data='random_time', n=10000, c=100, date_start="1-1-2000 00:10:05", date_stop="1-2-2000 23:59:59")
# df = d3.import_example(data='random_time', n=1000)

# # Compute delta
# df = d3.preprocessing(df, sample_id='sample_id', datetime='datetime', state='state')
# d3.labels

# Make the moving bubbles
d3.movingbubbles(df, datetime='datetime', state='state', sample_id='sample_id', center='Travel', speed={"slow": 1000, "medium": 200, "fast": 10}, filepath='c://temp/movingbubbles.html')


# %%
# Import example
df = d3.import_example(data='random_time', n=10000, c=100, date_start="1-1-2000 00:10:05", date_stop="1-2-2000 23:59:59")
# Normalize the time per sample id.
df = d3.normalize_time(df)
# Make the moving bubbles
d3.movingbubbles(df, datetime='datetime_norm', state='state', sample_id='sample_id', center='Travel', speed={"slow": 1000, "medium": 200, "fast": 10}, filepath='c://temp/movingbubbles.html')


# %%

X = ['0,10,1,10,2,10,3,10,4,10,5,10,6,10,7,10,8,10,9,10,10,10,0,10', '0,20,1,20,2,20,3,20,4,20,5,20,0,20']
d3.movingbubbles(X, filepath='c://temp/movingbubbles.html', center='Traveling')

# %%
# import pandas as pd
# X[0:10]

# 	{"index": "0", "short": "Sleeping", "desc": "Sleeping"},
# 	{"index": "1", "short": "Personal Care", "desc": "Personal Care"},
# 	{"index": "2", "short": "Eating & Drinking", "desc": "Eating and Drinking"},
# 	{"index": "3", "short": "Education", "desc": "Education"},
# 	{"index": "4", "short": "Work", "desc": "Work and Work-Related Activities"},
# 	{"index": "5", "short": "Housework", "desc": "Household Activities"},

# df = pd.DataFrame(columns=['Sleeping', 'Personal Care', 'Eating & Drinking', 'Work', 'Housework'], data)

# 0,270
# 5,32
# 5,165
# 2,35
# 4,300
# 1,53
# 0,370

# %%
