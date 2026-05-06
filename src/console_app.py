from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"

OUTPUTS_DIR = BASE_DIR / "outputs"
EDA_OUTPUT_DIR = OUTPUTS_DIR / "eda"
MODEL_OUTPUT_DIR = OUTPUTS_DIR / "models"
REPORT_OUTPUT_DIR = OUTPUTS_DIR / "reports"

IMAGE_SIZE = (128, 128)

SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp"}