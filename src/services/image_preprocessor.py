# Student Name:
# +  u3281913
# +   u3293786
# Unit: Software Technology 1 (8995)
# Assignment: Assignment 3 - Macroinvertebrate Image Analysis System

import cv2
import numpy as np

from src.config import IMAGE_SIZE


class ImagePreprocessor:
    """Convert raw images into model-ready numeric features."""

    def __init__(self, image_size: tuple[int, int] = IMAGE_SIZE) -> None:
        """Set target size used to resize all input images."""
        self.image_size = image_size

    def transform(self, file_path: str) -> np.ndarray:
        """
        Load, resize, normalise, and flatten one image.

        The output is a one-dimensional NumPy array that can be used
        by a Scikit-learn classification model.
        """
        # Load as greyscale to reduce input dimensionality (no colour information needed)
        image = cv2.imread(str(file_path), cv2.IMREAD_GRAYSCALE)

        # cv2 returns None when the file cannot be decoded
        if image is None:
            raise ValueError(f"Could not read image: {file_path}")

        # Resize to the standard input size defined in config (default 128x128)
        resized_image = cv2.resize(image, self.image_size)

        # Scale pixel values from [0, 255] to [0.0, 1.0]
        normalised_image = resized_image.astype("float32") / 255.0

        # Flatten the 2-D array into a 1-D feature vector for sklearn compatibility
        return normalised_image.flatten()