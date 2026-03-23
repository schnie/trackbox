from datetime import datetime
from time import sleep

from PIL import Image, ImageDraw

from trackbox.widget import Widget


class ClockWidget(Widget):
    """Displays the current time as HH:MM, updating every 10 seconds."""

    def run(self):
        try:
            from luma.core.legacy import text as luma_text
            from luma.core.legacy.font import CP437_FONT, proportional
            font = proportional(CP437_FONT)
        except ImportError:
            font = None

        while True:
            time_str = datetime.now().strftime("%H:%M")
            self.push(self._render(time_str, font))
            sleep(10)

    def _render(self, time_str: str, font) -> Image.Image:
        img = Image.new("1", (self.width, self.slot.height))
        if font is not None:
            draw = ImageDraw.Draw(img)
            from luma.core.legacy import text as luma_text
            luma_text(draw, (0, 0), time_str, fill="white", font=font)
        return img
