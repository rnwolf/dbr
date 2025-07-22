"""Application configuration settings."""

import os
from dataclasses import dataclass
from typing import Tuple


@dataclass
class AppConfig:
    """Application configuration constants."""

    # Window settings
    WINDOW_TITLE: str = "Grid Canvas Application"
    WINDOW_SIZE: Tuple[int, int] = (1400, 900)
    MIN_WINDOW_SIZE: Tuple[int, int] = (1000, 700)

    # Theme settings
    APPEARANCE_MODE: str = "dark"  # "dark", "light", "system"
    COLOR_THEME: str = "blue"  # "blue", "green", "dark-blue"

    # Grid settings
    DEFAULT_GRID_ROWS: int = 20
    DEFAULT_GRID_COLS: int = 15
    DEFAULT_CELL_SIZE: int = 100
    MIN_CELL_SIZE: int = 50
    MAX_CELL_SIZE: int = 200

    # Canvas settings
    CANVAS_BACKGROUND: str = "gray90"
    GRID_LINE_COLOR: str = "gray60"
    GRID_LINE_WIDTH: int = 1

    # Paths
    RESOURCES_PATH: str = os.path.join(os.path.dirname(__file__), "..", "resources")
    ICONS_PATH: str = os.path.join(RESOURCES_PATH, "icons")
    THEMES_PATH: str = os.path.join(RESOURCES_PATH, "themes")
