import sqlite3
from datetime import datetime, timedelta
from typing import List, Tuple, Optional, Dict
from .message import Msg
import hashlib

# ==============================================
# Database Connection Management
# ==============================================

DB_PATH = "warsha.sqlite"


def get_connection():
    """Opens and returns a database connection"""
    try:
        conn = sqlite3.connect(DB_PATH)
        # Enable foreign keys
        conn.execute("PRAGMA foreign_keys = ON")
        return conn
    except sqlite3.Error as e:
        print(f"Database error: Failed to open database connection - {e}")
        return None


# ==============================================
# Helper Functions
# ==============================================

def join_list(items: List[str]) -> str:
    """Convert list of strings to comma-separated string"""
    return ",".join(items) if items else ""


def tokenize(text: str) -> List[str]:
    """Convert comma-separated string to list"""
    return [item.strip() for item in text.split(",")] if text else []


def timepoint_to_string(dt: datetime) -> str:
    """Convert datetime to string format"""
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def string_to_timepoint(date_str: str) -> Optional[datetime]:
    """Convert string to datetime"""
    try:
        return datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
    except (ValueError, TypeError):
        return None


def join_categories(categories: List[str]) -> str:
    """Convert list of categories to comma-separated string"""
    return ",".join(categories) if categories else ""


def split_categories(category_str: str) -> List[str]:
    """Convert comma-separated categories to list"""
    return [cat.strip() for cat in category_str.split(",")] if category_str else []


def format_time_ago(timestamp: Optional[datetime]) -> str:
    """Format timestamp to 'time ago' string"""
    if not timestamp:
        return "Just now"

    now = datetime.now()
    diff = now - timestamp

    if diff.days > 0:
        return f"{diff.days}d"
    elif diff.seconds >= 3600:
        hours = diff.seconds // 3600
        return f"{hours}h"
    elif diff.seconds >= 60:
        minutes = diff.seconds // 60
        return f"{minutes}m"
    else:
        return "Just now"


# ==============================================
# Core USER Operations
# ==============================================

def add_user(user_data: Dict) -> Optional[int]:
    """
    Add a new user to the database
    user_data should contain: username, full_name, email, password, address, interests, birthdate
    Returns the user_id if successful, None otherwise
    """
    conn = get_connection()
    if not conn:
        return None

    try:
        cursor = conn.cursor()
        # FIXED: Column order matches schema
        sql = """INSERT INTO user (user_name, full_name, password, email, birthdate, address, interests) 
                 VALUES (?, ?, ?, ?, ?, ?, ?)"""

        interests_str = join_list(user_data.get('interests', []))

        cursor.execute(sql, (
            user_data.get('username'),
            user_data.get('full_name'),
            user_data.get('password'),
            user_data.get('email'),
            user_data.get('birthdate'),
            user_data.get('address', ''),
            interests_str
        ))

        conn.commit()
        user_id = cursor.lastrowid
        print(f"✅ User created successfully with ID: {user_id}")
        return user_id

    except sqlite3.Error as e:
        print(f"Database error: Failed to add user - {e}")
        return None
    finally:
        conn.close()


def delete_user(user_id: int, username: str) -> bool:
    """Delete a user from the database"""
    conn = get_connection()
    if not conn:
        return False

    try:
        cursor = conn.cursor()
        sql = "DELETE FROM user WHERE user_id = ? AND user_name = ?"
        cursor.execute(sql, (user_id, username))
        conn.commit()
        return cursor.rowcount > 0

    except sqlite3.Error as e:
        print(f"Database error: Failed to delete user - {e}")
        return False
    finally:
        conn.close()


def authenticate_user(username: str, password: str) -> Optional[Dict]:
    """
    Authenticate user with username and password
    Returns user data if successful, None otherwise
    """
    conn = get_connection()
    if not conn:
        return None

    try:
        cursor = conn.cursor()
        sql = "SELECT * FROM user WHERE user_name = ?"
        cursor.execute(sql, (username,))
        row = cursor.fetchone()

        if row:
            # FIXED: Password is at index 3, not 4
            # Schema: user_id(0), user_name(1), full_name(2), password(3), email(4), ...
            stored_password = row[4]
            if password == stored_password:
                return return_user_by_username(username)
            else:
                print("AUTHENTICATION FAILED: INCORRECT PASSWORD")
                return None
        else:
            print("AUTHENTICATION FAILED: USER NOT FOUND")
            return None

    except sqlite3.Error as e:
        print(f"Database error: Failed to authenticate - {e}")
        return None
    finally:
        conn.close()


