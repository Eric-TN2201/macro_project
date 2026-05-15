Student Name:
+  u3281913
+   u3293786
Unit: Software Technology 1 (8995)
Assignment: Assignment 3 - Macroinvertebrate Image Analysis System


# Macroinvertebrate Image Analysis System

## Project Goal

This project is a Python-based image analysis system for freshwater macroinvertebrate images. The system indexes image data, performs exploratory data analysis, trains a baseline image classifier, and provides user interaction through both a menu-driven console application and a Tkinter GUI.

The project was developed for Software Technology 1 (8995), Assignment 3.

## Group Members

| Student ID | Main Role |
|---|---|
| u3281913 | Technical implementation, EDA, classification, integration |
| u3293786 | Documentation, testing, review, presentation preparation |

## Main Features

- Dataset indexing from class-based image folders
- Dataset summary generation
- Class distribution analysis
- Image size distribution analysis
- Representative sample image grid
- Image preprocessing for machine learning
- Baseline image classification using RandomForestClassifier
- Class imbalance handling using `class_weight="balanced"`
- Model evaluation using accuracy, classification report, and confusion matrix
- Saved trained model using Joblib
- Menu-driven console application
- Tkinter GUI with folder-based prediction, sample cards, and confidence score
- In-app EDA and report viewers with selectable outputs

## Project Stages

### Stage 1: Exploratory Data Analysis

Stage 1 indexes the image dataset and generates useful EDA outputs.

The system creates:

- `dataset_index.csv`
- `dataset_summary.csv`
- `class_counts.csv`
- `class_distribution.png`
- `image_size_distribution.png`
- `sample_grid.png`

The EDA helps identify class imbalance and inconsistent image sizes. These findings inform the Stage 2 design, including image resizing and balanced class weighting.

### Stage 2: Predictive Analytics / Classification

Stage 2 trains a baseline image classifier.

Image preprocessing pipeline:

```text
Raw image
|   |-- utils/
|       |-- io/
|       |   |-- dataset_helpers.py
|       |   |-- output_helpers.py
|       |-- ui/
|           |-- dialog_helpers.py
→ greyscale
→ resize to 128x128
→ normalise pixel values to 0–1
→ flatten into a numeric feature vector
→ train RandomForestClassifier
```

The classifier uses:
 - Switch to a prediction view
 - Select one or more class folders
 - Preview a sample image from each selected folder
 - Predict the macroinvertebrate class for each sample
 - View the prediction confidence score
 - View EDA outputs and report outputs inside the app

- `RandomForestClassifier`
- `class_weight="balanced"`
- Train/test split
- Accuracy score
- Classification report
- Confusion matrix
- Joblib model saving

### Stage 3: Application Deployment

Stage 3 provides two user interfaces:
1. A menu-driven console application
2. A Tkinter GUI application

The application also uses shared helpers in `src.utils.io.*` and `src.utils.ui.*`.

The console application allows users to:

- Show dataset summary
- Generate EDA outputs
- Train the classifier
- Predict an image
- Run the full pipeline
- Exit the program

The GUI allows users to:

- Switch to a prediction view
- Select one or more class folders
- Preview a sample image from each selected folder
- Predict the macroinvertebrate class for each sample
- View the prediction confidence score
- View EDA outputs and report outputs inside the app

## Python Packages Used

| Package | Purpose |
|---|---|
| `pathlib` | File and folder path handling |
| `pandas` | Dataset indexing and summary tables |
| `numpy` | Numeric arrays and model feature vectors |
| `opencv-python` | Image loading, greyscale conversion, resizing, and preprocessing |
| `matplotlib` | EDA and evaluation chart generation |
| `seaborn` | Class distribution and confusion matrix visualisation |
| `scikit-learn` | Train/test split, RandomForestClassifier, and evaluation metrics |
| `joblib` | Saving and loading trained models |
| `Pillow` | Image display in the Tkinter GUI |
| `tkinter` | Desktop GUI application |

## Folder Structure

