import json
import network
import rp2
import time
import urequests


rp2.country('JP')

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect('PyConJP2024', 'python313')

while not (wlan.isconnected() and \
    wlan.status() == network.STAT_GOT_IP):
    print('Waiting to connect:')
    time.sleep(1)

print(wlan.ifconfig())

WEATHER_API_URL = 'https://api.open-meteo.com/v1/forecast?latitude=35.680959106959&longitude=139.76730676352&current=temperature_2m,wind_speed_10m'

response = urequests.get(WEATHER_API_URL)
response_body = json.loads(response.text)

for key in ['temperature_2m', 'wind_speed_10m']:
  print('key: ' + str(response_body['current'][key]))