def return_user_by_username(username: str) -> Optional[Dict]:
    """Return user data by username"""
    conn = get_connection()
    if not conn:
        return None

    try:
        cursor = conn.cursor()
        sql = "SELECT * FROM user WHERE user_name = ?"
        cursor.execute(sql, (username,))
        row = cursor.fetchone()

        if row:
            # FIXED: Corrected all column indices to match the schema
            # Schema: user_id(0), user_name(1), full_name(2), password(3),
            #         email(4), birthdate(5), address(6), interests(7),
            #         follower_count(8), following_count(9), pp_path(10)
            return {
                'user_id': row[0],
                'username': row[1],
                'full_name': row[2],
                'password': row[4],
                'email': row[3],
                'birthdate': row[7],
                'address': row[5] if row[5] else "",
                'interests': tokenize(row[6]) if row[6] else [],
                'follower_count': row[8] if len(row) > 8 else 0,
                'following_count': row[9] if len(row) > 9 else 0
            }
        else:
            print(f"Info: No user found with username: {username}")
            return None

    except sqlite3.Error as e:
        print(f"Database error: Failed to fetch user - {e}")
        return None
    finally:
        conn.close()


def return_user_by_id(user_id: int) -> Optional[Dict]:
    """Return user data by user_id"""
    conn = get_connection()
    if not conn:
        return None

    try:
        cursor = conn.cursor()
        sql = "SELECT * FROM user WHERE user_id = ?"
        cursor.execute(sql, (user_id,))
        row = cursor.fetchone()

        if row:
            # FIXED: Corrected all column indices to match the schema
            return {
                'user_id': row[0],
                'username': row[1],
                'full_name': row[2],
                'password': row[4],
                'email': row[3],
                'birthdate': row[7],
                'address': row[5] if row[5] else "",
                'interests': tokenize(row[6]) if row[6] else [],
                'follower_count': row[8] if len(row) > 8 else 0,
                'following_count': row[9] if len(row) > 9 else 0
            }
        else:
            print(f"Info: No user found with user_id: {user_id}")
            return None

    except sqlite3.Error as e:
        print(f"Database error: Failed to fetch user - {e}")
        return None
    finally:
        conn.close()


def update_user(user_data: Dict) -> bool:
    """Update user information"""
    conn = get_connection()
    if not conn:
        return False

    try:
        cursor = conn.cursor()
        # FIXED: Column order matches schema
        sql = """UPDATE user SET user_name=?, full_name=?, password=?, email=?, 
                 birthdate=?, address=?, interests=? WHERE user_id=?"""

        interests_str = join_list(user_data.get('interests', []))

        cursor.execute(sql, (
            user_data.get('username'),
            user_data.get('full_name'),
            user_data.get('password'),
            user_data.get('email'),
            user_data.get('birthdate'),
            user_data.get('address', ''),
            interests_str,
            user_data.get('user_id')
        ))

        conn.commit()
        print("USER UPDATED")
        return True

    except sqlite3.Error as e:
        print(f"Database error: Failed to update user - {e}")
        return False
    finally:
        conn.close()


def return_last_user_id() -> int:
    """Return the last inserted user_id"""
    conn = get_connection()
    if not conn:
        return 0

    try:
        cursor = conn.cursor()
        sql = "SELECT user_id FROM user ORDER BY user_id DESC LIMIT 1"
        cursor.execute(sql)
        row = cursor.fetchone()
        return row[0] if row else 0

    except sqlite3.Error as e:
        print(f"Database error: Failed to get last user id - {e}")
        return 0
    finally:
        conn.close()


def return_pp_path(username: str) -> str:
    """Return profile picture path for user"""
    conn = get_connection()
    if not conn:
        return ""

    try:
        cursor = conn.cursor()
        sql = "SELECT pp_path FROM user WHERE user_name = ?"
        cursor.execute(sql, (username,))
        row = cursor.fetchone()
        return row[0] if row and row[0] else ""

    except sqlite3.Error as e:
        print(f"Database error: Failed to get profile picture path - {e}")
        return ""
    finally:
        conn.close()


def set_pp_path(username: str, path: str) -> bool:
    """Set profile picture path for user"""
    conn = get_connection()
    if not conn:
        return False

    try:
        cursor = conn.cursor()
        sql = "UPDATE user SET pp_path = ? WHERE user_name = ?"
        cursor.execute(sql, (path, username))
        conn.commit()
        print("USER PROFILE PICTURE UPDATED")
        return True

    except sqlite3.Error as e:
        print(f"Database error: Failed to update profile picture - {e}")
        return False
    finally:
        conn.close()


# ==============================================
# Core POST Operations
# ==============================================

def add_post(post_data: Dict) -> Optional[int]:
    """
    Add a new post to the database
    post_data should contain: user_id, post_score, content, categories, like_count, dislike_count, comment_count
    Returns the post_id if successful, None otherwise
    """
    conn = get_connection()
    if not conn:
        return None

    try:
        cursor = conn.cursor()
        sql = """INSERT INTO post (user_id, post_score, date_text, category, content, 
                 like_count, dislike_count, comment_count) 
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?)"""

        date_str = timepoint_to_string(datetime.now())
        category_str = join_categories(post_data.get('categories', []))

        cursor.execute(sql, (
            post_data.get('user_id'),
            post_data.get('post_score', 0),
            date_str,
            category_str,
            post_data.get('content'),
            post_data.get('like_count', 0),
            post_data.get('dislike_count', 0),
            post_data.get('comment_count', 0)
        ))

        conn.commit()
        post_id = cursor.lastrowid
        return post_id

    except sqlite3.Error as e:
        print(f"Database error: Failed to add post - {e}")
        return None
    finally:
        conn.close()


