Student Name:
+  u3281913
+   u3293786
Unit: Software Technology 1 (8995)
Assignment: Assignment 3 - Macroinvertebrate Image Analysis System

## Manual Test Cases

| Scenario | Input | Expected Result | Actual Result | Evidence |
|---|---|---|---|---|
| Launch GUI | `python -m src.app` | Tkinter window opens | GUI window opened | ![GUI launch](docs/screenshots/gui_launch.png) |
| Generate EDA outputs in GUI | Click `Generate EDA Outputs` | EDA charts and CSV files are generated | EDA outputs generated successfully | ![Generate EDA](docs/screenshots/gui_generate_eda.png) |
| View EDA output in GUI | Click `View EDA Output` | Existing EDA outputs are displayed inside the app | EDA output displayed in-app | ![View EDA output](docs/screenshots/gui_view_eda_output.png) |
| Train model in GUI | Click `Train Model` | Model trains, accuracy is shown, and reports are saved | Training completed message displayed | ![GUI train model](docs/screenshots/gui_train_model.png) |
| View classification report | Click `Report View`, then choose `Classification Report` in the report selector | Classification report is shown inside the app | Classification report displayed in-app | ![Classification report](docs/screenshots/gui_classification_report.png) |
| View confusion matrix | Click `Report View`, then choose `Confusion Report` in the report selector | Confusion matrix is shown inside the app | Confusion matrix displayed in-app | ![Confusion matrix](docs/screenshots/gui_confusion_matrix.png) |
| Select class folders | Click `Select Class Folders`, choose a parent folder, then select at least 3 class folders | Selected class folders are listed in the prediction panel | Selected folders displayed | ![Select class folders](docs/screenshots/gui_select_class_folders.png) |
| Predict selected folders | Click `Predict Selected Folders` after selecting at least 3 folders | Sample cards show actual folder, image, predicted class, and confidence | Prediction cards displayed | ![Predict selected folders](docs/screenshots/gui_predict_selected_folders.png) |
| Select fewer than 3 class folders | In the folder picker, select fewer than 3 items and click `Confirm` | Warning message asks user to select at least 3 class folders | Warning message displayed | ![Minimum folders warning](docs/screenshots/gui_minimum_folders_warning.png) |

