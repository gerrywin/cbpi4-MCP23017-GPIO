# -*- coding: utf-8 -*-
import asyncio
import logging
from smbus2 import SMBus

from cbpi.api import *
from cbpi.api.config import ConfigType

logger = logging.getLogger(__name__)

# MCP23017 register addresses, BANK=0 default layout
IODIRA = 0x00
IODIRB = 0x01
GPIOA = 0x12
GPIOB = 0x13
OLATA = 0x14
OLATB = 0x15

PINS = [f"PA{i}" for i in range(8)] + [f"PB{i}" for i in range(8)]

mcp = None


class MCP23017Board:
    def __init__(self, address=0x20, bus=1):
        self.address = address
        self.bus_no = bus
        self.bus = SMBus(bus)
        self.port_a = 0x00
        self.port_b = 0x00
        self.init_outputs()

    def init_outputs(self):
        # 0 = output, 1 = input. Configure all PA/PB pins as outputs.
        self.bus.write_byte_data(self.address, IODIRA, 0x00)
        self.bus.write_byte_data(self.address, IODIRB, 0x00)
        self.write_port("A", 0x00)
        self.write_port("B", 0x00)

    def write_port(self, port, value):
        value = value & 0xFF
        if port == "A":
            self.port_a = value
            self.bus.write_byte_data(self.address, OLATA, value)
            self.bus.write_byte_data(self.address, GPIOA, value)
        else:
            self.port_b = value
            self.bus.write_byte_data(self.address, OLATB, value)
            self.bus.write_byte_data(self.address, GPIOB, value)

    def write_pin(self, pin, value):
        pin = str(pin).upper()
        port = pin[1]
        bit = int(pin[2])
        mask = 1 << bit

        if port == "A":
            new_value = (self.port_a | mask) if value else (self.port_a & ~mask)
            self.write_port("A", new_value)
        elif port == "B":
            new_value = (self.port_b | mask) if value else (self.port_b & ~mask)
            self.write_port("B", new_value)
        else:
            raise ValueError(f"Invalid MCP23017 pin: {pin}")


def MCPActor(address, bus):
    global mcp
    logger.info(
        "***************** Start MCP23017 Actor on I2C bus %s address %s ************************",
        bus,
        hex(address),
    )
    try:
        mcp = MCP23017Board(address=address, bus=bus)
    except Exception as e:
        mcp = None
        logger.error("Could not activate MCP23017 on I2C bus %s address %s: %s", bus, hex(address), e)


class MCP23017(CBPiExtension):
    def __init__(self, cbpi):
        self.cbpi = cbpi
        self._task = asyncio.create_task(self.init_actor())

    async def init_actor(self):
        await self.MCP23017_Settings()
        address = int(self.cbpi.config.get("MCP23017_Address", "0x20"), 16)
        bus = int(self.cbpi.config.get("MCP23017_Bus", "1"))
        MCPActor(address, bus)

    async def MCP23017_Settings(self):
        try:
            plugin = await self.cbpi.plugin.load_plugin_list("cbpi4-MCP23017-GPIO")
            self.version = plugin[0].get("Version", "0.0.2") if plugin else "0.0.2"
            self.name = plugin[0].get("Name", "cbpi4-MCP23017-GPIO") if plugin else "cbpi4-MCP23017-GPIO"
        except Exception as e:
            logger.warning("Could not read MCP23017 plugin metadata: %s", e)
            self.version = "0.0.2"
            self.name = "cbpi4-MCP23017-GPIO"
        update_key = self.name + "_update"
        plugin_update = self.cbpi.config.get(update_key, None)

        settings = [
            (
                "MCP23017_Address",
                "0x20",
                "MCP23017 I2C bus address, e.g. 0x20. Change requires reboot",
            ),
            (
                "MCP23017_Bus",
                "1",
                "MCP23017 I2C bus number, usually 1 on Raspberry Pi. Change requires reboot",
            ),
        ]

        for key, default, description in settings:
            current = self.cbpi.config.get(key, None)
            if current is None:
                current = default
            if plugin_update is None or plugin_update != self.version or self.cbpi.config.get(key, None) is None:
                try:
                    await self.cbpi.config.add(
                        key,
                        current,
                        type=ConfigType.STRING,
                        description=description,
                        source=self.name,
                    )
                except Exception as e:
                    logger.warning("Unable to update config %s: %s", key, e)

        if plugin_update is None or plugin_update != self.version:
            try:
                await self.cbpi.config.add(
                    update_key,
                    self.version,
                    type=ConfigType.STRING,
                    description="MCP23017 Plugin Version",
                    source="hidden",
                )
            except Exception as e:
                logger.warning("Unable to update config: %s", e)


@parameters(
    [
        Property.Select(label="GPIO", options=PINS),
        Property.Select(label="Inverted", options=["Yes", "No"], description="No: active high; Yes: active low"),
        Property.Select(label="SamplingTime", options=[2, 5], description="Time in seconds for power base interval. Default: 5"),
    ]
)
class MCP23017Actor(CBPiActor):
    @action("Set Power", parameters=[Property.Number(label="Power", configurable=True, description="Power Setting [0-100]")])
    async def setpower(self, Power=100, **kwargs):
        self.power = int(Power)
        if self.power < 0:
            self.power = 0
        if self.power > 100:
            self.power = 100
        await self.set_power(self.power)

    async def on_start(self):
        self.power = None
        self.inverted = True if self.props.get("Inverted", "No") == "Yes" else False
        self.off_value = True if self.inverted else False
        self.on_value = False if self.inverted else True
        self.gpio = self.props.get("GPIO", "PA0").upper()
        self.sampleTime = int(self.props.get("SamplingTime", 5))
        self.state = False

        if mcp is not None:
            mcp.write_pin(self.gpio, self.off_value)
        else:
            logger.error("MCP23017 is not initialized. Actor %s cannot set GPIO %s", self.id, self.gpio)

    async def on(self, power=None):
        self.power = power if power is not None else 100
        await self.set_power(self.power)
        logger.info("ACTOR %s ON - GPIO %s", self.id, self.gpio)
        if mcp is not None:
            mcp.write_pin(self.gpio, self.on_value)
        self.state = True

    async def off(self):
        logger.info("ACTOR %s OFF - GPIO %s", self.id, self.gpio)
        if mcp is not None:
            mcp.write_pin(self.gpio, self.off_value)
        self.state = False

    def get_state(self):
        return self.state

    async def run(self):
        while self.running is True:
            if self.state is True:
                heating_time = self.sampleTime * (self.power / 100)
                wait_time = self.sampleTime - heating_time
                if heating_time > 0:
                    if mcp is not None:
                        mcp.write_pin(self.gpio, self.on_value)
                    await asyncio.sleep(heating_time)
                if wait_time > 0:
                    if mcp is not None:
                        mcp.write_pin(self.gpio, self.off_value)
                    await asyncio.sleep(wait_time)
            else:
                await asyncio.sleep(1)

    async def set_power(self, power):
        self.power = power
        await self.cbpi.actor.actor_update(self.id, power)


def setup(cbpi):
    cbpi.plugin.register("MCP23017Actor", MCP23017Actor)
    cbpi.plugin.register("MCP23017_Config", MCP23017)
    logger.info("MCP23017 GPIO plugin registered")
