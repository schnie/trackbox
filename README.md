# Trackbox

Reads GPIO switches on a Raspberry Pi to display the current track condition. Outputs to terminal, a state file (`/run/trackbox/condition`), and an optional MAX7219 LED matrix panel.

## Wiring

### Condition Switches

Each switch connects a GPIO pin to **Pin 39 (GND - common ground)**. Pull-up resistors are enabled in software.

| GPIO | Physical Pin | Condition |
|------|--------------|-----------|
| 21   | 40           | FAST      |
| 20   | 38           | GOOD      |
| 16   | 36           | SLOW      |
| 26   | 37           | SLOPPY    |
| 19   | 35           | MUDDY     |
| 13   | 33           | HEAVY     |
| 12   | 32           | SOFT      |
| 6    | 31           | FIRM      |
| 5    | 29           | HARD      |
| 1    | 28           | YIELDING  |

All switches share **Pin 39** as common ground.

### MAX7219 LED Matrix (SPI)

5-wire connection using SPI:

| Board Pin | Pi Pin      | Physical Pin |
|-----------|-------------|--------------|
| VCC       | 5V          | 2            |
| GND       | GND         | 6            |
| DIN       | GPIO10 MOSI | 19           |
| CS        | GPIO8 CE0   | 24           |
| CLK       | GPIO11 SCLK | 23           |

**Note:** GPIO7, GPIO8, GPIO10, and GPIO11 are reserved for SPI and cannot be used for switches.

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

After making changes locally, you must both deploy the files AND reinstall the package:

```bash
make deploy                                                     # copy files to Pi
ssh trackbox@trackbox "cd ~/trackbox && make install-service"  # reinstall package and restart service
```

**Important:** `make deploy` only copies source files. The service runs from the installed Python package, so you must run `make install-service` on the Pi after deploying to see your changes take effect.

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

## LED Matrix

The MAX7219 8x8x4 dot matrix panel connects via SPI (see wiring above). If the panel isn't connected or `luma.led_matrix` isn't installed, it's silently skipped.

The `block_orientation` parameter in `trackbox.py` may need adjusting (`-90`, `0`, or `90`) depending on how the modules are wired. The default is `-90`.
