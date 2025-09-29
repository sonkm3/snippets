import machine
import network
import rp2
import time

from asyncwebserver import run_webserver, WebServer


WIFI_COUNTRY = ''
SSID = ''
PSK = ''

def main() -> None:
    def setup_network() -> None:
        network.hostname('micropython-demo')
        rp2.country(WIFI_COUNTRY)

        wlan = network.WLAN(network.STA_IF)
        wlan.active(True)

        wlan.connect(SSID, PSK)

        while not (wlan.isconnected() and wlan.status() == network.STAT_GOT_IP):
            print("Waiting to connect:")
            time.sleep(1)

        print(wlan.ifconfig())

    def setup_handlers() -> dict:
        led = machine.Pin('LED', machine.Pin.OUT)
        def led_on():
            led.value(1)
        
        def led_off():
            led.value(0)

        def led_on_handler(method, path, request_header, query_dict={}, request_body=None):
            led_on()
            return b'HTTP/1.0 200 OK\r\n\r\nLED ON'

        def led_off_handler(method, path, request_header, query_dict={}, request_body=None):
            led_off()
            return b'HTTP/1.0 200 OK\r\n\r\nLED OFF'

        return {'/led_on': led_on_handler, '/led_off': led_off_handler}

    setup_network()
    handlers = setup_handlers()

    web_server = WebServer(host='0.0.0.0', port=2080, handlers=handlers)
    run_webserver(web_server)


if __name__ == '__main__':
    main()
