from typing import List, Optional, Tuple, Dict
from datetime import datetime
from .POST import POST
from .social_network import get_social_network
from . import db_manager


class USER:
    """
    USER class representing a user in the social network
    Handles user information, posts, and social interactions
    """

    def __init__(self, user_id: int = 0, username: str = "", full_name: str = "",
                 password: str = "", email: str = "", birthdate: str = "",
                 address: str = "", interests: List[str] = None):
        self.id = user_id
        self.user_name = username
        self.full_name = full_name
        self.password = password
        self.email = email
        self.birth_date = birthdate
        self.address = address
        self.interests = interests if interests is not None else []
        self.followers_count = 0
        self.following_count = 0
        self.pp_path = ""

    # ===== Static / Class Methods for Data Retrieval =====

    @classmethod
    def get_by_id(cls, user_id: int) -> Optional['USER']:
        """Fetch a user object by ID from the database"""
        data = db_manager.return_user_by_id(user_id)
        if data:
            user = cls(
                user_id=data['user_id'],
                username=data['username'],
                full_name=data['full_name'],
                password=data['password'],
                email=data['email'],
                birthdate=data['birthdate'],
                address=data.get('address', ''),
                interests=data.get('interests', [])
            )
            user.set_follower_count(data.get('follower_count', 0))
            user.set_following_count(data.get('following_count', 0))
            user.pp_path = data.get('pp_path', "")
            return user
        return None

    @classmethod
    def get_by_username(cls, username: str) -> Optional['USER']:
        """Fetch a user object by username from the database"""
        data = db_manager.return_user_by_username(username)
        if data:
            user = cls(
                user_id=data['user_id'],
                username=data['username'],
                full_name=data['full_name'],
                password=data['password'],
                email=data['email'],
                birthdate=data['birthdate'],
                address=data.get('address', ''),
                interests=data.get('interests', [])
            )
            user.set_follower_count(data.get('follower_count', 0))
            user.set_following_count(data.get('following_count', 0))
            user.pp_path = data.get('pp_path', "")
            return user
        return None

    @classmethod
    def get_user_followers_count(cls, user_id: int) -> int:
        """Get follower count for a user ID"""
        return db_manager.get_follower_count(user_id)

    @classmethod
    def get_user_following_count(cls, user_id: int) -> int:
        """Get following count for a user ID"""
        return db_manager.get_following_count(user_id)

    @classmethod
    def get_user_followers_list(cls, user_id: int) -> List[Dict]:
        """Get followers list for a user ID"""
        return db_manager.get_followers_list_for_user(user_id)

    @classmethod
    def get_user_following_list(cls, user_id: int) -> List[str]:
        """Get following list for a user ID"""
        return db_manager.get_following_list_of_user(user_id)

    @classmethod
    def is_following(cls, follower_id: int, followed_id: int) -> bool:
        """Check if one user is following another"""
        return db_manager.is_following(follower_id, followed_id)

    @classmethod
    def add_follow_relationship(cls, follower_id: int, followed_id: int) -> bool:
        """Add a follow relationship between two users"""
        return db_manager.add_follow(follower_id, followed_id)

    @classmethod
    def remove_follow_relationship(cls, follower_id: int, followed_id: int) -> bool:
        """Remove a follow relationship between two users"""
        return db_manager.delete_follow(follower_id, followed_id)

    # ===== Setters =====
    def set_id(self, user_id: int) -> None:
        self.id = user_id

    def set_username(self, username: str) -> None:
        self.user_name = username

    def set_fullname(self, full_name: str) -> None:
        self.full_name = full_name

    def set_password(self, password: str) -> None:
        self.password = password

    def set_email(self, email: str) -> None:
        self.email = email

    def set_birthdate(self, birthdate: str) -> None:
        self.birth_date = birthdate

    def set_address(self, address: str) -> None:
        self.address = address

    def set_interests(self, interests: List[str]) -> None:
        self.interests = interests

    def set_follower_count(self, count: int) -> None:
        self.followers_count = count

    def set_following_count(self, count: int) -> None:
        self.following_count = count

    # ===== Getters =====
    def get_id(self) -> int:
        return self.id

    def get_username(self) -> str:
        return self.user_name

    def get_fullname(self) -> str:
        return self.full_name

    def get_password(self) -> str:
        return self.password

    def get_email(self) -> str:
        return self.email

    def get_birthdate(self) -> str:
        return self.birth_date

    def get_address(self) -> str:
        return self.address

    def get_interests(self) -> List[str]:
        return self.interests

    def get_followers_count(self) -> int:
        return self.followers_count

    def get_following_count(self) -> int:
        return self.following_count

    def get_followers(self) -> List[Dict]:
        """Get list of followers data"""
        return db_manager.get_followers_list_for_user(self.get_id())

    def get_following(self) -> List[str]:
        """Get list of usernames being followed"""
        return db_manager.get_following_list_of_user(self.get_id())

    def is_following_user(self, other_user_id: int) -> bool:
        """Check if this user is following another user"""
        return db_manager.is_following(self.get_id(), other_user_id)

    # ===== People Operations =====

    def follow(self, other_user_id: int) -> None:
        """Follow another user"""
        self.following_count += 1
        db_manager.add_follow(self.get_id(), other_user_id)
        # Update Singleton Graph
        get_social_network().add_edge(self.get_id(), other_user_id)

    def unfollow(self, other_user_id: int) -> None:
        """Unfollow another user"""
        self.following_count = max(0, self.following_count - 1)
        db_manager.delete_follow(self.get_id(), other_user_id)
        # Update Singleton Graph
        get_social_network().remove_edge(self.get_id(), other_user_id)

    def block_person(self, other_user_id: int) -> None:
        """Block a person (unfollows them)"""
        self.unfollow(other_user_id)

    # ===== Post Operations =====

    def create_post(self, content: str) -> Optional[int]:
        post = POST(user_id=self.get_id(), content=content)
        post.classify()  # Auto classify
        post_data = post.to_dict()
        return db_manager.add_post(post_data)

    def update_post(self, post_id: int, new_content: str) -> bool:
        return db_manager.update_post_content(post_id, self.get_id(), new_content)

    def remove_post(self, post_id: int) -> bool:
        return db_manager.delete_post(post_id, self.get_id())

    def like_post(self, post_id: int) -> bool:
        return db_manager.add_like(post_id, self.get_id())

    def unlike_post(self, post_id: int) -> bool:
        return db_manager.delete_like(post_id, self.get_id())

    def dislike_post(self, post_id: int) -> bool:
        return db_manager.add_dislike(post_id, self.get_id())

    def undislike_post(self, post_id: int) -> bool:
        return db_manager.delete_dislike(post_id, self.get_id())

    def comment_post(self, post_id: int, comment: str) -> bool:
        # For now, just increment counter as per DB schema
        return db_manager.increment_post_comment_count(post_id)

    # ===== Data Fetching Operations =====

    def get_feed_posts(self) -> List[Dict]:
        """Fetch raw posts for this user's feed"""
        return db_manager.return_following_posts(self.get_id())

    def get_my_posts(self) -> List[Dict]:
        """Fetch all posts created by this user"""
        post_ids = db_manager.prepare_all_user_posts(self.get_id())
        posts = []
        for pid in post_ids:
            p_data = db_manager.read_post(pid)
            if p_data:
                posts.append(p_data)
        return posts

    def get_activity(self, limit: int = 20) -> List[Dict]:
        """Fetch recent activity (likes/follows) relating to this user"""
        return db_manager.get_user_activity(self.get_id(), limit)

    def get_statistics(self) -> Dict:
        """Calculate and return user statistics"""
        posts = self.get_my_posts()
        total_likes = sum(p.get('like_count', 0) for p in posts)
        total_dislikes = sum(p.get('dislike_count', 0) for p in posts)
        total_comments = sum(p.get('comment_count', 0) for p in posts)

        return {
            'user_id': self.id,
            'username': self.user_name,
            'full_name': self.full_name,
            'total_posts': len(posts),
            'total_likes': total_likes,
            'total_dislikes': total_dislikes,
            'total_comments': total_comments,
            'followers': get_social_network().get_follower_count(self.id),
            'following': get_social_network().get_following_count(self.id)
        }

    def save_changes(self) -> bool:
        """Persist current user object state to the database"""
        user_data = {
            'user_id': self.id,
            'username': self.user_name,
            'full_name': self.full_name,
            'email': self.email,
            'password': self.password,
            'address': self.address,
            'interests': self.interests,
            'birthdate': self.birth_date
        }
        return db_manager.update_user(user_data)

    def recommend_friends(self) -> List[Tuple[str, float]]:
        """
        Get friend recommendations for this user.
        Delegates to the SocialNetwork singleton for the hybrid calculation.
        """
        # 1. Get raw recommendations (IDs and Scores) from the Graph logic
        # This now runs the 60% Jaccard + 40% Cosine logic we just wrote.
        recs_with_ids = get_social_network().get_recommendations(self.get_id())

        # 2. Convert IDs to Usernames for the Frontend UI
        final_list = []
        for uid, score in recs_with_ids:
            # We fetch the USER object briefly just to get the username string
            u_obj = USER.get_by_id(uid)
            if u_obj:
                final_list.append((u_obj.get_username(), score))

        return final_list


