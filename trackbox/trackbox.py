import os
import sys
from threading import Thread
from time import sleep

from trackbox.display import DisplayManager
from trackbox.widgets.condition import ConditionWidget
from trackbox.widgets.clock import ClockWidget
from trackbox.widgets.odds import OddsWidget

PANEL_WIDTH = 32        # pixels per 4-module panel
NUM_PANELS = int(os.environ.get("TRACKBOX_PANELS", 15))
MODULES_PER_PANEL = 4

HIDE_CURSOR = "\033[?25l"
SHOW_CURSOR = "\033[?25h"

# (panel_index, widget_class, kwargs)
WIDGET_MAP = [
    (0,  ConditionWidget, {}),
    (1,  OddsWidget,      {"label": "WIN"}),
    (2,  OddsWidget,      {"label": "PLC"}),
    (3,  ClockWidget,     {}),
    # panels 4–14 available for future widgets
]


def init_led():
    try:
        from luma.core.interface.serial import noop, spi
        from luma.led_matrix.device import max7219

        serial = spi(port=0, device=0, gpio=noop(), bus_speed_hz=4_000_000)
        return max7219(
            serial,
            cascaded=NUM_PANELS * MODULES_PER_PANEL,
            block_orientation=-90,
            rotate=0,
        )
    except Exception:
        return None


def main():
    is_tty = sys.stdout.isatty()
    if is_tty:
        print("Trackbox running... Press Ctrl+C to stop\n")
        sys.stdout.write(HIDE_CURSOR)

    device = init_led()
    dm = DisplayManager(device)

    threads = []
    for panel_idx, WidgetClass, kwargs in WIDGET_MAP:
        slot = dm.add_slot(offset_x=panel_idx * PANEL_WIDTH, width=PANEL_WIDTH)
        w = WidgetClass(slot, **kwargs)
        t = Thread(target=w.run, daemon=True)
        threads.append(t)

    dm.start()
    for t in threads:
        t.start()

    try:
        while True:
            sleep(1)
    except KeyboardInterrupt:
        if is_tty:
            sys.stdout.write(SHOW_CURSOR)
            print("\nStopped.")
