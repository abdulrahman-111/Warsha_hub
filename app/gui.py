from PySide6.QtWidgets import QMainWindow, QStackedWidget, QMessageBox
from PySide6.QtCore import QTimer
from .pages.login import LoginPage
from .pages.home import HomePage
from .pages.settings import SettingsPage
from .pages.user_profile import UserProfilePage
from .pages.my_profile import MyProfilePage
from .pages.create_account import create_account
from .pages.messages import MessagingPage
from .styles import get_stylesheet
from .pages.network_graph import NetworkGraph
from .socialmedia_app import SocialMedia  # Import the backend controller
from .utils.audio import AudioManager

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # 1. Initialize the Backend (The Brain)
        self.app = SocialMedia()

        self.audio = AudioManager()
        QTimer.singleShot(10, self.audio.play_start)

        self.setWindowTitle("Social Media App")
        self.resize(1200, 800)

        # Store current mode globally for ALL pages
        self.dark_mode = False

        # Main stacked interface
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        # Pages
        self.login_page = LoginPage(self)
        self.home_page = HomePage(self)
        self.settings_page = SettingsPage(self)
        self.create_account = create_account(self)
        self.user_profile_page = UserProfilePage(self)
        self.my_profile_page=MyProfilePage(self)
        self.message_page=MessagingPage(self)

        self.stack.addWidget(self.login_page)
        self.stack.addWidget(self.home_page)
        self.stack.addWidget(self.settings_page)
        self.stack.addWidget(self.create_account)
        self.stack.addWidget(self.user_profile_page)
        self.stack.addWidget(self.my_profile_page)
        self.stack.addWidget(self.message_page)

        # 2. Connect the Registration Signal
        # When create_account page emits 'account_created', call 'handle_registration'
        self.create_account.account_created.connect(self.handle_registration)

        # Apply initial light theme to ENTIRE APP
        self.apply_theme()

        self.network_page = NetworkGraph(self.app.network.get_graph(), main_window=self)
        self.stack.addWidget(self.network_page)

    def handle_registration(self, user_data):
        """Handle registration data from the form"""

        # 1. Prepare data for backend
        # Match the keys expected by socialmedia_app.register_user()
        data_for_backend = {
            "username": user_data.get("username"),
            "full_name": user_data.get("full_name"),
            "email": user_data.get("email"),
            "password": user_data.get("password"),
            "address": user_data.get("address", ""),
            "interests": user_data.get("interests", []), # Keep as list, not string
            "birthdate": user_data.get("date_of_birth")  # Key changed to "birthdate"
        }

        # 2. Call Backend using the SocialMedia class method
        success, message, user_obj = self.app.register_user(
            username=data_for_backend["username"],
            full_name=data_for_backend["full_name"],
            email=data_for_backend["email"],
            password=data_for_backend["password"],
            address=data_for_backend["address"],
            interests=data_for_backend["interests"],
            birthdate=data_for_backend["birthdate"],
        )

        # 3. Handle Result
        if success:
            QMessageBox.information(self, "Success", message)
            self.go_to_login()
        else:
            QMessageBox.warning(self, "Error", message)

    def show_create_post_page(self):
        self.stack.setCurrentWidget(self.create_post_page)

    def apply_theme(self):
        """Apply the current theme to the whole application."""
        self.setStyleSheet(get_stylesheet(light=not self.dark_mode))

    def toggle_theme(self):
        self.dark_mode = not self.dark_mode
        self.apply_theme()

        if hasattr(self, 'network_page'):
            self.network_page.update_theme()

    def go_to_home(self):
        self.stack.setCurrentWidget(self.home_page)

    def go_to_login(self):
        self.stack.setCurrentWidget(self.login_page)

    def go_to_create_account(self):
        self.stack.setCurrentWidget(self.create_account)

    def go_to_network(self):
        self.stack.setCurrentWidget(self.network_page)

    def go_to_settings(self):
        """Navigate to settings page"""
        self.stack.setCurrentWidget(self.settings_page)

    def update_logo(self):
        self.login_page.update_logo()

    def go_to_my_profile(self):
        self.stack.setCurrentWidget(self.my_profile_page)

    def show_user_profile(self, user_data):
        """Load user data and switch to Profile Page"""
        self.user_profile_page.load_user(user_data)
        self.stack.setCurrentWidget(self.user_profile_page)

    def go_to_message_page(self):
        self.stack.setCurrentWidget(self.message_page)