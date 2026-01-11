from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton

class PostWidget(QWidget):
    def __init__(self, username, text):
        super().__init__()
        layout = QVBoxLayout()
        layout.setSpacing(5)
        layout.addWidget(QLabel(f"<b>{username}</b>"))
        layout.addWidget(QLabel(text))
        layout.addWidget(QPushButton("Like"))
        self.setLayout(layout)
