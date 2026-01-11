import numpy as np
import random
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from app.backend_files import social_network, db_manager
from .prediction_engine import KNN
from sklearn.model_selection import train_test_split


class LinkPredictor:
    def __init__(self):
        self.knn = KNN(k=5)
        self.network = social_network.get_social_network()
        self.is_trained = False

        # New: Store scaling factors so prediction matches training
        self.scaler_mean = None
        self.scaler_std = None

        self.train_model()

    def prepare_data(self):
        size = self.network.return_num_of_users()

        positive_samples = []
        negative_samples = []

        print(f"DEBUG: Preparing AI Data for {size} users...")

        # Your loop logic (1 to size)
        for i in range(1, size):
            for j in range(1, size):
                if i == j: continue

                user1 = db_manager.return_user_by_id(i)
                user2 = db_manager.return_user_by_id(j)

                if not user1 or not user2:
                    continue

                my_interests_1 = set(user1.get('interests', []))
                my_interests_2 = set(user2.get('interests', []))

                jaccard = self.network._jaccard_similarity(i, j)
                cos = self.network._cosine_similarity(my_interests_1, my_interests_2)
                mutual = db_manager.get_mutual_friends_count(i, j)

                # Safety check for list vs int return type
                if isinstance(mutual, list): mutual = len(mutual)

                features = [jaccard, cos, mutual]

                # Check if they are already connected
                if self.network.is_edge(i, j):
                    positive_samples.append(features)
                else:
                    negative_samples.append(features)

        # --- FIX 1: Balance the Data ---
        # If we feed 1000 negatives and 2 positives, the AI will ignore the positives.
        if not positive_samples:
            print("DEBUG: No 'Follows' found in DB. AI cannot learn.")
            return [], []

        # We keep all positives, and take a limited sample of negatives (e.g., 2x positives)
        target_neg_count = min(len(negative_samples), len(positive_samples) * 2)

        if negative_samples:
            balanced_negatives = random.sample(negative_samples, target_neg_count)
        else:
            balanced_negatives = []

        # Combine them
        X = positive_samples + balanced_negatives
        y = [1] * len(positive_samples) + [0] * len(balanced_negatives)

        print(f"DEBUG: Training Data -> {len(positive_samples)} Links vs {len(balanced_negatives)} Non-Links")

        return np.array(X, dtype=float), np.array(y)

    def train_model(self):
        try:
            X, y = self.prepare_data()

            if len(X) > 0:
                # --- FIX 2: Calculate and STORE scaling factors ---
                # We do this manually so we can save 'mean' and 'std' for later use
                self.scaler_mean = X.mean(axis=0)
                self.scaler_std = X.std(axis=0)

                # Handle standard deviation of 0 (to avoid division by zero)
                self.scaler_std[self.scaler_std == 0] = 1.0

                # Apply scaling
                X_scaled = (X - self.scaler_mean) / self.scaler_std

                X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)
                self.knn.fit(X_train, y_train)

                self.is_trained = True
                print(f"DEBUG: KNN trained on {len(X)} samples.")
            else:
                self.is_trained = False
                print("DEBUG: AI Training Skipped (Not enough data).")
        except Exception as e:
            print(f"Error training model: {e}")
            self.is_trained = False

    def predict_follow(self, user1_id: int, user2_id: int):
        if not self.is_trained: return 0, [0, 0, 0]

        user1 = db_manager.return_user_by_id(user1_id)
        user2 = db_manager.return_user_by_id(user2_id)

        if not user1 or not user2: return 0, [0, 0, 0]

        my_interests_1 = set(user1.get('interests', []))
        my_interests_2 = set(user2.get('interests', []))

        jaccard_temp = self.network._jaccard_similarity(user1_id, user2_id)
        cos_temp = self.network._cosine_similarity(my_interests_1, my_interests_2)
        mutual = db_manager.get_mutual_friends_count(user1_id, user2_id)
        if isinstance(mutual, list): mutual = len(mutual)

        raw_features = [jaccard_temp, cos_temp, mutual]

        # --- FIX 3: Scale using the STORED factors ---
        # We must use the same mean/std from training, not recalculate from X_train
        x_input = np.array(raw_features, dtype=float)
        x_scaled = (x_input - self.scaler_mean) / self.scaler_std

        return self.knn.predict_one(x_scaled), raw_features

    def visualize_prediction_3d(self, user1_id, user2_id):
        if not self.is_trained: return

        # Get prediction and features
        prediction, raw_features = self.predict_follow(user1_id, user2_id)

        # Scale features for plotting (so they align with the training cloud)
        x_arr = np.array(raw_features, dtype=float)
        scaled_features = (x_arr - self.scaler_mean) / self.scaler_std

        X_train = np.array(self.knn.X_train)
        y_train = np.array(self.knn.y_train)

        fig = plt.figure(figsize=(10, 7))
        ax = fig.add_subplot(111, projection='3d')

        friends = X_train[y_train == 1]
        strangers = X_train[y_train == 0]

        # Plot existing data
        if len(friends) > 0:
            ax.scatter(friends[:, 0], friends[:, 1], friends[:, 2], c='green', label='Existing Friends', alpha=0.6)
        if len(strangers) > 0:
            ax.scatter(strangers[:, 0], strangers[:, 1], strangers[:, 2], c='red', label='Not Friends', alpha=0.3)

        # Plot selected pair (Use the SCALED features)
        color = 'blue' if prediction == 1 else 'gray'
        ax.scatter(scaled_features[0], scaled_features[1], scaled_features[2], c=color, s=300, marker='*',
                   label='Your Selection')

        ax.set_xlabel('Jaccard (Scaled)')
        ax.set_ylabel('Cosine (Scaled)')
        ax.set_zlabel('Mutual Friends (Scaled)')
        ax.set_title(f"AI Prediction: {'MATCH' if prediction == 1 else 'NO MATCH'}")
        ax.legend()
        plt.show()

    def get_ai_recommendations(self, user_id):
        # Helper function for "Suggest Friends" feature if needed
        if not self.is_trained: return []
        recommendations = []
        size = self.network.return_num_of_users()
        existing_graph = self.network.get_graph()

        for other_id in range(1, size):
            if user_id == other_id: continue
            if existing_graph[user_id][other_id] == 1: continue

            prediction, _ = self.predict_follow(user_id, other_id)
            if prediction == 1:
                recommendations.append(other_id)
        return recommendations