# %%
# import d3blocks
# print(dir(d3blocks))
# print(d3blocks.__version__)

# %%
from d3blocks import d3blocks
d3 = d3blocks()
X = d3.import_example(data='movingbubbles')
d3.movingbubbles(X, filepath='c://temp/movingbubbles.html', center='Sleeping')

# %% Create random dataset

from d3blocks import d3blocks

X = d3.import_example(data='random_time')

# from sklearn.datasets import load_breast_cancer 
# cancer = load_breast_cancer()
# data = np.c_[cancer.data, cancer.target]
# columns = np.append(cancer.feature_names, ["target"])
# df = pd.DataFrame(data, columns=columns)

X = d3.import_example(data='random_time')

df['datetime'] = None
df['id'] = None
df['event'] = None

n = 100
df = pd.DataFrame(columns=['datetime', 'id', 'event'], data=np.array([[None, None, None]]*n))
location_types = ['Home', 'Hospital', 'Bed', 'Sport', 'Sleeping', 'Sick', 'Leasure']
for i in range(0, df.shape[0]):
    df['datetime'].iloc[i] = random_date("1-1-2000 00:00:00", "1-1-2010 23:59:59", random.random())
    df['id'].iloc[i] = random.randint(0, 10)
    df['event'].iloc[i] = location_types[random.randint(0, len(location_types)-1)]
df['datetime'] = pd.to_datetime(df['datetime'])
df = df.sort_values(by="datetime")
df.reset_index(inplace=True, drop=True)

# %%
import random
import time
    
def str_time_prop(start, end, time_format, prop):
    """Get a time at a proportion of a range of two formatted times.

    start and end should be strings specifying times formatted in the
    given format (strftime-style), giving an interval [start, end].
    prop specifies how a proportion of the interval to be taken after
    start.  The returned time will be in the specified format.
    """

    stime = time.mktime(time.strptime(start, time_format))
    etime = time.mktime(time.strptime(end, time_format))

    ptime = stime + prop * (etime - stime)

    return time.strftime(time_format, time.localtime(ptime))


def random_date(start, end, prop):
    return str_time_prop(start, end, '%d-%m-%Y %H:%M:%S', prop)

print(random_date("1-1-2000 00:00:00", "1-1-2010 23:59:59", random.random()))


# %%
import numpy as np
s1 = np.c_[[0, 1, 2, 3, 4, 5], [10, 10, 10, 10, 10, 10]]
s2 = np.c_[[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10], [5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5]]


X = ['0,10,1,10,2,10,3,10,4,10,5,10,6,10,7,10,8,10,9,10,10,10', '0,20,1,20,2,20,3,20,4,20,5,20']
d3.movingbubbles(X, filepath='c://temp/movingbubbles.html')

# %%
import pandas as pd
X[0:10]

	{"index": "0", "short": "Sleeping", "desc": "Sleeping"},
	{"index": "1", "short": "Personal Care", "desc": "Personal Care"},
	{"index": "2", "short": "Eating & Drinking", "desc": "Eating and Drinking"},
	{"index": "3", "short": "Education", "desc": "Education"},
	{"index": "4", "short": "Work", "desc": "Work and Work-Related Activities"},
	{"index": "5", "short": "Housework", "desc": "Household Activities"},

df = pd.DataFrame(columns=['Sleeping', 'Personal Care', 'Eating & Drinking', 'Work', 'Housework'], data)

0,270
5,32
5,165
2,35
4,300
1,53
0,370

# %%
