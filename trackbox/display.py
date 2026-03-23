from threading import Lock, Thread
from time import sleep

from PIL import Image


class DisplaySlot:
    """A reservation in the display chain for one panel."""

    def __init__(self, offset_x: int, width: int, height: int = 8):
        self.offset_x = offset_x
        self.width = width
        self.height = height
        self.image = Image.new("1", (width, height))
        self.lock = Lock()


class DisplayManager:
    """Owns the LED device and composites all slots at ~20 FPS."""

    def __init__(self, device):
        self.device = device
        self.slots: list[DisplaySlot] = []
        self._thread = Thread(target=self._render_loop, daemon=True)

    def add_slot(self, offset_x: int, width: int) -> DisplaySlot:
        slot = DisplaySlot(offset_x=offset_x, width=width)
        self.slots.append(slot)
        return slot

    def start(self):
        self._thread.start()

    def _render_loop(self):
        if self.device is None:
            return
        framebuffer = Image.new("1", (self.device.width, self.device.height))
        while True:
            for slot in self.slots:
                with slot.lock:
                    framebuffer.paste(slot.image, (slot.offset_x, 0))
            self.device.display(framebuffer)
            sleep(0.05)
