import pandas as pd

from src.config import EDA_OUTPUT_DIR
from src.services.classifier_service import ClassifierService
from src.services.dataset_indexer import DatasetIndexer
from src.services.eda_service import EDAService
from src.services.image_preprocessor import ImagePreprocessor


class WorkflowService:
    """Coordinate the main project workflow."""

    def __init__(self) -> None:
        self.indexer = DatasetIndexer()
        self.preprocessor = ImagePreprocessor()
        self.classifier = ClassifierService(self.preprocessor)
        self.dataframe: pd.DataFrame | None = None

    def load_dataframe(self) -> pd.DataFrame:
        """Load and cache dataset dataframe."""
        if self.dataframe is None:
            self.dataframe = self.indexer.build_dataframe()
            self.indexer.save_index(self.dataframe)

        return self.dataframe

    def show_summary(self) -> pd.DataFrame:
        """Show dataset summary."""
        dataframe = self.load_dataframe()
        eda_service = EDAService(dataframe, EDA_OUTPUT_DIR)

        summary = eda_service.build_summary()

        print("\nDataset Summary")
        print(summary.to_string(index=False))

        print("\nClass Counts")
        print(dataframe["label"].value_counts())

        return summary

    def generate_eda(self) -> None:
        """Generate all EDA outputs."""
        dataframe = self.load_dataframe()
        eda_service = EDAService(dataframe, EDA_OUTPUT_DIR)

        eda_service.generate_all_outputs()

        print("\nEDA outputs generated successfully.")
        print(f"Saved to: {EDA_OUTPUT_DIR}")

    def train_model(self) -> dict[str, object]:
        """Train the baseline classifier and save evaluation outputs."""
        dataframe = self.load_dataframe()
        results = self.classifier.train(dataframe)

        print("\nModel training completed successfully.")
        print(f"Accuracy: {results['accuracy']:.4f}")

        print("\nClassification Report")
        print(results["report"])

        return results

    def predict_image(self, file_path: str) -> str:
        """Predict the class of a single image."""
        prediction = self.classifier.predict_image(file_path)

        print(f"\nPredicted class: {prediction}")

        return prediction

    def run_stage_1(self) -> None:
        """Run Stage 1 EDA workflow."""
        self.show_summary()
        self.generate_eda()

    def run_stage_2(self) -> None:
        """Run Stage 2 classification workflow."""
        self.train_model()

    def run_full_pipeline(self) -> None:
        """Run Stage 1 and Stage 2 together."""
        self.run_stage_1()
        self.run_stage_2()