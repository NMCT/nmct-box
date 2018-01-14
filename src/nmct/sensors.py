from nmct.drivers.onewire import OneWire


def get_temperature():
    return int(OneWire()["28-0417b27173ff"].data["t"])*1e-3

