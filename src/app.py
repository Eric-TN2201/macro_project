# Student Name:
# +  u3281913
# +   u3293786
# Unit: Software Technology 1 (8995)
# Assignment: Assignment 3 - Macroinvertebrate Image Analysis System

from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox

from PIL import Image, ImageTk

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

        # Application title displayed at the top of the window
        self.title_label = tk.Label(
            self,
            text="Macroinvertebrate Image Analysis System",
            font=("Arial", 18, "bold"),
        )
        self.title_label.pack(pady=15)

        # Canvas used to display the selected image preview
        self.image_canvas = tk.Canvas(
            self,
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
            self,
            text="Prediction result will appear here",
            font=("Arial", 14),
        )
        self.result_label.pack(pady=10)

        # Container frame that holds the three action buttons
        self.button_frame = tk.Frame(self)
        self.button_frame.pack(pady=10)

        # Button to open a file-picker dialog
        self.choose_button = tk.Button(
            self.button_frame,
            text="Choose Image",
            width=18,
            command=self.choose_image,
        )
        self.choose_button.grid(row=0, column=0, padx=5)

        # Button to classify the currently selected image
        self.predict_button = tk.Button(
            self.button_frame,
            text="Predict",
            width=18,
            command=self.predict_image,
        )
        self.predict_button.grid(row=0, column=1, padx=5)

        # Button to retrain the model from scratch
        self.train_button = tk.Button(
            self.button_frame,
            text="Train Model",
            width=18,
            command=self.train_model,
        )
        self.train_button.grid(row=0, column=2, padx=5)

        # Status bar at the bottom of the window for user feedback
        self.status_label = tk.Label(
            self,
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


def main() -> None:
    """Start the GUI application."""
    # Wire up the service layer then launch the Tkinter event loop
    workflow_service = WorkflowService()
    app = MacroApp(workflow_service)
    app.mainloop()


if __name__ == "__main__":
    main()