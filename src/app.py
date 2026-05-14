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

from src.config import EDA_OUTPUT_DIR, RAW_DATA_DIR, REPORT_OUTPUT_DIR, SUPPORTED_EXTENSIONS
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
        # User-selected class folders for multi-folder prediction workflow.
        self.selected_folders: list[str] = []
        # Keep references to PhotoImage objects so they are not garbage-collected
        self.preview_image = None
        self.body_image = None
        self.prediction_sample_images: list[ImageTk.PhotoImage] = []
        # Store available EDA output options (label -> (path, type)).
        self.eda_output_options: dict[str, tuple[Path, str]] = {}
        # Store available report output options (label -> (path, type)).
        self.report_output_options: dict[str, tuple[Path, str]] = {}
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

        # Prediction view (folder selection + prediction results)
        self.prediction_view = tk.Frame(self.body_frame)

        self.result_label = tk.Label(
            self.prediction_view,
            text="Prediction results",
            font=("Arial", 14),
        )
        self.result_label.pack(pady=10)

        # On-screen list of user-selected class folders.
        self.selected_folders_label = tk.Label(
            self.prediction_view,
            text="Selected class folders",
            font=("Arial", 11, "bold"),
            anchor="w",
        )
        self.selected_folders_label.pack(fill="x", padx=20)

        # Main-view action button for selecting class folders.
        self.add_folder_button = tk.Button(
            self.prediction_view,
            text="Select Class Folders",
            width=24,
            command=self.select_class_folders,
        )
        self.add_folder_button.pack(pady=(0, 10))

        self.selected_folders_text = tk.Text(
            self.prediction_view,
            height=6,
            wrap="word",
            relief="groove",
            bd=1,
        )
        self.selected_folders_text.pack(fill="x", padx=20, pady=(0, 10))
        self.selected_folders_text.configure(state="disabled")

        # Visual cards area to show sample image + prediction details for each class folder.
        self.sample_cards_label = tk.Label(
            self.prediction_view,
            text="Sample prediction cards",
            font=("Arial", 11, "bold"),
            anchor="w",
        )
        self.sample_cards_label.pack(fill="x", padx=20)

        self.sample_cards_frame = tk.Frame(self.prediction_view)
        self.sample_cards_frame.pack(fill="both", expand=True, padx=20, pady=(0, 10))

        self.sample_cards_canvas = tk.Canvas(
            self.sample_cards_frame,
            relief="groove",
            bd=1,
            highlightthickness=0,
        )
        self.sample_cards_scrollbar = tk.Scrollbar(
            self.sample_cards_frame,
            orient="vertical",
            command=self.sample_cards_canvas.yview,
        )
        self.sample_cards_canvas.configure(yscrollcommand=self.sample_cards_scrollbar.set)
        self.sample_cards_canvas.pack(side="left", fill="both", expand=True)
        self.sample_cards_scrollbar.pack(side="right", fill="y")

        self.sample_cards_inner = tk.Frame(self.sample_cards_canvas)
        self.sample_cards_canvas_window = self.sample_cards_canvas.create_window(
            (0, 0),
            window=self.sample_cards_inner,
            anchor="nw",
        )
        self.sample_cards_inner.bind("<Configure>", self._on_sample_cards_inner_configure)
        self.sample_cards_canvas.bind("<Configure>", self._on_sample_cards_canvas_configure)

        # Main-view action button for running predictions on selected folders.
        self.predict_selected_main_button = tk.Button(
            self.prediction_view,
            text="Predict Selected Folders",
            width=24,
            command=self.predict_selected_folders,
        )
        self.predict_selected_main_button.pack(pady=(0, 10))

        self._update_selected_folders_display()

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

        self.header_controls_frame = tk.Frame(self.output_header_frame)
        self.header_controls_frame.pack(side="right", anchor="e")

        # EDA controls (shown only on EDA view)
        self.eda_option_var = tk.StringVar(value="Select EDA output")
        self.eda_option_var.trace_add("write", self._on_eda_option_change)
        self.eda_control_frame = tk.Frame(self.header_controls_frame)
        self.eda_label = tk.Label(self.eda_control_frame, text="EDA View:")
        self.eda_label.pack(side="left", padx=(0, 8))
        self.eda_dropdown = tk.OptionMenu(self.eda_control_frame, self.eda_option_var, "Select EDA output")
        self.eda_dropdown.configure(width=28)
        self.eda_dropdown.pack(side="left")
        self.eda_dropdown.configure(state="disabled")

        # Report controls (shown only on report view)
        self.report_option_var = tk.StringVar(value="Select report output")
        self.report_option_var.trace_add("write", self._on_report_option_change)
        self.report_control_frame = tk.Frame(self.header_controls_frame)
        self.report_label = tk.Label(self.report_control_frame, text="Report View:")
        self.report_label.pack(side="left", padx=(0, 8))
        self.report_dropdown = tk.OptionMenu(
            self.report_control_frame,
            self.report_option_var,
            "Select report output",
        )
        self.report_dropdown.configure(width=28)
        self.report_dropdown.pack(side="left")
        self.report_dropdown.configure(state="disabled")

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

        # Container frame that holds grouped workflow action buttons in the navbar
        self.button_frame = tk.Frame(self.navbar_frame)
        self.button_frame.pack(fill="x")

        # Prediction section
        self.prediction_section_label = tk.Label(
            self.button_frame,
            text="Prediction",
            font=("Arial", 10, "bold"),
            anchor="w",
        )
        self.prediction_section_label.pack(fill="x", pady=(0, 4))

        self.prediction_section_frame = tk.Frame(self.button_frame)
        self.prediction_section_frame.pack(fill="x", pady=(0, 10))

        self.predict_view_button = tk.Button(
            self.prediction_section_frame,
            text="Predict View",
            width=22,
            command=self._show_prediction_view,
        )
        self.predict_view_button.pack(fill="x", pady=4)

        # EDA section
        self.eda_section_label = tk.Label(
            self.button_frame,
            text="EDA",
            font=("Arial", 10, "bold"),
            anchor="w",
        )
        self.eda_section_label.pack(fill="x", pady=(0, 4))

        self.eda_section_frame = tk.Frame(self.button_frame)
        self.eda_section_frame.pack(fill="x", pady=(0, 10))

        # Button to generate EDA outputs
        self.eda_button = tk.Button(
            self.eda_section_frame,
            text="Generate EDA Outputs",
            width=22,
            command=self.generate_eda,
        )
        self.eda_button.pack(fill="x", pady=4)

        # Button to view previously generated EDA outputs in the UI
        self.view_eda_button = tk.Button(
            self.eda_section_frame,
            text="View EDA Output",
            width=22,
            command=self.view_eda_output,
        )
        self.view_eda_button.pack(fill="x", pady=4)

        # Training and reports section
        self.model_section_label = tk.Label(
            self.button_frame,
            text="Training And Reports",
            font=("Arial", 10, "bold"),
            anchor="w",
        )
        self.model_section_label.pack(fill="x", pady=(0, 4))

        self.model_section_frame = tk.Frame(self.button_frame)
        self.model_section_frame.pack(fill="x", pady=(0, 10))

        # Button to retrain the model from scratch
        self.train_button = tk.Button(
            self.model_section_frame,
            text="Train Model",
            width=22,
            command=self.train_model,
        )
        self.train_button.pack(fill="x", pady=4)

        self.report_view_button = tk.Button(
            self.model_section_frame,
            text="Report View",
            width=22,
            command=self.view_classification_report,
        )
        self.report_view_button.pack(fill="x", pady=4)

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

    def _update_selected_folders_display(self) -> None:
        """Render selected class folder names in the prediction view."""
        self.selected_folders_text.configure(state="normal")
        self.selected_folders_text.delete("1.0", tk.END)

        if not self.selected_folders:
            self.selected_folders_text.insert("1.0", "No class folders selected.")
        else:
            folder_lines = [f"{index + 1}. {Path(path).name}" for index, path in enumerate(self.selected_folders)]
            self.selected_folders_text.insert("1.0", "\n".join(folder_lines))

        self.selected_folders_text.configure(state="disabled")

    def _on_sample_cards_inner_configure(self, _: tk.Event) -> None:
        """Update canvas scroll region when sample cards content changes."""
        self.sample_cards_canvas.configure(scrollregion=self.sample_cards_canvas.bbox("all"))

    def _on_sample_cards_canvas_configure(self, event: tk.Event) -> None:
        """Keep sample cards frame width synced to the visible canvas width."""
        self.sample_cards_canvas.itemconfigure(self.sample_cards_canvas_window, width=event.width)

    def _clear_prediction_sample_cards(self) -> None:
        """Remove existing sample prediction cards from the body view."""
        for widget in self.sample_cards_inner.winfo_children():
            widget.destroy()
        self.prediction_sample_images.clear()

    def _add_prediction_sample_card(
        self,
        folder_name: str,
        image_path: Path | None,
        prediction: str | None,
        confidence: float | None,
        error_message: str | None = None,
    ) -> None:
        """Create one visual card with sample image and prediction details."""
        card = tk.Frame(self.sample_cards_inner, relief="groove", bd=1, padx=10, pady=10)
        card.pack(fill="x", padx=8, pady=6)

        preview_label = tk.Label(card, width=220, height=160, bg="#f5f5f5")
        preview_label.pack(side="left", padx=(0, 12))

        details: list[str] = [f"Actual folder: {folder_name}"]
        if image_path is None or not image_path.exists():
            details.append("Image file: N/A")
            details.append(f"Result: {error_message or 'No valid image found.'}")
        else:
            sample_image = Image.open(image_path)
            sample_image.thumbnail((220, 160))
            preview_photo = ImageTk.PhotoImage(sample_image)
            self.prediction_sample_images.append(preview_photo)
            preview_label.configure(image=preview_photo)

            details.append(f"Image file: {image_path.name}")
            details.append(f"Predicted class: {prediction if prediction is not None else 'N/A'}")
            details.append(
                f"Confidence: {confidence:.2%}" if confidence is not None else "Confidence: N/A"
            )

        details_label = tk.Label(
            card,
            text="\n".join(details),
            justify="left",
            anchor="w",
            font=("Arial", 10),
        )
        details_label.pack(side="left", fill="x", expand=True)

    def _show_output_view(
        self,
        title: str,
        body_text: str,
        image_path: Path | None = None,
        eda_options: dict[str, tuple[Path, str]] | None = None,
        report_options: dict[str, tuple[Path, str]] | None = None,
    ) -> None:
        """Display text output and optionally an image in the body panel."""
        self.prediction_view.pack_forget()
        self.output_title_label.configure(text=title)
        self.output_base_text = body_text

        self._update_output_text(body_text)

        if eda_options:
            self._set_eda_options(eda_options)
            self.eda_control_frame.pack(side="right", anchor="e")
            self.eda_dropdown.configure(state="normal")
        else:
            self.eda_output_options.clear()
            self.eda_control_frame.pack_forget()
            self.eda_dropdown.configure(state="disabled")
            self.eda_option_var.set("N/A")
            menu = self.eda_dropdown["menu"]
            menu.delete(0, "end")
            menu.add_command(label="N/A", command=tk._setit(self.eda_option_var, "N/A"))

        if report_options:
            self._set_report_options(report_options)
            self.report_control_frame.pack(side="right", anchor="e")
            self.report_dropdown.configure(state="normal")
        else:
            self.report_output_options.clear()
            self.report_control_frame.pack_forget()
            self.report_dropdown.configure(state="disabled")
            self.report_option_var.set("N/A")
            report_menu = self.report_dropdown["menu"]
            report_menu.delete(0, "end")
            report_menu.add_command(label="N/A", command=tk._setit(self.report_option_var, "N/A"))

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

    def _set_report_options(self, options: dict[str, tuple[Path, str]]) -> None:
        """Populate the report dropdown with available report outputs."""
        self.report_output_options = options
        menu = self.report_dropdown["menu"]
        menu.delete(0, "end")

        for option_name in options:
            menu.add_command(label=option_name, command=tk._setit(self.report_option_var, option_name))

        first_option = next(iter(options), "Select report output")
        self.report_option_var.set(first_option)

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

    def _on_report_option_change(self, *_: object) -> None:
        """Update body content when the selected report dropdown option changes."""
        selected_option = self.report_option_var.get()
        option_data = self.report_output_options.get(selected_option)
        if option_data is None:
            return

        output_path, output_type = option_data
        if output_type == "text":
            report_text = output_path.read_text(encoding="utf-8") if output_path.exists() else "Report file not found."
            self._clear_csv_table()
            self.csv_table_frame.pack_forget()
            self.output_text.pack(fill="both", expand=True, pady=(0, 10))
            self._display_body_image(None)
            self._update_output_text(report_text)
            return

        self._clear_csv_table()
        self.csv_table_frame.pack_forget()
        self.output_text.pack_forget()
        self._update_output_text("")
        self._display_body_image(output_path)

    def select_class_folders(self) -> None:
        """Select class folders from any location (single folder or parent folder)."""
        default_parent = RAW_DATA_DIR if RAW_DATA_DIR.exists() else Path.home()
        selected_parent = filedialog.askdirectory(
            title="Select a class folder or a parent folder",
            initialdir=str(default_parent),
        )
        if not selected_parent:
            return

        selected_dir = Path(selected_parent)

        # Case 1: selected path is a parent folder that contains class subfolders.
        class_folders = sorted(path for path in selected_dir.iterdir() if path.is_dir())
        initial_selected_folder: Path | None = None

        # Case 2: selected path is itself a class folder; offer sibling class folders too.
        if not class_folders:
            direct_images = [
                path
                for path in selected_dir.iterdir()
                if path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS
            ]
            if not direct_images:
                messagebox.showwarning(
                    "No class folders",
                    f"No class folders or valid images were found in:\n{selected_dir}",
                )
                return

            sibling_candidates = sorted(path for path in selected_dir.parent.iterdir() if path.is_dir())
            usable_siblings = []
            for folder in sibling_candidates:
                has_valid_image = any(
                    file_path.is_file() and file_path.suffix.lower() in SUPPORTED_EXTENSIONS
                    for file_path in folder.iterdir()
                )
                if has_valid_image:
                    usable_siblings.append(folder)

            class_folders = usable_siblings if usable_siblings else [selected_dir]
            initial_selected_folder = selected_dir

        if not class_folders:
            messagebox.showwarning(
                "No class folders",
                f"No usable class folders were found in:\n{selected_dir}",
            )
            return

        # Multi-select dialog for choosing class folders in one step.
        selected_paths: list[str] = []
        selector = tk.Toplevel(self)
        selector.title("Select class folders")
        dialog_width = 520
        dialog_height = 420
        position_x = (self.winfo_screenwidth() - dialog_width) // 2
        position_y = (self.winfo_screenheight() - dialog_height) // 2
        selector.geometry(f"{dialog_width}x{dialog_height}+{position_x}+{position_y}")
        selector.transient(self)
        selector.grab_set()

        instruction = tk.Label(
            selector,
            text=(
                "Select one or more class folders (Ctrl/Shift for multi-select):\n"
                f"Source: {selected_dir}"
            ),
            anchor="w",
            justify="left",
        )
        instruction.pack(fill="x", padx=12, pady=(12, 6))

        list_frame = tk.Frame(selector)
        list_frame.pack(fill="both", expand=True, padx=12, pady=(0, 10))

        folder_listbox = tk.Listbox(list_frame, selectmode=tk.EXTENDED)
        folder_scrollbar = tk.Scrollbar(list_frame, orient="vertical", command=folder_listbox.yview)
        folder_listbox.configure(yscrollcommand=folder_scrollbar.set)
        folder_listbox.pack(side="left", fill="both", expand=True)
        folder_scrollbar.pack(side="right", fill="y")

        for folder in class_folders:
            folder_listbox.insert(tk.END, folder.name)

        # If user picked a direct class folder, preselect it in the list for convenience.
        if initial_selected_folder is not None:
            for index, folder in enumerate(class_folders):
                if folder == initial_selected_folder:
                    folder_listbox.selection_set(index)
                    folder_listbox.see(index)
                    break

        button_frame = tk.Frame(selector)
        button_frame.pack(fill="x", padx=12, pady=(0, 12))

        def _confirm_selection() -> None:
            indices = folder_listbox.curselection()
            if not indices:
                messagebox.showwarning(
                    "No folders selected",
                    "Please select at least one class folder.",
                    parent=selector,
                )
                return

            selected_paths.extend(str(class_folders[index]) for index in indices)
            selector.destroy()

        def _cancel_selection() -> None:
            selector.destroy()

        confirm_button = tk.Button(button_frame, text="Confirm", width=12, command=_confirm_selection)
        confirm_button.pack(side="right", padx=(8, 0))
        cancel_button = tk.Button(button_frame, text="Cancel", width=12, command=_cancel_selection)
        cancel_button.pack(side="right")

        self.wait_window(selector)

        if not selected_paths:
            return

        self.selected_folders = selected_paths
        selected_count = len(self.selected_folders)

        self._show_prediction_view()
        self._update_selected_folders_display()
        self._clear_prediction_sample_cards()
        self.status_label.configure(text=f"Status: Selected {selected_count} class folder(s)")

    def predict_selected_folders(self) -> None:
        """Predict one sample image from each manually selected class folder."""
        if len(self.selected_folders) < 3:
            messagebox.showwarning(
                "Not enough selected folders",
                "Please select at least 3 class folders before prediction.",
            )
            return

        self._show_prediction_view()
        self.status_label.configure(text="Status: Predicting selected folders...")
        self.update_idletasks()
        self._clear_prediction_sample_cards()

        for folder_path in self.selected_folders:
            class_folder = Path(folder_path)
            folder_name = class_folder.name

            if not class_folder.exists() or not class_folder.is_dir():
                self._add_prediction_sample_card(
                    folder_name=folder_name,
                    image_path=None,
                    prediction=None,
                    confidence=None,
                    error_message="Folder is missing or not accessible.",
                )
                continue

            valid_images = sorted(
                path
                for path in class_folder.iterdir()
                if path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS
            )

            if not valid_images:
                self._add_prediction_sample_card(
                    folder_name=folder_name,
                    image_path=None,
                    prediction=None,
                    confidence=None,
                    error_message="No valid image files found in this folder.",
                )
                continue

            image_path = valid_images[0]
            prediction, confidence = self.workflow_service.predict_image_with_confidence(
                str(image_path)
            )

            confidence_text = "N/A"
            if confidence is not None:
                confidence_text = f"{confidence:.2%}"

            self._add_prediction_sample_card(
                folder_name=folder_name,
                image_path=image_path,
                prediction=prediction,
                confidence=confidence,
            )

        self.status_label.configure(text="Status: Completed selected-folder predictions")

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

            body_text, available_eda_options, chart_path = self._build_eda_view_payload(
                "EDA outputs generated successfully."
            )
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

    def view_eda_output(self) -> None:
        """Show existing EDA outputs in the output panel without regenerating files."""
        try:
            body_text, available_eda_options, chart_path = self._build_eda_view_payload(
                "Showing existing EDA outputs."
            )

            if not available_eda_options:
                messagebox.showwarning(
                    "No EDA outputs",
                    "No EDA outputs found. Please generate EDA outputs first.",
                )
                self._show_output_view("EDA Outputs", body_text)
                self.status_label.configure(text="Status: No EDA outputs found")
                return

            self._show_output_view(
                "EDA Outputs",
                body_text,
                chart_path,
                available_eda_options,
            )
            messagebox.showinfo("EDA Outputs", "Loaded available EDA outputs.")
            self.status_label.configure(text="Status: EDA outputs loaded")
        except Exception as error:
            messagebox.showerror("EDA view error", str(error))
            self.status_label.configure(text="Status: Failed to load EDA outputs")

    def _build_eda_view_payload(
        self,
        intro_text: str,
    ) -> tuple[str, dict[str, tuple[Path, str]], Path | None]:
        """Collect EDA files and construct body text, dropdown options, and default image."""
        generated_files = [
            EDA_OUTPUT_DIR / "dataset_summary.csv",
            EDA_OUTPUT_DIR / "class_counts.csv",
            EDA_OUTPUT_DIR / "class_distribution.png",
            EDA_OUTPUT_DIR / "image_size_distribution.png",
            EDA_OUTPUT_DIR / "sample_grid.png",
        ]
        available = [file_path.name for file_path in generated_files if file_path.exists()]
        body_text = f"{intro_text}\n\nAvailable files:\n"
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
        return body_text, available_eda_options, chart_path

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

            report_file = REPORT_OUTPUT_DIR / "classification_report.txt"
            report_text = (
                report_file.read_text(encoding="utf-8")
                if report_file.exists()
                else str(results["report"])
            )

            report_options = {
                "Classification Report": (REPORT_OUTPUT_DIR / "classification_report.txt", "text"),
                "Confusion Report": (REPORT_OUTPUT_DIR / "confusion_matrix.png", "image"),
            }
            available_report_options = {
                name: option for name, option in report_options.items() if option[0].exists()
            }
            self._show_output_view(
                "Report View",
                report_text,
                report_options=available_report_options,
            )

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
        """Show report view in-app with selectable classification and confusion outputs."""
        report_file = REPORT_OUTPUT_DIR / "classification_report.txt"
        confusion_file = REPORT_OUTPUT_DIR / "confusion_matrix.png"
        if not report_file.exists() and not confusion_file.exists():
            messagebox.showwarning(
                "Report not found",
                "No report outputs found. Please train the model first.",
            )
            return

        try:
            report_options = {
                "Classification Report": (REPORT_OUTPUT_DIR / "classification_report.txt", "text"),
                "Confusion Report": (REPORT_OUTPUT_DIR / "confusion_matrix.png", "image"),
            }
            available_report_options = {
                name: option for name, option in report_options.items() if option[0].exists()
            }
            report_text = report_file.read_text(encoding="utf-8") if report_file.exists() else ""
            self._show_output_view(
                "Report View",
                report_text,
                report_options=available_report_options,
            )
            messagebox.showinfo("Report View", "Loaded report view.")
            self.status_label.configure(text="Status: Loaded report view")
        except Exception as error:
            messagebox.showerror("Report error", str(error))
            self.status_label.configure(text="Status: Failed to load report view")

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
                "",
                confusion_file,
            )
            messagebox.showinfo("Confusion Matrix", "Loaded confusion matrix view.")
            self.status_label.configure(text="Status: Loaded confusion matrix view")
        except Exception as error:
            messagebox.showerror("Confusion matrix error", str(error))
            self.status_label.configure(text="Status: Failed to load confusion matrix view")

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