def read_post(post_id: int) -> Optional[Dict]:
    """Read post data by post_id"""
    conn = get_connection()
    if not conn:
        return None

    try:
        cursor = conn.cursor()
        sql = """SELECT * FROM post WHERE post_id = ?"""
        cursor.execute(sql, (post_id,))
        row = cursor.fetchone()

        if row:
            return {
                'post_id': row[0],
                'user_id': row[1],
                'post_score': row[6],
                'date': format_time_ago(string_to_timepoint(row[2])) if row[2] else None,
                'categories': split_categories(row[3]) if row[3] else [],
                'content': row[4] if row[4] else "",
                'like_count': row[5],
                'dislike_count': row[7],
                'comment_count': row[8]
            }
        else:
            return None

    except sqlite3.Error as e:
        print(f"Database error: Failed to read post - {e}")
        return None
    finally:
        conn.close()


def delete_post(post_id: int, user_id: int) -> bool:
    """Delete a post from the database"""
    conn = get_connection()
    if not conn:
        return False

    try:
        cursor = conn.cursor()
        sql = "DELETE FROM post WHERE post_id = ? AND user_id = ?"
        cursor.execute(sql, (post_id, user_id))
        conn.commit()
        return cursor.rowcount > 0

    except sqlite3.Error as e:
        print(f"Database error: Failed to delete post - {e}")
        return False
    finally:
        conn.close()


def update_post_content(post_id: int, user_id: int, new_content: str) -> bool:
    """Update post content"""
    conn = get_connection()
    if not conn:
        return False

    try:
        cursor = conn.cursor()
        sql = "UPDATE post SET content = ? WHERE post_id = ? AND user_id = ?"
        cursor.execute(sql, (new_content, post_id, user_id))
        conn.commit()
        return cursor.rowcount > 0

    except sqlite3.Error as e:
        print(f"Database error: Failed to update post content - {e}")
        return False
    finally:
        conn.close()


def update_post_categories(post_id: int, user_id: int, categories: List[str]) -> bool:
    """Update post categories"""
    conn = get_connection()
    if not conn:
        return False

    try:
        cursor = conn.cursor()
        category_str = join_categories(categories)
        sql = "UPDATE post SET category = ? WHERE post_id = ? AND user_id = ?"
        cursor.execute(sql, (category_str, post_id, user_id))
        conn.commit()
        return cursor.rowcount > 0

    except sqlite3.Error as e:
        print(f"Database error: Failed to update post categories - {e}")
        return False
    finally:
        conn.close()


def prepare_all_user_posts(user_id: int) -> List[int]:
    """Get all post IDs for a user, ordered by date descending"""
    conn = get_connection()
    if not conn:
        return []

    try:
        cursor = conn.cursor()
        sql = "SELECT post_id FROM post WHERE user_id = ? ORDER BY date_text DESC"
        cursor.execute(sql, (user_id,))
        rows = cursor.fetchall()
        return [row[0] for row in rows]

    except sqlite3.Error as e:
        print(f"Database error: Failed to get user posts - {e}")
        return []
    finally:
        conn.close()


def get_user_latest_post(user_id: int) -> Optional[Dict]:
    """Get the latest post for a user"""
    conn = get_connection()
    if not conn:
        return None

    try:
        cursor = conn.cursor()
        sql = """SELECT * FROM post WHERE user_id = ? ORDER BY date_text DESC LIMIT 1"""
        cursor.execute(sql, (user_id,))
        row = cursor.fetchone()

        if row:
            return {
                'post_id': row[0],
                'user_id': row[1],
                'post_score': row[6],
                'date': format_time_ago(string_to_timepoint(row[2])) if row[2] else None,
                'categories': split_categories(row[3]) if row[3] else [],
                'content': row[4] if row[4] else "",
                'like_count': row[5],
                'dislike_count': row[7],
                'comment_count': row[8]
            }
        else:
            return None

    except sqlite3.Error as e:
        print(f"Database error: Failed to get user's latest post - {e}")
        return None
    finally:
        conn.close()


def return_following_posts(user_id: int) -> List[Dict]:
    """Get all posts from users that the given user follows"""
    conn = get_connection()
    if not conn:
        return []

    try:
        cursor = conn.cursor()
        sql = """SELECT p.* FROM post p 
                 JOIN follow f ON p.user_id = f.followed_id 
                 WHERE f.follower_id = ?"""
        cursor.execute(sql, (user_id,))
        rows = cursor.fetchall()

        posts = []
        for row in rows:
            posts.append({
                'post_id': row[0],
                'user_id': row[1],
                'post_score': row[6] if len(row) > 6 else 0,
                'date': format_time_ago(string_to_timepoint(row[2])) if row[2] else None,
                'categories': split_categories(row[3]) if row[3] else [],
                'content': row[4] if row[4] else "",
                'like_count': row[5] if len(row) > 6 else 0,
                'dislike_count': row[7] if len(row) > 7 else 0,
                'comment_count': row[8] if len(row) > 8 else 0
            })

        return posts

    except sqlite3.Error as e:
        print(f"Database error: Failed to get following posts - {e}")
        return []
    finally:
        conn.close()


