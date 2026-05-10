# dataset_indexer.py – scans data/raw/ and builds a metadata dataframe.
# Each row represents one image file with its label derived from the parent folder name.
from pathlib import Path

import cv2
import pandas as pd

from src.config import RAW_DATA_DIR, SUPPORTED_EXTENSIONS, EDA_OUTPUT_DIR
from src.models.records import ImageRecord


class DatasetIndexer:
    """Scan the image dataset and build a dataframe of image metadata."""

    def __init__(self, data_dir: Path = RAW_DATA_DIR) -> None:
        self.data_dir = data_dir

    def build_dataframe(self) -> pd.DataFrame:
        """Return a dataframe with file path, label, width, height and channels."""
        if not self.data_dir.exists():
            raise FileNotFoundError(
                f"Dataset folder not found: {self.data_dir}. "
                "Please place the dataset inside data/raw."
            )

        records = []

        # Recursively walk the dataset directory tree
        for file_path in self.data_dir.rglob("*"):
            # Skip non-image files based on file extension
            if file_path.suffix.lower() not in SUPPORTED_EXTENSIONS:
                continue

            image = cv2.imread(str(file_path))

            # cv2 returns None when a file cannot be decoded as an image
            if image is None:
                print(f"Warning: could not read image: {file_path}")
                continue

            height, width = image.shape[:2]
            # Greyscale images have shape (H, W); colour images have shape (H, W, C)
            channels = image.shape[2] if len(image.shape) == 3 else 1
            # The immediate parent folder name is used as the class label
            label = file_path.parent.name

            record = ImageRecord(
                file_path=file_path,
                label=label,
                width=width,
                height=height,
                channels=channels,
            )

            records.append(
                {
                    "file_path": str(record.file_path),
                    "label": record.label,
                    "width": record.width,
                    "height": record.height,
                    "channels": record.channels,
                }
            )

        dataframe = pd.DataFrame(records)

        if dataframe.empty:
            raise ValueError(
                "No valid images found. Check that data/raw contains image folders."
            )

        return dataframe

    def save_index(self, dataframe: pd.DataFrame) -> Path:
        """Save dataset index to CSV."""
        EDA_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

        output_path = EDA_OUTPUT_DIR / "dataset_index.csv"
        dataframe.to_csv(output_path, index=False)

        return output_path
