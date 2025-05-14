from flask import Flask, request, send_file, jsonify
import threading


class OAuthServer:
    def __init__(self, host: str, port: int):
        self.app = Flask(__name__)
        self.host = host
        self.port = port
        self.access_token = None
        self.token_received_event = threading.Event()

        self._setup_routes()

    def _setup_routes(self):
        @self.app.route("/callback")
        def callback():
            return send_file('callback.html')

        @self.app.route("/token")
        def receive_token():
            self.access_token = request.args.get("access_token")
            print(f"[Server] Access Token: {self.access_token}")
            self.token_received_event.set()
            return jsonify(status="ok")

    def get_app(self):
        return self.app
