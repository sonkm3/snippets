import aioble
import asyncio
import bluetooth


# https://www.bluetooth.com/specifications/assigned-numbers/
_ENV_SENSE_UUID = bluetooth.UUID(0x181A) # Environmental Sensing Service 0x181A Environmental Sensing Service
_ENV_SENSE_TEMP_UUID = bluetooth.UUID(0x2A6E) # Temperature characteristic 0x2A6E Temperature
_GENERIC_THERMOMETER = const(0x0300) # Generic Thermometer appearance 0x00C 0x0300 to 0x033F Thermometer

_ADV_INTERVAL_US = const(250_000)

temp_service = aioble.Service(_ENV_SENSE_UUID)

aioble.register_services(temp_service)

async def instance1_task():
   while True:
      async with await aioble.advertise(interval_us=_ADV_INTERVAL_US, name="temperature sensor", services=[_ENV_SENSE_UUID], appearance=_GENERIC_THERMOMETER, manufacturer=(0xabcd, b"1234")) as connection:
         print("Connection from", connection.device)
         await connection.disconnected(timeout_ms=None)

asyncio.run(instance1_task())