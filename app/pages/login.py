import os
from PySide6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout,
    QLineEdit, QPushButton, QMessageBox, QGraphicsOpacityEffect
)
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QPoint
from app.utils.paths import IMAGE_DIR
from app.utils.audio import AudioManager

class LoginPage(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.audio = AudioManager()

        # Setup Opacity Effect for the entire page
        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity_effect)
        self.opacity_effect.setOpacity(0)  # Start invisible

        self.build_ui()
        self.load_logos()
        self.update_logo()

    def showEvent(self, event):
        """Trigger animations when the page is shown"""
        super().showEvent(event)
        self.start_entry_animations()

    def start_entry_animations(self):
        # 1. Fade Animation
        self.fade_anim = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.fade_anim.setDuration(1000)  # 1 second
        self.fade_anim.setStartValue(0.0)
        self.fade_anim.setEndValue(1.0)
        self.fade_anim.setEasingCurve(QEasingCurve.InOutQuad)

        # 2. Slide Animation (Optional but cool)
        # Moves the window slightly up while fading
        self.slide_anim = QPropertyAnimation(self, b"pos")
        self.slide_anim.setDuration(800)
        current_pos = self.pos()
        self.slide_anim.setStartValue(current_pos + QPoint(0, 30))
        self.slide_anim.setEndValue(current_pos)
        self.slide_anim.setEasingCurve(QEasingCurve.OutCubic)

        # Start both
        self.fade_anim.start()
        self.slide_anim.start()

    # ---------- UI LAYOUT ----------
    def build_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignCenter)
        main_layout.setSpacing(20)

        # ===== Top bar (theme toggle) =====
        top_layout = QVBoxLayout()
        top_layout.setAlignment(Qt.AlignRight)

        self.theme_btn = QPushButton("🌙")
        self.theme_btn.setFixedSize(40, 40)
        self.theme_btn.clicked.connect(self.toggle_theme)
        self.theme_btn.clicked.connect(self.audio.play_click)

        self.network_btn = QPushButton("🌐")
        self.network_btn.setFixedSize(40, 40)
        self.network_btn.setToolTip("Open Network Map")
        self.network_btn.clicked.connect(self.go_to_network)
        self.network_btn.clicked.connect(self.audio.play_click)

        top_layout.addWidget(self.theme_btn)
        top_layout.addWidget(self.network_btn)

        wrapper = QHBoxLayout()
        wrapper.addStretch()
        wrapper.addLayout(top_layout)

        main_layout.addLayout(wrapper)

        # ===== Logo =====
        self.logo_label = QLabel()
        self.logo_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.logo_label)

        # ===== Username =====
        self.username = QLineEdit()
        self.username.setPlaceholderText("Username")
        self.username.setFixedWidth(260)
        main_layout.addWidget(self.username, alignment=Qt.AlignCenter)

        # ===== Password =====
        self.password = QLineEdit()
        self.password.setPlaceholderText("Password")
        self.password.setEchoMode(QLineEdit.Password)
        self.password.setFixedWidth(260)
        main_layout.addWidget(self.password, alignment=Qt.AlignCenter)

        # ===== Login Button =====
        login_btn = QPushButton("Login")
        login_btn.setFixedSize(140, 42)
        login_btn.clicked.connect(self.login)
        main_layout.addWidget(login_btn, alignment=Qt.AlignCenter)

        self.setLayout(main_layout)

        # ===== Create account Button =====
        create_btn = QPushButton("Don't have account")
        create_btn.setFixedSize(140, 42)
        create_btn.clicked.connect(self.go_to_create_account)
        login_btn.clicked.connect(self.audio.play_click)
        main_layout.addWidget(create_btn, alignment=Qt.AlignCenter)

        self.setLayout(main_layout)

    # ---------- LOAD LOGOS SAFELY ----------
    def load_logos(self):
        light_path = os.path.join(IMAGE_DIR, "logo_light.png")
        dark_path  = os.path.join(IMAGE_DIR, "logo_dark.png")

        self.light_logo = QPixmap(light_path)
        self.dark_logo = QPixmap(dark_path)

        if self.light_logo.isNull():
            print("❌ Light logo missing:", light_path)
        if self.dark_logo.isNull():
            print("❌ Dark logo missing:", dark_path)

        self.light_logo = self.light_logo.scaled(
            420, 420, Qt.KeepAspectRatio, Qt.SmoothTransformation
        )
        self.dark_logo = self.dark_logo.scaled(
            420, 420, Qt.KeepAspectRatio, Qt.SmoothTransformation
        )

    # ---------- UPDATE LOGO BASED ON MODE ----------
    def update_logo(self):
        if self.main_window.dark_mode:
            self.logo_label.setPixmap(self.dark_logo)
            self.theme_btn.setText("☀")
        else:
            self.logo_label.setPixmap(self.light_logo)
            self.theme_btn.setText("🌙")

    # ---------- TOGGLE THEME ----------
    def toggle_theme(self):
        self.main_window.toggle_theme()
        self.update_logo()

    # ---------- NETWORK ----------
    def go_to_network(self):
        self.main_window.go_to_network()

    # ---------- LOGIN ACTION ----------
    def login(self):
        """
        Connects the GUI input to the Backend logic
        """
        user_text = self.username.text().strip()
        pass_text = self.password.text().strip()

        if not user_text or not pass_text:
            QMessageBox.warning(self, "Missing Input", "Please enter both username and password.")
            return

        # CALL THE BACKEND
        # This returns a tuple: (Success_Bool, Message_String, User_Object)
        success, message, user_obj = self.main_window.app.login(user_text, pass_text)

        if success:
            print(f"Login Successful: {message}")
            self.main_window.app.current_user = user_obj
            self.username.clear()
            self.password.clear()
            self.main_window.go_to_home()
        else:
            QMessageBox.warning(self, "Login Failed", message)

    def go_to_create_account(self):
        self.main_window.go_to_create_account()