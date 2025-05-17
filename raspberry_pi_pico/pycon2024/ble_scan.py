import aioble
import asyncio


async def ble_scan_task():
   async with aioble.scan(duration_ms=5000) as scanner:
      async for result in scanner:
            print(result, result.name(), result.rssi, result.services())

asyncio.run(ble_scan_task())