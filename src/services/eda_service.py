from pathlib import Path

import cv2
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


class EDAService:
    """Generate exploratory data analysis outputs for the image dataset."""

    def __init__(self, dataframe: pd.DataFrame, output_dir: Path) -> None:
        self.dataframe = dataframe
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def build_summary(self) -> pd.DataFrame:
        """Create and save dataset summary."""
        summary = {
            "total_images": [len(self.dataframe)],
            "total_classes": [self.dataframe["label"].nunique()],
            "mean_width": [round(self.dataframe["width"].mean(), 2)],
            "mean_height": [round(self.dataframe["height"].mean(), 2)],
            "min_width": [self.dataframe["width"].min()],
            "max_width": [self.dataframe["width"].max()],
            "min_height": [self.dataframe["height"].min()],
            "max_height": [self.dataframe["height"].max()],
        }

        summary_df = pd.DataFrame(summary)
        summary_df.to_csv(self.output_dir / "dataset_summary.csv", index=False)

        class_counts = self.dataframe["label"].value_counts().reset_index()
        class_counts.columns = ["label", "image_count"]
        class_counts.to_csv(self.output_dir / "class_counts.csv", index=False)

        return summary_df

    def save_class_distribution(self) -> Path:
        """Save class distribution chart."""
        output_path = self.output_dir / "class_distribution.png"

        plt.figure(figsize=(12, 6))
        order = self.dataframe["label"].value_counts().index

        sns.countplot(data=self.dataframe, x="label", order=order)
        plt.title("Macroinvertebrate Images per Class")
        plt.xlabel("Class")
        plt.ylabel("Number of Images")
        plt.xticks(rotation=90)
        plt.tight_layout()
        plt.savefig(output_path)
        plt.close()

        return output_path

    def save_image_size_distribution(self) -> Path:
        """Save image width and height distribution chart."""
        output_path = self.output_dir / "image_size_distribution.png"

        fig, axes = plt.subplots(1, 2, figsize=(12, 5))

        sns.histplot(self.dataframe["width"], bins=20, ax=axes[0])
        axes[0].set_title("Image Width Distribution")
        axes[0].set_xlabel("Width")

        sns.histplot(self.dataframe["height"], bins=20, ax=axes[1])
        axes[1].set_title("Image Height Distribution")
        axes[1].set_xlabel("Height")

        plt.tight_layout()
        plt.savefig(output_path)
        plt.close()

        return output_path

    def save_sample_grid(self, sample_count: int = 9) -> Path:
        """Save a grid of sample images."""
        output_path = self.output_dir / "sample_grid.png"

        sample_df = self.dataframe.sample(
            min(sample_count, len(self.dataframe)),
            random_state=42,
        )

        cols = 3
        rows = 3

        fig, axes = plt.subplots(rows, cols, figsize=(10, 10))
        axes = axes.flatten()

        for ax, (_, row) in zip(axes, sample_df.iterrows()):
            image = cv2.imread(row["file_path"])

            if image is None:
                ax.axis("off")
                continue

            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            ax.imshow(image)
            ax.set_title(row["label"])
            ax.axis("off")

        for ax in axes[len(sample_df):]:
            ax.axis("off")

        plt.tight_layout()
        plt.savefig(output_path)
        plt.close()

        return output_path

    def generate_all_outputs(self) -> None:
        """Generate all EDA outputs."""
        self.build_summary()
        self.save_class_distribution()
        self.save_image_size_distribution()
        self.save_sample_grid()