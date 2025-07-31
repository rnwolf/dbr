"""
Event Bus for decoupled component communication.
"""

from typing import Any, Callable, Dict, List


class EventBus:
    """A simple event bus for decoupled communication between components."""

    def __init__(self) -> None:
        """Initializes the EventBus."""
        self._listeners: Dict[str, List[Callable[..., None]]] = {}

    def subscribe(self, event_type: str, callback: Callable[..., None]) -> None:
        """
        Subscribe to an event type.

        Args:
            event_type: The type of event to subscribe to.
            callback: The function to call when the event is published.
        """
        if event_type not in self._listeners:
            self._listeners[event_type] = []
        self._listeners[event_type].append(callback)

    def publish(self, event_type: str, *args: Any, **kwargs: Any) -> None:
        """
        Publish an event.

        Args:
            event_type: The type of event to publish.
            *args: Positional arguments to pass to the callbacks.
            **kwargs: Keyword arguments to pass to the callbacks.
        """
        if event_type in self._listeners:
            for callback in self._listeners[event_type]:
                callback(*args, **kwargs)
