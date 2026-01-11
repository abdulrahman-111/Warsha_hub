"""
SocialMedia Application Integration Class
Controller that delegates logic to USER, POST, and SocialNetwork layers.
"""
from typing import List, Optional, Dict, Tuple

# Import Domain Components (NO DIRECT DB ACCESS)
from .backend_files.USER import USER, System
from .backend_files.POST import POST
from .backend_files.social_network import get_social_network
from .backend_files.message import Msg
from .backend_files.link_predictor import LinkPredictor

class SocialMedia:
    def __init__(self):
        self.current_user: Optional[USER] = None
        self.system = System()  # Handles system-wide logic (Login, Reg, Trie)
        self.network = get_social_network()
        self.predictor = LinkPredictor()
        self._initialize()

    def _initialize(self) -> None:
        try:
            self.network.initialize_graph()
            print("Social network initialized successfully")
        except Exception as e:
            print(f"Warning: Could not initialize social network: {e}")

    # ========================================
    # USER AUTHENTICATION & MANAGEMENT
    # ========================================

    def register_user(self, username: str, full_name: str, email: str,
                      password: str, birthdate: str, address: str,
                      interests: List[str]) -> Tuple[bool, str, Optional[USER]]:
        """Register a new user via the System class"""
        return self.system.register_user(username, full_name, email, password, birthdate, address, interests)

    def login(self, username: str, password: str) -> Tuple[bool, str, Optional[USER]]:
        """Login via the System class"""
        success, msg, user = self.system.login(username, password)
        if success:
            self.current_user = user
        return (success, msg, user)

    def logout(self) -> None:
        """Logout the current user"""
        self.current_user = None

    def get_current_user(self) -> Optional[USER]:
        return self.current_user

    def is_logged_in(self) -> bool:
        return self.current_user is not None

    def get_posts_by_interest(self, interest: str):
        """Return posts that match a given interest/category"""
        if not self.current_user:
            return []

        # Fetch raw feed
        raw_posts = self.current_user.get_feed_posts()

        # Filter posts that contain this interest/category
        filtered = [p for p in raw_posts if interest.lower() in p.get("categories", "").lower()]
        return filtered

    def update_user_profile(self, user_data: Dict) -> Tuple[bool, str]:
        """Update current user profile"""
        if not self.current_user:
            return (False, "No user logged in")

        # Update in-memory object
        if 'username' in user_data: self.current_user.set_username(user_data['username'])
        if 'full_name' in user_data: self.current_user.set_fullname(user_data['full_name'])
        if 'email' in user_data: self.current_user.set_email(user_data['email'])
        if 'password' in user_data: self.current_user.set_password(user_data['password'])
        if 'address' in user_data: self.current_user.set_address(user_data['address'])
        if 'interests' in user_data: self.current_user.set_interests(user_data['interests'])

        # Persist changes
        success = self.current_user.save_changes()
        if success:
            return (True, "Profile updated successfully")
        return (False, "Failed to update profile")

    # ========================================
    # POST OPERATIONS
    # ========================================

    def create_post(self, content: str, auto_classify: bool = True) -> Tuple[bool, str, Optional[int]]:
        """Create a post using the current user object"""
        if not self.current_user:
            return (False, "No user logged in", None)

        post_id = self.current_user.create_post(content)
        if post_id:
            return (True, "Post created successfully", post_id)
        return (False, "Failed to create post", None)

    def get_post(self, post_id: int) -> Optional[Dict]:
        """Fetch post using POST static method"""
        return POST.get_by_id(post_id)

    def update_post(self, post_id: int, new_content: str) -> Tuple[bool, str]:
        if not self.current_user: return (False, "No user logged in")
        success = self.current_user.update_post(post_id, new_content)
        return (success, "Post updated" if success else "Failed")

    def delete_post(self, post_id: int) -> Tuple[bool, str]:
        if not self.current_user: return (False, "No user logged in")
        success = self.current_user.remove_post(post_id)
        return (success, "Post deleted" if success else "Failed")

    def get_user_posts(self, user_id: Optional[int] = None) -> List[Dict]:
        """Get all posts by a user"""
        # If no ID provided, use current user
        if user_id is None:
            if not self.current_user: return []
            return self.current_user.get_my_posts()

        # If ID provided, fetch that user first
        other_user = USER.get_by_id(user_id)
        if other_user:
            return other_user.get_my_posts()
        return []

    # ========================================
    # POST REACTIONS
    # ========================================

    def like_post(self, post_id: int) -> Tuple[bool, str]:
        if not self.current_user: return (False, "No user logged in")
        success = self.current_user.like_post(post_id)
        return (success, "Post liked" if success else "Failed")

    def unlike_post(self, post_id: int) -> Tuple[bool, str]:
        if not self.current_user: return (False, "No user logged in")
        success = self.current_user.unlike_post(post_id)
        return (success, "Like removed" if success else "Failed")

    def dislike_post(self, post_id: int) -> Tuple[bool, str]:
        if not self.current_user: return (False, "No user logged in")
        success = self.current_user.dislike_post(post_id)
        return (success, "Post disliked" if success else "Failed")

    def undislike_post(self, post_id: int) -> Tuple[bool, str]:
        if not self.current_user: return (False, "No user logged in")
        success = self.current_user.undislike_post(post_id)
        return (success, "Dislike removed" if success else "Failed")

    def comment_on_post(self, post_id: int, text: str) -> Tuple[bool, str]:
        if not self.current_user: return (False, "No user logged in")
        success = self.current_user.comment_post(post_id, text)
        return (success, "Comment added" if success else "Failed")

    def get_recent_post_likes(self, user_id: Optional[int] = None) -> List[Dict]:
        """Delegate to USER class"""
        target_user = self.current_user if user_id is None else USER.get_by_id(user_id)
        return target_user.get_activity() if target_user else [] # NOTE: Assuming get_activity handles this

    # ========================================
    # FEED GENERATION
    # ========================================

    def get_feed(self, page: int = 0, posts_per_page: int = 10) -> Dict:
        """
        Get paginated feed.
        Uses USER to get raw posts, and System to sort them.
        """
        if not self.current_user:
            return {'posts': [], 'total_posts': 0, 'current_page': 0}

        # 1. Fetch raw feed from the User object
        raw_posts = self.current_user.get_feed_posts()

        # 2. Sort using System algorithm (Merge Sort)
        sorted_posts = self.system.generate_feed(raw_posts)

        # 3. Pagination
        total_posts = len(sorted_posts)
        total_pages = (total_posts + posts_per_page - 1) // posts_per_page
        start_idx = page * posts_per_page
        end_idx = min(start_idx + posts_per_page, total_posts)
        page_posts = sorted_posts[start_idx:end_idx]

        # 4. Enrich posts with Author Names (requires fetching User objects)
        for post in page_posts:
            user = USER.get_by_id(post['user_id'])
            if user:
                post['author_name'] = user.get_fullname()
                post['author_username'] = user.get_username()

        return {
            'posts': page_posts,
            'total_posts': total_posts,
            'current_page': page,
            'total_pages': total_pages
        }
    # ========================================
    # SOCIAL CONNECTIONS
    # ========================================

    def follow_user(self, user_id: int) -> Tuple[bool, str]:
        if not self.current_user: return (False, "No user logged in")
        if user_id == self.current_user.get_id(): return (False, "Cannot follow yourself")

        # Check if already following
        if self.is_following(user_id):
            return (False, "Already following this user")

        self.current_user.follow(user_id)
        return (True, "User followed successfully")

    def unfollow_user(self, user_id: int) -> Tuple[bool, str]:
        if not self.current_user: return (False, "No user logged in")

        # Check if not following
        if not self.is_following(user_id):
            return (False, "Not following this user")

        self.current_user.unfollow(user_id)
        return (True, "User unfollowed successfully")

    def get_followers(self, user_id: Optional[int] = None) -> List[Dict]:
        """Get followers list - using USER class methods"""
        if user_id is None:
            if not self.current_user: return []
            return self.current_user.get_followers()

        # Use USER class method to get followers for any user
        return USER.get_user_followers_list(user_id)

    def get_following(self, user_id: Optional[int] = None) -> List[str]:
        """Get following list - using USER class methods"""
        if user_id is None:
            if not self.current_user: return []
            return self.current_user.get_following()

        # Use USER class method to get following for any user
        return USER.get_user_following_list(user_id)

    def is_following(self, user_id: int) -> bool:
        """Check if current user follows another user via Network Graph or USER class"""
        if not self.current_user: return False

        # Option 1: Use network graph (if available)
        if hasattr(self, 'network') and self.network:
            return self.network.is_edge(self.current_user.get_id(), user_id)

        # Option 2: Use USER class method
        return USER.is_following(self.current_user.get_id(), user_id)

    def get_follower_count(self, user_id: Optional[int] = None) -> int:
        """Get follower count - using USER class methods"""
        target_id = user_id if user_id is not None else (self.current_user.get_id() if self.current_user else 0)
        return USER.get_user_followers_count(target_id)

    def get_following_count(self, user_id: Optional[int] = None) -> int:
        """Get following count - using USER class methods"""
        target_id = user_id if user_id is not None else (self.current_user.get_id() if self.current_user else 0)
        return USER.get_user_following_count(target_id)

    def get_follow_relationship_info(self, user_id: int) -> Dict:
        """Get comprehensive follow relationship info between current user and another user"""
        if not self.current_user:
            return {'is_following': False, 'is_followed_by': False}

        current_id = self.current_user.get_id()
        return {
            'is_following': USER.is_following(current_id, user_id),
            'is_followed_by': USER.is_following(user_id, current_id)
        }

    # ========================================
    # SEARCH & DISCOVERY
    # ========================================

    def search_user_by_username(self, username: str) -> Optional[Dict]:
        """Search via USER static method, convert to dict for GUI"""
        user = USER.get_by_username(username)
        if user:
            return {
                'user_id': user.get_id(),
                'username': user.get_username(),
                'full_name': user.get_fullname(),
                'follower_count': user.get_followers_count(),
                'following_count': user.get_following_count(),
                'is_following': self.is_following(user.get_id()) if self.current_user else False,
                'is_followed_by': USER.is_following(user.get_id(), self.current_user.get_id()) if self.current_user else False,
                'interests': user.get_interests()
            }
        return None

    def search_user_by_id(self, user_id: int) -> Optional[Dict]:
        """Search via USER static method, convert to dict for GUI"""
        user = USER.get_by_id(user_id)
        if user:
            return {
                'user_id': user.get_id(),
                'username': user.get_username(),
                'full_name': user.get_fullname(),
                'follower_count': user.get_followers_count(),
                'following_count': user.get_following_count(),
                'is_following': self.is_following(user.get_id()) if self.current_user else False,
                'is_followed_by': USER.is_following(user.get_id(), self.current_user.get_id()) if self.current_user else False,
                'interests': user.get_interests()
            }
        return None

    def get_username_suggestions(self, prefix: str) -> List[str]:
        """Delegate to System class which holds the Trie"""
        return self.system.get_username_suggestions(prefix)

    def recommend_friends(self) -> List[Tuple[Dict, float]]:
        """Get friend recommendations via User object"""
        if not self.current_user: return []

        recommendations = self.current_user.recommend_friends()

        # Convert IDs to user dicts for the GUI
        result = []
        for uid, score in recommendations:
            u_obj = USER.get_by_id(uid)
            if u_obj:
                u_dict = {
                    'user_id': u_obj.get_id(),
                    'username': u_obj.get_username(),
                    'full_name': u_obj.get_fullname(),
                    'follower_count': USER.get_user_followers_count(uid),
                    'following_count': USER.get_user_following_count(uid),
                    'is_following': self.is_following(uid) if self.current_user else False
                }
                result.append((u_dict, score))
        return result

    def get_user_activity(self, user_id: Optional[int] = None) -> List[Dict]:
        """Get recent activity via User object"""
        target_user = self.current_user if user_id is None else USER.get_by_id(user_id)
        return target_user.get_activity() if target_user else []


    # ========================================
    # MESSAGES
    # ========================================

    def send_message(self, receiver_id: int, content: str) -> Tuple[bool, str]:
        """Send a message to another user"""
        if not self.current_user:
            return (False, "No user logged in")

         # Adjust import path
        from .backend_files import db_manager

        # Create message object
        msg = Msg()
        msg.set_sender_id(self.current_user.get_id())
        msg.set_receiver_id(receiver_id)
        msg.set_content(content)

        # Save to database
        success = db_manager.add_message(msg)

        if success:
            return (True, "Message sent")
        else:
            return (False, "Failed to send message")

    def get_chat(self, other_user_id: int) -> List[Dict]:
        """Get all messages between current user and another user"""
        if not self.current_user:
            return []

        from .backend_files import db_manager

        # Get messages from database
        messages = db_manager.get_chat(self.current_user.get_id(), other_user_id)

        # Convert Msg objects to dictionaries
        chat_list = []
        for msg in messages:
            chat_list.append({
                'msg_id': msg.msg_id,
                'sender_id': msg.sender_id,
                'receiver_id': msg.receiver_id,
                'date': msg.date,
                'content': msg.content,
                'is_sent': msg.sender_id == self.current_user.get_id()
            })

        return chat_list

    def delete_message(self, msg_id: int) -> Tuple[bool, str]:
        """Delete a message"""
        from .backend_files import db_manager

        msg = Msg()
        msg.set_msg_id(msg_id)

        success = db_manager.delete_message(msg)

        if success:
            return (True, "Message deleted")
        else:
            return (False, "Failed to delete message")

    def get_user_conversations(self) -> List[Dict]:
        """Get list of users who have conversations with current user"""
        if not self.current_user:
            return []

        from .backend_files import db_manager

        conn = db_manager.get_connection()
        if not conn:
            return []

        try:
            cursor = conn.cursor()
            # Get unique users who have chatted with current user
            sql = """
                SELECT DISTINCT 
                    CASE 
                        WHEN sender_id = ? THEN receiver_id 
                        ELSE sender_id 
                    END as other_user_id,
                    MAX(date_text) as last_date
                FROM messages 
                WHERE sender_id = ? OR receiver_id = ?
                GROUP BY other_user_id
                ORDER BY last_date DESC
            """

            user_id = self.current_user.get_id()
            cursor.execute(sql, (user_id, user_id, user_id))
            rows = cursor.fetchall()

            conversations = []
            for row in rows:
                other_user_id = row[0]
                last_date = row[2]

                # Get user data
                user_data = db_manager.return_user_by_id(other_user_id)
                if user_data:
                    conversations.append({
                        'user_data': user_data,
                        'last_date': last_date
                    })

            return conversations

        except Exception as e:
            print(f"Error getting conversations: {e}")
            return []
        finally:
            conn.close()


    # ========================================
    # STATISTICS
    # ========================================

    def get_user_statistics(self, user_id: Optional[int] = None) -> Dict:
        target_user = self.current_user if user_id is None else USER.get_by_id(user_id)
        return target_user.get_statistics() if target_user else {}

    def get_network_statistics(self) -> Dict:
        return {
            'total_users': self.network.return_num_of_users(),
            # Ideally this call should go through a specialized class, but network graph access is okay here
            'total_connections': self.network._count_connections()
        }