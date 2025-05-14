from werkzeug.serving import make_server


class ServerThread:
    def __init__(self, app, host: str, port: int):
        self.server = make_server(host, port, app)
        self.ctx = app.app_context()
        self.ctx.push()

        self.thread = None

    def start(self):
        import threading
        self.thread = threading.Thread(target=self.server.serve_forever)
        self.thread.daemon = True
        self.thread.start()

    def shutdown(self):
        self.server.shutdown()
        self.thread.join()
