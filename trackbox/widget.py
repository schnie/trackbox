from abc import ABC, abstractmethod

from PIL import Image


class Widget(ABC):
    """Abstract base class for all display widgets."""

    def __init__(self, slot):
        self.slot = slot

    @property
    def width(self) -> int:
        return self.slot.width

    def push(self, image: Image.Image):
        """Thread-safe write to this widget's slot."""
        with self.slot.lock:
            self.slot.image.paste(image, (0, 0))

    @abstractmethod
    def run(self):
        """Long-running loop. Called in a daemon thread at startup."""
        ...
