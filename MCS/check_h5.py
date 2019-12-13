import pandas as pd
data = pd.HDFStore('./mcs_european_2019_12_08_03_32_20.h5', 'r')['results']
print(data.head())