from asyncwebserver import run_webserver, WebServer


def main() -> None:

    handlers = {}

    web_server = WebServer(host='0.0.0.0', port=2080, handlers=handlers)

    # loop = asyncio.new_event_loop()
    # loop.create_task(web_server.serve())
    # loop.run_forever()

    run_webserver(web_server)

if __name__ == '__main__':
    main()