```text
macro_project/
|-- data/
|   |-- raw/
|
|-- docs/
|   |--screenshots
|
|-- outputs/
|   |-- eda/
|   |-- models/
|   |-- reports/
|
|-- src/
|   |-- config.py
|   |-- main.py
|   |-- app.py
|   |-- console_app.py
|   |
|   |-- models/
|   |   |-- records.py
|   |
|   |-- services/
|       |-- dataset_indexer.py
|       |-- eda_service.py
|       |-- image_preprocessor.py
|       |-- classifier_service.py
|       |-- workflow_service.py
|
|   |-- utils/
|       |-- io/
|       |   |-- dataset_helpers.py
|       |   |-- output_helpers.py
|       |-- ui/
|           |-- dialog_helpers.py
|
|-- README.md
|-- requirements.txt
|-- MANUAL_TESTING.md
|-- Implementation_Summary.md
```

## Dataset Setup

Place the unzipped dataset inside:

```text
data/raw/
```

The dataset should be organised by class folders:

```text
data/raw/
|-- Class_1/
|   |-- image1.jpg
|   |-- image2.jpg
|
|-- Class_2/
|   |-- image1.jpg
|   |-- image2.jpg
```

Each folder name is used as the image label.

Example:

```text
data/raw/
|-- Gammarus sp/
|-- Asellus sp/
|-- Leptophlebiidae sp/
```

## Installation Instructions

### 1. Clone the repository

```bash
git clone <repository-link>
cd macro_project
```

### 2. Create a virtual environment

#### Windows

```bash
python -m venv .venv
.venv\Scripts\activate
```

#### Mac / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

## How to Run Stage 1 and Stage 2

Run the full pipeline:

```bash
python -m src.main
```

This command runs:

```text
Stage 1: EDA generation
Stage 2: Model training and evaluation
```

Expected generated outputs:

```text
outputs/eda/
outputs/models/
outputs/reports/
```

## How to Run the Console Application

```bash
python -m src.console_app
```

Console menu:

```text
1. Show dataset summary
2. Generate EDA outputs
3. Train classifier
4. Predict an image
5. Run full pipeline
6. Exit
```

## How to Run the GUI Application

```bash
python -m src.app
```

GUI workflow:

```text
Predict View
→ Select Class Folders
→ Predict Selected Folders
→ View predicted class and confidence score
→ View report / EDA outputs in-app
```

## Generated Outputs

After running the system, the following outputs may be generated:

```text
outputs/eda/dataset_index.csv
outputs/eda/dataset_summary.csv
outputs/eda/class_counts.csv
outputs/eda/class_distribution.png
outputs/eda/image_size_distribution.png
outputs/eda/sample_grid.png

outputs/models/macro_classifier.joblib

outputs/reports/classification_report.txt
outputs/reports/confusion_matrix.png
```

## Main Classes

| Class | Responsibility |
|---|---|
| `ImageRecord` | Stores metadata for one indexed image |
| `DatasetIndexer` | Scans dataset folders and builds a structured DataFrame |
| `EDAService` | Generates dataset summaries, class charts, image size charts, and sample grids |
| `ImagePreprocessor` | Converts raw images into model-ready numeric features |
| `ClassifierService` | Trains, evaluates, saves, and loads the classifier |
| `WorkflowService` | Coordinates Stage 1, Stage 2, and prediction workflows |
| `ConsoleApp` | Provides menu-driven console interaction |
| `MacroApp` | Provides Tkinter GUI interaction |
| `src.utils.io.*` | Shared helpers for dataset, EDA, and report file handling |
| `src.utils.ui.*` | Shared helpers for GUI dialogs |

## Testing

Manual testing evidence is recorded in:

```text
MANUAL_TEST.md
```

The testing covers:

- Dataset summary generation
- EDA output generation
- Model training
- GUI folder-based prediction and report viewing
- Invalid image path handling
- Unsupported file type handling
- GUI folder selection and prediction
- GUI EDA and report output viewing

## Notes

The `data/`, `outputs/`, and trained model files should not normally be committed to GitHub because they can be large or generated locally.

Recommended `.gitignore` entries:

```gitignore
data/
outputs/
*.joblib
*.pkl
*.h5
*.keras
__pycache__/
*.pyc
```

## Acknowledgement

Some image loading, preprocessing, visualisation, and classification techniques were adapted from ST1 Week 5 to Week 8 tutorial and lab activities. The code was modified and integrated into a modular object-oriented project structure for this Assignment 3 project.
