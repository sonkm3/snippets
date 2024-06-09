import json
import network
import rp2
import time
import ubinascii
import urequests


WEATHER_API_URL = 'https://api.open-meteo.com/v1/forecast?latitude=35.680959106959&longitude=139.76730676352&current=temperature_2m,wind_speed_10m'

rp2.country('JP')

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
# wlan.config(pm = 0xa11140)

print(ubinascii.hexlify(network.WLAN().config('mac'),':').decode())
# print(wlan.config('channel'))
# print(wlan.config('essid'))
# print(wlan.config('txpower'))

wlan.connect('', '')

while not wlan.isconnected() and wlan.status() >= 0:
    print("Waiting to connect:")
    time.sleep(1)

print(wlan.ifconfig())

response = urequests.get(WEATHER_API_URL)
response_body = json.loads(response.text)

print(f"temperature_2m:{response_body['current']['temperature_2m']}")
print(f"wind_speed_10m:{response_body['current']['wind_speed_10m']}")

wlan.disconnect()
