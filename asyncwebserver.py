import asyncio


# https://developer.mozilla.org/ja/docs/Web/HTTP/Messages

class App:
    def __init__(self, host='0.0.0.0', port=80):
        self.host = host
        self.port = port
        self.handlers = []

    async def read_request_line(self, request):
        return (await request.readline()).decode('ascii').strip('\r\n')

    def parse_request_line(self, request_line):
        method, path, version = request_line.split(' ')
        return method, path, version

    def parse_header_line(self, header_line):
        return header_line.split(': ', 1)

    async def get_request_headers(self, request):
        header_dict = {}
        while True:
            header_line = await self.read_request_line(request)
            if header_line == '':
                break
            key, value = self.parse_header_line(header_line)
            print(f'key: {key}, value: {value}')
            header_dict[key] = value
        return header_dict

    async def get_request_body(self, request, content_length, charset='utf-8'):
        return (await request.read(content_length)).decode(charset)

    def get_request_line(self, request):
        method, path, version = self.parse_request_line(self.read_request_line(request))

    async def dispatch(self, request, response):

        request_line = await self.read_request_line(request)
        request_header = await self.get_request_headers(request)
        request_body = await self.get_request_body(request, int(request_header.get('Content-Length', 0)))
        print(f'request_line {request_line}')
        print(f'request_header {request_header}')
        print(f'request_body {request_body}')

        response.write(b'HTTP/1.0 404 Not Found\r\n\r\nNot Found')
        response.close()
        await response.wait_closed()

    async def serve(self):
        await asyncio.start_server(self.dispatch, self.host, self.port)

app = App(host='0.0.0.0', port=1080)
def main():
    loop = asyncio.new_event_loop()
    # loop.set_debug(True)
    loop.create_task(app.serve())
    loop.run_forever()

main()
