import numpy as np
import pandas as pd

np.random.seed(42)
normal_data = np.random.normal(loc=0, scale=1, size=(100, 2))
anomalous_data = np.random.normal(loc=10, scale=1, size=(10, 2))
data = np.vstack([normal_data, anomalous_data])
df = pd.DataFrame(data, columns=['feature1', 'feature2'])

print("Kurtosis:", df.kurtosis().mean())
print("Variance:", df.var().mean())

from sklearn.ensemble import IsolationForest


def calc_contam(df):
    kurt = df.kurtosis().mean()
    # Simple rule: if kurtosis > 0, we have heavy tails.
    # Let's say contamination = 0.05 + 0.01 * kurt
    contam = min(0.5, max(0.01, 0.05 + 0.01 * kurt))
    return contam

contam = calc_contam(df)
print("Contamination:", contam)

model = IsolationForest(contamination=contam, random_state=42)
preds = model.fit_predict(df)
print("Anomalies:", (preds == -1).sum())

