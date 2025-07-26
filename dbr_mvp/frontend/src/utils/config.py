"""Application configuration settings."""

import os
from dataclasses import dataclass
from typing import Tuple


@dataclass
class AppConfig:
    """Application configuration constants."""

    # Window settings
    WINDOW_TITLE: str = "DBR Buffer Management System"
    WINDOW_SIZE: Tuple[int, int] = (1200, 800)
    MIN_WINDOW_SIZE: Tuple[int, int] = (800, 600)

    # Theme settings
    APPEARANCE_MODE: str = "dark"  # "dark", "light", "system"
    COLOR_THEME: str = "blue"  # "blue", "green", "dark-blue"

    # Paths
    RESOURCES_PATH: str = os.path.join(os.path.dirname(__file__), "..", "resources")
    ICONS_PATH: str = os.path.join(RESOURCES_PATH, "icons")
    THEMES_PATH: str = os.path.join(RESOURCES_PATH, "themes")
