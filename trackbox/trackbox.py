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


def read_switches(buttons):
    for pin, btn in buttons.items():
        if btn.is_pressed:
            return switches[pin]
    return None


HIDE_CURSOR = "\033[?25l"
SHOW_CURSOR = "\033[?25h"


def display(word):
    text = word or ""
    sys.stdout.write(f"\r{text:<{CLEAR_WIDTH}}")
    sys.stdout.flush()


def main():
    buttons = {pin: Button(pin, pull_up=True) for pin in switches}

    print("Trackbox running... Press Ctrl+C to stop\n")
    sys.stdout.write(HIDE_CURSOR)

    last = None

    try:
        while True:
            current = read_switches(buttons)

            if current != last:
                display(current)
                last = current

            sleep(0.2)
    except KeyboardInterrupt:
        sys.stdout.write(SHOW_CURSOR)
        print("\nStopped.")
