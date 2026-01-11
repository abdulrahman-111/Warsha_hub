# account_creation_page.py
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QDateEdit, QTextEdit,
    QComboBox, QGroupBox, QFormLayout, QScrollArea,
    QMessageBox, QFileDialog, QCheckBox, QGridLayout
)
from PySide6.QtCore import Qt, QDate, Signal
from PySide6.QtGui import QPixmap, QFont, QIcon
import os
from datetime import datetime


class create_account(QWidget):
    # Signals for navigation
    account_created = Signal(dict)  # Emits user data when account is created
    back_to_login_requested = Signal()  # Signal to go back to login page

    def __init__(self,main_window):
        super().__init__()
        self.main_window = main_window
        self.profile_picture_path = None
        self.init_ui()

    def init_ui(self):
        """Initialize the user interface"""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)

        # Title
        title_label = QLabel("Create Your Account")
        title_font = QFont("Arial", 20, QFont.Bold)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: #2c3e50; margin: 10px;")
        main_layout.addWidget(title_label)

        # Scroll area for form
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QScrollArea.NoFrame)
        main_layout.addWidget(scroll_area)

        # Form container
        form_container = QWidget()
        scroll_area.setWidget(form_container)

        # Form layout
        form_layout = QVBoxLayout(form_container)
        form_layout.setSpacing(15)

        # Personal Information Section
        personal_info_group = self.create_personal_info_section()
        form_layout.addWidget(personal_info_group)

        # Account Information Section
        account_info_group = self.create_account_info_section()
        form_layout.addWidget(account_info_group)

        # Address Section
        address_group = self.create_address_section()
        form_layout.addWidget(address_group)

        # Interests Section
        interests_group = self.create_interests_section()
        form_layout.addWidget(interests_group)

        # Profile Picture Section
        picture_group = self.create_profile_picture_section()
        form_layout.addWidget(picture_group)

        # Buttons Section
        buttons_layout = self.create_buttons_section()
        form_layout.addLayout(buttons_layout)

        # Status label
        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("color: #7f8c8d; font-style: italic;")
        form_layout.addWidget(self.status_label)

    def create_personal_info_section(self):
        """Create personal information form section"""
        group = QGroupBox("Personal Information")
        group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #3498db;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #3498db;
            }
        """)

        layout = QFormLayout()
        layout.setSpacing(10)

        # Full Name
        self.full_name_input = QLineEdit()
        self.full_name_input.setPlaceholderText("Enter your full name")
        layout.addRow("Full Name:", self.full_name_input)

        # Date of Birth
        self.dob_input = QDateEdit()
        self.dob_input.setDate(QDate(2000, 1, 1))
        self.dob_input.setCalendarPopup(True)
        self.dob_input.setMaximumWidth(150)
        layout.addRow("Date of Birth:", self.dob_input)

        # Email
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("example@domain.com")
        layout.addRow("Email Address:", self.email_input)

        group.setLayout(layout)
        return group

    def create_account_info_section(self):
        """Create account information form section"""
        group = QGroupBox("Account Information")
        group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #3498db;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #3498db;
            }
        """)

        layout = QFormLayout()
        layout.setSpacing(10)

        # Username
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Choose a username")
        layout.addRow("Username:", self.username_input)

        # Password
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter a strong password")
        self.password_input.setEchoMode(QLineEdit.Password)

        # Show password checkbox
        password_layout = QHBoxLayout()
        password_layout.addWidget(self.password_input)

        self.show_password_checkbox = QCheckBox("Show")
        self.show_password_checkbox.toggled.connect(self.toggle_password_visibility)
        password_layout.addWidget(self.show_password_checkbox)

        layout.addRow("Password:", password_layout)

        # Confirm Password
        self.confirm_password_input = QLineEdit()
        self.confirm_password_input.setPlaceholderText("Confirm your password")
        self.confirm_password_input.setEchoMode(QLineEdit.Password)
        layout.addRow("Confirm Password:", self.confirm_password_input)

        group.setLayout(layout)
        return group

    def create_address_section(self):
        """Create address form section"""
        group = QGroupBox("Address")
        group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #3498db;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #3498db;
            }
        """)

        layout = QFormLayout()
        layout.setSpacing(10)

        # Address (multi-line)
        self.address_input = QTextEdit()
        self.address_input.setPlaceholderText("Enter your full address")
        self.address_input.setMaximumHeight(80)
        layout.addRow("Address:", self.address_input)

        group.setLayout(layout)
        return group

    def create_interests_section(self):
        """Create interests selection section"""
        group = QGroupBox("Interests")
        group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #3498db;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #3498db;
            }
        """)

        layout = QVBoxLayout()

        # Interest selection
        interests_label = QLabel("Select your interests (select at least one):")
        interests_label.setStyleSheet("font-weight: normal;")
        layout.addWidget(interests_label)

        # Create checkboxes for interests
        self.interests_checkboxes = []
        interests = [
            "Technology", "Sports", "Music", "Art", "Reading",
            "Travel", "Cooking", "Gaming", "Photography", "Fitness"
        ]

        grid_layout = QGridLayout()
        row, col = 0, 0

        for interest in interests:
            checkbox = QCheckBox(interest)
            self.interests_checkboxes.append(checkbox)
            grid_layout.addWidget(checkbox, row, col)
            col += 1
            if col > 2:  # 3 columns
                col = 0
                row += 1

        layout.addLayout(grid_layout)

        # Other interests
        other_layout = QHBoxLayout()
        other_label = QLabel("Other interests:")
        other_label.setStyleSheet("font-weight: normal;")
        other_layout.addWidget(other_label)

        self.other_interests_input = QLineEdit()
        self.other_interests_input.setPlaceholderText("Enter other interests separated by commas")
        other_layout.addWidget(self.other_interests_input)

        layout.addLayout(other_layout)

        group.setLayout(layout)
        return group

    def create_profile_picture_section(self):
        """Create profile picture upload section"""
        group = QGroupBox("Profile Picture")
        group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #3498db;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #3498db;
            }
        """)

        layout = QVBoxLayout()

        # Picture display area
        picture_display_layout = QHBoxLayout()

        self.picture_label = QLabel()
        self.picture_label.setFixedSize(150, 150)
        self.picture_label.setStyleSheet("""
            QLabel {
                border: 2px dashed #bdc3c7;
                border-radius: 5px;
                background-color: #ecf0f1;
            }
        """)
        self.picture_label.setAlignment(Qt.AlignCenter)
        self.picture_label.setText("No image selected")

        picture_display_layout.addStretch()
        picture_display_layout.addWidget(self.picture_label)
        picture_display_layout.addStretch()

        layout.addLayout(picture_display_layout)

        # Upload button
        button_layout = QHBoxLayout()
        self.upload_button = QPushButton("Upload Picture")
        self.upload_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #3498db;
            }
        """)
        self.upload_button.clicked.connect(self.upload_picture)

        button_layout.addStretch()
        button_layout.addWidget(self.upload_button)
        button_layout.addStretch()

        layout.addLayout(button_layout)

        # Picture info
        self.picture_info_label = QLabel("Maximum file size: 2MB. Supported formats: JPG, PNG")
        self.picture_info_label.setStyleSheet("font-size: 12px; color: #7f8c8d; font-style: italic;")
        self.picture_info_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.picture_info_label)

        group.setLayout(layout)
        return group

    def create_buttons_section(self):
        """Create the buttons section"""
        layout = QHBoxLayout()

        # Back Button
        self.back_button = QPushButton("← Back to Login")
        self.back_button.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 10px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)
        self.back_button.clicked.connect(self.back_to_login)

        # Clear Form Button
        self.clear_button = QPushButton("Clear Form")
        self.clear_button.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 10px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        self.clear_button.clicked.connect(self.clear_form)

        # Create Account Button
        self.create_button = QPushButton("Create Account")
        self.create_button.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
            QPushButton:disabled {
                background-color: #95a5a6;
            }
        """)
        self.create_button.clicked.connect(self.create_account)

        layout.addWidget(self.back_button)
        layout.addStretch()
        layout.addWidget(self.clear_button)
        layout.addWidget(self.create_button)

        return layout

    def toggle_password_visibility(self, checked):
        """Toggle password visibility"""
        if checked:
            self.password_input.setEchoMode(QLineEdit.Normal)
            self.confirm_password_input.setEchoMode(QLineEdit.Normal)
        else:
            self.password_input.setEchoMode(QLineEdit.Password)
            self.confirm_password_input.setEchoMode(QLineEdit.Password)

    def upload_picture(self):
        """Handle profile picture upload"""
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(
            self,
            "Select Profile Picture",
            "",
            "Image Files (*.png *.jpg *.jpeg *.bmp *.gif)"
        )

        if file_path:
            # Check file size (limit to 2MB)
            file_size = os.path.getsize(file_path) / (1024 * 1024)  # Convert to MB
            if file_size > 2:
                QMessageBox.warning(self, "File Too Large", "Please select an image smaller than 2MB.")
                return

            self.profile_picture_path = file_path
            pixmap = QPixmap(file_path)

            # Scale the image to fit the label while maintaining aspect ratio
            scaled_pixmap = pixmap.scaled(
                150, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation
            )

            self.picture_label.setPixmap(scaled_pixmap)
            self.status_label.setText(f"Picture uploaded: {os.path.basename(file_path)}")
            self.status_label.setStyleSheet("color: #27ae60; font-style: italic;")

    def validate_form(self):
        """Validate all form fields"""
        # Check required fields
        if not self.username_input.text().strip():
            QMessageBox.warning(self, "Validation Error", "Username is required.")
            return False

        if not self.full_name_input.text().strip():
            QMessageBox.warning(self, "Validation Error", "Full name is required.")
            return False

        if not self.email_input.text().strip():
            QMessageBox.warning(self, "Validation Error", "Email address is required.")
            return False

        # Validate email format
        email = self.email_input.text().strip()
        if "@" not in email or "." not in email:
            QMessageBox.warning(self, "Validation Error", "Please enter a valid email address.")
            return False

        if not self.password_input.text():
            QMessageBox.warning(self, "Validation Error", "Password is required.")
            return False

        # Check password length
        if len(self.password_input.text()) < 6:
            QMessageBox.warning(self, "Validation Error", "Password must be at least 6 characters long.")
            return False

        # Check password confirmation
        if self.password_input.text() != self.confirm_password_input.text():
            QMessageBox.warning(self, "Validation Error", "Passwords do not match.")
            return False

        # Check at least one interest is selected
        interests_selected = any(checkbox.isChecked() for checkbox in self.interests_checkboxes)
        other_interests = self.other_interests_input.text().strip()

        if not interests_selected and not other_interests:
            QMessageBox.warning(self, "Validation Error",
                                "Please select at least one interest or enter other interests.")
            return False

        return True

    def create_account(self):
        """Handle account creation"""
        if not self.validate_form():
            return

        # Gather all data
        user_data = {
            "username": self.username_input.text().strip(),
            "full_name": self.full_name_input.text().strip(),
            "date_of_birth": self.dob_input.date().toString("yyyy-MM-dd"),
            "email": self.email_input.text().strip(),
            "password": self.password_input.text(),  # Note: In real app, hash this!
            "address": self.address_input.toPlainText().strip(),
            "interests": [],
            "profile_picture_path": self.profile_picture_path,
            "registration_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        # Get selected interests
        for checkbox in self.interests_checkboxes:
            if checkbox.isChecked():
                user_data["interests"].append(checkbox.text())

        # Add other interests if provided
        other_interests = self.other_interests_input.text().strip()
        if other_interests:
            user_data["interests"].extend([interest.strip() for interest in other_interests.split(",")])

        # Emit the account created signal with user data
        self.account_created.emit(user_data)
        # Clear form for next registration
        self.clear_form()
        # Emit signal to go back to login page
        self.back_to_login_requested.emit()

    def clear_form(self):
        """Clear all form fields"""
        self.username_input.clear()
        self.full_name_input.clear()
        self.dob_input.setDate(QDate(2000, 1, 1))
        self.email_input.clear()
        self.password_input.clear()
        self.confirm_password_input.clear()
        self.address_input.clear()

        # Clear interest checkboxes
        for checkbox in self.interests_checkboxes:
            checkbox.setChecked(False)
        self.other_interests_input.clear()

        # Clear profile picture
        self.picture_label.clear()
        self.picture_label.setText("No image selected")
        self.profile_picture_path = None

        # Reset password visibility
        self.show_password_checkbox.setChecked(False)

        # Update status
        self.status_label.setText("Form cleared. You can start again.")
        self.status_label.setStyleSheet("color: #7f8c8d; font-style: italic;")

    def back_to_login(self):
        """Handle back to login button click"""
        self.main_window.go_to_login()

    def get_user_data(self):
        """Get the current form data (for debugging or manual integration)"""
        if not self.validate_form():
            return None

        user_data = {
            "username": self.username_input.text().strip(),
            "full_name": self.full_name_input.text().strip(),
            "date_of_birth": self.dob_input.date().toString("yyyy-MM-dd"),
            "email": self.email_input.text().strip(),
            "password": self.password_input.text(),
            "address": self.address_input.toPlainText().strip(),
            "interests": [],
            "profile_picture_path": self.profile_picture_path
        }

        # Get selected interests
        for checkbox in self.interests_checkboxes:
            if checkbox.isChecked():
                user_data["interests"].append(checkbox.text())

        # Add other interests if provided
        other_interests = self.other_interests_input.text().strip()
        if other_interests:
            user_data["interests"].extend([interest.strip() for interest in other_interests.split(",")])

        return user_data