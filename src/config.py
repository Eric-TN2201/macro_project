# config.py – central configuration for all project paths and constants.
# All other modules import from here so that paths are defined in one place.
from pathlib import Path

# Resolve the project root (two levels above this file: src/ -> project root)
BASE_DIR = Path(__file__).resolve().parent.parent

# Raw dataset lives inside data/raw/<class_name>/<image_file>
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"

# All generated artefacts are written under outputs/
OUTPUTS_DIR = BASE_DIR / "outputs"
EDA_OUTPUT_DIR = OUTPUTS_DIR / "eda"        # CSV summaries and EDA charts
MODEL_OUTPUT_DIR = OUTPUTS_DIR / "models"   # Saved classifier (.joblib)
REPORT_OUTPUT_DIR = OUTPUTS_DIR / "reports" # Classification report and confusion matrix

# Target size (width, height) that all images are resized to before feature extraction
IMAGE_SIZE = (128, 128)

# Only files with these extensions are treated as valid images
SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp"}