from typing import List, Tuple, Optional
import threading
from collections import deque

class SocialNetwork:
    """
    Singleton class that manages the social network graph using an adjacency matrix.
    Graph[i][j] == 1 means User i follows User j
    Graph[i][j] == 0 means no connection

    This class implements the Singleton pattern to ensure only one network instance exists.
    """

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        """
        Singleton implementation using __new__
        Ensures only one instance of SocialNetwork exists
        """
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(SocialNetwork, cls).__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        """
        Initialize the social network graph
        Only runs once due to singleton pattern
        """
        if self._initialized:
            return

        # The Adjacency Matrix
        # graph[i][j] == 1 means User i follows User j
        # graph[i][j] == 0 means no connection
        self.graph: List[List[int]] = []
        self._initialized = True

    @classmethod
    def get_network(cls) -> 'SocialNetwork':
        """
        Static method to get the singleton instance

        Returns:
            The single SocialNetwork instance
        """
        return cls()

    def initialize_graph(self) -> None:
        """
        Initialize the graph from database connections
        Loads all follow relationships and builds the adjacency matrix
        """
        # Import here to avoid circular imports
        from .db_manager import return_last_user_id, get_all_follows

        max_user_id = return_last_user_id()
        connections = get_all_follows()

        size = max_user_id + 1

        # Create a new graph of size (size x size) with all elements as 0
        self.graph = [[0 for _ in range(size)] for _ in range(size)]

        # Populate the graph with connections
        for follower, followee in connections:
            if follower < size and followee < size:
                if follower != followee:  # Prevent self-loops
                    self.graph[follower][followee] = 1

        print(f"DEBUG: Graph initialized with {size} nodes and {len(connections)} connections.")

    def create_node(self, user_id: int) -> None:
        """
        Create a new node in the graph for a user
        Resizes the adjacency matrix if necessary

        Args:
            user_id: ID of the user to add
        """
        current_size = len(self.graph)

        # Only resize if the new user_id is outside our current matrix
        if user_id >= current_size:
            new_size = user_id + 1

            # Resize existing rows to new column width
            for row in self.graph:
                row.extend([0] * (new_size - len(row)))

            # Add new rows
            for _ in range(new_size - current_size):
                self.graph.append([0] * new_size)

    def remove_node(self, user_id: int) -> None:
        """
        Remove a user's connections (clears their row and column)
        Does not shrink the matrix to keep IDs consistent

        Args:
            user_id: ID of the user to remove
        """
        if user_id >= len(self.graph):
            return

        size = len(self.graph)

        # The user stops following everyone (clear row)
        for j in range(size):
            self.graph[user_id][j] = 0

        # Everyone stops following the user (clear column)
        for i in range(size):
            self.graph[i][user_id] = 0

    def add_edge(self, from_user: int, to_user: int) -> None:
        """
        Add a follow relationship: from_user follows to_user

        Args:
            from_user: ID of the user who is following
            to_user: ID of the user being followed
        """
        # Check that both users exist
        if from_user >= len(self.graph) or to_user >= len(self.graph):
            print("One or both users do not exist.")
            return

        # Prevent self-loops
        if from_user == to_user:
            return

        self.graph[from_user][to_user] = 1

    def remove_edge(self, from_user: int, to_user: int) -> None:
        """
        Remove a follow relationship: from_user unfollows to_user

        Args:
            from_user: ID of the user who is unfollowing
            to_user: ID of the user being unfollowed
        """
        if from_user >= len(self.graph) or to_user >= len(self.graph):
            return

        self.graph[from_user][to_user] = 0

    def is_edge(self, user1: int, user2: int) -> bool:
        """
        Check if user1 follows user2

        Args:
            user1: ID of the follower
            user2: ID of the followee

        Returns:
            True if user1 follows user2, False otherwise
        """
        if user1 >= len(self.graph) or user2 >= len(self.graph):
            return False

        return self.graph[user1][user2] == 1

    def return_num_of_users(self) -> int:
        """
        Get the number of users in the network

        Returns:
            The size of the graph (number of potential users)
        """
        return len(self.graph)

    def get_followers(self, user_id: int) -> List[int]:
        """
        Get all users who follow the given user

        Args:
            user_id: ID of the user

        Returns:
            List of user IDs who follow this user
        """
        if user_id >= len(self.graph):
            return []

        followers = []
        for i in range(len(self.graph)):
            if self.graph[i][user_id] == 1:
                followers.append(i)

        return followers

    def get_following(self, user_id: int) -> List[int]:
        """
        Get all users that the given user follows

        Args:
            user_id: ID of the user

        Returns:
            List of user IDs that this user follows
        """
        if user_id >= len(self.graph):
            return []

        following = []
        for j in range(len(self.graph)):
            if self.graph[user_id][j] == 1:
                following.append(j)

        return following

    def get_follower_count(self, user_id: int) -> int:
        """
        Get the number of followers for a user

        Args:
            user_id: ID of the user

        Returns:
            Number of followers
        """
        return len(self.get_followers(user_id))

    def get_following_count(self, user_id: int) -> int:
        """
        Get the number of users that this user follows

        Args:
            user_id: ID of the user

        Returns:
            Number of users being followed
        """
        return len(self.get_following(user_id))

    def get_mutual_followers(self, user1: int, user2: int) -> List[int]:
        """
        Get users who follow both user1 and user2

        Args:
            user1: First user ID
            user2: Second user ID

        Returns:
            List of user IDs who follow both users
        """
        followers1 = set(self.get_followers(user1))
        followers2 = set(self.get_followers(user2))
        return list(followers1.intersection(followers2))

    def get_mutual_following(self, user1: int, user2: int) -> List[int]:
        """
        Get users that both user1 and user2 follow

        Args:
            user1: First user ID
            user2: Second user ID

        Returns:
            List of user IDs followed by both users
        """
        following1 = set(self.get_following(user1))
        following2 = set(self.get_following(user2))
        return list(following1.intersection(following2))

    def are_mutual_followers(self, user1: int, user2: int) -> bool:
        """
        Check if two users follow each other

        Args:
            user1: First user ID
            user2: Second user ID

        Returns:
            True if both users follow each other, False otherwise
        """
        return self.is_edge(user1, user2) and self.is_edge(user2, user1)

    def get_graph(self) -> List[List[int]]:
        """
        Get the entire adjacency matrix

        Returns:
            The adjacency matrix as a 2D list
        """
        return self.graph

    def print_graph(self) -> None:
        """Print the adjacency matrix (useful for debugging)"""
        if not self.graph:
            print("Graph is empty")
            return

        print("Social Network Graph (Adjacency Matrix):")
        print("Rows = Followers, Columns = Following")
        print()

        # Print column headers
        print("   ", end="")
        for j in range(len(self.graph)):
            print(f"{j:3}", end="")
        print()

        # Print rows with row headers
        for i in range(len(self.graph)):
            print(f"{i:3}", end="")
            for j in range(len(self.graph[i])):
                print(f"{self.graph[i][j]:3}", end="")
            print()

    def clear_graph(self) -> None:
        """Clear the entire graph"""
        self.graph = []

    def __str__(self) -> str:
        """String representation of the social network"""
        return f"SocialNetwork(users={len(self.graph)}, connections={self._count_connections()})"

    def _count_connections(self) -> int:
        """Count the total number of connections in the graph"""
        count = 0
        for row in self.graph:
            count += sum(row)
        return count

    def __repr__(self) -> str:
        """Developer-friendly representation"""
        return f"SocialNetwork(users={len(self.graph)}, connections={self._count_connections()})"

