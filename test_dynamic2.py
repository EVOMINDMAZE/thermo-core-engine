import numpy as np
import pandas as pd

df = pd.DataFrame({"A": [1, 2, np.nan], "B": [1, 1, 1]})
print(df.kurtosis().mean())
