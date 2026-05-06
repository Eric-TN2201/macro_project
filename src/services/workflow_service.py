import pandas as pd

from src.config import EDA_OUTPUT_DIR
from src.services.dataset_indexer import DatasetIndexer
from src.services.eda_service import EDAService


class WorkflowService:
    """Coordinate the main project workflow."""

    def __init__(self) -> None:
        self.indexer = DatasetIndexer()
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

    def run_stage_1(self) -> None:
        """Run Stage 1 EDA workflow."""
        self.show_summary()
        self.generate_eda()