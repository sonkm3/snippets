import asyncio


class WebServer:
    def __init__(self, host='0.0.0.0', port=80, handlers={}) -> None:
        self.host = host
        self.port = port
        self.handlers = handlers

    def default_handler(self, method, path, request_header, query_dict={}, request_body=None) -> bytes:
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

    def remove_fragment(self, path_with_query_and_fragment: str) -> str:
        if '#' in path_with_query_and_fragment:
            path_with_query, _ = path_with_query_and_fragment.split('#', 1)
        else:
            path_with_query = path_with_query_and_fragment
        return path_with_query

    def parse_request_path(self, path_with_query: str):
        query_dict = {}
        if '?' in path_with_query:
            path, query_string = path_with_query.split('?', 1)
            for query_pair in query_string.split('&'):
                key, value = query_pair.split('=', 1)
                query_dict.update({key: value})
        else:
            path = path_with_query
        return path, query_dict

    async def read_header(self, request) -> list:
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
        method, path_with_query_and_fragment, version = self.parse_request_line(headers.pop(0))
        path_with_query = self.remove_fragment(path_with_query_and_fragment)
        request_header = self.parse_request_header_to_dict(headers)
        path, query_dict = self.parse_request_path(path_with_query)

        if 'Content-Length' in request_header and int(request_header.get('Content-Length', 0)) > 0:
            request_body = await self.read_request_body(request_io, int(request_header.get('Content-Length', 0)))
        else:
            request_body = None

        handler = self.handlers.get(path, self.default_handler)
        response = handler(method, path, request_header, query_dict=query_dict, request_body=request_body)

        response_io.write(response)
        response_io.close()
        await response_io.wait_closed()

        request_io.close()
        await request_io.wait_closed()

    async def serve(self):
        await asyncio.start_server(self.dispatch, self.host, self.port)

async def run_forever(web_server):
        asyncio.create_task(web_server.serve())
        while True:
            await asyncio.sleep(0)

def run_webserver(web_server):
    asyncio.run(run_forever(web_server))
