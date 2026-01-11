from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QScrollArea, QFrame, QMessageBox,
    QDialog, QLineEdit, QTextEdit, QFormLayout, QDialogButtonBox
)
from PySide6.QtGui import QPixmap, QIcon, QFont,QPainter, QPainterPath,QColor
from PySide6.QtCore import Qt,QRectF
import os

class EditProfileDialog(QDialog):
    """Dialog for editing user profile information"""

    def __init__(self, current_user, parent=None):
        super().__init__(parent)
        self.current_user = current_user
        self.setWindowTitle("Edit Profile")
        self.setModal(True)
        self.setMinimumWidth(400)

        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()

        # Form
        form_layout = QFormLayout()

        # Full Name
        self.full_name_input = QLineEdit()
        self.full_name_input.setText(self.current_user.get_fullname())
        form_layout.addRow("Full Name:", self.full_name_input)

        # Username (read-only)
        username_label = QLabel(f"@{self.current_user.get_username()}")
        username_label.setStyleSheet("color: #666;")
        form_layout.addRow("Username:", username_label)

        # Email
        self.email_input = QLineEdit()
        self.email_input.setText(self.current_user.get_email())
        form_layout.addRow("Email:", self.email_input)

        # Address
        self.address_input = QLineEdit()
        self.address_input.setText(self.current_user.get_address())
        form_layout.addRow("Address:", self.address_input)

        # Interests
        self.interests_input = QTextEdit()
        self.interests_input.setMaximumHeight(80)
        interests_text = ", ".join(self.current_user.get_interests())
        self.interests_input.setPlainText(interests_text)
        form_layout.addRow("Interests:", self.interests_input)

        layout.addLayout(form_layout)

        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.Save | QDialogButtonBox.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        self.setLayout(layout)

    def get_updated_data(self):
        """Return the updated user data"""
        interests_text = self.interests_input.toPlainText().strip()
        interests = [i.strip() for i in interests_text.split(',') if i.strip()]

        return {
            'full_name': self.full_name_input.text().strip(),
            'email': self.email_input.text().strip(),
            'address': self.address_input.text().strip(),
            'interests': interests
        }


