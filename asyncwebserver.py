import asyncio
# import uasyncio as asyncio


# https://developer.mozilla.org/ja/docs/Web/HTTP/Messages

class WebServer:
    def __init__(self, host='0.0.0.0', port=80, handlers={}):
        self.host = host
        self.port = port
        self.handlers = handlers

    def default_handler(self, method, path, request_header, query_dict={}, request_body=None):
        pass

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
            print(f'key: {key}, value: {value}')
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

    async def dispatch(self, request, response):
        headers = await self.read_header(request)
        method, path, version = self.parse_request_line(headers.pop(0))
        request_header = self.parse_request_header_to_dict(headers)
        path, query_dict = self.parse_request_path(path)

        print(f'request_line {method} {path} {version}')
        print(f'request_header {request_header}')

        if 'Content-Length' in request_header and int(request_header.get('Content-Length', 0)) > 0:
            request_body = await self.read_request_body(request, int(request_header.get('Content-Length', 0)))
            print(f'request_body {request_body}')

        handler = self.handlers.get(path, self.default_handler)
        response = handler(method, path, request_header, query_dict=query_dict, request_body=request_body)

        response.write(b'HTTP/1.0 404 Not Found\r\n\r\nNot Found')
        response.close()
        await response.wait_closed()

    async def serve(self):
        await asyncio.start_server(self.dispatch, self.host, self.port)

web_server = WebServer(host='0.0.0.0', port=1080)
def main():
    loop = asyncio.new_event_loop()
    # loop.set_debug(True)
    loop.create_task(web_server.serve())
    loop.run_forever()

main()
