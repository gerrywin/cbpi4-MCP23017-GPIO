# cbpi4-MCP23017-GPIO

CraftBeerPi 4 actor plugin for the MCP23017 I2C GPIO expander.

Version 0.0.1

Tested target: CraftBeerPi 4.7.x / Winter Bock.

## Features

- MCP23017 via I2C
- 16 output pins: `PA0` - `PA7` and `PB0` - `PB7`
- Configurable I2C address, default `0x20`
- Configurable I2C bus, default `1`
- Actor option for inverted output logic
- Actor option for power/PWM-style control
- Custom pin label per actor with `PinName`
- Optional global pin names in CBPi settings: `MCP23017_PA0_Name` ... `MCP23017_PB7_Name`

## MCP23017 I2C addresses

The address depends on A0, A1 and A2:

| A2 | A1 | A0 | Address |
|---:|---:|---:|:--------|
| 0 | 0 | 0 | `0x20` |
| 0 | 0 | 1 | `0x21` |
| 0 | 1 | 0 | `0x22` |
| 0 | 1 | 1 | `0x23` |
| 1 | 0 | 0 | `0x24` |
| 1 | 0 | 1 | `0x25` |
| 1 | 1 | 0 | `0x26` |
| 1 | 1 | 1 | `0x27` |

Check your device with:

```bash
sudo i2cdetect -y 1
```

## Installation from GitHub

```bash
pipx runpip cbpi4 install git+https://github.com/gerrywin/cbpi4-MCP23017-GPIO.git
cbpi add cbpi4-MCP23017-GPIO
```

Enable CraftBeerPi autostart if it is not already enabled:

```bash
cbpi autostart status
cbpi autostart on
```

After installation or plugin changes, reboot the Raspberry Pi:

```bash
sudo reboot
```

## Local installation / development

```bash
git clone https://github.com/gerrywin/cbpi4-MCP23017-GPIO.git
cd cbpi4-MCP23017-GPIO
pipx runpip cbpi4 install --force-reinstall .
cbpi add cbpi4-MCP23017-GPIO
sudo reboot
```

## Service information

On CraftBeerPi 4.7.x the systemd service is called:

```bash
craftbeerpi
```

The service exists after enabling autostart:

```bash
cbpi autostart on
```

If autostart is enabled and you do not want to reboot, you can restart CraftBeerPi with:

```bash
sudo systemctl restart craftbeerpi
```

Check the service with:

```bash
sudo systemctl status craftbeerpi
```

## Configuration

In CraftBeerPi settings:

- `MCP23017_Address`: default `0x20`
- `MCP23017_Bus`: default `1`
- `MCP23017_PA0_Name` ... `MCP23017_PB7_Name`: optional global display names

In each actor:

- `GPIO`: hardware pin, e.g. `PA0` or `PB3`
- `PinName`: optional custom display name for this actor, e.g. `Pump 1`, `Heater`, `Mash Valve`
- `Inverted`: `No` for active-high, `Yes` for active-low
- `SamplingTime`: base interval for power control

Note: The hardware pin dropdown remains `PA0` - `PB7`. CraftBeerPi builds this dropdown when the plugin class is loaded. Use `PinName` to name the actor connection clearly.

## Recommended Git repository structure

```text
cbpi4-MCP23017-GPIO/
├── .gitignore
├── LICENSE
├── MANIFEST.in
├── README.md
├── setup.py
└── cbpi4_MCP23017_GPIO/
    └── __init__.py
```

Do not commit build artifacts:

```text
build/
dist/
*.egg-info/
__pycache__/
*.pyc
```

## License

MIT
