from PySide6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout,
    QPushButton, QListWidget, QScrollArea, QListWidgetItem,
    QFrame, QLineEdit, QTextEdit, QSpacerItem, QSizePolicy,
    QMessageBox,QInputDialog
)
from PySide6.QtGui import QPixmap, QIcon, QFont, QPainter, QPainterPath,QColor
from PySide6.QtCore import Qt, QRectF
import os
from datetime import datetime, timedelta
from app.utils import paths


class HomePage(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.nav_buttons = {}

        # Store references for dynamic updates
        self.post_input = None
        self.feed_layout = None

        # Store references to user info labels for updating
        self.name_label = None
        self.username_label = None
        self.posts_count_label = None
        self.followers_count_label = None
        self.following_count_label = None
        self.profile_pic_label = None

        # Store references for search section
        self.search_input = None
        self.search_results_list = None

        # Store references for dynamic sections
        self.shortcuts_container = None
        self.activity_container = None
        self.suggested_container = None

        # Store current filter state
        self.current_filter = None  # None = show all, or specific interest/category

        self.build_ui()
        self.apply_theme()

    def showEvent(self, event):
        """Called every time the page is shown. Refreshes all dynamic content."""
        self.update_user_info()
        self.update_profile_pic()
        self.update_shortcuts_section()
        self.load_posts()
        self.update_activity_section()
        self.update_suggested_section()
        super().showEvent(event)

    # ================= UPDATE USER INFO =================
    def update_user_info(self):
        """Fetch and display current user's information"""
        current_user = self.main_window.app.get_current_user()

        if not current_user:
            # If no user is logged in, show default values
            self.name_label.setText("Guest User")
            self.username_label.setText("@guest")
            self.posts_count_label.setText("0")
            self.followers_count_label.setText("0")
            self.following_count_label.setText("0")
            return

        # Get user statistics from backend
        stats = self.main_window.app.get_user_statistics()

        # Update profile section
        self.name_label.setText(current_user.get_fullname())
        self.username_label.setText(f"@{current_user.get_username()}")

        # Update stats
        self.posts_count_label.setText(str(stats.get('total_posts', 0)))
        self.followers_count_label.setText(str(stats.get('followers', 0)))
        self.following_count_label.setText(str(stats.get('following', 0)))

    # ================= SHORTCUTS SECTION =================
    def update_shortcuts_section(self):
        """Update shortcuts section with current user's interests"""
        if not self.shortcuts_container:
            return

        # Clear existing shortcuts
        layout = self.shortcuts_container.layout()
        if layout:
            while layout.count() > 2:  # Keep header (title + see all button)
                item = layout.takeAt(2)
                if item.widget():
                    item.widget().deleteLater()

        # Get current user
        current_user = self.main_window.app.get_current_user()

        if not current_user:
            no_interests = QLabel("Please login to see your interests")
            no_interests.setStyleSheet("color: #999; font-size: 12px; padding: 5px 0;")
            layout.addWidget(no_interests)
            return

        # Get interests
        interests = current_user.get_interests()

        # Handle if interests is a string
        if isinstance(interests, str):
            interests = [i.strip() for i in interests.split(",") if i.strip()]

        if not interests or len(interests) == 0:
            no_interests = QLabel("No interests yet. Edit your profile!")
            no_interests.setStyleSheet("color: #999; font-size: 12px; padding: 5px 0;")
            layout.addWidget(no_interests)
            return

        # Display first 4 interests with filter functionality
        for interest in interests[:4]:
            item = QPushButton(f"• {interest}")
            item.setStyleSheet("""
                QPushButton {
                    text-align: left;
                    padding: 8px 0;
                    border: none;
                    font-size: 14px;
                    color: #EAEAEA;
                }
                QPushButton:hover {
                    color: #6C5CE7;
                }
            """)
            # Connect to filter function
            item.clicked.connect(lambda checked, i=interest: self.filter_feed_by_interest(i))
            layout.addWidget(item)

    # ================= ACTIVITY SECTION =================
    def update_activity_section(self):
        """Update the activity section with recent followers and post likes"""
        current_user = self.main_window.app.get_current_user()
        if not current_user:
            self.update_activity_ui([])
            return

        # Get recent followers
        recent_followers = self.get_recent_followers()

        # Get recent likes on user's posts
        recent_post_likes = self.get_recent_post_likes()

        # Combine and sort activities by time (most recent first)
        activities = []

        # Add follower activities
        for follower_data in recent_followers:
            activities.append({
                'type': 'follow',
                'user': follower_data['username'],
                'action': 'started following you',
                'time': self.format_time_ago(follower_data['time']),
                'timestamp': follower_data['time'],
                'user_id': follower_data['user_id']
            })

        # Add post like activities
        for like_data in recent_post_likes:
            activities.append({
                'type': 'like',
                'user': like_data['username'],
                'action': f"liked your post: \"{like_data['post_preview']}\"",
                'time': self.format_time_ago(like_data['time']),
                'timestamp': like_data['time'],
                'user_id': like_data['user_id'],
                'post_id': like_data['post_id']
            })

        # Sort by timestamp (most recent first)
        activities.sort(key=lambda x: x['timestamp'], reverse=True)

        # Update the activity section UI
        self.update_activity_ui(activities[:10])

    def get_recent_followers(self):
        """Get recent followers"""
        current_user = self.main_window.app.get_current_user()
        if not current_user:
            return []

        followers = self.main_window.app.get_followers()

        recent_followers = []
        time_options = ['5m', '30m', '1h', '2h', '5h']

        for i, follower_username in enumerate(followers[:5]):
            follower_data = self.main_window.app.search_user_by_username(follower_username)
            if follower_data:
                time_str = time_options[min(i, len(time_options) - 1)]
                recent_followers.append({
                    'username': follower_username,
                    'full_name': follower_data.get('full_name', follower_username),
                    'user_id': follower_data.get('user_id'),
                    'time': self.calculate_timestamp(time_str)
                })

        return recent_followers

    def get_recent_post_likes(self):
        """Get recent likes on user's posts"""
        current_user = self.main_window.app.get_current_user()
        if not current_user:
            return []

        user_posts = self.main_window.app.get_user_posts()
        if not user_posts:
            return []

        latest_post = user_posts[0] if user_posts else None
        if not latest_post:
            return []

        post_content = latest_post.get('content', '')
        post_preview = post_content[:30] + '...' if len(post_content) > 30 else post_content

        recent_likes = []
        like_count = latest_post.get('like_count', 0)

        if like_count > 0:
            sample_users = ['essmat', 'zoz', 'wego']
            time_options = ['10m', '45m', '2h']

            for i, username in enumerate(sample_users[:min(3, like_count)]):
                user_data = self.main_window.app.search_user_by_username(username)
                if user_data:
                    recent_likes.append({
                        'username': username,
                        'full_name': user_data.get('full_name', username),
                        'user_id': user_data.get('user_id'),
                        'post_id': latest_post.get('post_id'),
                        'post_preview': post_preview,
                        'time': self.calculate_timestamp(time_options[min(i, len(time_options) - 1)])
                    })

        return recent_likes

    def calculate_timestamp(self, time_ago_str):
        """Convert time ago string to actual timestamp for sorting"""
        now = datetime.now()

        if time_ago_str.endswith('m'):
            minutes = int(time_ago_str[:-1])
            return now - timedelta(minutes=minutes)
        elif time_ago_str.endswith('h'):
            hours = int(time_ago_str[:-1])
            return now - timedelta(hours=hours)
        elif time_ago_str.endswith('d'):
            days = int(time_ago_str[:-1])
            return now - timedelta(days=days)
        else:
            return now - timedelta(hours=1)

    def format_time_ago(self, timestamp):
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

    def update_activity_ui(self, activities):
        """Update the activity section UI with the provided activities"""
        if not self.activity_container:
            return

        layout = self.activity_container.layout()
        if not layout:
            return

        # Clear existing items except header
        while layout.count() > 1:
            item = layout.takeAt(1)
            if item.widget():
                item.widget().deleteLater()

        # Add activity items
        if not activities:
            no_activity = QLabel("No recent activity")
            no_activity.setStyleSheet("color: #999; font-size: 14px; padding: 20px 0;")
            no_activity.setAlignment(Qt.AlignCenter)
            layout.addWidget(no_activity)
            return

        for activity in activities:
            item_layout = QHBoxLayout()

            user_text = f"<b>{activity['user']}</b> {activity['action']}. {activity['time']}"
            text = QLabel(user_text)
            text.setStyleSheet("font-size: 14px;")
            text.setTextFormat(Qt.RichText)
            text.setWordWrap(True)

            # Make text clickable
            text.setCursor(Qt.PointingHandCursor)
            text.mousePressEvent = lambda e, uid=activity['user_id']: self.view_user_profile(uid)

            item_layout.addWidget(text)
            item_layout.addStretch()

            # Add follow button for follow activities
            if activity['type'] == 'follow' and activity.get('user_id'):
                is_following_back = self.main_window.app.is_following(activity['user_id'])
                if not is_following_back:
                    btn = QPushButton("Follow back")
                    btn.setFixedSize(90, 30)
                    btn.setStyleSheet("""
                        QPushButton {
                            background-color: #6C5CE7;
                            color: white;
                            border-radius: 6px;
                            font-size: 12px;
                            font-weight: bold;
                        }
                        QPushButton:hover {
                            background-color: #5A4FD8;
                        }
                    """)
                    btn.clicked.connect(lambda checked=None, uid=activity['user_id']: self.handle_follow_back(uid))
                    if is_following_back:
                        btn = QPushButton("following")
                        btn.setFixedSize(90, 30)
                        btn.setStyleSheet("""
                             QPushButton {
                                 background-color: #6C5CE7;
                                 color: white;
                                 border-radius: 6px;
                                 font-size: 12px;
                                 font-weight: bold;
                             }
                             QPushButton:hover {
                                 background-color: #5A4FD8;
                             }
                         """)
                    item_layout.addWidget(btn)

            layout.addLayout(item_layout)

    def view_user_profile(self, user_id):
        """Navigate to user profile page"""
        user_data = self.main_window.app.search_user_by_id(user_id)
        if user_data:
            self.main_window.show_user_profile(user_data)

    def handle_follow_back(self, user_id):
        """Handle follow back button click"""
        success, message = self.main_window.app.follow_user(user_id)
        if success:
            QMessageBox.information(self, "Success", "You are now following back!")
            self.update_user_info()
            self.update_activity_section()
        else:
            QMessageBox.warning(self, "Error", message)

    # ================= SUGGESTED SECTION =================
    def update_suggested_section(self):
        """Update the suggested for you section"""
        if not self.suggested_container:
            return

        layout = self.suggested_container.layout()
        if not layout:
            return

        # Clear existing items except header
        while layout.count() > 1:
            item = layout.takeAt(1)
            if item.widget():
                item.widget().deleteLater()

        # Get friend recommendations
        recommendations = self.main_window.app.recommend_friends()

        if not recommendations:
            no_suggestions = QLabel("No suggestions available")
            no_suggestions.setStyleSheet("color: #999; font-size: 14px;")
            layout.addWidget(no_suggestions)
            return

        # Show top 3 recommendations
        for user_data, similarity in recommendations[:3]:
            user_layout = QHBoxLayout()

            username = user_data.get('username', 'Unknown')
            full_name = user_data.get('full_name', username)

            user_info = QLabel(
                f"<b>{username}</b><br><span style='color: #666; font-size: 12px;'>Suggested for you</span>"
            )
            user_info.setStyleSheet("font-size: 14px;")
            user_info.setTextFormat(Qt.RichText)

            user_layout.addWidget(user_info)
            user_layout.addStretch()

            btn = QPushButton("Follow")
            btn.setFixedSize(80, 30)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #6C5CE7;
                    color: white;
                    border-radius: 6px;
                    font-size: 12px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #5A4FD8;
                }
            """)

            user_id = user_data.get('user_id')
            btn.clicked.connect(lambda checked, uid=user_id: self.handle_follow(uid))

            user_layout.addWidget(btn)
            layout.addLayout(user_layout)

    # ================= BUILD UI =================
    def build_ui(self):
        main_layout = QHBoxLayout()
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Left Sidebar
        left_sidebar = self.create_left_sidebar()
        main_layout.addWidget(left_sidebar)

        # Center Feed
        center_feed = self.create_center_feed()
        main_layout.addWidget(center_feed, 2)

        # Right Sidebar
        right_sidebar = self.create_right_sidebar()
        main_layout.addWidget(right_sidebar)

        self.setLayout(main_layout)

    def create_left_sidebar(self):
        """Create the left sidebar with profile information"""
        sidebar = QFrame()
        sidebar.setFixedWidth(280)
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setAlignment(Qt.AlignTop)

        # Profile Section
        profile_section = self.create_profile_section()
        layout.addWidget(profile_section)

        # My Profile Button
        profile_btn = QPushButton("My Profile")
        profile_btn.setFixedHeight(45)
        profile_btn.setStyleSheet("""
            QPushButton {
                background-color: #6C5CE7;
                color: white;
                border-radius: 10px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #5A4FD8;
            }
        """)
        profile_btn.clicked.connect(self.main_window.go_to_my_profile)
        layout.addWidget(profile_btn)

        # Shortcuts Section
        shortcuts_section = self.create_shortcuts_section()
        layout.addWidget(shortcuts_section)

        # Share Section
        share_section = self.create_share_section()
        layout.addWidget(share_section)

        layout.addStretch()
        sidebar.setLayout(layout)
        return sidebar

    def create_profile_section(self):
        """Create the profile section with dynamic user data"""
        frame = QFrame()
        layout = QVBoxLayout()
        layout.setSpacing(15)

        # Profile header
        profile_header = QHBoxLayout()
        self.profile_pic_label = QLabel()
        self.profile_pic_label.setFixedSize(70, 70)
        self.profile_pic_label.setStyleSheet("border-radius: 35px; border: 3px solid #6C5CE7;")

        name_layout = QVBoxLayout()

        self.name_label = QLabel("Loading...")
        self.name_label.setStyleSheet("font-weight: bold; font-size: 18px;")

        self.username_label = QLabel("@loading")
        self.username_label.setStyleSheet("color: #666; font-size: 14px;")

        name_layout.addWidget(self.name_label)
        name_layout.addWidget(self.username_label)

        profile_header.addWidget(self.profile_pic_label)
        profile_header.addLayout(name_layout)
        layout.addLayout(profile_header)

        # Stats
        stats_layout = QHBoxLayout()

        # Posts
        posts_frame = QFrame()
        posts_layout = QVBoxLayout()
        self.posts_count_label = QLabel("0")
        self.posts_count_label.setStyleSheet("font-weight: bold; font-size: 20px;")
        self.posts_count_label.setAlignment(Qt.AlignCenter)
        posts_label = QLabel("Posts")
        posts_label.setStyleSheet("color: #666; font-size: 12px;")
        posts_label.setAlignment(Qt.AlignCenter)
        posts_layout.addWidget(self.posts_count_label)
        posts_layout.addWidget(posts_label)
        posts_frame.setLayout(posts_layout)

        # Followers
        followers_frame = QFrame()
        followers_layout = QVBoxLayout()
        self.followers_count_label = QLabel("0")
        self.followers_count_label.setStyleSheet("font-weight: bold; font-size: 20px;")
        self.followers_count_label.setAlignment(Qt.AlignCenter)
        followers_label = QLabel("Followers")
        followers_label.setStyleSheet("color: #666; font-size: 12px;")
        followers_label.setAlignment(Qt.AlignCenter)
        followers_layout.addWidget(self.followers_count_label)
        followers_layout.addWidget(followers_label)
        followers_frame.setLayout(followers_layout)

        # Following
        following_frame = QFrame()
        following_layout = QVBoxLayout()
        self.following_count_label = QLabel("0")
        self.following_count_label.setStyleSheet("font-weight: bold; font-size: 20px;")
        self.following_count_label.setAlignment(Qt.AlignCenter)
        following_label = QLabel("Following")
        following_label.setStyleSheet("color: #666; font-size: 12px;")
        following_label.setAlignment(Qt.AlignCenter)
        following_layout.addWidget(self.following_count_label)
        following_layout.addWidget(following_label)
        following_frame.setLayout(following_layout)

        stats_layout.addWidget(posts_frame)
        stats_layout.addWidget(followers_frame)
        stats_layout.addWidget(following_frame)
        layout.addLayout(stats_layout)

        frame.setLayout(layout)
        return frame

    def update_profile_pic(self):
        """Update the profile picture with user's image"""
        # Check if profile_pic_label exists
        if not hasattr(self, 'profile_pic_label') or not self.profile_pic_label:
            print("❌ profile_pic_label not initialized")
            return

        # Get current user
        current_user = self.main_window.app.get_current_user()
        if not current_user:
            print("❌ No current user logged in")
            return

        username = current_user.get_username()
        image_dir = paths.IMAGE_DIR

        # Try multiple image formats
        possible_extensions = ['.png', '.jpg', '.jpeg', '.PNG', '.JPG', '.JPEG']
        img_path = None

        for ext in possible_extensions:
            test_path = os.path.join(image_dir, f"{username}{ext}")
            if os.path.exists(test_path):
                img_path = test_path
                print(f"✅ Found profile image: {img_path}")
                break

        # If no user-specific image found, use default
        if not img_path:
            print(f"⚠️ No profile image found for {username}, using default")
            default_path = os.path.join(image_dir, "profile.png")
            if os.path.exists(default_path):
                img_path = default_path
            else:
                # Create a placeholder
                placeholder = QPixmap(70, 70)
                placeholder.fill(QColor("#6C5CE7"))
                self.profile_pic_label.setPixmap(placeholder)
                return

        # Load and set the circular image
        circular_pixmap = self.load_circular_image(img_path, 67)
        self.profile_pic_label.setPixmap(circular_pixmap)
        print(f"✅ Profile picture updated for {username}")

    def load_circular_image(self, path: str, size: int) -> QPixmap:
        """Load an image, crop it into a circle, and resize."""
        pixmap = QPixmap(path)

        if pixmap.isNull():
            print(f"❌ Image not found: {path}")
            # Create a gray circular placeholder
            placeholder = QPixmap(size, size)
            placeholder.fill(Qt.transparent)

            painter = QPainter(placeholder)
            painter.setRenderHint(QPainter.Antialiasing)
            painter.setBrush(QColor("#CCCCCC"))
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(0, 0, size, size)
            painter.end()

            return placeholder

        # Resize to square maintaining aspect ratio
        pixmap = pixmap.scaled(size, size, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)

        # Crop to exact square if needed
        if pixmap.width() != size or pixmap.height() != size:
            x = (pixmap.width() - size) // 2
            y = (pixmap.height() - size) // 2
            pixmap = pixmap.copy(x, y, size, size)

        # Create circular mask
        circular = QPixmap(size, size)
        circular.fill(Qt.transparent)

        painter = QPainter(circular)
        painter.setRenderHint(QPainter.Antialiasing)

        # Create circular clipping path
        clip_path = QPainterPath()
        clip_path.addEllipse(QRectF(0, 0, size, size))

        painter.setClipPath(clip_path)
        painter.drawPixmap(0, 0, pixmap)
        painter.end()

        return circular
    def create_shortcuts_section(self):
        """Create the shortcuts section (will be populated dynamically)"""
        frame = QFrame()
        layout = QVBoxLayout()
        layout.setSpacing(10)

        # Header
        header_layout = QHBoxLayout()
        title = QLabel("Your shortcuts")
        title.setStyleSheet("font-weight: bold; font-size: 16px;")
        see_all = QPushButton("See all")
        see_all.setStyleSheet("color: #6C5CE7; border: none; font-size: 12px;")

        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(see_all)
        layout.addLayout(header_layout)

        # Store reference for dynamic updates
        self.shortcuts_container = frame
        frame.setLayout(layout)
        return frame

    def create_share_section(self):
        """Create the share something section"""
        frame = QFrame()
        layout = QVBoxLayout()
        layout.setSpacing(15)

        title = QLabel("Share something.")
        title.setStyleSheet("font-weight: bold; font-size: 16px;")
        layout.addWidget(title)

        # Text input
        self.post_input = QTextEdit()
        self.post_input.setPlaceholderText("What's on your mind?")
        self.post_input.setMaximumHeight(100)
        self.post_input.setStyleSheet("""
            QTextEdit {
                border: 1px solid #ddd;
                border-radius: 10px;
                padding: 10px;
                font-size: 14px;
            }
        """)
        layout.addWidget(self.post_input)

        # Post button
        post_btn = QPushButton("Post")
        post_btn.setFixedHeight(40)
        post_btn.setStyleSheet("""
            QPushButton {
                background-color: #6C5CE7;
                color: white;
                border-radius: 10px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #5A4FD8;
            }
        """)
        post_btn.clicked.connect(self.handle_post_creation)
        layout.addWidget(post_btn)

        frame.setLayout(layout)
        return frame

    def handle_post_creation(self):
        """Logic to send post to backend"""
        content = self.post_input.toPlainText().strip()
        if not content:
            QMessageBox.warning(self, "Warning", "Post cannot be empty!")
            return

        success, message, post_id = self.main_window.app.create_post(content)

        if success:
            QMessageBox.information(self, "Success", "Post published!")
            self.post_input.clear()
            self.update_user_info()
            self.load_posts()
            self.update_activity_section()
        else:
            QMessageBox.warning(self, "Error", message)

    def create_center_feed(self):
        """Create the center feed with posts"""
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        container = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setAlignment(Qt.AlignTop)

        # Navigation
        nav_layout = QHBoxLayout()
        home_btn = QPushButton("Home")
        messages_btn = QPushButton("Messages")
        settings_btn = QPushButton("Settings")
        logout_btn = QPushButton("Switch account")

        self.nav_buttons = {
            "Home": home_btn,
            "Messages": messages_btn,
            "Settings": settings_btn,
            "Switch account": logout_btn
        }

        home_btn.clicked.connect(self.go_home)
        logout_btn.clicked.connect(self.logout)
        messages_btn.clicked.connect(self.go_to_message_page)
        settings_btn.clicked.connect(self.settings)

        for btn in self.nav_buttons.values():
            btn.setFixedHeight(40)
            btn.setStyleSheet("""
                QPushButton {
                    background: transparent;
                    color: #666;
                    border: none;
                    font-size: 14px;
                    padding: 0 15px;
                }
                QPushButton:hover {
                    color: #6C5CE7;
                }
            """)
            nav_layout.addWidget(btn)

        nav_layout.addStretch()
        layout.addLayout(nav_layout)

        # Feed Layout
        self.feed_layout = QVBoxLayout()
        self.feed_layout.setSpacing(20)
        layout.addLayout(self.feed_layout)

        layout.addStretch()
        container.setLayout(layout)
        scroll_area.setWidget(container)
        return scroll_area

    def load_posts(self):
        """Fetch real posts from backend and display them"""
        # Clear existing posts
        while self.feed_layout.count():
            child = self.feed_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        # Get Feed from Backend
        feed_data = self.main_window.app.get_feed(posts_per_page=50)
        posts = feed_data.get('posts', [])

        # Apply filter if active
        if self.current_filter:
            posts = self.filter_posts_by_category(posts, self.current_filter)

        if not posts:
            no_posts = QLabel(
                f"No posts found{' for ' + self.current_filter if self.current_filter else ''}. Follow users to see their posts!")
            no_posts.setAlignment(Qt.AlignCenter)
            no_posts.setStyleSheet("color: #999; margin-top: 20px; font-size: 16px;")
            self.feed_layout.addWidget(no_posts)

            # Add clear filter button if filter is active
            if self.current_filter:
                clear_btn = QPushButton("Clear Filter")
                clear_btn.setFixedSize(120, 35)
                clear_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #6C5CE7;
                        color: white;
                        border-radius: 8px;
                        font-weight: bold;
                    }
                    QPushButton:hover {
                        background-color: #5A4FD8;
                    }
                """)
                clear_btn.clicked.connect(self.clear_filter)

                btn_layout = QHBoxLayout()
                btn_layout.addStretch()
                btn_layout.addWidget(clear_btn)
                btn_layout.addStretch()
                self.feed_layout.addLayout(btn_layout)
            return

        # Show filter indicator if active
        if self.current_filter:
            filter_indicator = QFrame()
            filter_layout = QHBoxLayout()
            filter_layout.setContentsMargins(10, 10, 10, 10)

            filter_text = QLabel(f"🔍 Showing posts about: <b>{self.current_filter}</b>")
            filter_text.setStyleSheet("font-size: 14px; color: #6C5CE7;")
            filter_text.setTextFormat(Qt.RichText)

            clear_filter_btn = QPushButton("✕ Clear")
            clear_filter_btn.setFixedSize(70, 30)
            clear_filter_btn.setStyleSheet("""
                QPushButton {
                    background-color: #e74c3c;
                    color: white;
                    border-radius: 5px;
                    font-size: 12px;
                }
                QPushButton:hover {
                    background-color: #c0392b;
                }
            """)
            clear_filter_btn.clicked.connect(self.clear_filter)

            filter_layout.addWidget(filter_text)
            filter_layout.addStretch()
            filter_layout.addWidget(clear_filter_btn)

            filter_indicator.setLayout(filter_layout)
            filter_indicator.setStyleSheet("""
                QFrame {
                    background-color: #f0f0f0;
                    border-radius: 8px;
                    border: 1px solid #6C5CE7;
                }
            """)
            self.feed_layout.addWidget(filter_indicator)

        # Create widgets for each post
        for post_data in posts:
            widget = self.create_post_widget(post_data)
            self.feed_layout.addWidget(widget)

    def filter_posts_by_category(self, posts, interest):
        """Filter posts by matching category/interest"""
        filtered_posts = []

        # Normalize the interest to lowercase for case-insensitive matching
        interest_lower = interest.lower()

        for post in posts:
            # Check if post has categories
            categories = post.get('categories', [])

            # Handle different category formats
            if isinstance(categories, str):
                # If categories is a string, split by comma
                categories = [cat.strip() for cat in categories.split(',') if cat.strip()]

            # Convert all categories to lowercase for matching
            categories_lower = [cat.lower() for cat in categories]

            # Check if interest matches any category
            if interest_lower in categories_lower:
                filtered_posts.append(post)
                continue

            # Also check in post content for keyword matching
            content = post.get('content', '').lower()
            if interest_lower in content:
                filtered_posts.append(post)

        return filtered_posts

    def filter_feed_by_interest(self, interest):
        """Filter the feed to show only posts related to the selected interest"""
        self.current_filter = interest
        self.load_posts()

        # Show message
        QMessageBox.information(
            self,
            "Filter Applied",
            f"Now showing posts related to: {interest}\n\nClick the interest again or the 'Clear Filter' button to show all posts."
        )

    def clear_filter(self):
        """Clear the current filter and show all posts"""
        self.current_filter = None
        self.load_posts()
        QMessageBox.information(self, "Filter Cleared", "Showing all posts now.")

    def create_post_widget(self, post_data):
        """Create a post widget from DB data"""
        frame = QFrame()
        frame.setObjectName("PostCard")  # <--- THIS TRIGGERS THE STYLE FROM STYLES.PY

        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        author_name = post_data.get("author_name", "Unknown User")
        username = post_data.get("author_username", "@unknown")
        date_str = str(post_data.get("date", "Just now"))
        content = post_data.get("content", "")
        like_count = post_data.get("like_count", 0)
        dislike_count = post_data.get("dislike_count", 0)
        comment_count = post_data.get("comment_count", 0)
        post_id = post_data.get("post_id", 0)

        # Header
        header_layout = QHBoxLayout()

        user_layout = QVBoxLayout()
        user_name_lbl = QLabel(author_name)
        user_name_lbl.setObjectName("HeaderText")
        user_username_lbl = QLabel(username)
        user_username_lbl.setObjectName("SubText")
        user_layout.addWidget(user_name_lbl)
        user_layout.addWidget(user_username_lbl)

        header_layout.addLayout(user_layout)
        header_layout.addStretch()

        time_label = QLabel(date_str)
        time_label.setObjectName("SubText")
        header_layout.addWidget(time_label)

        menu_btn = QPushButton("⋮")
        menu_btn.setFixedSize(30, 30)
        menu_btn.setStyleSheet("background: transparent; color: #666; font-size: 20px; border: none;")
        header_layout.addWidget(menu_btn)

        layout.addLayout(header_layout)

        # Post text
        text_label = QLabel(content)
        text_label.setWordWrap(True)
        text_label.setObjectName("MainText") # Main Color
        layout.addWidget(text_label)

        # Actions
        actions_layout = QHBoxLayout()
        actions_layout.setSpacing(20)

        like_btn = QPushButton(f"❤️ {like_count} Like")
        dislike_btn = QPushButton(f"👎{dislike_count} dislike")
        comment_btn = QPushButton(f"💬 {comment_count}Comment")


        for btn in [like_btn, dislike_btn, comment_btn]:
            btn.setFixedHeight(35)
            btn.setObjectName("ActionButton") # <--- Triggers outlined style
            actions_layout.addWidget(btn)
        like_btn.clicked.connect(lambda: self.handle_action(post_data['post_id'], 'like'))
        dislike_btn.clicked.connect(lambda: self.handle_action(post_data['post_id'], 'dislike'))
        comment_btn.clicked.connect(lambda: self.handle_action(post_data['post_id'], 'comment'))

        actions_layout.addStretch()
        layout.addLayout(actions_layout)

        frame.setLayout(layout)
        return frame

    def handle_action(self, pid, action):
        if action == 'like':
            self.main_window.app.like_post(pid)
        elif action == 'dislike':
            self.main_window.app.dislike_post(pid)
        elif action == 'comment':
            t, ok = QInputDialog.getText(self, "Comment", "Text:")
            if ok and t: self.main_window.app.comment_on_post(pid, t)
        self.load_posts()
        self.update_activity_section()


    def create_right_sidebar(self):
        """Create the right sidebar"""
        sidebar = QFrame()
        sidebar.setFixedWidth(300)
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setAlignment(Qt.AlignTop)

        # Search Section
        search_section = self.create_search_section()
        layout.addWidget(search_section)

        # Activity Section
        activity_section = self.create_activity_section()
        layout.addWidget(activity_section)

        # Suggested Section
        suggested_section = self.create_suggested_section()
        layout.addWidget(suggested_section)

        layout.addStretch()
        sidebar.setLayout(layout)
        return sidebar

    def create_search_section(self):
        """Creates the search box in the sidebar"""
        frame = QFrame()
        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setAlignment(Qt.AlignTop)

        title = QLabel("Find People")
        title.setObjectName("HeaderText")
        layout.addWidget(title)

        # Search Input
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search username...")

        # Autocomplete on Typing
        self.search_input.textChanged.connect(self.update_search_suggestions)


        # Search on Enter key
        self.search_input.returnPressed.connect(self.perform_search)
        layout.addWidget(self.search_input)

        # Results List
        self.search_results_list = QListWidget()
        self.search_results_list.hide()
        self.search_results_list.setStyleSheet("""
            QListWidget { 
                border: 1px solid #ddd; 
                border-radius: 5px; 
            }
            QListWidget::item { 
                padding: 5px; 
            }
        """)

        self.search_results_list.itemClicked.connect(self.handle_search_click)
        layout.addWidget(self.search_results_list)

        frame.setLayout(layout)
        return frame

    def update_search_suggestions(self, text):
        """
        Triggered whenever the user types in the search box.
        Uses the Trie backend to fetch autocomplete suggestions.
        """
        text = text.strip()

        # If box is empty, hide the list
        if not text:
            self.search_results_list.clear()
            self.search_results_list.hide()
            return

        # 1. Get Suggestions from Trie (System -> db_manager -> Trie)
        # We assume self.main_window.app is your 'System' class instance
        suggestions = self.main_window.app.get_username_suggestions(text)

        self.search_results_list.clear()

        if suggestions:
            for username in suggestions:
                item = QListWidgetItem(username)
                # Store JUST the username string for now
                item.setData(Qt.UserRole, username)
                self.search_results_list.addItem(item)
            self.search_results_list.show()
        else:
            # Optional: Show "No matches" or just hide
            self.search_results_list.hide()

    def perform_search(self):
        """Search logic"""
        username = self.search_input.text().strip()
        if not username:
            self.search_results_list.hide()
            return

        # 1. Search in DB
        user = self.main_window.app.search_user_by_username(username)

        self.search_results_list.clear()
        if user:
            # Add item
            item = QListWidgetItem(f"{user['full_name']} (@{user['username']})")
            # Store full user data in the item
            item.setData(Qt.UserRole, user)
            self.search_results_list.addItem(item)
            self.search_results_list.show()
        else:
            # Show "Not Found"
            item = QListWidgetItem("User not found.")
            item.setFlags(Qt.NoItemFlags)  # Unclickable
            self.search_results_list.addItem(item)
            self.search_results_list.show()

    def handle_search_click(self, item):
        """When a search result is clicked"""
        data = item.data(Qt.UserRole)

        if not data:
            return

        user_data = None

        # Case A: Autocomplete gives a STRING (username)
        if isinstance(data, str):
            username = data
            # USE THE APP CONTROLLER instead of importing USER directly
            # This calls the method in socialmedia_app.py -> USER.get_by_username
            user_data = self.main_window.app.search_user_by_username(username)

        # Case B: Full Search gives a DICT
        elif isinstance(data, dict):
            user_data = data

        # Navigate
        if user_data:
            self.main_window.show_user_profile(user_data)
            self.search_input.clear()
            self.search_results_list.hide()

    def create_activity_section(self):
        """Create the activity section (will be populated dynamically)"""
        frame = QFrame()
        layout = QVBoxLayout()
        layout.setSpacing(15)

        # Header
        header_layout = QHBoxLayout()
        title = QLabel("Recent Activity")
        title.setStyleSheet("font-weight: bold; font-size: 18px;")
        refresh_btn = QPushButton("Refresh")
        refresh_btn.setStyleSheet("color: white; border: none; font-size: 12px;")
        refresh_btn.clicked.connect(self.update_activity_section)

        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(refresh_btn)
        layout.addLayout(header_layout)

        # Store reference
        self.activity_container = frame
        frame.setLayout(layout)
        return frame

    def create_suggested_section(self):
        """Create the suggested for you section (will be populated dynamically)"""
        frame = QFrame()
        layout = QVBoxLayout()
        layout.setSpacing(15)

        title = QLabel("Suggested For you")
        title.setStyleSheet("font-weight: bold; font-size: 18px;")
        layout.addWidget(title)

        # Store reference
        self.suggested_container = frame
        frame.setLayout(layout)
        return frame

    def handle_follow(self, user_id):
        """Handle following a user"""
        if user_id:
            success, message = self.main_window.app.follow_user(user_id)
            if success:
                QMessageBox.information(self, "Success", message)
                self.update_user_info()
                self.update_activity_section()
                self.update_suggested_section()
            else:
                QMessageBox.warning(self, "Error", message)

    # ================= IMAGE LOADER =================
    def load_image(self, filename, size):
        # Use the constant from utils instead of calculating base dir manually
        path = os.path.join(paths.IMAGE_DIR, filename)

        if not os.path.exists(path):
            print("❌ Image not found:", path)
            # Create a placeholder (it's good practice to fill it with a color or transparency)
            placeholder = QPixmap(size, size)
            placeholder.fill(Qt.lightGray)
            return placeholder

        pix = QPixmap(path)
        return pix.scaled(size, size, Qt.KeepAspectRatio, Qt.SmoothTransformation)

    # ================= NAVIGATION =================
    def go_home(self):
        self.set_active("Home")
        self.update_user_info()
        self.load_posts()
        self.update_activity_section()

    def logout(self):
        self.main_window.app.logout()
        self.main_window.go_to_login()

    def go_to_message_page(self):
        self.main_window.go_to_message_page()
    def settings(self):
        self.main_window.go_to_settings()

    def set_active(self, name):
        for btn_name, btn in self.nav_buttons.items():
            btn.setStyleSheet("""
                QPushButton {
                    background: transparent;
                    color: #666;
                    border: none;
                    font-size: 14px;
                    padding: 0 15px;
                }
                QPushButton:hover {
                    color: #6C5CE7;
                }
            """)
        if name in self.nav_buttons:
            self.nav_buttons[name].setStyleSheet("""
                QPushButton {
                    background: transparent;
                    color: #6C5CE7;
                    border: none;
                    font-size: 14px;
                    padding: 0 15px;
                    font-weight: bold;
                }
            """)

    # ================= THEME =================
    def apply_theme(self):
        """Apply theme based on main window's dark mode setting"""
        self.main_window.apply_theme()