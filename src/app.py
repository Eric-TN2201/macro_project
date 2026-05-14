# Student Name:
# +  u3281913
# +   u3293786
# Unit: Software Technology 1 (8995)
# Assignment: Assignment 3 - Macroinvertebrate Image Analysis System

from pathlib import Path
import csv
import webbrowser
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from PIL import Image, ImageTk

from src.config import EDA_OUTPUT_DIR, REPORT_OUTPUT_DIR
from src.services.workflow_service import WorkflowService


class MacroApp(tk.Tk):
    """Tkinter GUI for macroinvertebrate image analysis workflows."""

    # Maximum pixel dimensions for the image preview canvas
    PREVIEW_SIZE = (520, 520)
    # Maximum pixel dimensions for charts/reports shown in the body panel
    BODY_IMAGE_SIZE = (1100, 700)

    def __init__(self, workflow_service: WorkflowService) -> None:
        """Initialize the GUI window and connect button actions to services."""
        super().__init__()

        # Store reference to the service layer
        self.workflow_service = workflow_service
        # Path of the image file chosen by the user; None until a file is picked
        self.selected_file: str | None = None
        # Keep references to PhotoImage objects so they are not garbage-collected
        self.preview_image = None
        self.body_image = None
        # Store available EDA output options (label -> (path, type)).
        self.eda_output_options: dict[str, tuple[Path, str]] = {}
        self.output_base_text = ""

        self.title("Macroinvertebrate Image Analysis System")
        # Open maximized by default; fall back to fullscreen if needed.
        try:
            self.state("zoomed")
        except tk.TclError:
            self.attributes("-fullscreen", True)

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

        # Right panel to display title, dynamic body content, and status
        self.content_frame = tk.Frame(self.main_frame)
        self.content_frame.pack(side="left", fill="both", expand=True, padx=(0, 10), pady=10)

        # Application title displayed at the top of the content panel
        self.title_label = tk.Label(
            self.content_frame,
            text="Macroinvertebrate Image Analysis System",
            font=("Arial", 18, "bold"),
        )
        self.title_label.pack(pady=15)

        # Dynamic body area; each function can switch the visible content
        self.body_frame = tk.Frame(self.content_frame)
        self.body_frame.pack(fill="both", expand=True)

        # Prediction view (image preview + predicted class)
        self.prediction_view = tk.Frame(self.body_frame)
        self.image_canvas = tk.Canvas(
            self.prediction_view,
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
            self.prediction_view,
            text="Prediction result will appear here",
            font=("Arial", 14),
        )
        self.result_label.pack(pady=10)

        # Output view (summary/report text + optional chart image)
        self.output_view = tk.Frame(self.body_frame)

        # Fixed header keeps title on the left and options on the top-right.
        self.output_header_frame = tk.Frame(self.output_view)
        self.output_header_frame.pack(fill="x", pady=(0, 8))

        self.output_title_label = tk.Label(
            self.output_header_frame,
            text="Output",
            font=("Arial", 14, "bold"),
        )
        self.output_title_label.pack(side="left", anchor="w")

        # EDA controls (shown only on the EDA output screen)
        self.eda_option_var = tk.StringVar(value="Select EDA output")
        self.eda_option_var.trace_add("write", self._on_eda_option_change)
        self.eda_control_frame = tk.Frame(self.output_header_frame)
        self.eda_control_frame.pack(side="right", anchor="e")
        self.eda_label = tk.Label(self.eda_control_frame, text="EDA View:")
        self.eda_label.pack(side="left", padx=(0, 8))
        self.eda_dropdown = tk.OptionMenu(self.eda_control_frame, self.eda_option_var, "Select EDA output")
        self.eda_dropdown.configure(width=28)
        self.eda_dropdown.pack(side="left")
        self.eda_dropdown.configure(state="disabled")

        self.output_text = tk.Text(
            self.output_view,
            height=10,
            wrap="word",
            relief="groove",
            bd=1,
        )
        self.output_text.pack(fill="both", expand=True, pady=(0, 10))
        self.output_text.configure(state="disabled")

        # Table area for CSV previews.
        self.csv_table_frame = tk.Frame(self.output_view)
        self.csv_table = ttk.Treeview(self.csv_table_frame, show="headings")
        self.csv_scroll_y = ttk.Scrollbar(
            self.csv_table_frame,
            orient="vertical",
            command=self.csv_table.yview,
        )
        self.csv_scroll_x = ttk.Scrollbar(
            self.csv_table_frame,
            orient="horizontal",
            command=self.csv_table.xview,
        )
        self.csv_table.configure(
            yscrollcommand=self.csv_scroll_y.set,
            xscrollcommand=self.csv_scroll_x.set,
        )
        self.csv_table.grid(row=0, column=0, sticky="nsew")
        self.csv_scroll_y.grid(row=0, column=1, sticky="ns")
        self.csv_scroll_x.grid(row=1, column=0, sticky="ew")
        self.csv_table_frame.grid_rowconfigure(0, weight=1)
        self.csv_table_frame.grid_columnconfigure(0, weight=1)

        self.output_image_label = tk.Label(self.output_view)
        self.output_image_label.pack()

        # Show prediction view on initial load
        self._show_prediction_view()

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

    def _show_prediction_view(self) -> None:
        """Display the prediction-focused body view."""
        self.output_view.pack_forget()
        self.prediction_view.pack(fill="both", expand=True)

    def _show_output_view(
        self,
        title: str,
        body_text: str,
        image_path: Path | None = None,
        eda_options: dict[str, tuple[Path, str]] | None = None,
    ) -> None:
        """Display text output and optionally an image in the body panel."""
        self.prediction_view.pack_forget()
        self.output_title_label.configure(text=title)
        self.output_base_text = body_text

        self._update_output_text(body_text)

        if eda_options:
            self._set_eda_options(eda_options)
            self.eda_dropdown.configure(state="normal")
        else:
            self.eda_output_options.clear()
            self.eda_dropdown.configure(state="disabled")
            self.eda_option_var.set("N/A")
            menu = self.eda_dropdown["menu"]
            menu.delete(0, "end")
            menu.add_command(label="N/A", command=tk._setit(self.eda_option_var, "N/A"))

        self._display_body_image(image_path)

        self.output_view.pack(fill="both", expand=True)

    def _display_body_image(self, image_path: Path | None) -> None:
        """Render an output image in the body panel if the file exists."""
        self.csv_table_frame.pack_forget()
        if image_path is not None and image_path.exists():
            chart_image = Image.open(image_path)

            # Scale image to the current available panel area for better readability.
            self.update_idletasks()
            available_width = self.output_view.winfo_width() - 40
            available_height = self.output_view.winfo_height() - 220
            target_size = (
                max(640, min(self.BODY_IMAGE_SIZE[0], available_width)),
                max(420, min(self.BODY_IMAGE_SIZE[1], available_height)),
            )

            chart_image.thumbnail(target_size)
            self.body_image = ImageTk.PhotoImage(chart_image)
            self.output_image_label.configure(image=self.body_image)
            return

        self.body_image = None
        self.output_image_label.configure(image="")

    def _clear_csv_table(self) -> None:
        """Reset CSV table contents and column definitions."""
        self.csv_table.delete(*self.csv_table.get_children())
        self.csv_table["columns"] = ()

    def _display_csv_table(self, csv_path: Path) -> None:
        """Render CSV content in a tabular view with scrollbars."""
        if not csv_path.exists():
            self._update_output_text(
                f"{self.output_base_text}\n\nCSV file not found:\n{csv_path.name}"
            )
            self._clear_csv_table()
            self.csv_table_frame.pack_forget()
            return

        with csv_path.open("r", encoding="utf-8", newline="") as file_handle:
            rows = list(csv.reader(file_handle))

        if not rows:
            self._update_output_text(
                f"{self.output_base_text}\n\nSelected output: {csv_path.name}\n\n(No rows found in this CSV file.)"
            )
            self._clear_csv_table()
            self.csv_table_frame.pack_forget()
            return

        header = rows[0]
        data_rows = rows[1:]
        self._clear_csv_table()
        self.csv_table["columns"] = tuple(header)

        for column in header:
            self.csv_table.heading(column, text=column)
            self.csv_table.column(column, width=140, minwidth=80, anchor="w")

        for row in data_rows:
            padded_row = row + [""] * (len(header) - len(row))
            self.csv_table.insert("", "end", values=padded_row[: len(header)])

        self._update_output_text(
            f"{self.output_base_text}\n\nSelected output: {csv_path.name}\n"
            f"Rows: {len(data_rows)}"
        )
        self.body_image = None
        self.output_image_label.configure(image="")
        self.csv_table_frame.pack(fill="both", expand=True, pady=(0, 10))

    def _update_output_text(self, text: str) -> None:
        """Write text content into the output text widget."""
        self.output_text.configure(state="normal")
        self.output_text.delete("1.0", tk.END)
        self.output_text.insert("1.0", text)
        self.output_text.configure(state="disabled")

    def _set_eda_options(self, options: dict[str, tuple[Path, str]]) -> None:
        """Populate the EDA dropdown with available EDA file outputs."""
        self.eda_output_options = options
        menu = self.eda_dropdown["menu"]
        menu.delete(0, "end")

        for option_name in options:
            menu.add_command(label=option_name, command=tk._setit(self.eda_option_var, option_name))

        # Select and render the first available option by default.
        first_option = next(iter(options), "Select EDA output")
        self.eda_option_var.set(first_option)

    def _on_eda_option_change(self, *_: object) -> None:
        """Update body content when the selected EDA dropdown option changes."""
        selected_option = self.eda_option_var.get()
        option_data = self.eda_output_options.get(selected_option)
        if option_data is None:
            return

        output_path, output_type = option_data
        if output_type == "csv":
            self._update_output_text(
                f"{self.output_base_text}\n\nSelected output: {selected_option}\n"
                f"Source: {output_path.name}"
            )
            self._display_csv_table(output_path)
            return

        self._clear_csv_table()
        self.csv_table_frame.pack_forget()
        self._update_output_text(
            f"{self.output_base_text}\n\nSelected output: {selected_option}\n"
            f"Source: {output_path.name}"
        )
        self._display_body_image(output_path)

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
        self._show_prediction_view()

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
        self._show_prediction_view()
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
            class_counts = self.workflow_service.load_dataframe()["label"].value_counts()
            body_text = "Dataset Summary\n\n"
            body_text += summary.to_string(index=False)
            body_text += "\n\nClass Counts\n"
            body_text += class_counts.to_string()
            self._show_output_view("Dataset Summary", body_text)
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

            generated_files = [
                EDA_OUTPUT_DIR / "dataset_summary.csv",
                EDA_OUTPUT_DIR / "class_counts.csv",
                EDA_OUTPUT_DIR / "class_distribution.png",
                EDA_OUTPUT_DIR / "image_size_distribution.png",
                EDA_OUTPUT_DIR / "sample_grid.png",
            ]
            available = [file_path.name for file_path in generated_files if file_path.exists()]
            body_text = "EDA outputs generated successfully.\n\nAvailable files:\n"
            body_text += "\n".join(f"- {name}" for name in available) if available else "No files found yet."

            eda_options = {
                "Dataset Summary (CSV)": (EDA_OUTPUT_DIR / "dataset_summary.csv", "csv"),
                "Class Counts (CSV)": (EDA_OUTPUT_DIR / "class_counts.csv", "csv"),
                "Class Distribution": (EDA_OUTPUT_DIR / "class_distribution.png", "image"),
                "Image Size Distribution": (EDA_OUTPUT_DIR / "image_size_distribution.png", "image"),
                "Sample Grid": (EDA_OUTPUT_DIR / "sample_grid.png", "image"),
            }
            available_eda_options = {
                name: option for name, option in eda_options.items() if option[0].exists()
            }

            image_options = [option[0] for option in available_eda_options.values() if option[1] == "image"]
            chart_path = image_options[0] if image_options else None
            self._show_output_view(
                "EDA Outputs",
                body_text,
                chart_path,
                available_eda_options,
            )

            messagebox.showinfo("EDA completed", f"EDA outputs saved to:\n{EDA_OUTPUT_DIR}")
            self.status_label.configure(text="Status: EDA outputs generated")
        except Exception as error:
            messagebox.showerror("EDA error", str(error))
            self.status_label.configure(text="Status: EDA generation failed")

    def open_eda_folder(self) -> None:
        """Ensure the EDA folder exists and open it in the default file browser."""
        try:
            EDA_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
            self._show_output_view(
                "Open EDA Folder",
                f"EDA folder is ready:\n{EDA_OUTPUT_DIR}\n\nThe folder has been opened in your system browser.",
            )
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

            training_text = (
                f"Model training completed successfully.\n\n"
                f"Accuracy: {results['accuracy']:.4f}\n\n"
                "Classification report:\n"
                f"{results['report']}"
            )
            matrix_path = REPORT_OUTPUT_DIR / "confusion_matrix.png"
            self._show_output_view("Training Results", training_text, matrix_path)

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
            report_text = report_file.read_text(encoding="utf-8")
            self._show_output_view("Classification Report", report_text)
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
            self._show_output_view(
                "Confusion Matrix",
                "Confusion matrix generated from the latest model training run.",
                confusion_file,
            )
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

            matrix_path = REPORT_OUTPUT_DIR / "confusion_matrix.png"
            pipeline_text = (
                "Full pipeline completed successfully.\n\n"
                "Stages run:\n"
                "- Dataset summary\n"
                "- EDA outputs\n"
                "- Model training and evaluation\n\n"
                f"Check generated outputs in:\n{EDA_OUTPUT_DIR}\n{REPORT_OUTPUT_DIR}"
            )
            self._show_output_view("Full Pipeline Results", pipeline_text, matrix_path)

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