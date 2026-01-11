from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QScrollArea, QFrame, QMessageBox, QInputDialog
)
from PySide6.QtCore import Qt


class UserProfilePage(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.current_profile_user = None
        self.is_following_user = False

        # UI References
        self.followers_val_lbl = None
        self.following_val_lbl = None
        self.follow_btn = None
        self.feed_layout = None

        self.build_ui()

    def build_ui(self):
        main_layout = QVBoxLayout()

        # Top Bar
        top_bar = QHBoxLayout()
        back_btn = QPushButton("← Back")
        back_btn.setFixedSize(80, 30)
        back_btn.setStyleSheet("""
            QPushButton { border: none; font-weight: bold; color: white; }
            QPushButton:hover { color: #6C5CE7; }
        """)
        back_btn.clicked.connect(self.go_back)
        top_bar.addWidget(back_btn)
        top_bar.addStretch()
        main_layout.addLayout(top_bar)

        # Content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.NoFrame)

        container = QWidget()
        self.content_layout = QVBoxLayout(container)
        self.content_layout.setSpacing(20)
        self.content_layout.setContentsMargins(20, 0, 20, 20)

        # Header
        self.header_frame = QFrame()
        self.header_frame.setStyleSheet("background: white; border-radius: 15px; border: 1px solid #ddd;")
        self.header_layout = QVBoxLayout(self.header_frame)
        self.header_layout.setContentsMargins(30, 30, 30, 30)
        self.content_layout.addWidget(self.header_frame)

        # Posts Title
        lbl = QLabel("User Posts")
        lbl.setStyleSheet("font-weight: bold; font-size: 18px; margin-top: 10px; color: #2c3e50;")
        self.content_layout.addWidget(lbl)

        # Feed
        self.feed_layout = QVBoxLayout()
        self.feed_layout.setSpacing(15)
        self.content_layout.addLayout(self.feed_layout)
        self.content_layout.addStretch()

        scroll.setWidget(container)
        main_layout.addWidget(scroll)
        self.setLayout(main_layout)

    def load_user(self, user_data):
        self.current_profile_user = user_data

        # 1. Fetch fresh Data
        user_id = user_data['user_id']
        fresh = self.main_window.app.search_user_by_id(user_id)
        if fresh: self.current_profile_user = fresh

        # 2. CHECK FOLLOW STATUS FROM BACKEND (Crucial Fix)
        self.is_following_user = self.main_window.app.is_following(user_id)

        self.refresh_profile()

    def refresh_profile(self):
        if not self.current_profile_user: return
        user = self.current_profile_user

        # Clear
        self.clear_layout(self.header_layout)
        self.clear_layout(self.feed_layout)

        # Name
        name_lbl = QLabel(user.get('full_name', 'Unknown'))
        name_lbl.setAlignment(Qt.AlignCenter)
        name_lbl.setStyleSheet("font-size: 26px; font-weight: bold; color: #2c3e50;")
        self.header_layout.addWidget(name_lbl)

        user_lbl = QLabel(f"@{user.get('username', 'unknown')}")
        user_lbl.setAlignment(Qt.AlignCenter)
        user_lbl.setStyleSheet("color: #7f8c8d; font-size: 16px; margin-bottom: 15px;")
        self.header_layout.addWidget(user_lbl)

        # Stats
        stats_box = QHBoxLayout()
        stats_box.addStretch()

        self.followers_val_lbl = QLabel(str(user.get('follower_count', 0)))
        self.followers_val_lbl.setStyleSheet("font-size:20px; font-weight:bold;")
        self.followers_val_lbl.setAlignment(Qt.AlignCenter)
        stats_box.addLayout(self.make_stat_box(self.followers_val_lbl, "Followers"))

        stats_box.addWidget(self.create_vertical_line())

        self.following_val_lbl = QLabel(str(user.get('following_count', 0)))
        self.following_val_lbl.setStyleSheet("font-size:20px; font-weight:bold;")
        self.following_val_lbl.setAlignment(Qt.AlignCenter)
        stats_box.addLayout(self.make_stat_box(self.following_val_lbl, "Following"))

        stats_box.addStretch()
        self.header_layout.addLayout(stats_box)

        # Follow Button
        curr = self.main_window.app.get_current_user()
        if curr and curr.get_id() != user['user_id']:
            self.follow_btn = QPushButton()
            self.follow_btn.setFixedSize(140, 40)
            self.follow_btn.clicked.connect(self.toggle_follow)
            self.update_follow_btn_visuals()

            box = QHBoxLayout()
            box.addStretch()
            box.addWidget(self.follow_btn)
            box.addStretch()
            self.header_layout.addLayout(box)

        # Posts
        posts = self.main_window.app.get_user_posts(user['user_id'])
        if not posts:
            self.feed_layout.addWidget(QLabel("No posts yet."))
        else:
            for p in posts:
                p['author_name'] = user.get('full_name')
                p['author_username'] = user.get('username')
                self.feed_layout.addWidget(self.create_profile_post_widget(p))

    def make_stat_box(self, val_lbl, title):
        b = QVBoxLayout()
        b.addWidget(val_lbl)
        l = QLabel(title)
        l.setStyleSheet("color:#7f8c8d; font-size:12px;")
        l.setAlignment(Qt.AlignCenter)
        b.addWidget(l)
        return b

    def toggle_follow(self):
        tid = self.current_profile_user['user_id']
        if self.is_following_user:
            success, msg = self.main_window.app.unfollow_user(tid)
            if success:
                self.is_following_user = False
                self.update_stats(False)
        else:
            success, msg = self.main_window.app.follow_user(tid)
            if success:
                self.is_following_user = True
                self.update_stats(True)
        self.update_follow_btn_visuals()

    def update_follow_btn_visuals(self):
        if self.is_following_user:
            self.follow_btn.setText("Unfollow")
            self.follow_btn.setStyleSheet("""
                QPushButton { background-color: #e74c3c; color: white; font-weight: bold; border-radius: 20px; }
                QPushButton:hover { background-color: #c0392b; }
            """)
        else:
            self.follow_btn.setText("Follow")
            self.follow_btn.setStyleSheet("""
                QPushButton { background-color: #6C5CE7; color: white; font-weight: bold; border-radius: 20px; }
                QPushButton:hover { background-color: #5A4FD8; }
            """)

    def update_stats(self, increment):
        try:
            val = int(self.followers_val_lbl.text())
            val = val + 1 if increment else max(0, val - 1)
            self.followers_val_lbl.setText(str(val))
        except:
            pass

    def create_profile_post_widget(self, post_data):
        frame = QFrame()
        frame.setStyleSheet("background: white; border-radius: 12px; border: 1px solid #ddd;")
        l = QVBoxLayout()
        l.setContentsMargins(20, 20, 20, 20)

        l.addWidget(QLabel(f"<b>{post_data.get('date')}</b>"))
        c = QLabel(post_data.get('content'))
        c.setWordWrap(True)
        l.addWidget(c)

        actions = QHBoxLayout()

        # Like
        lb = QPushButton(f"❤️ {post_data.get('like_count', 0)}")
        lb.clicked.connect(lambda: self.handle_action(post_data['post_id'], 'like'))

        # Dislike
        db = QPushButton(f"👎 {post_data.get('dislike_count', 0)}")
        db.clicked.connect(lambda: self.handle_action(post_data['post_id'], 'dislike'))

        # Comment
        cb = QPushButton(f"💬 {post_data.get('comment_count', 0)}")
        cb.clicked.connect(lambda: self.handle_action(post_data['post_id'], 'comment'))

        # HOVER STYLES ADDED HERE
        base_style = """
            QPushButton { border: 1px solid #ddd; border-radius: 5px; padding: 5px 15px; background: white; }
            QPushButton:hover { background-color: #f0f0f0; border-color: #6C5CE7; color: #6C5CE7; }
        """
        for btn in [lb, db, cb]:
            btn.setStyleSheet(base_style)
            actions.addWidget(btn)

        actions.addStretch()
        l.addLayout(actions)
        frame.setLayout(l)
        return frame

    def handle_action(self, pid, action):
        if action == 'like':
            self.main_window.app.like_post(pid)
        elif action == 'dislike':
            self.main_window.app.dislike_post(pid)
        elif action == 'comment':
            t, ok = QInputDialog.getText(self, "Comment", "Text:")
            if ok and t: self.main_window.app.comment_on_post(pid, t)

        self.load_user(self.current_profile_user)

    def create_vertical_line(self):
        l = QFrame()
        l.setFrameShape(QFrame.VLine)
        l.setFrameShadow(QFrame.Sunken)
        l.setFixedHeight(30)
        l.setStyleSheet("color: #ccc;")
        return l

    def clear_layout(self, layout):
        while layout.count():
            child = layout.takeAt(0)
            if child.widget(): child.widget().deleteLater()

    def go_back(self):
        self.main_window.go_to_home()