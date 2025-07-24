"""Scrollable canvas frame component with horizontal and vertical scrollbars."""

import customtkinter as ctk
import tkinter as tk


class ScrollableCanvasFrame(ctk.CTkFrame):
    """A frame containing a canvas with horizontal and vertical scrollbars."""

    def __init__(
        self, parent, canvas_width: int = 1500, canvas_height: int = 2000, **kwargs
    ):
        super().__init__(parent, **kwargs)

        self.canvas_width = canvas_width
        self.canvas_height = canvas_height

        self._setup_scrollable_canvas()
        self._bind_mouse_events()

    def _setup_scrollable_canvas(self) -> None:
        """Setup the canvas with scrollbars."""
        # Create canvas
        self.canvas = tk.Canvas(
            self,
            bg="white",
            scrollregion=(0, 0, self.canvas_width, self.canvas_height),
            highlightthickness=0,
        )

        # Create scrollbars
        self.h_scrollbar = ctk.CTkScrollbar(
            self, orientation="horizontal", command=self.canvas.xview
        )
        self.v_scrollbar = ctk.CTkScrollbar(
            self, orientation="vertical", command=self.canvas.yview
        )

        # Configure canvas scrolling
        self.canvas.configure(
            xscrollcommand=self.h_scrollbar.set, yscrollcommand=self.v_scrollbar.set
        )

        # Note: No canvas_frame needed since we're drawing directly on canvas
        self.canvas_frame = None
        self.canvas_window = None

        # Layout
        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.h_scrollbar.grid(row=1, column=0, sticky="ew")
        self.v_scrollbar.grid(row=0, column=1, sticky="ns")

        # Configure grid weights
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Canvas frame removed - drawing directly on canvas

        # Bind canvas resize
        self.canvas.bind("<Configure>", self._on_canvas_configure)

    def _bind_mouse_events(self) -> None:
        """Bind mouse wheel scrolling events."""
        # Bind mousewheel to canvas
        self.canvas.bind("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind("<Button-4>", self._on_mousewheel)
        self.canvas.bind("<Button-5>", self._on_mousewheel)

        # Bind shift+mousewheel for horizontal scrolling
        self.canvas.bind("<Shift-MouseWheel>", self._on_shift_mousewheel)

    def _on_canvas_configure(self, event) -> None:
        """Handle canvas resize events."""
        # Canvas frame removed - no need to update frame width
        pass

    def _on_mousewheel(self, event) -> None:
        """Handle vertical mouse wheel scrolling."""
        # Determine scroll direction and amount
        if event.num == 4 or event.delta > 0:
            delta = -1
        elif event.num == 5 or event.delta < 0:
            delta = 1
        else:
            return

        # Scroll the canvas
        self.canvas.yview_scroll(delta, "units")

    def _on_shift_mousewheel(self, event) -> None:
        """Handle horizontal mouse wheel scrolling (with Shift)."""
        # Determine scroll direction and amount
        if event.delta > 0:
            delta = -1
        elif event.delta < 0:
            delta = 1
        else:
            return

        # Scroll the canvas horizontally
        self.canvas.xview_scroll(delta, "units")

    def get_canvas(self) -> tk.Canvas:
        """Get the canvas widget."""
        return self.canvas

    def get_canvas_frame(self) -> ctk.CTkFrame:
        """Get the frame inside the canvas."""
        return self.canvas_frame

    def scroll_to(self, x: float = 0, y: float = 0) -> None:
        """Scroll to specific position (0-1 range)."""
        self.canvas.xview_moveto(x)
        self.canvas.yview_moveto(y)

    def update_scroll_region(self, width: int = None, height: int = None) -> None:
        """Update the scroll region of the canvas."""
        if width:
            self.canvas_width = width
        if height:
            self.canvas_height = height

        self.canvas.configure(
            scrollregion=(0, 0, self.canvas_width, self.canvas_height)
        )
