from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox

from PIL import Image, ImageTk

from src.services.workflow_service import WorkflowService


class MacroApp(tk.Tk):
    """Tkinter GUI for macroinvertebrate image prediction."""

    PREVIEW_SIZE = (350, 350)

    def __init__(self, workflow_service: WorkflowService) -> None:
        super().__init__()

        self.workflow_service = workflow_service
        self.selected_file: str | None = None
        self.preview_image = None

        self.title("Macroinvertebrate Image Analysis System")
        self.geometry("800x600")

        self.title_label = tk.Label(
            self,
            text="Macroinvertebrate Image Analysis System",
            font=("Arial", 18, "bold"),
        )
        self.title_label.pack(pady=15)

        self.image_canvas = tk.Canvas(
            self,
            width=self.PREVIEW_SIZE[0],
            height=self.PREVIEW_SIZE[1],
            bg="white",
            relief="groove",
            highlightthickness=0,
        )
        self.image_canvas.pack(pady=10)
        self.image_canvas.create_text(
            self.PREVIEW_SIZE[0] // 2,
            self.PREVIEW_SIZE[1] // 2,
            text="No image selected",
        )

        self.result_label = tk.Label(
            self,
            text="Prediction result will appear here",
            font=("Arial", 14),
        )
        self.result_label.pack(pady=10)

        self.button_frame = tk.Frame(self)
        self.button_frame.pack(pady=10)

        self.choose_button = tk.Button(
            self.button_frame,
            text="Choose Image",
            width=18,
            command=self.choose_image,
        )
        self.choose_button.grid(row=0, column=0, padx=5)

        self.predict_button = tk.Button(
            self.button_frame,
            text="Predict",
            width=18,
            command=self.predict_image,
        )
        self.predict_button.grid(row=0, column=1, padx=5)

        self.train_button = tk.Button(
            self.button_frame,
            text="Train Model",
            width=18,
            command=self.train_model,
        )
        self.train_button.grid(row=0, column=2, padx=5)

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

        if not file_path:
            return

        self.selected_file = file_path

        image = Image.open(file_path)
        image.thumbnail(self.PREVIEW_SIZE)

        self.preview_image = ImageTk.PhotoImage(image)
        self.image_canvas.delete("all")
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
        if not self.selected_file:
            messagebox.showwarning("No image", "Please choose an image first.")
            return

        try:
            prediction = self.workflow_service.predict_image(self.selected_file)
            self.result_label.configure(text=f"Predicted class: {prediction}")
            self.status_label.configure(text="Status: Prediction completed")
        except Exception as error:
            messagebox.showerror("Prediction error", str(error))
            self.status_label.configure(text="Status: Prediction failed")

    def train_model(self) -> None:
        """Train the model from the GUI."""
        try:
            self.status_label.configure(text="Status: Training model...")
            self.update_idletasks()

            results = self.workflow_service.train_model()

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
    workflow_service = WorkflowService()
    app = MacroApp(workflow_service)
    app.mainloop()


if __name__ == "__main__":
    main()