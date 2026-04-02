import numpy as np
from sklearn.ensemble import IsolationForest

X = np.random.randn(100, 5)
clf = IsolationForest(random_state=42)
clf.fit(X)

print(len(clf.estimators_))

# How to get per tree score?
# The path length can be obtained from _compute_chunked_score_samples if we pass estimators
# But let's see if we can just do:
# scores = np.zeros((X.shape[0], len(clf.estimators_)))
# for i, (tree, features) in enumerate(zip(clf.estimators_, clf.estimators_features_)):
#     # tree is an ExtraTreeRegressor
#     # but predict doesn't give path length.
#     pass

# Actually, _compute_score_samples is available?
try:
    scores = clf.score_samples(X)
    print("score_samples shape:", scores.shape)
except Exception as e:
    print("Error:", e)
