# Manual Testing Evidence

## Project

**Project Title:** Macroinvertebrate Image Analysis System  
**Unit:** Software Technology 1 (8995)  
**Assessment:** Assignment 3 Group Project

## Testing Purpose

The purpose of this manual testing record is to show that the application was tested across the main workflow, including Stage 1 EDA, Stage 2 classification, Stage 3 deployment, and common error scenarios.

The rubric rewards readable code, useful documentation, and clear evidence of testing. Therefore, this file records the expected and actual outcomes for the main system functions.

## Test Environment

| Item                  | Description                 |
|-----------------------|-----------------------------|
| Operating System      | Windows / Mac / Linux       |
| Python Version        | Python 3.10+                |
| Dataset Location      | `data/raw/`                 |
| Console Entry Point   | `python -m src.console_app` |
| GUI Entry Point       | `python -m src.app`         |
| Full Pipeline Entry Point | `python -m src.main`    |

## Dataset Preparation

Before testing, the dataset should be placed inside:

```text
data/raw/
```

Expected folder structure:

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

Each folder name is used as the class label.

## Manual Test Cases

| Test ID | Scenario                        | Input / Action        | Expected Result | Actual Result | Status |
|---------|---------------------------------|---|---|---|---|
| T01     | Run full pipeline               | `python -m src.main` | Stage 1 EDA and Stage 2 training run successfully | Pipeline completed successfully | Passed |
| T02     | Launch console app              | `python -m src.console_app` | Console menu is displayed | Console menu displayed | Passed |
| T03     | Show dataset summary            | Console option `1` | Dataset summary and class counts are printed | Dataset summary and class counts printed | Passed |
| T04     | Generate EDA outputs            | Console option `2` | EDA charts and CSV files are generated in `outputs/eda/` | EDA outputs generated successfully | Passed |
| T05     | Train classifier                | Console option `3` | Model trains, accuracy is printed, reports are saved | Model training completed successfully | Passed |
| T06     | Predict valid image in console  | Console option `4` with valid image path | Predicted class is displayed | Predicted class displayed | Passed |
| T07     | Run full pipeline from console  | Console option `5` | EDA and model training run together | Full pipeline completed successfully | Passed |
| T08     | Exit console app                | Console option `6` | Program exits cleanly | Program exited cleanly | Passed |
| T09     | Invalid menu option | Enter `9` | Invalid option message is displayed | Invalid option message displayed | Passed |
| T10     | Empty image path                | Console option `4`, then press Enter | Message says image path cannot be empty | Empty path message displayed | Passed |
| T11     | Invalid image path              | Console option `4`, enter `wrong_file.jpg` | File error is displayed | File error displayed | Passed |
| T12     | Unsupported file type | Enter a `.txt` file path | Unsupported file type error is displayed | Unsupported file type error displayed | Passed |
| T13     | Predict before training         | Remove or rename model file, then predict | Error asks user to train model first | Friendly error message displayed | Passed |
| T14     | Launch GUI                      | `python -m src.app` | Tkinter window opens | GUI window opened | Passed |
| T15     | GUI image selection             | Click `Choose Image` and select image | Image appears in preview canvas | Image preview displayed | Passed |
| T16 | GUI prediction | Click `Predict` after selecting image | Predicted class and confidence are displayed | Prediction and confidence displayed | Passed |
| T17 | GUI predict without image | Click `Predict` before choosing image | Warning dialog asks user to choose image first | Warning dialog displayed | Passed |
| T18 | GUI train model | Click `Train Model` | Model trains and accuracy message appears | Training completed message displayed | Passed |

## Output Files Checked

The following files were checked after running the system:

### Stage 1 EDA Outputs

```text
outputs/eda/dataset_index.csv
outputs/eda/dataset_summary.csv
outputs/eda/class_counts.csv
outputs/eda/class_distribution.png
outputs/eda/image_size_distribution.png
outputs/eda/sample_grid.png
```

### Stage 2 Model and Evaluation Outputs

```text
outputs/models/macro_classifier.joblib
outputs/reports/classification_report.txt
outputs/reports/confusion_matrix.png
```

## Evidence Captured
- Console menu screenshot
- Dataset summary screenshot
- EDA output folder screenshot
- `class_distribution.png`
- `image_size_distribution.png`
- `sample_grid.png`
- Model training result screenshot
- `classification_report.txt` screenshot
- `confusion_matrix.png`
- Console prediction result screenshot
- Invalid input error screenshot
- GUI image preview screenshot
- GUI prediction result screenshot

## Error Handling Evidence

The application was tested with invalid or incomplete inputs.

| Error Scenario            | Expected Behaviour |
|---------------------------|---------------------------------------|
| Missing dataset folder    | Display clear dataset folder error |
| Empty image path          | Display message that image path cannot be empty |
| Invalid image path        | Display file not found error |
| Unsupported file type     | Display supported file extensions |
| Missing trained model     | Ask user to train model first |
| Invalid menu option       | Ask user to choose a number from 1 to 6 |
| GUI predict without image | Show warning dialog |

## Testing Summary

The manual tests confirm that:

- The dataset can be indexed successfully.
- EDA outputs are generated correctly.
- The classifier can be trained and evaluated.
- The trained model can be saved and reused.
- The console application supports the full workflow.
- The Tkinter GUI allows image selection, preview, prediction, and confidence display.
- Error handling is present for common invalid input scenarios.

Overall, the system works as an integrated application rather than a collection of separate scripts.
