import asyncio


# https://developer.mozilla.org/ja/docs/Web/HTTP/Messages

class App:
    def __init__(self, host='0.0.0.0', port=80):
        self.host = host
        self.port = port
        self.handlers = []

    async def dispatch(self, request, response):
        request_line = (await request.readline()).decode('ascii').strip('\r\n')
        method, path, version = request_line.split(' ')

        print(f'method: {method}, path: {path}, version: {version}')

        header_dict = {}
        while True:
            header_line = (await request.readline()).decode('ascii').strip('\r\n')
            print(f'line: {header_line}')
            if header_line == '':
                break
            header_dict.update([header_line.split(': ', 1)])

        charset = 'utf-8'
        if 'Content-Type' in header_dict:
            content_type = header_dict['Content-Type']
            if 'charset=' in content_type:
                charset = content_type.split('charset=')[1]

        if 'Content-Length' in header_dict:
            content_length = int(header_dict['Content-Length'])
            body = (await request.read(content_length)).decode(charset)
            print(f'body: {body}')

        print(f'headers: {header_dict}')

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