# ---------------- ALGORITHMS ----------------

    def get_degree_of_separation(self, start_user: int, target_user: int) -> int:
        """
        BFS to find the shortest path distance between two users.
        Returns: -1 if no connection, 0 if same user, >0 for path length.
        """
        size = len(self.graph)
        if start_user >= size or target_user >= size:
            return -1
        if start_user == target_user:
            return 0

        visited = [False] * size
        distance = [-1] * size
        queue = deque()

        visited[start_user] = True
        distance[start_user] = 0
        queue.append(start_user)

        while queue:
            current = queue.popleft()

            if current == target_user:
                return distance[current]

            for neighbor in range(size):
                if self.graph[neighbor][current] == 1 and not visited[neighbor]:
                    visited[neighbor] = True
                    distance[neighbor] = distance[current] + 1
                    queue.append(neighbor)

        return -1

    def get_shortest_path(self, start_user: int, target_user: int) -> List[int]:
        """
        Returns the list of user_ids representing the shortest path.
        Example: [0, 4, 7] means 0 follows 4, and 4 follows 7.
        Returns empty list [] if no path exists.
        """
        size = len(self.graph)
        if start_user >= size or target_user >= size:
            return []
        if start_user == target_user:
            return [start_user]

        visited = [False] * size
        # parent[i] stores the node that discovered node i
        parent = [-1] * size
        queue = deque()

        visited[start_user] = True
        queue.append(start_user)

        found = False
        while queue:
            current = queue.popleft()
            if current == target_user:
                found = True
                break

            for neighbor in range(size):
                # Standard Outbound BFS: Does 'current' follow 'neighbor'?
                if self.graph[current][neighbor] == 1 and not visited[neighbor]:
                    visited[neighbor] = True
                    parent[neighbor] = current
                    queue.append(neighbor)

        if found:
            # Reconstruct path by backtracking from target to start
            path = []
            curr = target_user
            while curr != -1:
                path.append(curr)
                curr = parent[curr]
            return path[::-1]  # Reverse to get Start -> End

        return []

    def calculate_centrality(self, user_id: int) -> float:
        """
        Calculates Closeness Centrality (0.0 to 1.0).
        Higher score = More influential (closer to everyone else).
        """
        size = len(self.graph)
        if user_id >= size:
            return 0.0

        total_distance = 0
        reachable_nodes = 0

        for i in range(size):
            if i == user_id: continue

            dist = self.get_degree_of_separation(user_id, i)
            if dist > 0:
                total_distance += dist
                reachable_nodes += 1

        if total_distance == 0:
            return 0.0

        # Formula: Reachable / Sum_of_Distances
        # (Users who can reach many people quickly get a higher score)
        return reachable_nodes / total_distance

    def calculate_pagerank(self):
        """
        Calculates PageRank (Influence Score) for all users.
        Returns a dictionary: {user_id: score (0.0 to 1.0)}
        """
        N = len(self.graph)
        if N == 0: return {}

        # 1. Configuration
        d = 0.85  # Damping factor (Standard value: 85% chance to follow a link)
        iterations = 20  # 20 iterations is enough for convergence on social graphs

        # 2. Initialize everyone with equal importance
        scores = [1.0 / N] * N

        # 3. Run the "Voting" Process
        for _ in range(iterations):
            new_scores = [0.0] * N

            # Base score everyone gets (The "Teleport" probability)
            base_score = (1 - d) / N
            for i in range(N):
                new_scores[i] = base_score

            # Distribute influence
            for i in range(N):  # i is the Source Node
                out_degree = sum(self.graph[i])

                if out_degree == 0:
                    # "Sink Node" problem: If someone follows nobody,
                    # they distribute their score equally to everyone (to prevent score loss)
                    split_score = (d * scores[i]) / N
                    for j in range(N):
                        new_scores[j] += split_score
                else:
                    # Normal Case: Distribute score to people they follow
                    share = (d * scores[i]) / out_degree
                    for j in range(N):
                        if self.graph[i][j] == 1:
                            new_scores[j] += share

            scores = new_scores

        # 4. Normalize (Scale so the highest influencer is 1.0)
        max_score = max(scores) if scores else 1.0
        if max_score == 0: max_score = 1.0

        result = {}
        for i in range(N):
            # Scale result to 0-1 range for our UI
            result[i] = scores[i] / max_score

        return result

    def calculate_influence(self):
        """
        Calculates Influence based purely on Follower Count relative to the top user.
        Returns: {user_id: score (0.0 to 1.0)}
        """
        N = len(self.graph)
        if N == 0: return {}

        # 1. Count followers for everyone
        follower_counts = {}
        for i in range(N):
            # Sum the column 'i' (incoming edges)
            count = 0
            for j in range(N):
                if self.graph[j][i] == 1:
                    count += 1
            follower_counts[i] = count

        # 2. Find the "King" (Max followers)
        max_followers = max(follower_counts.values())

        # Avoid division by zero if nobody follows anyone yet
        if max_followers == 0:
            return {i: 0.0 for i in range(N)}

        # 3. Normalize: Top person gets 1.0, others are relative to them
        scores = {}
        for i in range(N):
            scores[i] = follower_counts[i] / max_followers

        return scores

    def get_recommendations(self, user_id: int, threshold: float = 0.0) -> List[Tuple[int, float]]:
        """
        Hybrid Recommendation System
        Combines:
        1. Graph Structure (Jaccard Similarity) - 60% weight
        2. User Profile (Cosine Similarity) - 40% weight
        """
        # Import here to avoid circular dependency
        from .db_manager import return_user_by_id

        size = len(self.graph)
        if user_id >= size: return []

        # 1. Fetch Current User Data
        user_data = return_user_by_id(user_id)
        if not user_data: return []

        my_interests = set(user_data.get('interests', []))
        my_following = set(self.get_following(user_id))

        recommendations = []

        for candidate_id in range(size):
            # Skip yourself and people you already follow
            if candidate_id == user_id: continue
            if candidate_id in my_following: continue

            # --- Metric 1: Jaccard (Graph) ---
            # We call the helper function now!
            jaccard_score = self._jaccard_similarity(user_id, candidate_id)

            # --- Metric 2: Cosine (Interests) ---
            cand_data = return_user_by_id(candidate_id)
            if not cand_data: continue

            cand_interests = set(cand_data.get('interests', []))
            cosine_score = self._cosine_similarity(my_interests, cand_interests)

            # --- Final Weighted Score ---
            final_score = (0.6 * jaccard_score) + (0.4 * cosine_score)

            if final_score > threshold:
                recommendations.append((candidate_id, final_score))

        # Sort by highest score first
        recommendations.sort(key=lambda x: x[1], reverse=True)

        return recommendations

    # ---------------- HELPER METRICS ----------------

    def intersection(set1: List[str], set2: List[str]) -> int:
        """
        Count the intersection of two lists
        """
        count = 0
        for item1 in set1:
            for item2 in set2:
                if item1 == item2:
                    count += 1
        return count

    def _jaccard_similarity(self, user1_id: int, user2_id: int) -> float:
        """
        Calculates Jaccard Similarity based on shared connections.
        Formula: (Intersection) / (Union)
        """
        # Get following lists directly from the graph (Fast)
        following1 = set(self.get_following(user1_id))
        following2 = set(self.get_following(user2_id))

        if not following1 or not following2:
            return 0.0

        intersection = len(following1.intersection(following2))
        union = len(following1.union(following2))

        if union == 0:
            return 0.0

        return intersection / union

    def _cosine_similarity(self, interests1: set, interests2: set) -> float:
        """
        Calculates Cosine Similarity based on shared interests.
        Formula: (A . B) / (||A|| * ||B||)
        """
        if not interests1 or not interests2:
            return 0.0

        intersection = len(interests1.intersection(interests2))

        # Magnitude (Square root of size)
        magnitude1 = len(interests1) ** 0.5
        magnitude2 = len(interests2) ** 0.5

        denominator = magnitude1 * magnitude2

        if denominator == 0:
            return 0.0

        return intersection / denominator

# Convenience function to get the singleton instance
def get_social_network() -> SocialNetwork:
    """
    Get the singleton instance of the social network

    Returns:
        The SocialNetwork singleton instance
    """
    return SocialNetwork.get_network()