from time import sleep

from PIL import Image, ImageDraw

from trackbox.widget import Widget


class OddsWidget(Widget):
    """Displays odds for a given label (e.g. WIN, PLC). Placeholder implementation."""

    def __init__(self, slot, label: str = ""):
        super().__init__(slot)
        self.label = label

    def run(self):
        try:
            from luma.core.legacy import text as luma_text
            from luma.core.legacy.font import CP437_FONT, proportional
            font = proportional(CP437_FONT)
        except ImportError:
            font = None

        while True:
            # TODO: fetch odds from data source
            image = self._render(f"{self.label}:N/A", font)
            self.push(image)
            sleep(10)

    def _render(self, text_str: str, font) -> Image.Image:
        img = Image.new("1", (self.width, self.slot.height))
        if font is not None:
            draw = ImageDraw.Draw(img)
            from luma.core.legacy import text as luma_text
            luma_text(draw, (0, 0), text_str, fill="white", font=font)
        return img
