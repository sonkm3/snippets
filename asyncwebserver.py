import asyncio
# import uasyncio as asyncio


# https://developer.mozilla.org/ja/docs/Web/HTTP/Messages

class LogLevel:
    DEBUG = 0
    INFO = 1
    WARNING = 2
    ERROR = 3

    @classmethod
    def get_name(self, log_level: int) -> str|None:
        attributes = filter(lambda x: x[1].isupper(), enumerate(self.__dict__))
        for _, level_name in attributes:
            if hasattr(self, level_name):
                level_value = getattr(self, level_name)
                if level_value == log_level:
                    return level_name
        return None

def log_message(level: int, message: str):
    print(f'log: {LogLevel.get_name(level)} {message}')


class WebServer:
    def __init__(self, host='0.0.0.0', port=80, handlers={}):
        self.host = host
        self.port = port
        self.handlers = handlers
        log_message(LogLevel.INFO, f'WebServer started: host={self.host}, port={self.port}')

    def default_handler(self, method, path, request_header, query_dict={}, request_body=None):
        pass

    async def read_request(self, request):
        return (await request.readline()).decode('ascii').strip('\r\n')

    def parse_request_line(self, request_line):
        method, path_query, version = request_line.split(' ')
        return method, path_query, version

    def parse_header_line(self, header_line):
        return header_line.split(': ', 1)

    def parse_request_header_to_dict(self, header_list):
        header_dict = {}
        for header_line in header_list:
            key, value = self.parse_header_line(header_line)
            log_message(LogLevel.DEBUG, f'key: {key}, value: {value}')
            header_dict.update({key: value})
        return header_dict

    def parse_request_path_query(self, path_query):
        query_dict = {}
        if '?' in path_query:
            path, query_string = path_query.split('?', 1)
            for query_pair in query_string.split('&'):
                #  todo add decoding mechanism to handle url encoded string
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
        try:
            headers = await self.read_header(request)
            method, path_query, version = self.parse_request_line(headers.pop(0))
            request_header = self.parse_request_header_to_dict(headers)
            path, query_dict = self.parse_request_path_query(path_query)

            log_message(LogLevel.INFO, f'request_header {request_header}')
            log_message(LogLevel.INFO, f'request_line {method} {path_query} {version}')
            log_message(LogLevel.INFO, f'request_query {query_dict}')

            if 'Content-Length' in request_header and int(request_header.get('Content-Length', 0)) > 0:
                request_body = await self.read_request_body(request, int(request_header.get('Content-Length', 0)))
                log_message(LogLevel.DEBUG, f'request_body {request_body}')

            handler = self.handlers.get(path, self.default_handler)
            response = handler(method, path, request_header, query_dict=query_dict, request_body=request_body)
        except Exception as e:
            log_message(LogLevel.ERROR, f'Error: {e}')
        finally:
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
