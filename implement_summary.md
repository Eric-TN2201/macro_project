# Implementation Summary

## 1. Project Title and Group Members

**Project Title:** Macroinvertebrate Image Analysis System  
**Unit:** Software Technology 1 (8995)

| Student ID    |           Main Responsibility                                         | 
|---------------|-----------------------------------------------------------------------|
| u3281913      | Technical implementation, EDA, classification, integration            |
| u3293786      | GUI build, Documentation, testing, review, presentation preparation   |

## 2. Project Goal

The goal of this project is to build a Python-based image analysis system for freshwater macroinvertebrate images. The system indexes image data, performs exploratory data analysis, trains a baseline classifier, and provides user interaction through a console application and Tkinter GUI.

## 3. System Design Overview

The project was designed as a modular object-oriented Python application. Different responsibilities were separated into different classes and modules. This makes the system easier to test, maintain, and explain.

The main workflow is:

Dataset images → Dataset indexing → EDA outputs → Image preprocessing → Model training → Model evaluation → Prediction interface

## 4. Class and Module Overview

| Class / Module        |           Responsibility                  |
|-----------------------|----------------------------------------|
| `ImageRecord`         | Stores metadata for one indexed image                                                     |
| `DatasetIndexer`      | Scans the dataset and creates a structured Pandas DataFrame                               |
| `EDAService`          | Generates summary tables, class distribution charts, image size charts, and sample grids  |
| `ImagePreprocessor`   | Loads, resizes, normalises, and flattens images                                           |
| `ClassifierService`   | Trains, evaluates, saves, and loads the classification model                              |
| `WorkflowService`     | Coordinates the full workflow across Stage 1, Stage 2, and prediction                     |
| `ConsoleApp`          | Provides a menu-driven console interface                                                  |
| `MacroApp`            | Provides a Tkinter GUI for image selection and prediction                                 |

## 5. Python Packages Used

| Package           |                           Purpose                                
|-------------------|-------------------------------------------------------------------|
| `pathlib`         | File and folder path handling                                     |
| `pandas`          | Store image metadata and create summary tables                    |
| `numpy`           | Numeric array handling for image features                         |
| `opencv-python`   | Read, resize, and preprocess images                               |
| `matplotlib`      | Create visual outputs                                             |
| `seaborn`         | Create class distribution and confusion matrix visualisations     |
| `scikit-learn`    | Train/test split, RandomForestClassifier, evaluation metrics      |
| `joblib`          | Save and load trained model                                       |
| `tkinter`         | GUI deployment                                                    |
| `Pillow`          | Display selected images in the GUI                                |

## 6. Key Features Implemented

### Stage 1: Exploratory Data Analysis

- Indexed image dataset from class folders
- Created dataset summary
- Created class counts
- Created class distribution chart
- Created image size distribution chart
- Created representative sample image grid

### Stage 2: Predictive Analytics

- Preprocessed images using grayscale, resize, normalisation, and flattening
- Trained a `RandomForestClassifier`
- Used `class_weight="balanced"` to reduce the impact of class imbalance
- Generated accuracy score, classification report, and confusion matrix
- Saved the trained model using Joblib

### Stage 3: Deployment

- Created a menu-driven console application
- Created a Tkinter GUI application
- Added image selection, preview, prediction, and confidence score
- Added error handling for invalid input and missing model files

## 7. Testing Summary

Manual testing was completed for normal and error scenarios. The testing included dataset summary generation, EDA output generation, model training, valid image prediction, invalid image path handling, unsupported file type handling, invalid menu input, and GUI prediction.

Detailed testing evidence is recorded in `MANUAL_TESTING.md`.

## 8. Screenshots or Sample Outputs

The following outputs were generated and used as evidence:

- `outputs/eda/dataset_summary.csv`
- `outputs/eda/class_counts.csv`
- `outputs/eda/class_distribution.png`
- `outputs/eda/image_size_distribution.png`
- `outputs/eda/sample_grid.png`
- `outputs/reports/classification_report.txt`
- `outputs/reports/confusion_matrix.png`
- Console app menu screenshot
- GUI prediction screenshot

## 9. Acknowledgement of Reused or Adapted Code

Some image loading, preprocessing, visualisation, and classification techniques were adapted from ST1 Week 5 to Week 8 tutorial and lab activities. The code was modified and integrated into a modular object-oriented project structure for the macroinvertebrate image analysis system.

## 10. Work Division Summary

u3281913 was mainly responsible for the technical implementation, including dataset indexing, EDA generation, image preprocessing, model training, model evaluation, application deployment, debugging, and system integration.

u3293786 was mainly responsible for project review, documentation support, manual testing, screenshot collection, presentation preparation, GUI build and workflow validation.