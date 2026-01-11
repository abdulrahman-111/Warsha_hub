import os

# project/
BASE_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..")
)
backend_path = os.path.join(BASE_DIR, "app", "backend_files")
IMAGE_DIR = os.path.join(BASE_DIR, "resources", "images")
SOUND_DIR = os.path.join(BASE_DIR, "resources", "audio")