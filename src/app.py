# Student Name:
# +  u3281913
# +   u3293786
# Unit: Software Technology 1 (8995)
# Assignment: Assignment 3 - Macroinvertebrate Image Analysis System

from pathlib import Path
import csv
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from PIL import Image, ImageTk

from src.config import EDA_OUTPUT_DIR, RAW_DATA_DIR, REPORT_OUTPUT_DIR, SUPPORTED_EXTENSIONS
from src.services.workflow_service import WorkflowService
from src.utils.io.dataset_helpers import (
    list_subdirectories,
    list_valid_images,
    sibling_folders_with_images,
)
from src.utils.io.output_helpers import (
    build_eda_options,
    build_report_options,
    filter_existing_options,
    read_text_or_default,
)
from src.utils.ui.dialog_helpers import select_class_folders_dialog


class MacroApp(tk.Tk):
    """Tkinter GUI for macroinvertebrate image analysis workflows."""

    # Maximum pixel dimensions for charts/reports shown in the body panel
    BODY_IMAGE_SIZE = (1100, 700)

    def __init__(self, workflow_service: WorkflowService) -> None:
        """Initialize the GUI window and connect button actions to services."""
        super().__init__()

        # Store reference to the service layer
        self.workflow_service = workflow_service
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

        self._setup_theme()

        self.title("Macroinvertebrate Image Analysis System")
        self.configure(bg=self.colors["app_bg"])
        # Open maximized by default; fall back to fullscreen if needed.
        try:
            self.state("zoomed")
        except tk.TclError:
            self.attributes("-fullscreen", True)

        self._build_layout()
        self._build_prediction_view()
        self._build_output_view()
        self._build_navbar()

        # Show prediction view on initial load
        self._show_prediction_view()

        # Status bar at the bottom of the content panel for user feedback
        self.status_label = tk.Label(
            self.content_frame,
            text="Status: Ready",
            font=("Arial", 10),
            bg=self.colors["panel_bg"],
            fg=self.colors["text"],
        )
        self.status_label.pack(pady=10)

    def _setup_theme(self) -> None:
        """Configure shared color palette and reusable button styles."""
        # Simple color palette to improve visual clarity without changing layout.
        self.colors = {
            "app_bg": "#eaf1f8",
            "panel_bg": "#ffffff",
            "nav_bg": "#1f3b57",
            "nav_text": "#f3f7fb",
            "accent": "#2f80c2",
            "accent_hover": "#25689e",
            "text": "#22313f",
        }
        self.nav_button_style = {
            "bg": "#2d5478",
            "fg": self.colors["nav_text"],
            "activebackground": "#3b6792",
            "activeforeground": self.colors["nav_text"],
            "relief": "flat",
            "bd": 0,
        }
        self.action_button_style = {
            "bg": self.colors["accent"],
            "fg": "#ffffff",
            "activebackground": self.colors["accent_hover"],
            "activeforeground": "#ffffff",
            "relief": "flat",
            "bd": 0,
        }

    def _build_layout(self) -> None:
        """Build top-level frames shared by all UI sections."""
        # Main content area with a left navbar and right content panel
        self.main_frame = tk.Frame(self, bg=self.colors["app_bg"])
        self.main_frame.pack(fill="both", expand=True)

        # Left navigation bar for all main function buttons
        self.navbar_frame = tk.Frame(
            self.main_frame,
            bd=0,
            relief="flat",
            padx=10,
            pady=10,
            bg=self.colors["nav_bg"],
        )
        self.navbar_frame.pack(side="left", fill="y", padx=(10, 8), pady=10)

        self.navbar_title = tk.Label(
            self.navbar_frame,
            text="Functions",
            font=("Arial", 12, "bold"),
            bg=self.colors["nav_bg"],
            fg=self.colors["nav_text"],
        )
        self.navbar_title.pack(anchor="w", pady=(0, 10))

        # Right panel to display title, dynamic body content, and status
        self.content_frame = tk.Frame(self.main_frame, bg=self.colors["panel_bg"])
        self.content_frame.pack(side="left", fill="both", expand=True, padx=(0, 10), pady=10)

        # Application title displayed at the top of the content panel
        self.title_label = tk.Label(
            self.content_frame,
            text="Macroinvertebrate Image Analysis System",
            font=("Arial", 18, "bold"),
            bg=self.colors["panel_bg"],
            fg=self.colors["accent"],
        )
        self.title_label.pack(pady=15)

        # Dynamic body area; each function can switch the visible content
        self.body_frame = tk.Frame(self.content_frame, bg=self.colors["panel_bg"])
        self.body_frame.pack(fill="both", expand=True)

    def _build_prediction_view(self) -> None:
        """Build prediction view widgets (folder selection + sample cards)."""
        self.prediction_view = tk.Frame(self.body_frame, bg=self.colors["panel_bg"])

        self.result_label = tk.Label(
            self.prediction_view,
            text="Prediction results",
            font=("Arial", 14),
            bg=self.colors["panel_bg"],
            fg=self.colors["text"],
        )
        self.result_label.pack(pady=10)

        self.selected_folders_label = tk.Label(
            self.prediction_view,
            text="Selected class folders",
            font=("Arial", 11, "bold"),
            anchor="w",
            bg=self.colors["panel_bg"],
            fg=self.colors["text"],
        )
        self.selected_folders_label.pack(fill="x", padx=20)

        self.add_folder_button = tk.Button(
            self.prediction_view,
            text="Select Class Folders",
            width=24,
            command=self.select_class_folders,
            **self.action_button_style,
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

        self.sample_cards_label = tk.Label(
            self.prediction_view,
            text="Sample prediction cards",
            font=("Arial", 11, "bold"),
            anchor="w",
            bg=self.colors["panel_bg"],
            fg=self.colors["text"],
        )
        self.sample_cards_label.pack(fill="x", padx=20)

        self.sample_cards_frame = tk.Frame(self.prediction_view, bg=self.colors["panel_bg"])
        self.sample_cards_frame.pack(fill="both", expand=True, padx=20, pady=(0, 10))

        self.sample_cards_canvas = tk.Canvas(
            self.sample_cards_frame,
            relief="groove",
            bd=1,
            highlightthickness=0,
            bg="#ffffff",
        )
        self.sample_cards_scrollbar = tk.Scrollbar(
            self.sample_cards_frame,
            orient="vertical",
            command=self.sample_cards_canvas.yview,
        )
        self.sample_cards_canvas.configure(yscrollcommand=self.sample_cards_scrollbar.set)
        self.sample_cards_canvas.pack(side="left", fill="both", expand=True)
        self.sample_cards_scrollbar.pack(side="right", fill="y")

        self.sample_cards_inner = tk.Frame(self.sample_cards_canvas, bg="#ffffff")
        self.sample_cards_canvas_window = self.sample_cards_canvas.create_window(
            (0, 0),
            window=self.sample_cards_inner,
            anchor="nw",
        )
        self.sample_cards_inner.bind("<Configure>", self._on_sample_cards_inner_configure)
        self.sample_cards_canvas.bind("<Configure>", self._on_sample_cards_canvas_configure)

        self.predict_selected_main_button = tk.Button(
            self.prediction_view,
            text="Predict Selected Folders",
            width=24,
            command=self.predict_selected_folders,
            **self.action_button_style,
        )
        self.predict_selected_main_button.pack(pady=(0, 10))

        self._update_selected_folders_display()

    def _build_output_view(self) -> None:
        """Build output view widgets (text, image, and selectors)."""
        self.output_view = tk.Frame(self.body_frame, bg=self.colors["panel_bg"])

        self.output_header_frame = tk.Frame(self.output_view, bg=self.colors["panel_bg"])
        self.output_header_frame.pack(fill="x", pady=(0, 8))

        self.output_title_label = tk.Label(
            self.output_header_frame,
            text="Output",
            font=("Arial", 14, "bold"),
            bg=self.colors["panel_bg"],
            fg=self.colors["text"],
        )
        self.output_title_label.pack(side="left", anchor="w")

        self.header_controls_frame = tk.Frame(self.output_header_frame, bg=self.colors["panel_bg"])
        self.header_controls_frame.pack(side="right", anchor="e")

        self.eda_option_var = tk.StringVar(value="Select EDA output")
        self.eda_option_var.trace_add("write", self._on_eda_option_change)
        self.eda_control_frame = tk.Frame(self.header_controls_frame, bg=self.colors["panel_bg"])
        self.eda_label = tk.Label(
            self.eda_control_frame,
            text="EDA View:",
            bg=self.colors["panel_bg"],
            fg=self.colors["text"],
        )
        self.eda_label.pack(side="left", padx=(0, 8))
        self.eda_dropdown = tk.OptionMenu(self.eda_control_frame, self.eda_option_var, "Select EDA output")
        self.eda_dropdown.configure(width=28, bg="#ffffff", fg=self.colors["text"], highlightthickness=0)
        self.eda_dropdown["menu"].configure(bg="#ffffff", fg=self.colors["text"])
        self.eda_dropdown.pack(side="left")
        self.eda_dropdown.configure(state="disabled")

        self.report_option_var = tk.StringVar(value="Select report output")
        self.report_option_var.trace_add("write", self._on_report_option_change)
        self.report_control_frame = tk.Frame(self.header_controls_frame, bg=self.colors["panel_bg"])
        self.report_label = tk.Label(
            self.report_control_frame,
            text="Report View:",
            bg=self.colors["panel_bg"],
            fg=self.colors["text"],
        )
        self.report_label.pack(side="left", padx=(0, 8))
        self.report_dropdown = tk.OptionMenu(
            self.report_control_frame,
            self.report_option_var,
            "Select report output",
        )
        self.report_dropdown.configure(width=28, bg="#ffffff", fg=self.colors["text"], highlightthickness=0)
        self.report_dropdown["menu"].configure(bg="#ffffff", fg=self.colors["text"])
        self.report_dropdown.pack(side="left")
        self.report_dropdown.configure(state="disabled")

        self.output_text = tk.Text(
            self.output_view,
            height=10,
            wrap="word",
            relief="groove",
            bd=1,
            bg="#ffffff",
            fg=self.colors["text"],
            insertbackground=self.colors["text"],
        )
        self.output_text.pack(fill="both", expand=True, pady=(0, 10))
        self.output_text.configure(state="disabled")

        self.csv_table_frame = tk.Frame(self.output_view, bg=self.colors["panel_bg"])
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

        self.output_image_label = tk.Label(self.output_view, bg=self.colors["panel_bg"])
        self.output_image_label.pack()

    def _build_navbar(self) -> None:
        """Build grouped action buttons in the left navigation panel."""
        self.button_frame = tk.Frame(self.navbar_frame, bg=self.colors["nav_bg"])
        self.button_frame.pack(fill="x")

        self.prediction_section_label = tk.Label(
            self.button_frame,
            text="Prediction",
            font=("Arial", 10, "bold"),
            anchor="w",
            bg=self.colors["nav_bg"],
            fg=self.colors["nav_text"],
        )
        self.prediction_section_label.pack(fill="x", pady=(0, 4))

        self.prediction_section_frame = tk.Frame(self.button_frame, bg=self.colors["nav_bg"])
        self.prediction_section_frame.pack(fill="x", pady=(0, 10))

        self.predict_view_button = tk.Button(
            self.prediction_section_frame,
            text="Predict View",
            width=22,
            command=self._show_prediction_view,
            **self.nav_button_style,
        )
        self.predict_view_button.pack(fill="x", pady=4)

        self.eda_section_label = tk.Label(
            self.button_frame,
            text="EDA",
            font=("Arial", 10, "bold"),
            anchor="w",
            bg=self.colors["nav_bg"],
            fg=self.colors["nav_text"],
        )
        self.eda_section_label.pack(fill="x", pady=(0, 4))

        self.eda_section_frame = tk.Frame(self.button_frame, bg=self.colors["nav_bg"])
        self.eda_section_frame.pack(fill="x", pady=(0, 10))

        self.eda_button = tk.Button(
            self.eda_section_frame,
            text="Generate EDA Outputs",
            width=22,
            command=self.generate_eda,
            **self.nav_button_style,
        )
        self.eda_button.pack(fill="x", pady=4)

        self.view_eda_button = tk.Button(
            self.eda_section_frame,
            text="View EDA Output",
            width=22,
            command=self.view_eda_output,
            **self.nav_button_style,
        )
        self.view_eda_button.pack(fill="x", pady=4)

        self.model_section_label = tk.Label(
            self.button_frame,
            text="Training And Reports",
            font=("Arial", 10, "bold"),
            anchor="w",
            bg=self.colors["nav_bg"],
            fg=self.colors["nav_text"],
        )
        self.model_section_label.pack(fill="x", pady=(0, 4))

        self.model_section_frame = tk.Frame(self.button_frame, bg=self.colors["nav_bg"])
        self.model_section_frame.pack(fill="x", pady=(0, 10))

        self.train_button = tk.Button(
            self.model_section_frame,
            text="Train Model",
            width=22,
            command=self.train_model,
            **self.nav_button_style,
        )
        self.train_button.pack(fill="x", pady=4)

        self.report_view_button = tk.Button(
            self.model_section_frame,
            text="Report View",
            width=22,
            command=self.view_classification_report,
            **self.nav_button_style,
        )
        self.report_view_button.pack(fill="x", pady=4)

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
            # Keep dropdown inert when the current output view is not EDA-related.
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
            # Keep dropdown inert when the current output view is not report-related.
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
            # Report text mode: show text pane and hide image content.
            report_text = output_path.read_text(encoding="utf-8") if output_path.exists() else "Report file not found."
            self._clear_csv_table()
            self.csv_table_frame.pack_forget()
            self.output_text.pack(fill="both", expand=True, pady=(0, 10))
            self._display_body_image(None)
            self._update_output_text(report_text)
            return

        # Image mode (confusion report): hide text pane to focus on matrix image.
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
        class_folders = list_subdirectories(selected_dir)
        initial_selected_folder: Path | None = None

        # Case 2: selected path is itself a class folder; offer sibling class folders too.
        if not class_folders:
            direct_images = list_valid_images(selected_dir, SUPPORTED_EXTENSIONS)
            if not direct_images:
                messagebox.showwarning(
                    "No class folders",
                    f"No class folders or valid images were found in:\n{selected_dir}",
                )
                return

            usable_siblings = sibling_folders_with_images(selected_dir, SUPPORTED_EXTENSIONS)

            class_folders = usable_siblings if usable_siblings else [selected_dir]
            initial_selected_folder = selected_dir

        if not class_folders:
            messagebox.showwarning(
                "No class folders",
                f"No usable class folders were found in:\n{selected_dir}",
            )
            return

        selected_paths = select_class_folders_dialog(
            parent=self,
            source_dir=selected_dir,
            class_folders=class_folders,
            initial_selected_folder=initial_selected_folder,
        )

        # Empty result means user canceled or closed the picker.
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

            valid_images = list_valid_images(class_folder, SUPPORTED_EXTENSIONS)

            if not valid_images:
                self._add_prediction_sample_card(
                    folder_name=folder_name,
                    image_path=None,
                    prediction=None,
                    confidence=None,
                    error_message="No valid image files found in this folder.",
                )
                continue

            # Use the first valid file so results stay deterministic across runs.
            image_path = valid_images[0]
            prediction, confidence = self.workflow_service.predict_image_with_confidence(
                str(image_path)
            )

            self._add_prediction_sample_card(
                folder_name=folder_name,
                image_path=image_path,
                prediction=prediction,
                confidence=confidence,
            )

        self.status_label.configure(text="Status: Completed selected-folder predictions")

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

        eda_options = build_eda_options(EDA_OUTPUT_DIR)
        available_eda_options = filter_existing_options(eda_options)

        image_options = [option[0] for option in available_eda_options.values() if option[1] == "image"]
        chart_path = image_options[0] if image_options else None
        return body_text, available_eda_options, chart_path

    def train_model(self) -> None:
        """Train the model from the GUI."""
        try:
            # Update status before the long-running training call
            self.status_label.configure(text="Status: Training model...")
            self.update_idletasks()  # Flush pending UI events so the label updates immediately

            # Run training through the service layer
            results = self.workflow_service.train_model()

            report_file = REPORT_OUTPUT_DIR / "classification_report.txt"
            report_text = read_text_or_default(report_file, default=str(results["report"]))

            report_options = build_report_options(REPORT_OUTPUT_DIR)
            available_report_options = filter_existing_options(report_options)
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
            report_options = build_report_options(REPORT_OUTPUT_DIR)
            available_report_options = filter_existing_options(report_options)
            report_text = read_text_or_default(report_file, default="")
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

def main() -> None:
    """Start the GUI application."""
    # Wire up the service layer then launch the Tkinter event loop
    workflow_service = WorkflowService()
    app = MacroApp(workflow_service)
    app.mainloop()


if __name__ == "__main__":
    main()