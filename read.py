import pandas as pd
pd.core.common.is_list_like = pd.api.types.is_list_like

import pandas_datareader.data as web

from datetime import datetime

start = datetime(2015, 2, 9)

end = datetime(2017, 5, 24)

f = web.DataReader('GDP', 'fred', start, end)

f.head()

import quandl