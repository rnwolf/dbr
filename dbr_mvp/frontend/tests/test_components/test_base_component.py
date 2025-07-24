"""Base component class for reusable UI components."""

import customtkinter as ctk
from abc import ABC, abstractmethod
from typing import Any, Dict


class BaseComponent(ctk.CTkFrame, ABC):
    """Abstract base class for reusable UI components."""

    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.parent = parent
        self._data: Dict[str, Any] = {}

        self._setup_component()
        self._create_widgets()
        self._setup_layout()
        self._bind_events()

    @abstractmethod
    def _setup_component(self) -> None:
        """Setup component-specific configuration."""
        pass

    @abstractmethod
    def _create_widgets(self) -> None:
        """Create component widgets."""
        pass

    @abstractmethod
    def _setup_layout(self) -> None:
        """Setup component layout."""
        pass

    def _bind_events(self) -> None:
        """Bind component events. Override if needed."""
        pass

    def get_data(self) -> Dict[str, Any]:
        """Get component data."""
        return self._data.copy()

    def set_data(self, data: Dict[str, Any]) -> None:
        """Set component data."""
        self._data.update(data)
        self._update_display()

    @abstractmethod
    def _update_display(self) -> None:
        """Update component display based on data."""
        pass

    def validate(self) -> bool:
        """Validate component data. Override if needed."""
        return True

    def reset(self) -> None:
        """Reset component to initial state."""
        self._data.clear()
        self._update_display()
