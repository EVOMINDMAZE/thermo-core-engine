import numpy as np
from sklearn.ensemble import IsolationForest

X = np.random.randn(10, 5)
clf = IsolationForest(random_state=42)
clf.fit(X)

print(dir(clf))

# Let's see if we can get per-tree path length
# The path length is calculated using tree.decision_path?
# Actually, sklearn.ensemble._iforest has a function _average_path_length
# and the tree predict methods might return the depth?

def get_tree_scores(clf, X):
    n_samples = X.shape[0]
    n_trees = len(clf.estimators_)
    depths = np.zeros((n_samples, n_trees))

    # Actually, IsolationForest relies on _compute_chunked_score_samples
    # wait, the simplest way to get "bootstrapping on the Isolation Forest decision function"
    # is to manually sample the estimators, compute the score for each subset of estimators

    # Number of bootstrap iterations
    n_bootstraps = 50
    scores_boot = np.zeros((n_samples, n_bootstraps))

    for i in range(n_bootstraps):
        # sample indices of estimators with replacement
        indices = np.random.choice(n_trees, n_trees, replace=True)
        # Create a temporary IF object or just compute score manually?
        # A simpler way is to just compute the score with the selected estimators

        # clf.score_samples uses all estimators.
        pass

# Let's try creating a dummy IF and set estimators
try:
    boot_clf = IsolationForest()
    # we need to set estimators_, estimators_features_, etc.
    # maybe it's easier to just call _compute_score_samples if it takes estimators as arg?
except Exception as e:
    print(e)