class System:
    """
    System class handling Registration, Login, and Search Indexing (Trie)
    Acts as a higher-level manager.
    """

    def __init__(self):
        self.search_trie = db_manager.TrieNode()
        db_manager.initialize_trie_tree(self.search_trie)

    def register_user(self, username, full_name, email, password, birthdate, address, interests) -> Tuple[
        bool, str, Optional[USER]]:
        """Register a new user via the GUI"""

        # 1. Check existence
        if db_manager.return_user_by_username(username):
            return (False, "Username already exists", None)

        # 2. Prepare Data
        user_data = {
            'username': username,
            'full_name': full_name,
            'email': email,
            'password': password,
            'birthdate': birthdate,
            'address': address,
            'interests': interests
        }

        # 3. Add to DB
        user_id = db_manager.add_user(user_data)

        if user_id:
            # 4. Create Object
            user = USER(user_id, username, full_name, password, email, birthdate, address, interests)

            # 5. Update Network & Trie
            get_social_network().create_node(user_id)
            db_manager.insert_trie(self.search_trie, username)

            return (True, f"Registration successful! User ID: {user_id}", user)

        return (False, "Database error during registration", None)

    def login(self, username, password) -> Tuple[bool, str, Optional[USER]]:
        """Login a user"""
        user_data = db_manager.authenticate_user(username, password)
        if user_data:
            # Create USER object
            user = USER.get_by_id(user_data['user_id'])
            return (True, f"Welcome, {username}!", user)
        return (False, "Invalid username or password", None)

    def get_username_suggestions(self, prefix: str) -> List[str]:
        """Get autocomplete suggestions from Trie"""
        return db_manager.get_suggestions(prefix, self.search_trie)

    def generate_feed(self, raw_posts: List[dict]) -> List[dict]:
        """Sort posts by score using Merge Sort"""
        # Calculate scores
        for post_dict in raw_posts:
            post = POST.from_dict(post_dict)
            post.update_score()
            post_dict['score'] = post.get_score()

        # Sort
        if len(raw_posts) > 1:
            self.merge_sort(raw_posts, 0, len(raw_posts) - 1)

        return raw_posts

    def merge_sort(self, posts: List[dict], left: int, right: int) -> None:
        if left < right:
            mid = left + (right - left) // 2
            self.merge_sort(posts, left, mid)
            self.merge_sort(posts, mid + 1, right)
            self.merge(posts, left, mid, right)

    def merge(self, posts: List[dict], left: int, mid: int, right: int) -> None:
        left_array = posts[left:mid + 1]
        right_array = posts[mid + 1:right + 1]
        i = j = 0
        k = left
        while i < len(left_array) and j < len(right_array):
            if left_array[i]['score'] >= right_array[j]['score']:  # Descending
                posts[k] = left_array[i]
                i += 1
            else:
                posts[k] = right_array[j]
                j += 1
            k += 1
        while i < len(left_array):
            posts[k] = left_array[i]
            i += 1
            k += 1
        while j < len(right_array):
            posts[k] = right_array[j]
            j += 1
            k += 1