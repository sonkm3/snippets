import asyncio
import machine

import network
import rp2
import time


def setup_wifi():
    network.hostname('micropython-demo')
    rp2.country('JP')

    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect('PyConJP2024', 'python313')

    while not (wlan.isconnected() and \
        wlan.status() == network.STAT_GOT_IP):
        print('Waiting to connect:')
        time.sleep(1)
    print(wlan.ifconfig())


class WebServer:
    def __init__(self, host='0.0.0.0', port=80, handlers={}):
        self.host = host
        self.port = port
        self.handlers = handlers

    def default_handler(self, method, path, request_header, query_dict={}, request_body=None):
        return b'HTTP/1.0 404 Not Found\r\n\r\nNot Found'

    async def read_request(self, request):
        return (await request.readline()).decode('ascii').strip('\r\n')

    def parse_request_line(self, request_line):
        method, path, version = request_line.split(' ')
        return method, path, version

    def parse_header_line(self, header_line):
        return header_line.split(': ', 1)

    def parse_request_header_to_dict(self, header_list):
        header_dict = {}
        for header_line in header_list:
            key, value = self.parse_header_line(header_line)
            header_dict.update({key: value})
        return header_dict

    def parse_request_path(self, path):
        query_dict = {}
        if '?' in path:
            path, query_string = path.split('?', 1)
            for query_pair in query_string.split('&'):
                key, value = query_pair.split('=', 1)
                query_dict.update({key: value})
        return path, query_dict

    async def read_header(self, request):
        header_list = []
        while True:
            header_line = await self.read_request(request)
            if header_line == '':
                break
            header_list.append(header_line)
        return header_list

    async def read_request_body(self, request, content_length, charset='utf-8'):
        return (await request.read(content_length)).decode(charset)

    async def dispatch(self, request_io, response_io):
        headers = await self.read_header(request_io)
        method, path, version = self.parse_request_line(headers.pop(0))
        request_header = self.parse_request_header_to_dict(headers)
        path, query_dict = self.parse_request_path(path)

        if 'Content-Length' in request_header and int(request_header.get('Content-Length', 0)) > 0:
            request_body = await self.read_request_body(request_io, int(request_header.get('Content-Length', 0)))
        else:
            request_body = None

        handler = self.handlers.get(path, self.default_handler)
        response = handler(method, path, request_header, query_dict=query_dict, request_body=request_body)

        response_io.write(response)
        response_io.close()
        await response_io.wait_closed()

    async def serve(self):
        await asyncio.start_server(self.dispatch, self.host, self.port)


def main():
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

    handlers = {'/led_on': led_on_handler, '/led_off': led_off_handler}

    web_server = WebServer(host='0.0.0.0', port=80, handlers=handlers)
    loop = asyncio.new_event_loop()
    loop.create_task(web_server.serve())
    loop.run_forever()

setup_wifi()
main()