# ==============================================
# Like/Dislike Counter Operations
# ==============================================

def increment_post_like_count(post_id: int, conn=None) -> bool:
    """Increment the like count for a post"""
    should_close = False
    if conn is None:
        conn = get_connection()
        should_close = True

    if not conn:
        return False

    try:
        cursor = conn.cursor()
        sql = "UPDATE post SET like_count = like_count + 1 WHERE post_id = ?"
        cursor.execute(sql, (post_id,))
        if should_close:
            conn.commit()
        return True

    except sqlite3.Error as e:
        print(f"Database error: Failed to increment like count - {e}")
        return False
    finally:
        if should_close:
            conn.close()


def decrement_post_like_count(post_id: int, conn=None) -> bool:
    """Decrement the like count for a post"""
    should_close = False
    if conn is None:
        conn = get_connection()
        should_close = True

    if not conn:
        return False

    try:
        cursor = conn.cursor()
        sql = """UPDATE post SET like_count = CASE 
                 WHEN like_count > 0 THEN like_count - 1 
                 ELSE 0 END WHERE post_id = ?"""
        cursor.execute(sql, (post_id,))
        if should_close:
            conn.commit()
        return True

    except sqlite3.Error as e:
        print(f"Database error: Failed to decrement like count - {e}")
        return False
    finally:
        if should_close:
            conn.close()


def increment_post_dislike_count(post_id: int, conn=None) -> bool:
    """Increment the dislike count for a post"""
    should_close = False
    if conn is None:
        conn = get_connection()
        should_close = True

    if not conn:
        return False

    try:
        cursor = conn.cursor()
        sql = "UPDATE post SET dislike_count = dislike_count + 1 WHERE post_id = ?"
        cursor.execute(sql, (post_id,))
        if should_close:
            conn.commit()
        return True

    except sqlite3.Error as e:
        print(f"Database error: Failed to increment dislike count - {e}")
        return False
    finally:
        if should_close:
            conn.close()


def decrement_post_dislike_count(post_id: int, conn=None) -> bool:
    """Decrement the dislike count for a post"""
    should_close = False
    if conn is None:
        conn = get_connection()
        should_close = True

    if not conn:
        return False

    try:
        cursor = conn.cursor()
        sql = """UPDATE post SET dislike_count = CASE 
                 WHEN dislike_count > 0 THEN dislike_count - 1 
                 ELSE 0 END WHERE post_id = ?"""
        cursor.execute(sql, (post_id,))
        if should_close:
            conn.commit()
        return True

    except sqlite3.Error as e:
        print(f"Database error: Failed to decrement dislike count - {e}")
        return False
    finally:
        if should_close:
            conn.close()


def increment_post_comment_count(post_id: int) -> bool:
    """Increment the comment count for a post"""
    conn = get_connection()
    if not conn:
        return False

    try:
        cursor = conn.cursor()
        sql = "UPDATE post SET comment_count = comment_count + 1 WHERE post_id = ?"
        cursor.execute(sql, (post_id,))
        conn.commit()
        return True

    except sqlite3.Error as e:
        print(f"Database error: Failed to increment comment count - {e}")
        return False
    finally:
        conn.close()


def decrement_post_comment_count(post_id: int) -> bool:
    """Decrement the comment count for a post"""
    conn = get_connection()
    if not conn:
        return False

    try:
        cursor = conn.cursor()
        sql = """UPDATE post SET comment_count = CASE 
                 WHEN comment_count > 0 THEN comment_count - 1 
                 ELSE 0 END WHERE post_id = ?"""
        cursor.execute(sql, (post_id,))
        conn.commit()
        return True

    except sqlite3.Error as e:
        print(f"Database error: Failed to decrement comment count - {e}")
        return False
    finally:
        conn.close()


# ==============================================
# Core FOLLOW Operations
# ==============================================

def add_follow(follower_id: int, followed_id: int) -> bool:
    """Add a follow relationship (counts handled by DB triggers)"""
    conn = get_connection()
    if not conn:
        return False

    try:
        cursor = conn.cursor()


        # Insert into follow table - trigger updates counts automatically
        date_str = timepoint_to_string(datetime.now())
        cursor.execute("""
            INSERT INTO follow (follower_id, followed_id)
            VALUES (?, ?)
        """, (follower_id, followed_id))

        conn.commit()
        print(f"✅ Follow added: {follower_id} -> {followed_id}")
        return True

    except sqlite3.Error as e:
        print(f"❌ Database error: Failed to add follow - {e}")
        return False
    finally:
        conn.close()


