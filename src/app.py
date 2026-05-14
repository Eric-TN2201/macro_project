# Student Name:
# +  u3281913
# +   u3293786
# Unit: Software Technology 1 (8995)
# Assignment: Assignment 3 - Macroinvertebrate Image Analysis System

from pathlib import Path
import webbrowser
import tkinter as tk
from tkinter import filedialog, messagebox

from PIL import Image, ImageTk

from src.config import EDA_OUTPUT_DIR, REPORT_OUTPUT_DIR
from src.services.workflow_service import WorkflowService


class MacroApp(tk.Tk):
    """Tkinter GUI for macroinvertebrate image prediction."""

    # Maximum pixel dimensions for the image preview canvas
    PREVIEW_SIZE = (350, 350)

    def __init__(self, workflow_service: WorkflowService) -> None:
        """Initialize the GUI window and connect button actions to services."""
        super().__init__()

        # Store reference to the service layer
        self.workflow_service = workflow_service
        # Path of the image file chosen by the user; None until a file is picked
        self.selected_file: str | None = None
        # Keep a reference to the PhotoImage so it is not garbage-collected
        self.preview_image = None

        self.title("Macroinvertebrate Image Analysis System")
        self.geometry("800x600")

        # Main content area with a left navbar and right content panel
        self.main_frame = tk.Frame(self)
        self.main_frame.pack(fill="both", expand=True)

        # Left navigation bar for all main function buttons
        self.navbar_frame = tk.Frame(self.main_frame, bd=1, relief="groove", padx=10, pady=10)
        self.navbar_frame.pack(side="left", fill="y", padx=(10, 8), pady=10)

        self.navbar_title = tk.Label(
            self.navbar_frame,
            text="Functions",
            font=("Arial", 12, "bold"),
        )
        self.navbar_title.pack(anchor="w", pady=(0, 10))

        # Right panel to display title, image preview, result, and status
        self.content_frame = tk.Frame(self.main_frame)
        self.content_frame.pack(side="left", fill="both", expand=True, padx=(0, 10), pady=10)

        # Application title displayed at the top of the content panel
        self.title_label = tk.Label(
            self.content_frame,
            text="Macroinvertebrate Image Analysis System",
            font=("Arial", 18, "bold"),
        )
        self.title_label.pack(pady=15)

        # Canvas used to display the selected image preview
        self.image_canvas = tk.Canvas(
            self.content_frame,
            width=self.PREVIEW_SIZE[0],
            height=self.PREVIEW_SIZE[1],
            bg="white",
            relief="groove",
            highlightthickness=0,
        )
        self.image_canvas.pack(pady=10)
        # Placeholder text shown before any image is loaded
        self.image_canvas.create_text(
            self.PREVIEW_SIZE[0] // 2,
            self.PREVIEW_SIZE[1] // 2,
            text="No image selected",
        )

        # Label that shows the predicted class after running inference
        self.result_label = tk.Label(
            self.content_frame,
            text="Prediction result will appear here",
            font=("Arial", 14),
        )
        self.result_label.pack(pady=10)

        # Container frame that holds all workflow action buttons in the navbar
        self.button_frame = tk.Frame(self.navbar_frame)
        self.button_frame.pack(fill="x")

        # Button to show dataset summary statistics
        self.summary_button = tk.Button(
            self.button_frame,
            text="Show Dataset Summary",
            width=22,
            command=self.show_summary,
        )
        self.summary_button.pack(fill="x", pady=4)

        # Button to generate EDA outputs
        self.eda_button = tk.Button(
            self.button_frame,
            text="Generate EDA Outputs",
            width=22,
            command=self.generate_eda,
        )
        self.eda_button.pack(fill="x", pady=4)

        # Button to open EDA output folder
        self.open_eda_button = tk.Button(
            self.button_frame,
            text="Open EDA Folder",
            width=22,
            command=self.open_eda_folder,
        )
        self.open_eda_button.pack(fill="x", pady=4)

        # Button to open a file-picker dialog
        self.choose_button = tk.Button(
            self.button_frame,
            text="Choose Image",
            width=22,
            command=self.choose_image,
        )
        self.choose_button.pack(fill="x", pady=4)

        # Button to classify the currently selected image
        self.predict_button = tk.Button(
            self.button_frame,
            text="Predict Single Image",
            width=22,
            command=self.predict_image,
        )
        self.predict_button.pack(fill="x", pady=4)

        # Button to retrain the model from scratch
        self.train_button = tk.Button(
            self.button_frame,
            text="Train Model",
            width=22,
            command=self.train_model,
        )
        self.train_button.pack(fill="x", pady=4)

        # Button to open the saved classification report
        self.report_button = tk.Button(
            self.button_frame,
            text="View Classification Report",
            width=22,
            command=self.view_classification_report,
        )
        self.report_button.pack(fill="x", pady=4)

        # Button to open the saved confusion matrix image
        self.confusion_button = tk.Button(
            self.button_frame,
            text="View Confusion Matrix",
            width=22,
            command=self.view_confusion_matrix,
        )
        self.confusion_button.pack(fill="x", pady=4)

        # Button to run the full project workflow in sequence
        self.pipeline_button = tk.Button(
            self.button_frame,
            text="Run Full Pipeline",
            width=22,
            command=self.run_full_pipeline,
        )
        self.pipeline_button.pack(fill="x", pady=4)

        # Status bar at the bottom of the content panel for user feedback
        self.status_label = tk.Label(
            self.content_frame,
            text="Status: Ready",
            font=("Arial", 10),
        )
        self.status_label.pack(pady=10)

    def choose_image(self) -> None:
        """Open a file dialog and preview the selected image."""
        file_path = filedialog.askopenfilename(
            title="Select an image",
            filetypes=[
                ("Image files", "*.jpg *.jpeg *.png *.bmp"),
                ("All files", "*.*"),
            ],
        )

        # User cancelled the dialog – do nothing
        if not file_path:
            return

        # Remember the path so predict_image can use it
        self.selected_file = file_path

        # Resize image to fit the preview canvas while keeping aspect ratio
        image = Image.open(file_path)
        image.thumbnail(self.PREVIEW_SIZE)

        # Convert to Tkinter-compatible format and display on canvas
        self.preview_image = ImageTk.PhotoImage(image)
        self.image_canvas.delete("all")  # Clear any previous image
        self.image_canvas.create_image(
            self.PREVIEW_SIZE[0] // 2,
            self.PREVIEW_SIZE[1] // 2,
            image=self.preview_image,
            anchor="center",
        )

        file_name = Path(file_path).name
        self.status_label.configure(text=f"Status: Selected {file_name}")

    def predict_image(self) -> None:
        """Predict the class of the selected image."""
        # Guard: a file must be selected before prediction can run
        if not self.selected_file:
            messagebox.showwarning("No image", "Please choose an image first.")
            return

        try:
            prediction, confidence = self.workflow_service.predict_image_with_confidence(
                self.selected_file
            )

            if confidence is not None:
                self.result_label.configure(
                    text=f"Predicted class: {prediction}\nConfidence: {confidence:.2%}"
                )
            else:
                self.result_label.configure(text=f"Predicted class: {prediction}")
            self.status_label.configure(text="Status: Prediction completed")
        except Exception as error:
            messagebox.showerror("Prediction error", str(error))
            self.status_label.configure(text="Status: Prediction failed")

    def show_summary(self) -> None:
        """Generate and display a concise dataset summary in a dialog."""
        try:
            summary = self.workflow_service.show_summary()
            messagebox.showinfo("Dataset Summary", summary.to_string(index=False))
            self.status_label.configure(text="Status: Dataset summary generated")
        except Exception as error:
            messagebox.showerror("Summary error", str(error))
            self.status_label.configure(text="Status: Summary generation failed")

    def generate_eda(self) -> None:
        """Generate exploratory data analysis outputs and notify the user."""
        try:
            self.status_label.configure(text="Status: Generating EDA outputs...")
            self.update_idletasks()
            self.workflow_service.generate_eda()
            messagebox.showinfo("EDA completed", f"EDA outputs saved to:\n{EDA_OUTPUT_DIR}")
            self.status_label.configure(text="Status: EDA outputs generated")
        except Exception as error:
            messagebox.showerror("EDA error", str(error))
            self.status_label.configure(text="Status: EDA generation failed")

    def open_eda_folder(self) -> None:
        """Ensure the EDA folder exists and open it in the default file browser."""
        try:
            EDA_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
            webbrowser.open(EDA_OUTPUT_DIR.resolve().as_uri())
            messagebox.showinfo("EDA folder", "Opened EDA output folder.")
            self.status_label.configure(text="Status: Opened EDA folder")
        except Exception as error:
            messagebox.showerror("Open folder error", str(error))
            self.status_label.configure(text="Status: Failed to open EDA folder")

    def train_model(self) -> None:
        """Train the model from the GUI."""
        try:
            # Update status before the long-running training call
            self.status_label.configure(text="Status: Training model...")
            self.update_idletasks()  # Flush pending UI events so the label updates immediately

            # Run training through the service layer
            results = self.workflow_service.train_model()

            # Inform the user of the outcome with a pop-up
            messagebox.showinfo(
                "Training completed",
                f"Model training completed.\nAccuracy: {results['accuracy']:.4f}",
            )
            self.status_label.configure(text="Status: Model training completed")
        except Exception as error:
            messagebox.showerror("Training error", str(error))
            self.status_label.configure(text="Status: Training failed")

    def view_classification_report(self) -> None:
        """Open the saved classification report if it exists."""
        report_file = REPORT_OUTPUT_DIR / "classification_report.txt"
        if not report_file.exists():
            messagebox.showwarning(
                "Report not found",
                "Classification report not found. Please train the model first.",
            )
            return

        try:
            webbrowser.open(report_file.resolve().as_uri())
            messagebox.showinfo("Classification Report", "Opened classification report.")
            self.status_label.configure(text="Status: Opened classification report")
        except Exception as error:
            messagebox.showerror("Report error", str(error))
            self.status_label.configure(text="Status: Failed to open classification report")

    def view_confusion_matrix(self) -> None:
        """Open the saved confusion matrix image if it exists."""
        confusion_file = REPORT_OUTPUT_DIR / "confusion_matrix.png"
        if not confusion_file.exists():
            messagebox.showwarning(
                "Confusion matrix not found",
                "Confusion matrix not found. Please train the model first.",
            )
            return

        try:
            webbrowser.open(confusion_file.resolve().as_uri())
            messagebox.showinfo("Confusion Matrix", "Opened confusion matrix.")
            self.status_label.configure(text="Status: Opened confusion matrix")
        except Exception as error:
            messagebox.showerror("Confusion matrix error", str(error))
            self.status_label.configure(text="Status: Failed to open confusion matrix")

    def run_full_pipeline(self) -> None:
        """Run summary, EDA, and model training in a single workflow."""
        try:
            self.status_label.configure(text="Status: Running full pipeline...")
            self.update_idletasks()
            self.workflow_service.run_full_pipeline()
            messagebox.showinfo("Pipeline completed", "Full pipeline completed successfully.")
            self.status_label.configure(text="Status: Full pipeline completed")
        except Exception as error:
            messagebox.showerror("Pipeline error", str(error))
            self.status_label.configure(text="Status: Full pipeline failed")


def main() -> None:
    """Start the GUI application."""
    # Wire up the service layer then launch the Tkinter event loop
    workflow_service = WorkflowService()
    app = MacroApp(workflow_service)
    app.mainloop()


if __name__ == "__main__":
    main()