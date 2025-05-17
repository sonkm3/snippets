import network
import rp2
import time


rp2.country('JP')

wlan = network.WLAN(network.AP_IF)
wlan.config(ssid='raspberry_pi_pico_w',
            key='password')
wlan.ifconfig(('192.168.31.4', '255.255.255.0',
               '192.168.31.1', '8.8.8.8'))
wlan.active(True)

while wlan.active() == False:
   print('Waiting to active')
   time.sleep(1)
print('ready')