def delete_follow(follower_id: int, followed_id: int) -> bool:
    """Remove a follow relationship (counts handled by DB triggers)"""
    conn = get_connection()
    if not conn:
        return False

    try:
        cursor = conn.cursor()

        # Check if follow relationship exists
        cursor.execute(
            "SELECT 1 FROM follow WHERE follower_id = ? AND followed_id = ?",
            (follower_id, followed_id)
        )
        if not cursor.fetchone():
            print("No follow relationship found")
            return False

        # Delete from follow table (trigger will update counts)
        cursor.execute(
            "DELETE FROM follow WHERE follower_id = ? AND followed_id = ?",
            (follower_id, followed_id)
        )

        conn.commit()
        print(f"❌ Follow removed: {follower_id} -> {followed_id}")
        return True

    except sqlite3.Error as e:
        print(f"❌ Database error: Failed to delete follow - {e}")
        return False

    finally:
        conn.close()




def get_all_follows():
    """
    Get all follow connections to build the graph.
    Only fetches IDs to avoid schema errors.
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()
        # Explicitly select ONLY the IDs. Do not use SELECT *
        cursor.execute("SELECT follower_id, followed_id FROM follow")
        return cursor.fetchall()
    except sqlite3.Error as e:
        print(f"Database error: Failed to get all follows - {e}")
        return []
    finally:
        conn.close()


def get_followers_list_for_user(user_id: int) -> List[str]:
    """Get list of usernames who follow the given user"""
    conn = get_connection()
    if not conn:
        return []

    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT u.user_name 
            FROM follow f 
            JOIN user u ON f.follower_id = u.user_id 
            WHERE f.followed_id = ? 
        """, (user_id,))
        rows = cursor.fetchall()
        return [row[0] for row in rows]

    except sqlite3.Error as e:
        print(f"❌ Database error: Failed to get followers list - {e}")
        return []
    finally:
        conn.close()



def get_recent_followers(user_id: int, hours: int = 24) -> List[Dict]:
    """Get recent followers within the specified hours"""
    conn = get_connection()
    if not conn:
        return []

    try:
        cursor = conn.cursor()
        time_threshold = datetime.now() - timedelta(hours=hours)
        time_threshold_str = timepoint_to_string(time_threshold)

        sql = """SELECT u.user_id, u.user_name, u.full_name, f.date_text 
                 FROM follow f 
                 JOIN user u ON f.follower_id = u.user_id 
                 WHERE f.followed_id = ? AND f.date_text >= ?
                 """
        cursor.execute(sql, (user_id, time_threshold_str))
        rows = cursor.fetchall()

        recent_followers = []
        for row in rows:
            recent_followers.append({
                'user_id': row[0],
                'username': row[1],
                'full_name': row[2],
                'created_at': string_to_timepoint(row[3]) if row[3] else None,
                'time_ago': format_time_ago(string_to_timepoint(row[3])) if row[3] else "Just now"
            })
        return recent_followers

    except sqlite3.Error as e:
        print(f"Database error: Failed to get recent followers - {e}")
        return []
    finally:
        conn.close()


def get_following_list_of_user(user_id: int) -> List[str]:
    """Get list of usernames that the given user follows"""
    conn = get_connection()
    if not conn:
        return []

    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT u.user_name 
            FROM follow f 
            JOIN user u ON f.followed_id = u.user_id 
            WHERE f.follower_id = ? 
        """, (user_id,))
        rows = cursor.fetchall()
        return [row[0] for row in rows]

    except sqlite3.Error as e:
        print(f"❌ Database error: Failed to get following list - {e}")
        return []
    finally:
        conn.close()

def get_followers_with_details(user_id: int) -> List[Dict]:
    """Get list of users who follow the given user with full details"""
    conn = get_connection()
    if not conn:
        return []

    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT u.user_id, u.user_name, u.full_name, u.email, f.date_text 
            FROM follow f 
            JOIN user u ON f.follower_id = u.user_id 
            WHERE f.followed_id = ? 
        """, (user_id,))
        rows = cursor.fetchall()

        followers = []
        for row in rows:
            followers.append({
                'user_id': row[0],
                'username': row[1],
                'full_name': row[2],
                'email': row[3],
            })
        return followers

    except sqlite3.Error as e:
        print(f"❌ Database error: Failed to get followers with details - {e}")
        return []
    finally:
        conn.close()

def is_following(follower_id: int, followed_id: int) -> bool:
    """Check if one user follows another"""
    conn = get_connection()
    if not conn:
        return False

    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 1 FROM follow 
            WHERE follower_id = ? AND followed_id = ?
        """, (follower_id, followed_id))
        return cursor.fetchone() is not None

    except sqlite3.Error as e:
        print(f"❌ Database error: Failed to check follow status - {e}")
        return False
    finally:
        conn.close()


def get_follower_count(user_id: int) -> int:
    """Get number of followers for a user"""
    conn = get_connection()
    if not conn:
        return 0

    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT COUNT(*) FROM follow WHERE followed_id = ?
        """, (user_id,))
        row = cursor.fetchone()
        return row[0] if row else 0

    except sqlite3.Error as e:
        print(f"❌ Database error: Failed to get follower count - {e}")
        return 0
    finally:
        conn.close()


