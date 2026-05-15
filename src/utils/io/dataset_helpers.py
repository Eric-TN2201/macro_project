# Student Name:
# +  u3281913
# +   u3293786
# Unit: Software Technology 1 (8995)
# Assignment: Assignment 3 - Macroinvertebrate Image Analysis System

from pathlib import Path


def list_subdirectories(directory: Path) -> list[Path]:
    """Return direct subdirectories of a directory in sorted order."""
    return sorted(path for path in directory.iterdir() if path.is_dir())


def list_valid_images(directory: Path, extensions: tuple[str, ...]) -> list[Path]:
    """Return image files in a directory that match supported extensions."""
    return sorted(
        path
        for path in directory.iterdir()
        if path.is_file() and path.suffix.lower() in extensions
    )


def folder_has_valid_images(directory: Path, extensions: tuple[str, ...]) -> bool:
    """Check whether a folder contains at least one valid image file."""
    return any(
        file_path.is_file() and file_path.suffix.lower() in extensions
        for file_path in directory.iterdir()
    )


def sibling_folders_with_images(directory: Path, extensions: tuple[str, ...]) -> list[Path]:
    """Return sibling folders that contain valid images."""
    return [
        folder
        for folder in list_subdirectories(directory.parent)
        if folder_has_valid_images(folder, extensions)
    ]
