## Group Members
-u3281913
-u3293786

## Stages
- Stage 1: Exploratory Data Analysis
- Stage 2: Predictive Analytics / Classification
- Stage 3: Application Deployment

## Main Classes
- DatasetIndexer
- EDAService
- ImagePreprocessor
- ClassifierService
- WorkflowService
- ConsoleApp
- MacroApp

## Testing
Testing evidence is documented in MANUAL_TESTING.md.

## Acknowledgement
Some image loading, preprocessing, visualisation, and classification techniques were adapted from ST1 Week 5–8 tutorial/lab activities and modified for this project.

# Macroinvertebrate Image Analysis System

This project builds a baseline image classification pipeline for freshwater
macroinvertebrate taxa.

The system supports:
- Dataset indexing from class folders
- Exploratory Data Analysis (EDA) outputs
- Baseline model training and evaluation
- Single-image prediction
- Two interfaces: console menu and Tkinter GUI

## Project Layout

.
|- data/raw/                       # Input dataset arranged by class folder
|- outputs/eda/                    # EDA CSV files and charts
|- outputs/models/                 # Trained model (.joblib)
|- outputs/reports/                # Classification report outputs
|- src/
|  |- app.py                       # Tkinter GUI entry point
|  |- console_app.py               # Menu-driven console app
|  |- main.py                      # Full pipeline entry point
|  |- config.py                    # Paths and constants
|  `- services/                    # Workflow, EDA, indexing, model services
|- requirements.txt                # Python dependencies
`- README.md

## Requirements

- Python 3.10+
- pip

Install dependencies:

python -m pip install -r requirements.txt

## Dataset Format

Place images under class directories inside data/raw:

data/raw/
|- Class_A/
|  |- img1.jpg
|  `- img2.png
`- Class_B/
	`- img3.jpeg

Supported image extensions are:
- .jpg
- .jpeg
- .png
- .bmp

## How to Run

From the repository root:

1. Run full pipeline (EDA + training)

python -m src.main

2. Run interactive console app

python -m src.console_app

3. Run GUI app

python -m src.app

## What Gets Generated

After running EDA and training, generated files are saved under outputs/.

Typical artifacts include:
- Dataset index CSV
- Dataset summary CSV
- Class counts CSV
- EDA charts
- Trained model file (macro_classifier.joblib)
- Classification report

## Notes

- Paths and global settings are defined in src/config.py.
- IMAGE_SIZE is currently configured as (128, 128).
- If prediction fails, ensure the model has been trained first.
