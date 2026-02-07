```
  _                  _    _
 | |_ _ __ __ _  ___| | _| |__   _____  __
 | __| '__/ _` |/ __| |/ / '_ \ / _ \ \/ /
 | |_| | | (_| | (__|   <| |_) | (_) >  <
  \__|_|  \__,_|\___|_|\_\_.__/ \___/_/\_\
```

Reads GPIO switches on a Raspberry Pi to display the current track condition. Outputs to terminal, a state file (`/run/trackbox/condition`), and an optional MAX7219 LED matrix panel.

## GPIO Pin Map

| GPIO | Physical Pin | Condition |
|------|-------------|-----------|
| 2    | 3           | FAST      |
| 3    | 5           | GOOD      |
| 4    | 7           | SLOW      |
| 17   | 11          | SLOPPY    |
| 27   | 13          | MUDDY     |
| 22   | 15          | HEAVY     |
| 10   | 19          | FIRM      |
| 9    | 21          | HARD      |
| 11   | 23          | SOFT      |
| 0    | 27          | YIELDING  |

Switches connect each GPIO pin to GND (common ground). Pull-up resistors are enabled in software.

## Pi Setup

These steps only need to be done once on a fresh Pi.

### 1. OS image

Use Raspberry Pi Imager to flash the SD card. Set the username to `trackbox` and the hostname to `trackbox` during setup.

### 2. Enable SPI (required for LED matrix)

```bash
sudo raspi-config
```

Navigate to **Interfacing Options > SPI** and enable it. Reboot.

### 3. Set up SSH access

From your dev machine, copy your SSH key so deploys work without a password:

```bash
ssh-copy-id trackbox@trackbox
```

This assumes the Pi is reachable at hostname `trackbox`. Edit `PI_HOST` in the Makefile if yours differs.

## Deploy and Run

From your dev machine:

```bash
make deploy          # rsync code to the Pi
```

Then SSH into the Pi and run:

```bash
cd ~/trackbox
make install-service # installs the package, sets up and starts the systemd service
```

The service starts automatically on boot. To check the current condition:

```bash
cat /run/trackbox/condition
```

Or from your dev machine:

```bash
make watch-remote
```

## Updating

After making changes locally:

```bash
make deploy                                    # from dev machine
ssh trackbox@trackbox "cd ~/trackbox && make install-service"  # reinstall on Pi
```

## Make Targets

Run on the **Pi**:

| Target              | Description                                    |
|---------------------|------------------------------------------------|
| `make install`      | Install system deps and the trackbox package   |
| `make uninstall`    | Remove the trackbox package                    |
| `make install-service` | Install + set up and start the systemd service |
| `make uninstall-service` | Stop and remove the systemd service        |
| `make run`          | Run interactively (stop the service first)     |
| `make watch`        | Monitor the condition file                     |

Run on your **dev machine**:

| Target              | Description                                    |
|---------------------|------------------------------------------------|
| `make deploy`       | Rsync code to the Pi                           |
| `make dev`          | Run locally with mock GPIO                     |
| `make watch-remote` | Monitor the condition file over SSH            |
| `make clean`        | Remove build artifacts                         |

## LED Matrix (optional)

Supports a MAX7219 8x8x4 dot matrix panel connected via SPI. If the panel isn't connected or `luma.led_matrix` isn't installed, it's silently skipped.

The `block_orientation` parameter in `trackbox.py` may need adjusting (`-90`, `0`, or `90`) depending on how the modules are wired. The default is `-90`.
