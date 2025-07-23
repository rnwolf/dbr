"""
Component for displaying real-time statistics from the grid.
"""
from collections import Counter
from typing import Dict

import customtkinter as ctk

from .base_component import BaseComponent
from app.utils.event_bus import EventBus


class StatsDisplayFrame(BaseComponent):
    """A frame to display real-time statistics from the grid."""

    def __init__(self, parent: ctk.CTk, event_bus: EventBus, **kwargs: Dict) -> None:
        """Initializes the StatsDisplayFrame."""
        super().__init__(parent, **kwargs)
        self.event_bus = event_bus
        self.stats: Counter = Counter()

        self.label = ctk.CTkLabel(self, text="Live Stats:")
        self.label.pack(side="left", padx=10)

        self.stats_label = ctk.CTkLabel(self, text=self._format_stats())
        self.stats_label.pack(side="left", padx=10)

        self.event_bus.subscribe("grid_value_changed", self.handle_grid_update)

    def handle_grid_update(self, data: Dict) -> None:
        """Handles updates from the grid and refreshes the stats."""
        old_value = data.get("old_value")
        new_value = data.get("new_value")

        if old_value:
            self.stats[old_value] -= 1
            if self.stats[old_value] == 0:
                del self.stats[old_value]

        if new_value:
            self.stats[new_value] += 1

        self.stats_label.configure(text=self._format_stats())

    def _format_stats(self) -> str:
        """Formats the stats for display."""
        if not self.stats:
            return "No selections yet."
        return " | ".join(f'"{k}": {v}' for k, v in self.stats.items())
