import os
import sys
from threading import Thread
from time import sleep

from trackbox.render import ScrollingText
from trackbox.widget import Widget

# Map GPIO pins to labels
switches = {
    21: "FAST",     # GPIO21 (physical pin 40)
    20: "GOOD",     # GPIO20 (physical pin 38)
    16: "SLOW",     # GPIO16 (physical pin 36)
    26: "SLOPPY",   # GPIO26 (physical pin 37)
    19: "MUDDY",    # GPIO19 (physical pin 35)
    13: "HEAVY",    # GPIO13 (physical pin 33)
    12: "SOFT",     # GPIO12 (physical pin 32)
    6:  "FIRM",     # GPIO6  (physical pin 31)
    5:  "HARD",     # GPIO5  (physical pin 29)
    1:  "YIELDING", # GPIO1  (physical pin 28)
}

STATE_DIR = "/run/trackbox"
STATE_FILE = os.path.join(STATE_DIR, "condition")
CLEAR_WIDTH = 20


def _read_switches(buttons: dict) -> str | None:
    for pin, btn in buttons.items():
        if btn.is_pressed:
            return switches[pin]
    return None


def _display_state(word: str | None):
    text = word or ""
    if sys.stdout.isatty():
        sys.stdout.write(f"\r{text:<{CLEAR_WIDTH}}")
        sys.stdout.flush()
    if os.path.isdir(STATE_DIR):
        with open(STATE_FILE, "w") as f:
            f.write(text + "\n")


class ConditionWidget(Widget):
    """Reads GPIO track-condition switches and scrolls the active condition."""

    def run(self):
        try:
            from gpiozero import Button
            buttons = {pin: Button(pin, pull_up=True) for pin in switches}
        except Exception:
            buttons = {}

        scroller = ScrollingText(width=self.width)
        scroll_thread = Thread(target=scroller.run, args=(self.push,), daemon=True)
        scroll_thread.start()

        last = None
        while True:
            current = _read_switches(buttons)
            if current != last:
                scroller.set_text(current or "")
                _display_state(current)
                last = current
            sleep(0.2)
