import cv2
import numpy as np

from src.config import IMAGE_SIZE


class ImagePreprocessor:
    """Convert raw images into model-ready numeric features."""

    def __init__(self, image_size: tuple[int, int] = IMAGE_SIZE) -> None:
        self.image_size = image_size

    def transform(self, file_path: str) -> np.ndarray:
        """
        Load, resize, normalise, and flatten one image.

        The output is a one-dimensional NumPy array that can be used
        by a Scikit-learn classification model.
        """
        image = cv2.imread(str(file_path), cv2.IMREAD_GRAYSCALE)

        if image is None:
            raise ValueError(f"Could not read image: {file_path}")

        resized_image = cv2.resize(image, self.image_size)

        normalised_image = resized_image.astype("float32") / 255.0

        return normalised_image.flatten()