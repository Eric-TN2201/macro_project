# records.py – data models used by the image analysis system.
from dataclasses import dataclass
from pathlib import Path


@dataclass
class ImageRecord:
    """Store metadata for one indexed macroinvertebrate image."""

    file_path: Path
    label: str
    width: int
    height: int
    channels: int