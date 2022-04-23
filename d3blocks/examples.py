# %%
# import d3blocks
# print(dir(d3blocks))
# print(d3blocks.__version__)

# %% Timeseries Examples
import pandas as pd
from d3blocks import d3blocks
d3 = d3blocks(cmap='Set2_r')

# Import example dataset
df = d3.import_example('timeseries', n=1000)
# Make the timeseries graph
df = d3.timeseries(df, datetime='datetime', filepath='c://temp/timeseries.html')


# %%
# from d3blocks import d3blocks
# d3 = d3blocks()
# X = d3.import_example(data='movingbubbles')
# d3.movingbubbles(X, filepath='c://temp/movingbubbles_original.html', center='Traveling')

# %% Make dataset manually to test the working
import pandas as pd
from d3blocks import d3blocks
d3 = d3blocks(cmap='Set2_r')

df1 = pd.DataFrame(columns=['datetime', 'sample_id', 'state'])
df1['datetime'] = ['2000-01-01 00:00:00', '2000-01-01 00:00:05', '2000-01-01 00:00:10', '2000-01-01 00:00:15', '2000-01-01 00:00:20', '2000-01-01 00:00:25']
df1['sample_id'] = [1, 1, 1, 1, 1, 1]
df1['state'] = ['home', 'school', 'work', 'eating', 'coffee', 'sleeping']

df2 = pd.DataFrame(columns=['datetime', 'sample_id', 'state'])
df2['datetime'] = ['2000-01-01 00:00:00', '2000-01-01 00:00:10', '2000-01-01 00:00:15', '2000-01-01 00:00:20', '2000-01-01 00:00:25', '2000-01-01 00:00:30']
df2['sample_id'] = [2, 2, 2, 2, 2, 2]
df2['state'] = ['home', 'school', 'work', 'eating', 'coffee', 'sleeping']

df3 = pd.DataFrame(columns=['datetime', 'sample_id', 'state'])
df3['datetime'] = ['2000-12-12 00:00:00', '2000-12-12 00:00:15', '2000-12-12 00:00:20', '2000-12-12 00:00:25', '2000-12-12 00:00:30', '2000-12-12 00:00:35']
df3['sample_id'] = [3, 3, 3, 3, 3, 3]
df3['state'] = ['home', 'school', 'work', 'eating', 'coffee', 'sleeping']

df = pd.concat([df1, df2, df3], axis=0)

# Normalize the time per sample id and make the starting-point the same
df_new = d3.standardize(df, sample_id='sample_id', datetime='datetime')
# # Compute delta (this is automatically done if not available)
df = d3.compute_time_delta(df, sample_id='sample_id', datetime='datetime', state='state')
# Make the moving bubbles
df = d3.movingbubbles(df, datetime='datetime', state='state', sample_id='sample_id', speed={"slow": 1000, "medium": 200, "fast": 10}, filepath='c://temp/movingbubbles.html')


# %% Create random dataset
from d3blocks import d3blocks
d3 = d3blocks(cmap='Set1')

df = d3.import_example(graph='random_time', n=10000, c=100, date_start="1-1-2000 00:10:05", date_stop="1-2-2000 23:59:59")
# df = d3.import_example(data='random_time', n=1000)

# df = d3.standardize(df, sample_id='sample_id', datetime='datetime')

# # Compute delta (this is automatically done if not available)
# df = d3.compute_time_delta(df, sample_id='sample_id', datetime='datetime', state='state')
# d3.labels

# Make the moving bubbles
d3.movingbubbles(df, datetime='datetime', state='state', sample_id='sample_id', center='Travel', speed={"slow": 1000, "medium": 200, "fast": 10}, filepath='c://temp/movingbubbles.html')


# %%
d3 = d3blocks(cmap='Set1')
# Import example
df = d3.import_example(graph='random_time', n=10000, c=100, date_start="1-1-2000 00:10:05", date_stop="1-1-2000 23:59:59")
# Normalize the time per sample id.
df = d3.standardize(df, sample_id='sample_id', datetime='datetime')
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
