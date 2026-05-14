from pathlib import Path
import tkinter as tk
from tkinter import messagebox


def select_class_folders_dialog(
    parent: tk.Misc,
    source_dir: Path,
    class_folders: list[Path],
    initial_selected_folder: Path | None = None,
) -> list[str]:
    """Show a modal multi-select dialog and return selected class folder paths."""
    selected_paths: list[str] = []
    selector = tk.Toplevel(parent)
    selector.title("Select class folders")

    dialog_width = 520
    dialog_height = 420
    position_x = (selector.winfo_screenwidth() - dialog_width) // 2
    position_y = (selector.winfo_screenheight() - dialog_height) // 2
    selector.geometry(f"{dialog_width}x{dialog_height}+{position_x}+{position_y}")
    selector.transient(parent)
    selector.grab_set()
    # `grab_set` makes this picker modal until user confirms/cancels.

    instruction = tk.Label(
        selector,
        text=(
            "Select one or more class folders (Ctrl/Shift for multi-select):\n"
            f"Source: {source_dir}"
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

    if initial_selected_folder is not None:
        # Preserve context by preselecting the folder the user initially picked.
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

        # Return absolute folder paths, not just labels shown in the list.
        selected_paths.extend(str(class_folders[index]) for index in indices)
        selector.destroy()

    def _cancel_selection() -> None:
        selector.destroy()

    confirm_button = tk.Button(button_frame, text="Confirm", width=12, command=_confirm_selection)
    confirm_button.pack(side="right", padx=(8, 0))
    cancel_button = tk.Button(button_frame, text="Cancel", width=12, command=_cancel_selection)
    cancel_button.pack(side="right")

    parent.wait_window(selector)
    return selected_paths
