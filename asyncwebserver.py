import asyncio


class App:
    def __init__(self, host='0.0.0.0', port=80):
        self.host = host
        self.port = port
        self.handlers = []

    def route(self, path, methods=['GET']):
        def wrapper(handler):
            self.handlers.append((path, methods, handler))
            return handler
        return wrapper

    async def dispatch(self, request, response):
        line_list = []
        while True:
            line = await request.readline()
            line = line.decode('ascii').strip('\r\n')
            if line:
                break
            line_list.append(line)

        response.write(b'HTTP/1.0 404 Not Found\r\n\r\nNot Found')
        response.close()
        await response.wait_closed()

    async def serve(self):
        await asyncio.start_server(self.dispatch, self.host, self.port)

app = App(host='0.0.0.0', port=80)
def main():
    loop = asyncio.new_event_loop()
    # loop.set_debug(True)
    loop.create_task(app.serve())
    loop.run_forever()

main()