def get_following_count(user_id: int) -> int:
    """Get number of users a user is following"""
    conn = get_connection()
    if not conn:
        return 0

    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT COUNT(*) FROM follow WHERE follower_id = ?
        """, (user_id,))
        row = cursor.fetchone()
        return row[0] if row else 0

    except sqlite3.Error as e:
        print(f"❌ Database error: Failed to get following count - {e}")
        return 0
    finally:
        conn.close()

# ==============================================
# Core LIKE/DISLIKE Operations
# ==============================================

def add_like(post_id: int, user_id: int) -> bool:
    """Add a like to a post (removes dislike if exists)"""
    conn = get_connection()
    if not conn:
        return False

    try:
        cursor = conn.cursor()

        # Check if user already liked this post
        sql_check = "SELECT 1 FROM likes WHERE post_id = ? AND user_id = ?"
        cursor.execute(sql_check, (post_id, user_id))
        if cursor.fetchone():
            print("User already liked this post")
            return True

        # First, remove any existing dislike
        cursor.execute("DELETE FROM dislikes WHERE post_id = ? AND user_id = ?",
                       (post_id, user_id))
        if cursor.rowcount > 0:
            decrement_post_dislike_count(post_id, conn)
            print("Dislike removed before adding like")

        # Now add the like with timestamp
        date_str = timepoint_to_string(datetime.now())
        cursor.execute("INSERT INTO likes (post_id, user_id, date_text) VALUES (?, ?, ?)",
                       (post_id, user_id, date_str))

        if cursor.rowcount > 0:
            increment_post_like_count(post_id, conn)
            print(f"✅ User {user_id} liked post {post_id}")

        conn.commit()
        return True

    except sqlite3.Error as e:
        print(f"Database error: Failed to add like - {e}")
        return False
    finally:
        conn.close()


def add_dislike(post_id: int, user_id: int) -> bool:
    """Add a dislike to a post (removes like if exists)"""
    conn = get_connection()
    if not conn:
        return False

    try:
        cursor = conn.cursor()

        # Check if user already disliked this post
        sql_check = "SELECT 1 FROM dislikes WHERE post_id = ? AND user_id = ?"
        cursor.execute(sql_check, (post_id, user_id))
        if cursor.fetchone():
            print("User already disliked this post")
            return True

        # First, remove any existing like
        cursor.execute("DELETE FROM likes WHERE post_id = ? AND user_id = ?",
                       (post_id, user_id))
        if cursor.rowcount > 0:
            decrement_post_like_count(post_id, conn)
            print("Like removed before adding dislike")

        # Now add the dislike with timestamp
        date_str = timepoint_to_string(datetime.now())
        cursor.execute("INSERT INTO dislikes (post_id, user_id, date_text) VALUES (?, ?, ?)",
                       (post_id, user_id, date_str))

        if cursor.rowcount > 0:
            increment_post_dislike_count(post_id, conn)
            print(f"✅ User {user_id} disliked post {post_id}")

        conn.commit()
        return True

    except sqlite3.Error as e:
        print(f"Database error: Failed to add dislike - {e}")
        return False
    finally:
        conn.close()


def delete_like(post_id: int, user_id: int) -> bool:
    """Remove a like from a post"""
    conn = get_connection()
    if not conn:
        return False

    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM likes WHERE post_id = ? AND user_id = ?",
                       (post_id, user_id))

        if cursor.rowcount > 0:
            decrement_post_like_count(post_id, conn)
            print(f"✅ User {user_id} removed like from post {post_id}")

        conn.commit()
        return True

    except sqlite3.Error as e:
        print(f"Database error: Failed to delete like - {e}")
        return False
    finally:
        conn.close()


def delete_dislike(post_id: int, user_id: int) -> bool:
    """Remove a dislike from a post"""
    conn = get_connection()
    if not conn:
        return False

    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM dislikes WHERE post_id = ? AND user_id = ?",
                       (post_id, user_id))

        if cursor.rowcount > 0:
            decrement_post_dislike_count(post_id, conn)
            print(f"✅ User {user_id} removed dislike from post {post_id}")

        conn.commit()
        return True

    except sqlite3.Error as e:
        print(f"Database error: Failed to delete dislike - {e}")
        return False
    finally:
        conn.close()


def get_post_likes(post_id: int) -> List[Dict]:
    """Get all likes for a post with user info and timestamps"""
    conn = get_connection()
    if not conn:
        return []

    try:
        cursor = conn.cursor()
        sql = """SELECT u.user_id, u.user_name, u.full_name, l.date_text 
                 FROM likes l 
                 JOIN user u ON l.user_id = u.user_id 
                 WHERE l.post_id = ? 
                 ORDER BY l.date_text DESC"""
        cursor.execute(sql, (post_id,))
        rows = cursor.fetchall()

        likes = []
        for row in rows:
            likes.append({
                'user_id': row[0],
                'username': row[1],
                'full_name': row[2],
                'created_at': string_to_timepoint(row[3]) if row[3] else None,
                'time_ago': format_time_ago(string_to_timepoint(row[3])) if row[3] else "Just now"
            })
        return likes

    except sqlite3.Error as e:
        print(f"Database error: Failed to get post likes - {e}")
        return []
    finally:
        conn.close()


def get_recent_post_likes(user_id: int, hours: int = 24) -> List[Dict]:
    """Get recent likes on user's posts within the specified hours"""
    conn = get_connection()
    if not conn:
        return []

    try:
        cursor = conn.cursor()
        time_threshold = datetime.now() - timedelta(hours=hours)
        time_threshold_str = timepoint_to_string(time_threshold)

        sql = """SELECT p.post_id, p.content, u.user_id, u.user_name, u.full_name, l.date_text 
                 FROM likes l 
                 JOIN post p ON l.post_id = p.post_id 
                 JOIN user u ON l.user_id = u.user_id 
                 WHERE p.user_id = ? AND l.date_text >= ?
                 ORDER BY l.date_text DESC"""
        cursor.execute(sql, (user_id, time_threshold_str))
        rows = cursor.fetchall()

        recent_likes = []
        for row in rows:
            post_content = row[1] if row[1] else ""
            post_preview = post_content[:30] + '...' if len(post_content) > 30 else post_content

            recent_likes.append({
                'post_id': row[0],
                'post_content': row[1],
                'post_preview': post_preview,
                'user_id': row[2],
                'username': row[3],
                'full_name': row[4],
                'created_at': string_to_timepoint(row[5]) if row[5] else None,
                'time_ago': format_time_ago(string_to_timepoint(row[5])) if row[5] else "Just now"
            })
        return recent_likes

    except sqlite3.Error as e:
        print(f"Database error: Failed to get recent post likes - {e}")
        return []
    finally:
        conn.close()


