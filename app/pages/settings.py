# settings.py
import os
from PySide6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout,
    QPushButton, QFrame, QLineEdit, QComboBox,
    QScrollArea, QSizePolicy, QSpacerItem, QMessageBox,
    QDialog, QDialogButtonBox
)
from PySide6.QtGui import QFont, QPixmap
from PySide6.QtCore import Qt, Signal

# ---------- SAFE IMAGE PATH ----------
BASE_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..")
)
IMAGE_DIR = os.path.join(BASE_DIR, "resources", "images")


class SettingsPage(QWidget):
    # Signal to notify main window about theme change
    theme_changed = Signal(str)

    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.load_logos()
        self.build_ui()
        self.apply_theme()

    def load_logos(self):
        """Load theme icons like login page"""
        light_path = os.path.join(IMAGE_DIR, "logo_light.png")
        dark_path = os.path.join(IMAGE_DIR, "logo_dark.png")

        self.light_logo = QPixmap(light_path)
        self.dark_logo = QPixmap(dark_path)

        if self.light_logo.isNull():
            print("❌ Light logo missing:", light_path)
        if self.dark_logo.isNull():
            print("❌ Dark logo missing:", dark_path)

        # Scale logos for settings page if needed
        self.light_logo = self.light_logo.scaled(
            120, 120, Qt.KeepAspectRatio, Qt.SmoothTransformation
        )
        self.dark_logo = self.dark_logo.scaled(
            120, 120, Qt.KeepAspectRatio, Qt.SmoothTransformation
        )

    def build_ui(self):
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        # ===== TOP BAR WITH BACK BUTTON =====
        top_layout = QHBoxLayout()

        # Back button
        back_btn = QPushButton("← Back")
        back_btn.setFixedSize(80, 35)
        back_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #6C5CE7;
                border: 2px solid #6C5CE7;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #6C5CE7;
                color: white;
            }
        """)
        back_btn.clicked.connect(self.go_to_home)
        top_layout.addWidget(back_btn)

        top_layout.addStretch()

        # Title
        title_label = QLabel("Settings")
        title_label.setStyleSheet("font-size: 32px; font-weight: bold; color: #333;")
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)

        # Create scroll area for content
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setStyleSheet("border: none; background: transparent;")

        # Container widget
        container = QWidget()
        container_layout = QVBoxLayout()
        container_layout.setSpacing(30)

        home_btn = QPushButton("Back")
        home_btn.setFixedSize(140, 42)
        home_btn.clicked.connect(self.go_to_home)
        main_layout.addWidget(home_btn)

        self.setLayout(main_layout)

        # ========== PERSONAL INFORMATION SECTION ==========
        personal_info_section = self.create_personal_info_section()
        container_layout.addWidget(personal_info_section)

        # Add separator line
        separator1 = QFrame()
        separator1.setFrameShape(QFrame.HLine)
        separator1.setStyleSheet("background-color: #e0e0e0;")
        container_layout.addWidget(separator1)

        # ========== CHANGE PASSWORD SECTION ==========
        password_section = self.create_password_section()
        container_layout.addWidget(password_section)

        # Add separator line
        separator2 = QFrame()
        separator2.setFrameShape(QFrame.HLine)
        separator2.setStyleSheet("background-color: #e0e0e0;")
        container_layout.addWidget(separator2)

        # ========== PREFERENCES SECTION ==========
        preferences_section = self.create_preferences_section()
        container_layout.addWidget(preferences_section)

        # Add separator line
        separator3 = QFrame()
        separator3.setFrameShape(QFrame.HLine)
        separator3.setStyleSheet("background-color: #e0e0e0;")
        container_layout.addWidget(separator3)

        # ========== DANGER ZONE SECTION ==========
        danger_zone_section = self.create_danger_zone_section()
        container_layout.addWidget(danger_zone_section)

        container_layout.addStretch()
        container.setLayout(container_layout)
        scroll_area.setWidget(container)

        main_layout.addWidget(scroll_area)
        self.setLayout(main_layout)

    def create_personal_info_section(self):
        """Create the Personal Information section"""
        section_frame = QFrame()
        section_layout = QVBoxLayout()
        section_layout.setSpacing(15)

        # Section title
        title_label = QLabel("Personal Information")
        title_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #333;")
        section_layout.addWidget(title_label)

        # User information card
        info_card = QFrame()
        info_card.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border-radius: 12px;
                padding: 20px;
            }
        """)
        info_layout = QVBoxLayout()
        info_layout.setSpacing(15)

        # Current user info
        current_user = self.main_window.app.get_current_user()
        if current_user:
            user_name = current_user.get_fullname()
            user_email = current_user.get_email()
        else:
            user_name = "Guest User"
            user_email = "guest@example.com"

        # Name field
        name_layout = QHBoxLayout()
        name_label = QLabel("Name")
        name_label.setStyleSheet("font-size: 16px; color: #666; width: 120px;")
        self.name_value = QLabel(user_name)
        self.name_value.setStyleSheet("font-size: 16px; color: #333; font-weight: 500;")
        change_name_btn = QPushButton("Change")
        change_name_btn.setFixedSize(80, 35)
        change_name_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: 2px solid #6C5CE7;
                color: #6C5CE7;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #6C5CE7;
                color: white;
            }
        """)
        change_name_btn.clicked.connect(self.change_name)

        name_layout.addWidget(name_label)
        name_layout.addWidget(self.name_value)
        name_layout.addStretch()
        name_layout.addWidget(change_name_btn)
        info_layout.addLayout(name_layout)

        # Email field
        email_layout = QHBoxLayout()
        email_label = QLabel("Email")
        email_label.setStyleSheet("font-size: 16px; color: #666; width: 120px;")
        self.email_value = QLabel(user_email)
        self.email_value.setStyleSheet("font-size: 16px; color: #333; font-weight: 500;")
        change_email_btn = QPushButton("Change")
        change_email_btn.setFixedSize(80, 35)
        change_email_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: 2px solid #6C5CE7;
                color: #6C5CE7;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #6C5CE7;
                color: white;
            }
        """)
        change_email_btn.clicked.connect(self.change_email)

        email_layout.addWidget(email_label)
        email_layout.addWidget(self.email_value)
        email_layout.addStretch()
        email_layout.addWidget(change_email_btn)
        info_layout.addLayout(email_layout)

        info_card.setLayout(info_layout)
        section_layout.addWidget(info_card)

        section_frame.setLayout(section_layout)
        return section_frame

    def create_password_section(self):
        """Create the Change Password section"""
        section_frame = QFrame()
        section_layout = QVBoxLayout()
        section_layout.setSpacing(15)

        # Section title
        title_label = QLabel("Change Password")
        title_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #333;")
        section_layout.addWidget(title_label)

        # Password form
        form_card = QFrame()
        form_card.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border-radius: 12px;
                padding: 20px;
            }
        """)
        form_layout = QVBoxLayout()
        form_layout.setSpacing(15)

        # Old password
        old_pass_layout = QVBoxLayout()
        old_pass_layout.setSpacing(8)
        old_pass_label = QLabel("Old Password")
        old_pass_label.setStyleSheet("font-size: 14px; color: #666;")
        self.old_password_input = QLineEdit()
        self.old_password_input.setPlaceholderText("Enter your current password")
        self.old_password_input.setEchoMode(QLineEdit.Password)
        self.old_password_input.setStyleSheet("""
            QLineEdit {
                padding: 12px;
                border: 1px solid #ddd;
                border-radius: 8px;
                font-size: 14px;
                background-color: white;
            }
            QLineEdit:focus {
                border: 2px solid #6C5CE7;
            }
        """)
        old_pass_layout.addWidget(old_pass_label)
        old_pass_layout.addWidget(self.old_password_input)
        form_layout.addLayout(old_pass_layout)

        # New password
        new_pass_layout = QVBoxLayout()
        new_pass_layout.setSpacing(8)
        new_pass_label = QLabel("New Password")
        new_pass_label.setStyleSheet("font-size: 14px; color: #666;")
        self.new_password_input = QLineEdit()
        self.new_password_input.setPlaceholderText("Enter your new password")
        self.new_password_input.setEchoMode(QLineEdit.Password)
        self.new_password_input.setStyleSheet("""
            QLineEdit {
                padding: 12px;
                border: 1px solid #ddd;
                border-radius: 8px;
                font-size: 14px;
                background-color: white;
            }
            QLineEdit:focus {
                border: 2px solid #6C5CE7;
            }
        """)
        new_pass_layout.addWidget(new_pass_label)
        new_pass_layout.addWidget(self.new_password_input)
        form_layout.addLayout(new_pass_layout)

        # Confirm new password
        confirm_pass_layout = QVBoxLayout()
        confirm_pass_layout.setSpacing(8)
        confirm_pass_label = QLabel("Confirm New Password")
        confirm_pass_label.setStyleSheet("font-size: 14px; color: #666;")
        self.confirm_password_input = QLineEdit()
        self.confirm_password_input.setPlaceholderText("Re-enter your new password")
        self.confirm_password_input.setEchoMode(QLineEdit.Password)
        self.confirm_password_input.setStyleSheet("""
            QLineEdit {
                padding: 12px;
                border: 1px solid #ddd;
                border-radius: 8px;
                font-size: 14px;
                background-color: white;
            }
            QLineEdit:focus {
                border: 2px solid #6C5CE7;
            }
        """)
        confirm_pass_layout.addWidget(confirm_pass_label)
        confirm_pass_layout.addWidget(self.confirm_password_input)
        form_layout.addLayout(confirm_pass_layout)

        # Save button
        save_pass_btn = QPushButton("Save Changes")
        save_pass_btn.setFixedHeight(40)
        save_pass_btn.setStyleSheet("""
            QPushButton {
                background-color: #6C5CE7;
                color: white;
                border-radius: 8px;
                font-size: 16px;
                font-weight: bold;
                border: none;
            }
            QPushButton:hover {
                background-color: #5A4FD8;
            }
            QPushButton:disabled {
                background-color: #ccc;
                color: #666;
            }
        """)
        save_pass_btn.clicked.connect(self.change_password)
        form_layout.addWidget(save_pass_btn)

        form_card.setLayout(form_layout)
        section_layout.addWidget(form_card)

        section_frame.setLayout(section_layout)
        return section_frame

    def create_preferences_section(self):
        """Create the Preferences section with theme toggle"""
        section_frame = QFrame()
        section_layout = QVBoxLayout()
        section_layout.setSpacing(15)

        # Section title
        title_label = QLabel("Preferences")
        title_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #333;")
        section_layout.addWidget(title_label)

        # Preferences card
        pref_card = QFrame()
        pref_card.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border-radius: 12px;
                padding: 20px;
            }
        """)
        pref_layout = QVBoxLayout()
        pref_layout.setSpacing(20)

        # Theme preference with icon like login page
        theme_card = QFrame()
        theme_card.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 10px;
                padding: 15px;
                border: 1px solid #e0e0e0;
            }
        """)
        theme_card_layout = QHBoxLayout()

        # Theme label
        theme_label_layout = QVBoxLayout()
        theme_title = QLabel("Theme")
        theme_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #333;")
        theme_desc = QLabel("Change between light and dark mode")
        theme_desc.setStyleSheet("font-size: 14px; color: #666;")
        theme_label_layout.addWidget(theme_title)
        theme_label_layout.addWidget(theme_desc)

        theme_card_layout.addLayout(theme_label_layout)
        theme_card_layout.addStretch()

        # Theme toggle button (like login page)
        self.theme_btn = QPushButton("🌙")
        self.theme_btn.setFixedSize(50, 50)
        self.theme_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: 2px solid #6C5CE7;
                border-radius: 25px;
                font-size: 24px;
            }
            QPushButton:hover {
                background-color: #f0f0f0;
            }
        """)
        self.theme_btn.clicked.connect(self.toggle_theme)
        theme_card_layout.addWidget(self.theme_btn)

        theme_card.setLayout(theme_card_layout)
        pref_layout.addWidget(theme_card)

        pref_card.setLayout(pref_layout)
        section_layout.addWidget(pref_card)

        section_frame.setLayout(section_layout)
        return section_frame

    def create_danger_zone_section(self):
        """Create the Danger Zone section for account deletion"""
        section_frame = QFrame()
        section_layout = QVBoxLayout()
        section_layout.setSpacing(15)

        # Section title in red
        title_label = QLabel("Danger Zone")
        title_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #e74c3c;")
        section_layout.addWidget(title_label)

        # Danger zone card with red accent
        danger_card = QFrame()
        danger_card.setStyleSheet("""
            QFrame {
                background-color: #fff5f5;
                border-radius: 12px;
                padding: 20px;
                border: 2px solid #ffebee;
            }
        """)
        danger_layout = QVBoxLayout()
        danger_layout.setSpacing(15)

        # Warning text
        warning_text = QLabel(
            "Deleting your account is permanent. All your data, posts, and "
            "connections will be removed and cannot be recovered."
        )
        warning_text.setWordWrap(True)
        warning_text.setStyleSheet("font-size: 14px; color: #666; line-height: 1.5;")
        danger_layout.addWidget(warning_text)

        # Delete account button
        delete_account_btn = QPushButton("Delete Account")
        delete_account_btn.setFixedHeight(40)
        delete_account_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border-radius: 8px;
                font-size: 16px;
                font-weight: bold;
                border: none;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
            QPushButton:pressed {
                background-color: #a93226;
            }
        """)
        delete_account_btn.clicked.connect(self.delete_account)
        danger_layout.addWidget(delete_account_btn)

        danger_card.setLayout(danger_layout)
        section_layout.addWidget(danger_card)

        section_frame.setLayout(section_layout)
        return section_frame

    def change_name(self):
        """Handle name change with a dialog"""
        current_user = self.main_window.app.get_current_user()
        if not current_user:
            QMessageBox.warning(self, "Error", "No user logged in")
            return

        # Create a simple dialog for name change
        dialog = QDialog(self)
        dialog.setWindowTitle("Change Name")
        dialog.setFixedSize(400, 200)

        layout = QVBoxLayout()

        # Current name
        current_label = QLabel(f"Current Name: {current_user.get_fullname()}")
        current_label.setStyleSheet("font-size: 14px; color: #666;")
        layout.addWidget(current_label)

        # New name input
        new_name_label = QLabel("New Name:")
        new_name_label.setStyleSheet("font-size: 14px; color: #333; font-weight: bold;")
        layout.addWidget(new_name_label)

        new_name_input = QLineEdit()
        new_name_input.setPlaceholderText("Enter your new name")
        new_name_input.setText(current_user.get_fullname())
        new_name_input.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                border: 1px solid #ddd;
                border-radius: 6px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 2px solid #6C5CE7;
            }
        """)
        layout.addWidget(new_name_input)

        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)

        dialog.setLayout(layout)

        if dialog.exec() == QDialog.Accepted:
            new_name = new_name_input.text().strip()
            if new_name and new_name != current_user.get_fullname():
                # Update database through SocialMedia application
                user_data = {
                    'full_name': new_name
                }

                # Call update_user_profile method from SocialMedia
                success, message = self.main_window.app.update_user_profile(user_data)

                if success:
                    QMessageBox.information(self, "Success", "Name updated successfully!")
                    # Refresh the displayed name
                    self.name_value.setText(new_name)
                    # Also update the main window if needed
                    if hasattr(self.main_window, 'update_user_display'):
                        self.main_window.update_user_display()
                else:
                    QMessageBox.warning(self, "Error", message)

    def change_email(self):
        """Handle email change with a dialog"""
        from app.backend_files import db_manager  # Import here to avoid circular imports

        current_user = self.main_window.app.get_current_user()
        if not current_user:
            QMessageBox.warning(self, "Error", "No user logged in")
            return

        # Create a dialog for email change
        dialog = QDialog(self)
        dialog.setWindowTitle("Change Email")
        dialog.setFixedSize(400, 250)

        layout = QVBoxLayout()

        # Current email
        current_label = QLabel(f"Current Email: {current_user.get_email()}")
        current_label.setStyleSheet("font-size: 14px; color: #666;")
        layout.addWidget(current_label)

        # New email input
        new_email_label = QLabel("New Email:")
        new_email_label.setStyleSheet("font-size: 14px; color: #333; font-weight: bold;")
        layout.addWidget(new_email_label)

        new_email_input = QLineEdit()
        new_email_input.setPlaceholderText("Enter your new email address")
        new_email_input.setText(current_user.get_email())
        new_email_input.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                border: 1px solid #ddd;
                border-radius: 6px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 2px solid #6C5CE7;
            }
        """)
        layout.addWidget(new_email_input)

        # Confirm password
        password_label = QLabel("Confirm with Password:")
        password_label.setStyleSheet("font-size: 14px; color: #333; font-weight: bold;")
        layout.addWidget(password_label)

        password_input = QLineEdit()
        password_input.setPlaceholderText("Enter your password to confirm")
        password_input.setEchoMode(QLineEdit.Password)
        password_input.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                border: 1px solid #ddd;
                border-radius: 6px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 2px solid #6C5CE7;
            }
        """)
        layout.addWidget(password_input)

        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)

        dialog.setLayout(layout)

        if dialog.exec() == QDialog.Accepted:
            new_email = new_email_input.text().strip()
            password = password_input.text().strip()

            if not new_email:
                QMessageBox.warning(self, "Error", "Please enter a new email address")
                return

            if not password:
                QMessageBox.warning(self, "Error", "Please enter your password to confirm")
                return

            # Verify password using database authentication
            # We'll authenticate with the current username and password
            username = current_user.get_username()
            user_data = db_manager.authenticate_user(username, password)

            if not user_data:
                QMessageBox.warning(self, "Error", "Incorrect password")
                return

            # Update email through the SocialMedia application
            user_data = {
                'email': new_email
            }

            # Call update_user_profile method from SocialMedia
            success, message = self.main_window.app.update_user_profile(user_data)

            if success:
                QMessageBox.information(self, "Success", "Email updated successfully!")
                # Refresh the displayed email
                self.email_value.setText(new_email)
            else:
                QMessageBox.warning(self, "Error", message)

    def change_password(self):
        """Handle password change using the SocialMedia application methods"""
        from app.backend_files import db_manager  # Import here to avoid circular imports

        old_pass = self.old_password_input.text().strip()
        new_pass = self.new_password_input.text().strip()
        confirm_pass = self.confirm_password_input.text().strip()

        # Validation
        if not old_pass or not new_pass or not confirm_pass:
            QMessageBox.warning(self, "Error", "Please fill in all password fields")
            return

        if new_pass != confirm_pass:
            QMessageBox.warning(self, "Error", "New passwords do not match")
            return

        if len(new_pass) < 6:
            QMessageBox.warning(self, "Error", "New password must be at least 6 characters")
            return

        current_user = self.main_window.app.get_current_user()
        if not current_user:
            QMessageBox.warning(self, "Error", "No user logged in")
            return

        # First, verify the old password by authenticating
        username = current_user.get_username()
        user_data = db_manager.authenticate_user(username, old_pass)

        if not user_data:
            QMessageBox.warning(self, "Error", "Current password is incorrect")
            return

        # Update password through the SocialMedia application
        # Create user_data with all required fields
        user_data = {
            'password': new_pass,
        }

        # Call update_user_profile method from SocialMedia
        success, message = self.main_window.app.update_user_profile(user_data)

        if success:
            QMessageBox.information(self, "Success", "Password changed successfully!")
            # Clear fields
            self.old_password_input.clear()
            self.new_password_input.clear()
            self.confirm_password_input.clear()
        else:
            QMessageBox.warning(self, "Error", message)

    def toggle_theme(self):
        """Toggle theme like login page"""
        self.main_window.toggle_theme()
        self.main_window.update_logo()
        self.update_theme_button()

    def update_theme_button(self):
        """Update theme button icon based on current mode"""
        if self.main_window.dark_mode:
            self.theme_btn.setText("☀")
        else:
            self.theme_btn.setText("🌙")


    def delete_account(self):
        """Handle account deletion with confirmation dialog"""
        from app.backend_files import db_manager  # Import here to avoid circular imports

        current_user = self.main_window.app.get_current_user()
        if not current_user:
            QMessageBox.warning(self, "Error", "No user logged in")
            return

        # Create a serious confirmation dialog
        dialog = QDialog(self)
        dialog.setWindowTitle("Delete Account")
        dialog.setFixedSize(500, 300)

        layout = QVBoxLayout()

        # Warning icon and text
        warning_layout = QHBoxLayout()
        warning_icon = QLabel("⚠️")
        warning_icon.setStyleSheet("font-size: 48px;")
        warning_layout.addWidget(warning_icon)

        warning_text = QLabel(
            "<b>Are you absolutely sure?</b><br><br>"
            "This action <font color='#e74c3c'><b>cannot be undone</b></font>. "
            "This will permanently delete your account and remove all your data from our servers."
        )
        warning_text.setWordWrap(True)
        warning_text.setStyleSheet("font-size: 14px; color: #333; line-height: 1.5;")
        warning_text.setTextFormat(Qt.RichText)
        warning_layout.addWidget(warning_text, 1)

        layout.addLayout(warning_layout)

        # Confirmation text
        confirm_label = QLabel(
            "Please type your username to confirm:"
        )
        confirm_label.setStyleSheet("font-size: 14px; color: #666; margin-top: 20px;")
        layout.addWidget(confirm_label)

        # Username confirmation
        username_input = QLineEdit()
        username_input.setPlaceholderText(f"Type '{current_user.get_username()}' to confirm")
        username_input.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                border: 2px solid #e74c3c;
                border-radius: 6px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 2px solid #c0392b;
            }
        """)
        layout.addWidget(username_input)

        # Password confirmation
        password_label = QLabel("Enter your password:")
        password_label.setStyleSheet("font-size: 14px; color: #666; margin-top: 10px;")
        layout.addWidget(password_label)

        password_input = QLineEdit()
        password_input.setPlaceholderText("Enter your password")
        password_input.setEchoMode(QLineEdit.Password)
        password_input.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                border: 2px solid #e74c3c;
                border-radius: 6px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 2px solid #c0392b;
            }
        """)
        layout.addWidget(password_input)

        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.button(QDialogButtonBox.Ok).setText("Delete Account")
        button_box.button(QDialogButtonBox.Ok).setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                font-weight: bold;
                padding: 8px 20px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)

        dialog.setLayout(layout)

        if dialog.exec() == QDialog.Accepted:
            username = username_input.text().strip()
            password = password_input.text().strip()

            if username != current_user.get_username():
                QMessageBox.warning(self, "Error", "Username does not match")
                return

            if not password:
                QMessageBox.warning(self, "Error", "Please enter your password")
                return

            # Verify password by authenticating
            user_data = db_manager.authenticate_user(username, password)

            if not user_data:
                QMessageBox.warning(self, "Error", "Incorrect password")
                return

            # Final confirmation
            reply = QMessageBox.question(
                self, "Final Confirmation",
                "This is your last chance to cancel. Are you REALLY sure you want to delete your account?",
                QMessageBox.Yes | QMessageBox.No,
                QDialogButtonBox.No
            )

            if reply == QMessageBox.Yes:
                QMessageBox.warning(self, "Not Implemented",
                                    "Account deletion feature is not yet implemented in the backend.")
                # If you implement delete_account in SocialMedia, uncomment below:
                # success, message = self.main_window.app.delete_account(current_user.get_id())
                # if success:
                #     QMessageBox.information(self, "Account Deleted",
                #                             "Your account has been deleted successfully. You will be logged out.")
                #     self.main_window.app.logout()
                #     self.main_window.go_to_login()
                # else:
                #     QMessageBox.warning(self, "Error", message)

    def apply_theme(self):
        """Apply theme based on main window's dark mode setting"""
        self.main_window.apply_theme()
        self.update_theme_button()

    def showEvent(self, event):
        """Called when the page is shown"""
        # Refresh user information when page is shown
        self.refresh_user_info()
        self.update_theme_button()
        super().showEvent(event)

    def refresh_user_info(self):
        """Refresh displayed user information"""
        current_user = self.main_window.app.get_current_user()
        if current_user:
            self.name_value.setText(current_user.get_fullname())
            self.email_value.setText(current_user.get_email())

    def go_to_home(self):
        """Navigate back to home page"""
        self.main_window.go_to_home()

    def go_to_network(self):
        """Navigate to network page"""
        self.main_window.go_to_network()

