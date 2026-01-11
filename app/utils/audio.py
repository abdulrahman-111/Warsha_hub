# app/utils/audio.py
import os
from PySide6.QtMultimedia import QSoundEffect
from PySide6.QtCore import QUrl
from .paths import SOUND_DIR  # Import the path we just defined

class AudioManager:
    def __init__(self):
        self.start_sound = QSoundEffect()
        self.hover_sound = QSoundEffect()
        self.click_sound = QSoundEffect()
        self.error_sound = QSoundEffect()


        # Load sounds using the central path
        self._load(self.start_sound, "soft_startup.wav", 0.5)
        self._load(self.hover_sound, "hover.wav", 0.5)
        self._load(self.click_sound, "notification_pluck_on.wav", 0.5)
        self._load(self.error_sound, "error.wav", 0.5)


    def _load(self, effect, filename, vol):
        path = os.path.join(SOUND_DIR, filename)
        if os.path.exists(path):
            effect.setSource(QUrl.fromLocalFile(path))
            effect.setVolume(vol)
        else:
            print(f"AUDIO ERROR: Missing {path}")

    def play_start(self):
        if self.start_sound.status() == QSoundEffect.Ready:
            self.start_sound.play()

    def play_hover(self):
        if self.hover_sound.status() == QSoundEffect.Ready:
            self.hover_sound.play()

    def play_click(self):
        if self.click_sound.status() == QSoundEffect.Ready:
            self.click_sound.play()

    def play_error(self):
        if self.error_sound.status() == QSoundEffect.Ready:
            self.error_sound.play()