class MyProfilePage(QWidget):
    """My Profile page - for viewing and editing current user's own profile"""

    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window

        # UI References
        self.name_lbl = None
        self.username_lbl = None
        self.email_lbl = None
        self.address_lbl = None
        self.interests_lbl = None
        self.posts_val_lbl = None
        self.followers_val_lbl = None
        self.following_val_lbl = None
        self.total_likes_lbl = None
        self.feed_layout = None

        self.build_ui()

    def showEvent(self, event):
        """Called when page is shown - refresh profile data"""
        self.refresh_profile()
        super().showEvent(event)

    def build_ui(self):
        main_layout = QVBoxLayout()

        # Top Bar
        top_bar = QHBoxLayout()
        back_btn = QPushButton("← Back")
        back_btn.setFixedSize(80, 30)
        back_btn.setStyleSheet("""
            QPushButton { 
                border: none; 
                font-weight: bold; 
                color: white; 
            }
            QPushButton:hover { 
                color: #6C5CE7; 
            }
        """)
        back_btn.clicked.connect(self.go_back)
        top_bar.addWidget(back_btn)
        top_bar.addStretch()

        # Title
        title = QLabel("My Profile")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: white;")
        top_bar.addWidget(title)
        top_bar.addStretch()

        main_layout.addLayout(top_bar)

        # Scrollable Content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.NoFrame)

        container = QWidget()
        self.content_layout = QVBoxLayout(container)
        self.content_layout.setSpacing(20)
        self.content_layout.setContentsMargins(20, 20, 20, 20)

        # Profile Header Card
        self.header_frame = QFrame()
        self.header_frame.setStyleSheet("""
            QFrame {
                background: white; 
                border-radius: 15px; 
                border: 1px solid #ddd;
            }
        """)
        self.header_layout = QVBoxLayout(self.header_frame)
        self.header_layout.setContentsMargins(30, 30, 30, 30)
        self.header_layout.setSpacing(15)
        self.content_layout.addWidget(self.header_frame)

        # Statistics Card
        self.stats_frame = QFrame()
        self.stats_frame.setStyleSheet("""
            QFrame {
                background: white; 
                border-radius: 15px; 
                border: 1px solid #ddd;
            }
        """)
        self.stats_layout = QVBoxLayout(self.stats_frame)
        self.stats_layout.setContentsMargins(30, 20, 30, 20)
        self.content_layout.addWidget(self.stats_frame)

        # Posts Section
        posts_title = QLabel("My Posts")
        posts_title.setStyleSheet("""
            font-weight: bold; 
            font-size: 18px; 
            margin-top: 10px; 
            color: #2c3e50;
        """)
        self.content_layout.addWidget(posts_title)

        # Feed Layout
        self.feed_layout = QVBoxLayout()
        self.feed_layout.setSpacing(15)
        self.content_layout.addLayout(self.feed_layout)

        self.content_layout.addStretch()

        scroll.setWidget(container)
        main_layout.addWidget(scroll)
        self.setLayout(main_layout)

    def refresh_profile(self):
        """Refresh all profile data from backend"""
        current_user = self.main_window.app.get_current_user()

        if not current_user:
            QMessageBox.warning(self, "Error", "No user logged in")
            self.go_back()
            return

        # Get fresh statistics
        stats = self.main_window.app.get_user_statistics()

        # Clear existing content
        self.clear_layout(self.header_layout)
        self.clear_layout(self.stats_layout)
        self.clear_layout(self.feed_layout)

        # Build Profile Header
        self.build_profile_header(current_user, stats)

        # Build Statistics Section
        self.build_statistics_section(stats)

        # Load Posts
        self.load_posts(current_user.get_id())

    def build_profile_header(self, user, stats):
        """Build the profile header section"""
        # Profile Picture Placeholder
        self.profile_pic_label = QLabel("👤")
        self.profile_pic_label.setAlignment(Qt.AlignCenter)
        self.profile_pic_label.setStyleSheet("""
            font-size: 60px; 
            background-color: #6C5CE7; 
            color: white; 
            border-radius: 50px; 
            min-width: 100px; 
            min-height: 100px; 
            max-width: 100px; 
            max-height: 100px;
        """)

        pic_layout = QHBoxLayout()
        pic_layout.addStretch()
        pic_layout.addWidget(self.profile_pic_label)
        pic_layout.addStretch()
        self.header_layout.addLayout(pic_layout)
        self.update_profile_pic()

        # Name
        self.name_lbl = QLabel(user.get_fullname())
        self.name_lbl.setAlignment(Qt.AlignCenter)
        self.name_lbl.setStyleSheet("""
            font-size: 26px; 
            font-weight: bold; 
            color: #2c3e50;
        """)
        self.header_layout.addWidget(self.name_lbl)

        # Username
        self.username_lbl = QLabel(f"@{user.get_username()}")
        self.username_lbl.setAlignment(Qt.AlignCenter)
        self.username_lbl.setStyleSheet("""
            color: #7f8c8d; 
            font-size: 16px;
        """)
        self.header_layout.addWidget(self.username_lbl)

        # Email
        self.email_lbl = QLabel(f"📧 {user.get_email()}")
        self.email_lbl.setAlignment(Qt.AlignCenter)
        self.email_lbl.setStyleSheet("color: #95a5a6; font-size: 14px;")
        self.header_layout.addWidget(self.email_lbl)

        # Address (if available)
        if user.get_address():
            self.address_lbl = QLabel(f"📍 {user.get_address()}")
            self.address_lbl.setAlignment(Qt.AlignCenter)
            self.address_lbl.setStyleSheet("color: #95a5a6; font-size: 14px;")
            self.header_layout.addWidget(self.address_lbl)

        # Interests
        if user.get_interests():
            interests_text = ", ".join(user.get_interests())
            self.interests_lbl = QLabel(f"💡 {interests_text}")
            self.interests_lbl.setAlignment(Qt.AlignCenter)
            self.interests_lbl.setWordWrap(True)
            self.interests_lbl.setStyleSheet("""
                color: #6C5CE7; 
                font-size: 14px; 
                margin-top: 10px;
            """)
            self.header_layout.addWidget(self.interests_lbl)

        # Stats Row
        stats_box = QHBoxLayout()
        stats_box.addStretch()

        # Posts
        self.posts_val_lbl = QLabel(str(stats.get('total_posts', 0)))
        self.posts_val_lbl.setStyleSheet("font-size: 24px; font-weight: bold; color: #2c3e50;")
        self.posts_val_lbl.setAlignment(Qt.AlignCenter)
        stats_box.addLayout(self.make_stat_box(self.posts_val_lbl, "Posts"))

        stats_box.addWidget(self.create_vertical_line())

        # Followers
        self.followers_val_lbl = QLabel(str(stats.get('followers', 0)))
        self.followers_val_lbl.setStyleSheet("font-size: 24px; font-weight: bold; color: #2c3e50;")
        self.followers_val_lbl.setAlignment(Qt.AlignCenter)
        stats_box.addLayout(self.make_stat_box(self.followers_val_lbl, "Followers"))

        stats_box.addWidget(self.create_vertical_line())

        # Following
        self.following_val_lbl = QLabel(str(stats.get('following', 0)))
        self.following_val_lbl.setStyleSheet("font-size: 24px; font-weight: bold; color: #2c3e50;")
        self.following_val_lbl.setAlignment(Qt.AlignCenter)
        stats_box.addLayout(self.make_stat_box(self.following_val_lbl, "Following"))

        stats_box.addStretch()
        self.header_layout.addLayout(stats_box)

        # Edit Profile Button
        edit_btn = QPushButton("✏️ Edit Profile")
        edit_btn.setFixedSize(160, 40)
        edit_btn.setStyleSheet("""
            QPushButton {
                background-color: #6C5CE7; 
                color: white; 
                font-weight: bold; 
                border-radius: 20px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #5A4FD8;
            }
        """)
        edit_btn.clicked.connect(self.edit_profile)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(edit_btn)
        btn_layout.addStretch()
        self.header_layout.addLayout(btn_layout)

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

        # Build path to user's profile image
        BASE_DIR = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "..")
        )
        IMAGE_DIR = os.path.join(BASE_DIR, "resources", "images")

        # Try multiple image formats
        possible_extensions = ['.png', '.jpg', '.jpeg', '.PNG', '.JPG', '.JPEG']
        img_path = None

        for ext in possible_extensions:
            test_path = os.path.join(IMAGE_DIR, f"{username}{ext}")
            if os.path.exists(test_path):
                img_path = test_path
                print(f"✅ Found profile image: {img_path}")
                break

        # If no user-specific image found, use default
        if not img_path:
            print(f"⚠️ No profile image found for {username}, using default")
            default_path = os.path.join(IMAGE_DIR, "profile.png")
            if os.path.exists(default_path):
                img_path = default_path
            else:
                # Create a placeholder
                placeholder = QPixmap(80, 80)
                placeholder.fill(QColor("#6C5CE7"))
                self.profile_pic_label.setPixmap(placeholder)
                return

        # Load and set the circular image
        circular_pixmap = self.load_circular_image(img_path, 80)
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

    def build_statistics_section(self, stats):
        """Build the detailed statistics section"""
        title = QLabel("📊 Activity Statistics")
        title.setStyleSheet("""
            font-size: 18px; 
            font-weight: bold; 
            color: #2c3e50; 
            margin-bottom: 15px;
        """)
        self.stats_layout.addWidget(title)

        # Stats Grid
        grid = QHBoxLayout()
        grid.setSpacing(30)

        # Total Likes
        likes_box = QVBoxLayout()
        likes_val = QLabel(str(stats.get('total_likes', 0)))
        likes_val.setStyleSheet("font-size: 28px; font-weight: bold; color: #e74c3c;")
        likes_val.setAlignment(Qt.AlignCenter)
        likes_label = QLabel("❤️ Total Likes")
        likes_label.setStyleSheet("color: #7f8c8d; font-size: 13px;")
        likes_label.setAlignment(Qt.AlignCenter)
        likes_box.addWidget(likes_val)
        likes_box.addWidget(likes_label)
        grid.addLayout(likes_box)

        # Total Dislikes
        dislikes_box = QVBoxLayout()
        dislikes_val = QLabel(str(stats.get('total_dislikes', 0)))
        dislikes_val.setStyleSheet("font-size: 28px; font-weight: bold; color: #95a5a6;")
        dislikes_val.setAlignment(Qt.AlignCenter)
        dislikes_label = QLabel("👎 Total Dislikes")
        dislikes_label.setStyleSheet("color: #7f8c8d; font-size: 13px;")
        dislikes_label.setAlignment(Qt.AlignCenter)
        dislikes_box.addWidget(dislikes_val)
        dislikes_box.addWidget(dislikes_label)
        grid.addLayout(dislikes_box)

        # Total Comments
        comments_box = QVBoxLayout()
        comments_val = QLabel(str(stats.get('total_comments', 0)))
        comments_val.setStyleSheet("font-size: 28px; font-weight: bold; color: #3498db;")
        comments_val.setAlignment(Qt.AlignCenter)
        comments_label = QLabel("💬 Total Comments")
        comments_label.setStyleSheet("color: #7f8c8d; font-size: 13px;")
        comments_label.setAlignment(Qt.AlignCenter)
        comments_box.addWidget(comments_val)
        comments_box.addWidget(comments_label)
        grid.addLayout(comments_box)

        self.stats_layout.addLayout(grid)

    def make_stat_box(self, val_lbl, title):
        """Create a stat box layout"""
        box = QVBoxLayout()
        box.addWidget(val_lbl)
        label = QLabel(title)
        label.setStyleSheet("color: #7f8c8d; font-size: 13px;")
        label.setAlignment(Qt.AlignCenter)
        box.addWidget(label)
        return box

    def create_vertical_line(self):
        """Create a vertical separator line"""
        line = QFrame()
        line.setFrameShape(QFrame.VLine)
        line.setFrameShadow(QFrame.Sunken)
        line.setFixedHeight(40)
        line.setStyleSheet("color: #ddd;")
        return line

    def load_posts(self, user_id):
        """Load and display user's posts"""
        posts = self.main_window.app.get_user_posts(user_id)

        if not posts:
            no_posts = QLabel("📝 No posts yet. Share your first post!")
            no_posts.setAlignment(Qt.AlignCenter)
            no_posts.setStyleSheet("""
                color: #95a5a6; 
                font-size: 16px; 
                padding: 40px;
            """)
            self.feed_layout.addWidget(no_posts)
            return

        # Add each post
        for post in posts:
            current_user = self.main_window.app.get_current_user()
            post['author_name'] = current_user.get_fullname()
            post['author_username'] = current_user.get_username()
            widget = self.create_post_widget(post)
            self.feed_layout.addWidget(widget)

    def create_post_widget(self, post_data):
        """Create a post widget"""
        frame = QFrame()
        frame.setStyleSheet("""
            QFrame {
                background: white; 
                border-radius: 12px; 
                border: 1px solid #ddd;
            }
        """)

        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        # Header with date
        header = QHBoxLayout()
        date_label = QLabel(f"📅 {post_data.get('date', 'Unknown date')}")
        date_label.setStyleSheet("color: #95a5a6; font-size: 12px;")
        header.addWidget(date_label)
        header.addStretch()

        # Delete button
        delete_btn = QPushButton("🗑️ Delete")
        delete_btn.setFixedSize(80, 25)
        delete_btn.setStyleSheet("""
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
        delete_btn.clicked.connect(
            lambda: self.handle_delete_post(post_data['post_id'])
        )
        header.addWidget(delete_btn)

        layout.addLayout(header)

        # Content
        content_label = QLabel(post_data.get('content', ''))
        content_label.setWordWrap(True)
        content_label.setStyleSheet("""
            font-size: 15px; 
            line-height: 1.6; 
            color: #2c3e50;
            padding: 10px 0;
        """)
        layout.addWidget(content_label)

        # Categories (if any)
        if post_data.get('categories'):
            categories = post_data['categories']
            if isinstance(categories, list) and categories:
                cat_text = " ".join([f"#{cat}" for cat in categories])
                cat_label = QLabel(cat_text)
                cat_label.setStyleSheet("color: #6C5CE7; font-size: 13px;")
                layout.addWidget(cat_label)

        # Actions
        actions_layout = QHBoxLayout()

        like_btn = QPushButton(f"❤️ {post_data.get('like_count', 0)}")
        dislike_btn = QPushButton(f"👎 {post_data.get('dislike_count', 0)}")
        comment_btn = QPushButton(f"💬 {post_data.get('comment_count', 0)}")

        action_style = """
            QPushButton {
                border: 1px solid #ddd;
                border-radius: 5px;
                padding: 5px 15px;
                background: white;
                color: #7f8c8d;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #f0f0f0;
                border-color: #6C5CE7;
                color: #6C5CE7;
            }
        """

        for btn in [like_btn, dislike_btn, comment_btn]:
            btn.setStyleSheet(action_style)
            actions_layout.addWidget(btn)

        actions_layout.addStretch()
        layout.addLayout(actions_layout)

        frame.setLayout(layout)
        return frame

    def handle_delete_post(self, post_id):
        """Handle post deletion"""
        reply = QMessageBox.question(
            self,
            "Delete Post",
            "Are you sure you want to delete this post?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            success, message = self.main_window.app.delete_post(post_id)
            if success:
                QMessageBox.information(self, "Success", "Post deleted successfully")
                self.refresh_profile()
            else:
                QMessageBox.warning(self, "Error", message)

    def edit_profile(self):
        """Open edit profile dialog"""
        current_user = self.main_window.app.get_current_user()
        if not current_user:
            return

        dialog = EditProfileDialog(current_user, self)

        if dialog.exec() == QDialog.Accepted:
            updated_data = dialog.get_updated_data()
            success, message = self.main_window.app.update_user_profile(updated_data)

            if success:
                QMessageBox.information(self, "Success", message)
                self.refresh_profile()
            else:
                QMessageBox.warning(self, "Error", message)

    def clear_layout(self, layout):
        """Clear all widgets from a layout"""
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def go_back(self):
        """Go back to home page"""
        self.main_window.go_to_home()