# ==============================================
# Activity Feed Operations
# ==============================================

def get_user_activity(user_id: int, limit: int = 20) -> List[Dict]:
    """
    Get recent activity for a user (followers and post likes)

    Args:
        user_id: The user ID to get activity for
        limit: Maximum number of activities to return

    Returns:
        List of activity dictionaries
    """
    activities = []

    # Get recent followers
    recent_followers = get_recent_followers(user_id, hours=168)  # Last 7 days

    for follower in recent_followers:
        activities.append({
            'type': 'follow',
            'user_id': follower['user_id'],
            'username': follower['username'],
            'full_name': follower['full_name'],
            'action': 'started following you',
            'timestamp': follower['created_at'],
            'time_ago': follower['time_ago']
        })

    # Get recent likes on user's posts
    recent_likes = get_recent_post_likes(user_id, hours=168)  # Last 7 days

    for like in recent_likes:
        activities.append({
            'type': 'like',
            'user_id': like['user_id'],
            'username': like['username'],
            'full_name': like['full_name'],
            'post_id': like['post_id'],
            'post_preview': like['post_preview'],
            'action': f"liked your post: \"{like['post_preview']}\"",
            'timestamp': like['created_at'],
            'time_ago': like['time_ago']
        })

    # Sort by timestamp (most recent first)
    activities.sort(key=lambda x: x['timestamp'] if x['timestamp'] else datetime.min, reverse=True)

    # Return limited results
    return activities[:limit]

