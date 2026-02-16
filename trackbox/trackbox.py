import os
import sys
import threading
from time import sleep

from gpiozero import Button

# Map GPIO pins to labels/words
switches = {
    21: "FAST",  # GPIO21 (physical pin 40)
    20: "GOOD",  # GPIO20 (physical pin 38)
    16: "SLOW",  # GPIO16 (physical pin 36)
    26: "SLOPPY",  # GPIO26 (physical pin 37)
    19: "MUDDY",  # GPIO19 (physical pin 35)
    13: "HEAVY",  # GPIO13 (physical pin 33)
    12: "SOFT",  # GPIO12 (physical pin 32)
    6: "FIRM",  # GPIO6 (physical pin 31)
    5: "HARD",  # GPIO5 (physical pin 29)
    1: "YIELDING",  # GPIO1 (physical pin 28)
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
        from luma.core.interface.serial import noop, spi
        from luma.led_matrix.device import max7219

        serial = spi(port=0, device=0, gpio=noop(), bus_speed_hz=1000000)
        return max7219(serial, cascaded=4, block_orientation=-90, rotate=0)
    except Exception:
        return None


def led_thread(device, state_holder):
    """Background thread that continuously scrolls the current state on the LED."""
    if device is None:
        return

    from luma.core.legacy import text
    from luma.core.legacy.font import CP437_FONT, proportional
    from luma.core.render import canvas
    from luma.core.virtual import viewport

    font = proportional(CP437_FONT)
    last_word = None
    last_text_width = 0
    last_gap = 32
    virtual = None

    while True:
        word = state_holder[0]

        if not word:
            device.clear()
            last_word = None
            virtual = None
            sleep(0.2)
            continue

        # Recreate virtual canvas if word changed
        if word != last_word:
            # Use a reasonable estimate: 6 pixels per character avg
            text_width = len(word) * 6
            gap = 32  # 32 pixels = ~1.6 second gap between iterations
            # Virtual canvas: [text][gap][text] for seamless looping
            virtual = viewport(device, width=(text_width + gap) * 2, height=8)
            with canvas(virtual) as draw:
                # Draw text twice with gap between
                text(draw, (0, 0), word, fill="white", font=font)
                text(draw, (text_width + gap, 0), word, fill="white", font=font)
            last_word = word
            last_text_width = text_width
            last_gap = gap

        # Scroll one cycle: text + gap
        for offset in range(0, last_text_width + last_gap):
            if state_holder[0] != word:
                break
            virtual.set_position((offset, 0))
            sleep(0.05)


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

    # Shared state for LED thread (using list so it's mutable)
    led_state = [None]

    # Start LED background thread
    if led is not None:
        thread = threading.Thread(target=led_thread, args=(led, led_state), daemon=True)
        thread.start()

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
                led_state[0] = current  # Update LED state
                last = current

            sleep(0.2)
    except KeyboardInterrupt:
        if is_tty:
            sys.stdout.write(SHOW_CURSOR)
            print("\nStopped.")
