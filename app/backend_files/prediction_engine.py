import numpy as np
from collections import Counter

## feature vector component
def euclidean_distance (x1,x2):
    return np.sqrt(np.sum( (x1-x2) ** 2 ) )



class KNN:

    def __init__(self, k=3, weighted=False):
        self.k = k
        self.weighted = weighted

    # x is our data , y is the label
    # Function to store training set

    def fit(self, X, y):  # to fit training samples
        self.X_train = X
        self.y_train = y

        if len(self.X_train) != len(self.y_train):
            raise ValueError("X and y must have the same length")

        if self.k > len(self.X_train):
            raise ValueError("k cannot be larger than number of training samples")

    def predict(self, X): # predict for new points X(test) : have multiple sample points
       predicted_labels  = [self._predict_single(x) for x in X]
       return np.array(predicted_labels)

     # -------------------- Predict one sample
    def predict_one(self, x):
         x = np.array(x, dtype=float)
         return self._predict_single(x)

# we will use this for our classifier predictor

    def _predict_single (self,x): # helper for predict one sample
        # compute distances -> using euclidean distance
        distances = [ euclidean_distance(x,x_train) for x_train in self.X_train ]
        ## sort
        k_indices = np.argsort(distances)[:self.k]

        k_nearest_labels=[self.y_train[i] for i in k_indices]

        # majority vote -> most common class label

        if self.weighted:
            # Weighted vote by 1/distance
            k_distances = [distances[i] for i in k_indices]
            votes = {}
            for label, d in zip(k_nearest_labels, k_distances):
                w = 1 / (d + 1e-5)
                votes[label] = votes.get(label, 0) + w
            majority_class = max(votes, key=votes.get)
        else:
            # Simple majority vote
            counts = Counter(k_nearest_labels)
            max_count = max(counts.values())
            candidates = [label for label, count in counts.items() if count == max_count]
            majority_class = min(candidates)  # tie-break by smallest label

        return majority_class