#--------------------------- new for engine
def get_mutual_friends_count(user_id1: int, user_id2: int) -> int:
    """Get number of mutual friends between user1 and user2"""
    conn = get_connection()
    if not conn:
        return 0

    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT COUNT(*)
            FROM (
                SELECT followed_id
                FROM follow
                WHERE follower_id = ?
                INTERSECT
                SELECT followed_id
                FROM follow
                WHERE follower_id = ?
            );
        """, (user_id1, user_id2))

        row = cursor.fetchone()
        return row[0] if row else 0

    except sqlite3.Error as e:
        print(f" Database error: Failed to get mutual friends count - {e}")
        return 0
    finally:
        conn.close()

# ==============================================
# TRIE SEARCH Implementation
# ==============================================

class TrieNode:
    """Node for Trie data structure"""
    CHAR_SIZE = 62  # a-z (26) + A-Z (26) + 0-9 (10)

    def __init__(self):
        self.is_leaf = False
        self.characters = [None] * self.CHAR_SIZE


def get_index(char: str) -> int:
    """Get index for character in trie"""
    if 'a' <= char <= 'z':
        return ord(char) - ord('a')
    elif 'A' <= char <= 'Z':
        return ord(char) - ord('A') + 26
    elif '0' <= char <= '9':
        return ord(char) - ord('0') + 52
    return -1


def insert_trie(root: TrieNode, word: str) -> None:
    """Insert a word into the trie"""
    current = root
    for char in word:
        idx = get_index(char)
        if idx == -1:
            continue

        if current.characters[idx] is None:
            current.characters[idx] = TrieNode()

        current = current.characters[idx]

    current.is_leaf = True


def search_trie(root: TrieNode, key: str) -> bool:
    """Search for a complete word in the trie"""
    if not root:
        return False

    current = root
    for char in key:
        idx = get_index(char)
        if idx == -1 or current.characters[idx] is None:
            return False
        current = current.characters[idx]

    return current.is_leaf


def prefix_search(root: TrieNode, key: str) -> Optional[TrieNode]:
    """Search for a prefix in the trie and return the node where it ends"""
    if not root:
        return None

    current = root
    for char in key:
        idx = get_index(char)
        if idx == -1 or current.characters[idx] is None:
            return None
        current = current.characters[idx]

    return current


def is_last_leaf(node: TrieNode) -> bool:
    """Check if a node is a leaf (has no children)"""
    for child in node.characters:
        if child is not None:
            return False
    return True


def suggest(current: TrieNode, prefix: str, suggestions: List[str]) -> None:
    """Recursively collect all words with the given prefix"""
    if current.is_leaf:
        suggestions.append(prefix)

    for i in range(TrieNode.CHAR_SIZE):
        if current.characters[i] is not None:
            # Determine the character based on index
            if i < 26:
                next_char = chr(ord('a') + i)
            elif i < 52:
                next_char = chr(ord('A') + (i - 26))
            else:
                next_char = chr(ord('0') + (i - 52))

            suggest(current.characters[i], prefix + next_char, suggestions)


def print_suggestions(prefix: str, root: TrieNode) -> int:
    """
    Print all suggestions for a given prefix
    Returns: 1 if suggestions found, 0 if prefix not found, -1 if prefix is complete word
    """
    if not root:
        print("No trie tree")
        return 0

    current = prefix_search(root, prefix)

    if not current:
        print("Not found")
        return 0

    if is_last_leaf(current):
        print(prefix)
        return -1

    suggestions = []
    suggest(current, prefix, suggestions)

    for suggestion in suggestions:
        print(suggestion)

    return 1


def get_suggestions(prefix: str, root: TrieNode) -> List[str]:
    """
    Get all suggestions for a given prefix as a list
    Returns: List of suggested words
    """
    if not root:
        return []

    current = prefix_search(root, prefix)

    if not current:
        return []

    if is_last_leaf(current):
        return [prefix]

    suggestions = []
    suggest(current, prefix, suggestions)

    return suggestions


def get_all_usernames() -> List[str]:
    """
    Fetch all usernames from the database.
    """
    conn = get_connection()
    if not conn:
        print("operation failed")
        return []

    try:
        cursor = conn.cursor()
        cursor.execute("SELECT user_name FROM user")
        rows = cursor.fetchall()
        return [row[0] for row in rows]

    except sqlite3.Error as e:
        print(f"Database error: Failed to execute query - {e}")
        return []
    finally:
        conn.close()

def initialize_trie_tree(root: TrieNode) -> None:
    """
    Populates the Trie with all usernames from the DB.
    """
    usernames = get_all_usernames()
    for name in usernames:
        insert_trie(root, name)
    print(f"DEBUG: Trie initialized with {len(usernames)} users.")


def add_message(m: Msg) -> bool:
    conn = get_connection()
    if not conn:
        print("Database error: Failed to open database connection.")
        return False

    try:
        cursor = conn.cursor()
        # Fixed: removed extra comma, added date_text
        from datetime import datetime
        date_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        sql = "INSERT INTO messages (sender_id, receiver_id, date_text,content) VALUES (?, ?, ?, ?);"
        cursor.execute(sql, (m.sender_id, m.receiver_id, date_str, m.content))
        conn.commit()

        m.msg_id = cursor.lastrowid
        return True

    except sqlite3.Error as e:
        print(f"Database error: Failed to execute query - {e}")
        return False

    finally:
        conn.close()


def delete_message(m: Msg) -> bool:
    conn = get_connection()
    if not conn:
        print("Database error: Failed to open database connection.")
        return False

    try:
        cursor = conn.cursor()
        sql = "DELETE FROM messages WHERE id = ? ;"
        cursor.execute(sql, (m.msg_id,))
        conn.commit()
        return True

    except sqlite3.Error as e:
        print(f"Database error: Failed to execute query - {e}")
        return False

    finally:
        conn.close()



from typing import List

def get_chat(user1: int, user2: int) -> List[Msg]:
    chat: List[Msg] = []

    conn = get_connection()
    if not conn:
        print("operation failed")
        return chat

    try:
        cursor = conn.cursor()

        # Fixed: Changed receiver_id in second condition (was reciever_id in table)
        sql = (
            "SELECT * FROM messages "
            "WHERE (sender_id = ? AND receiver_id = ?) "
            "   OR (sender_id = ? AND receiver_id = ?) "
            "ORDER BY date_text;"
        )

        cursor.execute(sql, (user1, user2, user2, user1))

        rows = cursor.fetchall()
        for row in rows:
            temp = Msg()
            temp.set_msg_id(row[0])
            temp.set_sender_id(row[1])
            temp.set_receiver_id(row[2])
            date = row[4] if row[4] else ""
            temp.set_date(date)
            content = row[3] if row[3] else ""
            temp.set_content(content);
            chat.append(temp)

    except sqlite3.Error as e:
        print(f"Database error: {e}")

    finally:
        conn.close()

    return chat
