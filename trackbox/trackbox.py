import os
import sys

from gpiozero import Button
from time import sleep

# Map GPIO pins to labels/words
switches = {
    2:  "FAST",      # GPIO2   (physical pin 3)
    3:  "GOOD",      # GPIO3   (physical pin 5)
    4:  "SLOW",      # GPIO4   (physical pin 7)
    17: "SLOPPY",    # GPIO17  (physical pin 11)
    27: "MUDDY",     # GPIO27  (physical pin 13)
    22: "HEAVY",     # GPIO22  (physical pin 15)
    10: "FIRM",      # GPIO10  (physical pin 19)
    9:  "HARD",      # GPIO9   (physical pin 21)
    11: "SOFT",      # GPIO11  (physical pin 23)
    0:  "YIELDING",  # GPIO0   (physical pin 27)
}

CLEAR_WIDTH = 20
STATE_DIR = "/run/trackbox"
STATE_FILE = os.path.join(STATE_DIR, "condition")

HIDE_CURSOR = "\033[?25l"
SHOW_CURSOR = "\033[?25h"


def read_switches(buttons):
    for pin, btn in buttons.items():
        if btn.is_pressed:
            return switches[pin]
    return None


def init_led():
    try:
        from luma.core.interface.serial import spi, noop
        from luma.led_matrix.device import max7219
        serial = spi(port=0, device=0, gpio=noop())
        return max7219(serial, cascaded=4, block_orientation=-90)
    except Exception:
        return None


def display_led(device, word):
    if device is None:
        return
    from luma.core.render import canvas
    from luma.core.legacy import text
    from luma.core.legacy.font import proportional, CP437_FONT
    with canvas(device) as draw:
        if word:
            text(draw, (0, 0), word, fill="white", font=proportional(CP437_FONT))


def display(word):
    text = word or ""
    if sys.stdout.isatty():
        sys.stdout.write(f"\r{text:<{CLEAR_WIDTH}}")
        sys.stdout.flush()
    if os.path.isdir(STATE_DIR):
        with open(STATE_FILE, "w") as f:
            f.write(text + "\n")


def main():
    buttons = {pin: Button(pin, pull_up=True) for pin in switches}
    led = init_led()

    is_tty = sys.stdout.isatty()

    if is_tty:
        print("Trackbox running... Press Ctrl+C to stop\n")
        sys.stdout.write(HIDE_CURSOR)

    last = None

    try:
        while True:
            current = read_switches(buttons)

            if current != last:
                display(current)
                display_led(led, current)
                last = current

            sleep(0.2)
    except KeyboardInterrupt:
        if is_tty:
            sys.stdout.write(SHOW_CURSOR)
            print("\nStopped.")
