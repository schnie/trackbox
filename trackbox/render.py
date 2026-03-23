from threading import Lock
from time import sleep

from PIL import Image, ImageDraw


class ScrollingText:
    """Rendering primitive that drives a scrolling text loop.

    Not a Widget — no slot, no Widget inheritance. Any widget that wants
    scrolling text creates one and passes self.push as the push callable.
    """

    def __init__(self, width: int, height: int = 8):
        self.width = width
        self.height = height
        self._text = ""
        self._lock = Lock()

    def set_text(self, text: str):
        with self._lock:
            self._text = text

    def get_text(self) -> str:
        with self._lock:
            return self._text

    def run(self, push: callable):
        """Scrolling loop. Calls push(image) at ~20 FPS. Runs until thread dies."""
        try:
            from luma.core.legacy import text as luma_text
            from luma.core.legacy.font import CP437_FONT, proportional
            font = proportional(CP437_FONT)
        except ImportError:
            font = None

        last_word = None
        buffer = None
        text_width = 0
        gap = self.width

        while True:
            word = self.get_text()

            if not word:
                push(Image.new("1", (self.width, self.height)))
                last_word = None
                sleep(0.2)
                continue

            if word != last_word:
                text_width = self._compute_text_width(word, font)
                gap = self.width
                total_width = (text_width + gap) * 2
                buffer = Image.new("1", (total_width, self.height))
                if font is not None:
                    draw = ImageDraw.Draw(buffer)
                    from luma.core.legacy import text as luma_text
                    luma_text(draw, (0, 0), word, fill="white", font=font)
                    luma_text(draw, (text_width + gap, 0), word, fill="white", font=font)
                last_word = word

            # Scroll one cycle: text width + gap
            for offset in range(0, text_width + gap):
                if self.get_text() != word:
                    break
                cropped = buffer.crop((offset, 0, offset + self.width, self.height))
                push(cropped)
                sleep(0.05)

    def _compute_text_width(self, word: str, font) -> int:
        if font is None:
            return len(word) * 6
        try:
            from luma.core.legacy import text as luma_text
            test_img = Image.new("1", (len(word) * 8 + 10, 8))
            draw = ImageDraw.Draw(test_img)
            luma_text(draw, (0, 0), word, fill="white", font=font)
            bbox = test_img.getbbox()
            if bbox:
                return bbox[2]
        except Exception:
            pass
        return len(word) * 6
