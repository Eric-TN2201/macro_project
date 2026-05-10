# Student Name:
# +  u3281913
# +   u3293786
# Unit: Software Technology 1 (8995)
# Assignment: Assignment 3 - Macroinvertebrate Image Analysis System


from pathlib import Path

import joblib
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
)
from sklearn.model_selection import train_test_split

from src.config import MODEL_OUTPUT_DIR, REPORT_OUTPUT_DIR, SUPPORTED_EXTENSIONS


class ClassifierService:
    """Train, evaluate, and save the baseline image classification model."""

    def __init__(self, preprocessor, model_output_dir: Path = MODEL_OUTPUT_DIR) -> None:
        """Initialize classifier settings and output directories."""
        self.preprocessor = preprocessor
        self.model_output_dir = model_output_dir
        self.report_output_dir = REPORT_OUTPUT_DIR

        self.model = RandomForestClassifier(
            n_estimators=200,
            random_state=42,
            n_jobs=-1,
            class_weight="balanced",
        )

        # Ensure output directories exist before any file is written
        self.model_output_dir.mkdir(parents=True, exist_ok=True)
        self.report_output_dir.mkdir(parents=True, exist_ok=True)

    def prepare_features(self, dataframe: pd.DataFrame) -> tuple[np.ndarray, np.ndarray]:
        """Convert image file paths into feature arrays and labels."""
        features = []
        labels = []

        for _, row in dataframe.iterrows():
            try:
                # Transform each image into a flat float32 array
                image_features = self.preprocessor.transform(row["file_path"])
                features.append(image_features)
                labels.append(row["label"])
            except ValueError as error:
                # Log unreadable images and continue rather than aborting
                print(f"Skipping image: {error}")

        if not features:
            raise ValueError("No valid image features were created.")

        return np.array(features), np.array(labels)

    def train(self, dataframe: pd.DataFrame) -> dict[str, object]:
        """Train the classifier and return evaluation results."""
        X, y = self.prepare_features(dataframe)

        if len(y) < 2:
            raise ValueError("At least 2 valid images are required for model training.")

        unique_classes = np.unique(y)
        if len(unique_classes) < 2:
            raise ValueError(
                "At least 2 classes are required for classification training."
            )

        # Stratified split requires at least 2 samples per class; fall back if not met
        class_counts = pd.Series(y).value_counts()
        test_count = max(1, int(round(len(y) * 0.2)))
        test_count = min(test_count, len(y) - 1)
        can_stratify = class_counts.min() >= 2 and test_count >= len(unique_classes)

        # Default to an 80 / 20 split while remaining valid for small datasets.
        test_size = test_count / len(y)

        X_train, X_test, y_train, y_test = train_test_split(
            X,
            y,
            test_size=test_size,
            random_state=42,
            stratify=y if can_stratify else None,
        )

        self.model.fit(X_train, y_train)

        predictions = self.model.predict(X_test)

        # Compute evaluation metrics
        accuracy = accuracy_score(y_test, predictions)
        report = classification_report(
            y_test,
            predictions,
            zero_division=0,  # Suppress warnings for classes with no predicted samples
        )

        # Build confusion matrix with a consistent label order
        labels = sorted(np.unique(y))
        matrix = confusion_matrix(y_test, predictions, labels=labels)

        results = {
            "accuracy": accuracy,
            "report": report,
            "confusion_matrix": matrix,
            "labels": labels,
        }

        # Persist artefacts so subsequent prediction runs do not need retraining
        self.save_training_report(results)
        self.save_confusion_matrix_plot(results)
        self.save_model()

        return results

    def save_model(self, file_name: str = "macro_classifier.joblib") -> Path:
        """Save the trained model to disk."""
        output_path = self.model_output_dir / file_name
        joblib.dump(self.model, output_path)
        return output_path

    def save_training_report(self, results: dict[str, object]) -> Path:
        """Save the classification report to a text file."""
        output_path = self.report_output_dir / "classification_report.txt"

        report_text = (
            f"Model: RandomForestClassifier\n"
            f"Accuracy: {results['accuracy']:.4f}\n\n"
            f"Classification Report:\n{results['report']}\n"
        )

        output_path.write_text(report_text, encoding="utf-8")

        return output_path

    def save_confusion_matrix_plot(self, results: dict[str, object]) -> Path:
        """Save the confusion matrix as an image."""
        output_path = self.report_output_dir / "confusion_matrix.png"

        labels = results["labels"]
        matrix = results["confusion_matrix"]

        plt.figure(figsize=(10, 8))
        sns.heatmap(
            matrix,
            annot=True,
            fmt="d",
            xticklabels=labels,
            yticklabels=labels,
        )

        plt.title("Confusion Matrix")
        plt.xlabel("Predicted Class")
        plt.ylabel("Actual Class")
        plt.xticks(rotation=90)
        plt.yticks(rotation=0)
        plt.tight_layout()
        plt.savefig(output_path)
        plt.close()

        return output_path

    def predict_image(self, file_path: str) -> str:
        """Predict the class of one image using the trained model."""
        image_path = Path(file_path)

        # Validate that the image file actually exists on disk
        if not image_path.exists() or not image_path.is_file():
            raise FileNotFoundError(f"Image file not found: {file_path}")

        if image_path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            raise ValueError(
                "Unsupported file type. Supported extensions are: "
                + ", ".join(sorted(SUPPORTED_EXTENSIONS))
            )

        model_path = self.model_output_dir / "macro_classifier.joblib"

        # The model must be trained before prediction can run
        if not model_path.exists():
            raise FileNotFoundError(
                "Trained model not found. Please train the model first."
            )

        # Load the persisted model from disk
        self.model = joblib.load(model_path)

        # Preprocess the image and reshape to a 2-D array (1 sample x n features)
        features = self.preprocessor.transform(str(image_path)).reshape(1, -1)
        prediction = self.model.predict(features)[0]

        return str(prediction)
    
    def predict_image_with_confidence(self, file_path: str) -> tuple[str, float | None]:
        """Predict one image and return predicted class with confidence."""
        image_path = Path(file_path)

        if not image_path.exists() or not image_path.is_file():
            raise FileNotFoundError(f"Image file not found: {file_path}")

        if image_path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            raise ValueError(
                "Unsupported file type. Supported extensions are: "
                + ", ".join(sorted(SUPPORTED_EXTENSIONS))
            )

        model_path = self.model_output_dir / "macro_classifier.joblib"

        if not model_path.exists():
            raise FileNotFoundError(
                "Trained model not found. Please train the model first."
            )

        self.model = joblib.load(model_path)

        features = self.preprocessor.transform(str(image_path)).reshape(1, -1)
        prediction = self.model.predict(features)[0]

        confidence = None
        if hasattr(self.model, "predict_proba"):
            confidence = float(self.model.predict_proba(features).max())

        return str(prediction), confidence