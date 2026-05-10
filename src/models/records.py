# Student Name:
# +  u3281913
# +   u3293786
# Unit: Software Technology 1 (8995)
# Assignment: Assignment 3 - Macroinvertebrate Image Analysis System

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