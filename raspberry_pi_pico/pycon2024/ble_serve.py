import asyncio
import aioble
import bluetooth
import machine

import struct

# https://www.bluetooth.com/specifications/assigned-numbers/
_ENV_SENSE_UUID = bluetooth.UUID(0x181A) # Environmental Sensing Service 0x181A Environmental Sensing Service
_ENV_SENSE_TEMP_UUID = bluetooth.UUID(0x2A6E) # Temperature characteristic 0x2A6E Temperature
_GENERIC_THERMOMETER = const(0x0300) # Generic Thermometer appearance 0x00C 0x0300 to 0x033F Thermometer

_ADV_INTERVAL_US = const(250_000)

# --- ここまでおなじ ---

# GATTサーバーの登録
temp_service = aioble.Service(_ENV_SENSE_UUID)
temp_characteristic = aioble.Characteristic(temp_service, _ENV_SENSE_TEMP_UUID, read=True, notify=True)
aioble.register_services(temp_service)

temp_adc = machine.ADC(4) # RP2040内蔵の温度計は5つ目のADコンバーターに接続されています

def _encode_tem(temp_deg_c):
    return struct.pack("<h", int(temp_deg_c * 100))

def _get_temp():
    v = (3.3/65535) * temp_adc.read_u16()
    return 27 - (v - 0.706)/0.001721

# GATTサーバーとしてCPUの温度を1秒ごとに更新する
async def sensor_task():
    while True:
        temp_characteristic.write(_encode_temp(_get_temp()), send_update=True)
        await asyncio.sleep_ms(1_000)

async def peripheral_task():
    while True:
        async with await aioble.advertise(interval_us=_ADV_INTERVAL_US, name="temperature sensor", services=[_ENV_SENSE_UUID], appearance=_GENERIC_THERMOMETER,) as connection:
            print("Connection from", connection.device)
            await connection.disconnected(timeout_ms=None)

async def main():
    task_sensor_update = asyncio.create_task(sensor_task())
    task_peripheral = asyncio.create_task(peripheral_task())
    await asyncio.gather(task_sensor_update, task_peripheral)

asyncio.run(main())