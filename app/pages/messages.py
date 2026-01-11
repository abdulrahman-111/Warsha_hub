from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QScrollArea, QFrame, QListWidget, QListWidgetItem,
    QTextEdit, QStackedWidget, QMessageBox
)
from PySide6.QtGui import QPixmap, QPainter, QPainterPath, QColor, QIcon, QFont, QLinearGradient, QBrush
from PySide6.QtCore import Qt, QRectF, QTimer
import os
from datetime import datetime
from app.utils import paths


class MessagingPage(QWidget):
    """Complete messaging interface with conversation list and chat view"""

    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window

        # State management
        self.current_conversation_user = None
        self.conversations = []

        self.build_ui()

    def showEvent(self, event):
        """Refresh conversations when page is shown"""
        self.load_conversations()
        super().showEvent(event)

    def build_ui(self):
        """Build the main messaging interface"""
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        # Left side - Conversation list
        conversations_panel = self.create_conversations_panel()
        main_layout.addWidget(conversations_panel, 2)

        # Right side - Chat view
        chat_panel = self.create_chat_panel()
        main_layout.addWidget(chat_panel, 3)

        self.setLayout(main_layout)

    # ================= CONVERSATIONS PANEL =================
    def create_conversations_panel(self):
        """Create the left panel with conversation list"""
        panel = QFrame()
        panel.setObjectName("ConversationPanel")  # <--- Linked to styles.py

        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # Header
        header = self.create_conversations_header()
        layout.addLayout(header)

        # Search bar
        search_container = self.create_search_bar()
        layout.addWidget(search_container)

        # Active users carousel
        active_users = self.create_active_users_section()
        layout.addWidget(active_users)

        # Conversations title
        conv_title = QLabel("CONVERSATIONS")
        # Keep simple inline style for text opacity
        conv_title.setStyleSheet("font-weight: bold; font-size: 12px; opacity: 0.7; border: none;")
        layout.addWidget(conv_title)

        # Conversations list scroll area
        self.conversations_scroll = QScrollArea()
        self.conversations_scroll.setWidgetResizable(True)
        self.conversations_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.conversations_scroll.setStyleSheet("background: transparent; border: none;")

        self.conversations_container = QWidget()
        self.conversations_container.setStyleSheet("background: transparent;")

        self.conversations_layout = QVBoxLayout(self.conversations_container)
        self.conversations_layout.setSpacing(8)
        self.conversations_layout.setAlignment(Qt.AlignTop)
        self.conversations_layout.setContentsMargins(2, 2, 2, 2)

        self.conversations_scroll.setWidget(self.conversations_container)
        layout.addWidget(self.conversations_scroll)

        # Bottom navigation
        bottom_nav = self.create_bottom_nav()
        layout.addLayout(bottom_nav)

        panel.setLayout(layout)
        return panel

    def create_search_bar(self):
        """Create search bar for conversations"""
        container = QFrame()
        container.setFixedHeight(45)
        container.setStyleSheet("""
            QFrame {
                background: rgba(255, 255, 255, 0.15);
                border-radius: 22px;
                border: 1px solid rgba(255, 255, 255, 0.2);
            }
            QFrame:hover {
                background: rgba(255, 255, 255, 0.2);
                border: 1px solid rgba(255, 255, 255, 0.3);
            }
        """)

        layout = QHBoxLayout(container)
        layout.setContentsMargins(15, 0, 15, 0)
        layout.setSpacing(10)

        # Search icon
        search_icon = QLabel("🔍")
        search_icon.setStyleSheet("""
            QLabel {
                color: rgba(255, 255, 255, 0.7);
                font-size: 16px;
            }
        """)

        # Search input
        search_input = QLineEdit()
        search_input.setPlaceholderText("Search conversations...")
        search_input.setStyleSheet("""
            QLineEdit {
                background: transparent;
                border: none;
                color: white;
                font-size: 13px;
                selection-background-color: rgba(255, 255, 255, 0.3);
            }
            QLineEdit::placeholder {
                color: rgba(255, 255, 255, 0.5);
                font-style: italic;
            }
        """)

        layout.addWidget(search_icon)
        layout.addWidget(search_input, 1)

        return container

    def create_conversations_header(self):
        """Create header with menu and profile"""
        header = QHBoxLayout()

        # Menu button
        menu_btn = QPushButton("🏠")
        menu_btn.setFixedSize(45, 45)
        menu_btn.clicked.connect(self.go_to_home)
        menu_btn.setCursor(Qt.PointingHandCursor)
        menu_btn.setStyleSheet("""
            QPushButton {
                background: rgba(255, 255, 255, 0.15);
                color: white;
                font-size: 22px;
                border: none;
                border-radius: 22px;
            }
            QPushButton:hover {
                background: rgba(255, 255, 255, 0.25);
            }
            QPushButton:pressed {
                background: rgba(255, 255, 255, 0.35);
            }
        """)

        # Title
        title = QLabel("MESSAGES")
        title.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 18px;
                font-weight: 800;
                letter-spacing: 2px;
                text-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
            }
        """)

        # Profile pic
        current_user = self.main_window.app.get_current_user()
        profile_btn = QPushButton()
        profile_btn.setFixedSize(45, 45)
        profile_btn.setCursor(Qt.PointingHandCursor)

        if current_user:
            img_path = self.get_user_image_path(current_user.get_username())
            profile_btn.setIcon(QIcon(self.load_circular_image(img_path, 45)))
            profile_btn.setIconSize(profile_btn.size())

        profile_btn.setStyleSheet("""
            QPushButton {
                background: white;
                border-radius: 22px;
                border: 2px solid white;
                box-shadow: 0 3px 8px rgba(0, 0, 0, 0.2);
            }
            QPushButton:hover {
                border: 2px solid rgba(255, 255, 255, 0.8);
                box-shadow: 0 4px 10px rgba(0, 0, 0, 0.3);
            }
        """)
        profile_btn.clicked.connect(self.main_window.go_to_my_profile)

        header.addWidget(menu_btn)
        header.addStretch()
        header.addWidget(title)
        header.addStretch()
        header.addWidget(profile_btn)

        return header

    def create_active_users_section(self):
        """Create horizontal scrolling list of active/following users"""
        scroll = QScrollArea()
        scroll.setFixedHeight(85)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setStyleSheet("QScrollArea { background: transparent; border: none; }")

        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setSpacing(12)
        layout.setContentsMargins(5, 5, 5, 5)

        # Get following list
        following = self.main_window.app.get_following()

        for username in following[:10]:  # Show first 10
            user_data = self.main_window.app.search_user_by_username(username)
            if user_data:
                user_btn = self.create_active_user_widget(user_data)
                layout.addWidget(user_btn)

        layout.addStretch()
        scroll.setWidget(container)
        return scroll

    def create_active_user_widget(self, user_data):
        """Create a circular user button for active users"""
        btn = QPushButton()
        btn.setFixedSize(65, 65)
        btn.setCursor(Qt.PointingHandCursor)

        img_path = self.get_user_image_path(user_data['username'])
        pixmap = self.load_circular_image(img_path, 65)

        btn.setIcon(QIcon(pixmap))
        btn.setIconSize(btn.size())
        btn.setStyleSheet("""
            QPushButton {
                background: white;
                border-radius: 32px;
                border: 3px solid rgba(255, 255, 255, 0.6);
                box-shadow: 0 3px 6px rgba(0, 0, 0, 0.15);
            }
            QPushButton:hover {
                border: 3px solid white;
                box-shadow: 0 5px 12px rgba(0, 0, 0, 0.25);
                transform: translateY(-2px);
            }
        """)

        btn.clicked.connect(lambda: self.open_conversation(user_data))
        btn.setToolTip(f"{user_data['full_name']}\n@{user_data['username']}")

        return btn

    def create_bottom_nav(self):
        """Create bottom navigation buttons"""
        nav = QHBoxLayout()
        nav.setSpacing(15)

        nav_items = [
            ("💬", "Chats"),
            ("👤", "Friends"),
            ("⚙", "Settings")
        ]

        for icon, tooltip in nav_items:
            btn = QPushButton(icon)
            btn.setFixedSize(45, 45)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setToolTip(tooltip)
            btn.setStyleSheet("""
                QPushButton {
                    background: rgba(255, 255, 255, 0.15);
                    color: white;
                    font-size: 18px;
                    border: none;
                    border-radius: 22px;
                }
                QPushButton:hover {
                    background: rgba(255, 255, 255, 0.25);
                }
                QPushButton:pressed {
                    background: rgba(255, 255, 255, 0.35);
                }
            """)

            if tooltip == "Settings":
                btn.clicked.connect(self.go_to_settings)
            nav.addWidget(btn)

        nav.addStretch()
        return nav

    def load_conversations(self):
        """Load all conversations for current user"""
        current_user = self.main_window.app.get_current_user()
        if not current_user:
            return

        # Clear existing conversations
        while self.conversations_layout.count():
            item = self.conversations_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Get users with existing conversations
        conversations = self.main_window.app.get_user_conversations()
        conversation_user_ids = [conv['user_data']['user_id'] for conv in conversations]

        # Add users with messages
        for conv in conversations:
            user_data = conv['user_data']
            conv_widget = self.create_conversation_item(user_data, conv.get('last_date'))
            self.conversations_layout.addWidget(conv_widget)

        # Also add following users (even without messages)
        following = self.main_window.app.get_following()
        for username in following:
            user_data = self.main_window.app.search_user_by_username(username)
            if user_data:
                # Only add if not already in conversations
                if user_data['user_id'] not in conversation_user_ids:
                    conv_widget = self.create_conversation_item(user_data, None)
                    self.conversations_layout.addWidget(conv_widget)

        # Show message if no one to chat with
        if not conversations and not following:
            no_conv = QLabel("No friends to chat with. Follow users to start messaging!")
            no_conv.setStyleSheet("""
                color: rgba(255, 255, 255, 0.7); 
                font-size: 13px; 
                padding: 30px; 
                font-style: italic;
                text-align: center;
                border: 2px dashed rgba(255, 255, 255, 0.2);
                border-radius: 15px;
                margin: 10px;
            """)
            no_conv.setWordWrap(True)
            no_conv.setAlignment(Qt.AlignCenter)
            self.conversations_layout.addWidget(no_conv)

    def create_conversation_item(self, user_data, last_date=None):
        """Create a single conversation list item"""
        item = QFrame()
        item.setFixedHeight(85)
        item.setCursor(Qt.PointingHandCursor)
        item.setObjectName("ConversationItem")

        layout = QHBoxLayout()
        layout.setContentsMargins(15, 12, 15, 12)
        layout.setSpacing(15)

        # Profile picture
        profile_pic = QLabel()
        img_path = self.get_user_image_path(user_data['username'])
        profile_pic.setPixmap(self.load_circular_image(img_path, 50))
        profile_pic.setFixedSize(50, 50)
        profile_pic.setStyleSheet("background: transparent; border: none;")

        # User info
        info_layout = QVBoxLayout()
        info_layout.setSpacing(4)

        name_label = QLabel(user_data['full_name'])
        name_label.setStyleSheet("font-weight: 600; font-size: 14px; background: transparent; border: none;")

        # Username label
        username_label = QLabel(f"@{user_data['username']}")
        username_label.setStyleSheet("font-size: 11px; background: transparent; border: none; opacity: 0.7;")

        status_text = "Click to chat"
        if last_date:
            try:
                last_msg_time = datetime.strptime(last_date, "%Y-%m-%d %H:%M:%S")
                status_text = f"Last: {last_msg_time.strftime('%b %d')}"
            except:
                status_text = "Click to chat"

        last_msg = QLabel(status_text)
        last_msg.setStyleSheet("""
            QLabel {
                color: rgba(255, 255, 255, 0.6);
                font-size: 11px;
                background: transparent;
                font-style: italic;
            }
        """)

        info_layout.addWidget(name_label)
        info_layout.addWidget(username_label)
        info_layout.addWidget(last_msg)

        layout.addWidget(profile_pic)
        layout.addLayout(info_layout, 1)

        item.setLayout(layout)
        item.mousePressEvent = lambda e: self.open_conversation(user_data)

        return item

    # ================= CHAT PANEL =================
    def create_chat_panel(self):
        """Create the right panel with chat interface"""
        panel = QFrame()
        panel.setObjectName("ChatPanel")

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Chat header
        self.chat_header_container = QWidget()
        self.chat_header_container.setObjectName("ChatHeader")
        self.chat_header_container.setFixedHeight(100)

        self.chat_header_layout = QVBoxLayout(self.chat_header_container)
        self.chat_header_layout.setContentsMargins(25, 20, 25, 20)
        layout.addWidget(self.chat_header_container)

        # Messages area
        self.messages_scroll = QScrollArea()
        self.messages_scroll.setWidgetResizable(True)
        self.messages_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.messages_scroll.setStyleSheet("background: transparent; border: none;")

        self.messages_container = QWidget()
        self.messages_container.setStyleSheet("background: transparent;")

        self.messages_layout = QVBoxLayout(self.messages_container)
        self.messages_layout.setSpacing(12)
        self.messages_layout.setAlignment(Qt.AlignTop)
        self.messages_layout.setContentsMargins(25, 20, 25, 20)

        self.messages_scroll.setWidget(self.messages_container)
        layout.addWidget(self.messages_scroll, 1)

        # Message input
        input_section = self.create_message_input()
        layout.addWidget(input_section)

        panel.setLayout(layout)

        # Show initial state
        self.show_no_conversation_state()

        return panel

    def create_chat_header(self, user_data):
        """Create chat header with user info"""
        # Clear existing header
        self.clear_layout(self.chat_header_layout)

        header = QHBoxLayout()
        header.setSpacing(15)

        # Back button
        back_btn = QPushButton("←")
        back_btn.setFixedSize(45, 45)
        back_btn.setCursor(Qt.PointingHandCursor)
        back_btn.setStyleSheet("""
            QPushButton {
                background: rgba(91, 141, 238, 0.1);
                color: #5B8DEE;
                font-size: 22px;
                font-weight: bold;
                border-radius: 22px;
                border: 1px solid rgba(91, 141, 238, 0.2);
            }
            QPushButton:hover {
                background: rgba(91, 141, 238, 0.2);
                border: 1px solid rgba(91, 141, 238, 0.4);
            }
            QPushButton:pressed {
                background: rgba(91, 141, 238, 0.3);
            }
        """)
        back_btn.clicked.connect(self.show_no_conversation_state)

        # Profile pic with gradient border
        profile_container = QFrame()
        profile_container.setFixedSize(50, 50)

        profile_pic = QLabel()
        img_path = self.get_user_image_path(user_data['username'])
        profile_pic.setPixmap(self.load_circular_image(img_path, 46))
        profile_pic.setGeometry(2, 2, 46, 46)
        profile_container.setLayout(QVBoxLayout())
        profile_container.layout().addWidget(profile_pic)

        profile_container.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #5B8DEE, stop:1 #4A7DDD);
                border-radius: 25px;
            }
        """)

        # User info
        info_layout = QVBoxLayout()
        info_layout.setSpacing(2)

        name_label = QLabel(user_data['full_name'])
        name_label.setObjectName("HeaderText")
        name_label.setStyleSheet("""
            font-size: 18px;
            letter-spacing: 0.2px;
            background: transparent;
            border: none;
        """)

        # Status with online indicator
        status_layout = QHBoxLayout()
        status_layout.setSpacing(6)

        online_dot = QLabel("●")
        online_dot.setStyleSheet("""
            QLabel {
                color: #4CAF50;
                font-size: 10px;
            }
        """)

        status_label = QLabel("Online")
        status_label.setObjectName("SubText")
        status_label.setStyleSheet("""
            font-size: 12px;
            font-weight: 500;
            background: transparent;
            border: none;
        """)

        status_layout.addWidget(online_dot)
        status_layout.addWidget(status_label)
        status_layout.addStretch()

        info_layout.addWidget(name_label)
        info_layout.addLayout(status_layout)

        # Action buttons
        action_layout = QHBoxLayout()
        action_layout.setSpacing(8)

        buttons = [
            ("📞", "#4CAF50"),
            ("📹", "#FF6B6B"),
            ("⋮", "#718096")
        ]

        for icon, color in buttons:
            btn = QPushButton(icon)
            btn.setFixedSize(42, 42)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background: rgba({color.replace('#', '')}, 0.1);
                    color: {color};
                    font-size: 16px;
                    border-radius: 21px;
                    border: 1px solid rgba({color.replace('#', '')}, 0.2);
                }}
                QPushButton:hover {{
                    background: rgba({color.replace('#', '')}, 0.2);
                    border: 1px solid rgba({color.replace('#', '')}, 0.4);
                }}
            """)
            action_layout.addWidget(btn)

        header.addWidget(back_btn)
        header.addWidget(profile_container)
        header.addLayout(info_layout, 1)
        header.addLayout(action_layout)

        self.chat_header_container.setVisible(True)
        self.chat_header_container.setFixedHeight(100)

        self.chat_header_layout.addLayout(header)

    def create_message_input(self):
        """Create message input area"""
        container = QWidget()
        container.setFixedHeight(90)
        container.setObjectName("MessageInputContainer")

        layout = QHBoxLayout()
        layout.setContentsMargins(25, 20, 25, 20)
        layout.setSpacing(12)

        # Attachment button
        attach_btn = QPushButton("📎")
        attach_btn.setFixedSize(45, 45)
        attach_btn.setCursor(Qt.PointingHandCursor)
        attach_btn.setStyleSheet("background: transparent; border: none; font-size: 18px;")

        # Emoji button
        emoji_btn = QPushButton("😊")
        emoji_btn.setFixedSize(45, 45)
        emoji_btn.setCursor(Qt.PointingHandCursor)
        emoji_btn.setStyleSheet(attach_btn.styleSheet())

        # Message input
        self.message_input = QLineEdit()
        self.message_input.setPlaceholderText("Type your message...")
        self.message_input.setFixedHeight(50)
        self.message_input.setStyleSheet("border-radius: 25px; padding-left: 20px;")
        self.message_input.returnPressed.connect(self.send_message)

        # Send button
        self.send_btn = QPushButton("➤")
        self.send_btn.setFixedSize(52, 52)
        self.send_btn.setCursor(Qt.PointingHandCursor)
        self.send_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #5B8DEE, stop:1 #4A7DDD);
                color: white;
                font-size: 22px;
                font-weight: bold;
                border-radius: 26px;
                border: none;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #4A7DDD, stop:1 #5B8DEE);
                box-shadow: 0 3px 10px rgba(91, 141, 238, 0.3);
            }
            QPushButton:pressed {
                padding-top: 2px;
            }
        """)
        self.send_btn.clicked.connect(self.send_message)

        layout.addWidget(attach_btn)
        layout.addWidget(emoji_btn)
        layout.addWidget(self.message_input, 1)
        layout.addWidget(self.send_btn)

        container.setLayout(layout)
        return container

    def show_no_conversation_state(self):
        """Show empty state when no conversation is selected"""
        self.current_conversation_user = None

        # Clear header
        while self.chat_header_layout.count():
            item = self.chat_header_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        self.chat_header_container.setStyleSheet("QWidget { background: transparent; }")
        self.chat_header_container.setFixedHeight(0)

        # Clear messages
        while self.messages_layout.count():
            item = self.messages_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Show empty state
        empty_container = QWidget()
        empty_container.setStyleSheet("background: transparent;")

        layout = QVBoxLayout(empty_container)
        layout.setSpacing(20)
        layout.setContentsMargins(0, 100, 0, 100)

        icon = QLabel("💬")
        icon.setStyleSheet("""
            QLabel {
                font-size: 60px;
                color: #CBD5E0;
                opacity: 0.7;
            }
        """)
        icon.setAlignment(Qt.AlignCenter)

        message = QLabel("Select a conversation to start messaging")
        message.setStyleSheet("""
            QLabel {
                color: #718096;
                font-size: 16px;
                font-weight: 600;
                text-align: center;
            }
        """)
        message.setAlignment(Qt.AlignCenter)

        sub_message = QLabel("Choose from your conversations on the left")
        sub_message.setStyleSheet("""
            QLabel {
                color: #A0AEC0;
                font-size: 13px;
                text-align: center;
            }
        """)
        sub_message.setAlignment(Qt.AlignCenter)

        layout.addWidget(icon)
        layout.addWidget(message)
        layout.addWidget(sub_message)

        self.messages_layout.addWidget(empty_container)

    def open_conversation(self, user_data):
        """Open a conversation with a user"""
        self.current_conversation_user = user_data

        # Update header
        self.create_chat_header(user_data)

        # Load messages
        self.load_messages(user_data['user_id'])

    def load_messages(self, other_user_id):
        """Load messages between current user and another user"""
        # Clear existing messages
        while self.messages_layout.count():
            item = self.messages_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        current_user = self.main_window.app.get_current_user()
        if not current_user:
            return

        # Get messages from database (already sorted by date)
        messages = self.main_window.app.get_chat(other_user_id)

        if not messages:
            # Show welcome message
            welcome_container = QWidget()
            welcome_container.setStyleSheet("""
                QWidget {
                    background: rgba(91, 141, 238, 0.05);
                    border-radius: 15px;
                    border: 1px dashed rgba(91, 141, 238, 0.3);
                    margin: 20px;
                }
            """)

            welcome_layout = QVBoxLayout(welcome_container)
            welcome_layout.setSpacing(5)
            welcome_layout.setContentsMargins(30, 20, 30, 20)

            welcome_msg = QLabel(f"Start your conversation with {self.current_conversation_user['full_name']}!")
            welcome_msg.setAlignment(Qt.AlignCenter)
            welcome_msg.setStyleSheet("""
                QLabel {
                    color: #5B8DEE;
                    font-size: 15px;
                    font-weight: 600;
                }
            """)
            welcome_msg.setWordWrap(True)

            tip_msg = QLabel("Send a message to begin chatting!")
            tip_msg.setAlignment(Qt.AlignCenter)
            tip_msg.setStyleSheet("""
                QLabel {
                    color: #718096;
                    font-size: 12px;
                    font-style: italic;
                }
            """)

            welcome_layout.addWidget(welcome_msg)
            welcome_layout.addWidget(tip_msg)

            self.messages_layout.addWidget(welcome_container)
            return

        # Display all messages (already sorted from database)
        for msg in messages:
            # Just display, no date parsing needed
            bubble = self.create_message_bubble(
                msg['content'],
                msg['is_sent'],
                msg['date']  # Pass date string directly
            )
            self.messages_layout.addWidget(bubble)

        # Scroll to bottom
        QTimer.singleShot(100, lambda: self.messages_scroll.verticalScrollBar().setValue(
            self.messages_scroll.verticalScrollBar().maximum()
        ))

    def create_message_bubble(self, text, is_sent, date_str):
        """Create a message bubble widget"""
        bubble_container = QWidget()
        container_layout = QHBoxLayout(bubble_container)
        container_layout.setContentsMargins(0, 0, 0, 0)

        if is_sent:
            container_layout.addStretch()

        bubble = QFrame()
        bubble.setMaximumWidth(380)

        # ASSIGN ID BASED ON SENDER
        if is_sent:
            bubble.setObjectName("ChatBubbleSent")
        else:
            bubble.setObjectName("ChatBubbleReceived")

        bubble_layout = QVBoxLayout(bubble)
        bubble_layout.setSpacing(5)
        bubble_layout.setContentsMargins(15, 12, 15, 8)

        # Message text
        msg_label = QLabel(text)
        msg_label.setWordWrap(True)
        msg_label.setStyleSheet("background: transparent; border: none; font-size: 14px;")

        # Format timestamp
        if isinstance(date_str, str) and date_str:
            try:
                timestamp = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
                time_text = timestamp.strftime("%I:%M %p")
            except:
                time_text = "Now"
        elif isinstance(date_str, datetime):
            time_text = date_str.strftime("%I:%M %p")
        else:
            time_text = "Now"

        # Timestamp
        time_label = QLabel(time_text)
        time_label.setStyleSheet("background: transparent; border: none; font-size: 11px; opacity: 0.7;")
        time_label.setAlignment(Qt.AlignRight if is_sent else Qt.AlignLeft)

        bubble_layout.addWidget(msg_label)
        bubble_layout.addWidget(time_label)

        container_layout.addWidget(bubble)

        if not is_sent:
            container_layout.addStretch()

        return bubble_container

    def send_message(self):
        """Send a message to current conversation"""
        if not self.current_conversation_user:
            QMessageBox.warning(self, "No Conversation", "Please select a user to message")
            return

        text = self.message_input.text().strip()
        if not text:
            return

        current_user = self.main_window.app.get_current_user()
        if not current_user:
            return

        # Send message through backend
        success, message = self.main_window.app.send_message(
            self.current_conversation_user['user_id'],
            text
        )

        if success:
            # Display message immediately
            msg_bubble = self.create_message_bubble(text, True, datetime.now())
            self.messages_layout.addWidget(msg_bubble)

            # Clear input
            self.message_input.clear()

            # Scroll to bottom
            QTimer.singleShot(100, lambda: self.messages_scroll.verticalScrollBar().setValue(
                self.messages_scroll.verticalScrollBar().maximum()
            ))
        else:
            QMessageBox.warning(self, "Error", f"Failed to send message: {message}")

    def clear_layout(self, layout):
        """Helper to properly clear a layout including child layouts"""
        if layout is None: return
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self.clear_layout(item.layout())
                item.layout().deleteLater()

    def go_to_home(self):
        self.main_window.go_to_home()

    def go_to_settings(self):
        self.main_window.go_to_settings()

    # ================= UTILITY FUNCTIONS =================
    def get_user_image_path(self, username):
        """Get the path to a user's profile image"""
        IMAGE_DIR = paths.IMAGE_DIR

        # Try multiple formats
        for ext in ['.png', '.jpg', '.jpeg', '.PNG', '.JPG']:
            img_path = os.path.join(IMAGE_DIR, f"{username}{ext}")
            if os.path.exists(img_path):
                return img_path

        # Return default
        return os.path.join(IMAGE_DIR, "profile.png")

    def load_circular_image(self, path: str, size: int) -> QPixmap:
        """Load an image and make it circular"""
        pixmap = QPixmap(path)

        if pixmap.isNull():
            # Create gradient placeholder
            placeholder = QPixmap(size, size)
            placeholder.fill(Qt.transparent)

            painter = QPainter(placeholder)
            painter.setRenderHint(QPainter.Antialiasing)

            # Create gradient background
            gradient = QLinearGradient(0, 0, size, size)
            gradient.setColorAt(0, QColor("#5B8DEE"))
            gradient.setColorAt(1, QColor("#4A7DDD"))

            painter.setBrush(QBrush(gradient))
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(0, 0, size, size)

            painter.end()
            return placeholder

        # Resize and crop to square
        pixmap = pixmap.scaled(size, size, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)

        if pixmap.width() != size or pixmap.height() != size:
            x = (pixmap.width() - size) // 2
            y = (pixmap.height() - size) // 2
            pixmap = pixmap.copy(x, y, size, size)

        # Make circular
        circular = QPixmap(size, size)
        circular.fill(Qt.transparent)

        painter = QPainter(circular)
        painter.setRenderHint(QPainter.Antialiasing)

        path_obj = QPainterPath()
        path_obj.addEllipse(QRectF(0, 0, size, size))

        painter.setClipPath(path_obj)
        painter.drawPixmap(0, 0, pixmap)

        # Add white border
        painter.setPen(Qt.NoPen)
        painter.setBrush(Qt.NoBrush)
        painter.setPen(QColor("white"))
        painter.drawEllipse(0, 0, size - 1, size - 1)

        painter.end()

        return circular