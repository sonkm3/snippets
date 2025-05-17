import network
import rp2
import time


rp2.country('JP')

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect('PyConJP2024', 'python313')

while not (wlan.isconnected() and \
    wlan.status() == network.STAT_GOT_IP):
    print('Waiting to connect:')
    time.sleep(1)


print(wlan.ifconfig())