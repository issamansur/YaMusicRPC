import os
import threading

from flask import Flask, jsonify, render_template


class DeviceAuthServer:
    def __init__(self, host: str, port: int):
        self.app = Flask(__name__, template_folder=os.path.dirname(__file__))
        self._status = "pending"
        self._user_code = ""
        self._verification_url = ""
        self._lock = threading.Lock()
        self._setup_routes()

    def set_device_code(self, user_code: str, verification_url: str) -> None:
        self._user_code = user_code
        self._verification_url = verification_url

    def set_success(self) -> None:
        with self._lock:
            self._status = "success"

    def set_expired(self) -> None:
        with self._lock:
            self._status = "expired"

    def _setup_routes(self) -> None:
        @self.app.route("/")
        def index():
            return render_template(
                "auth.html",
                user_code=self._user_code,
                verification_url=self._verification_url,
            )

        @self.app.route("/status")
        def status():
            with self._lock:
                return jsonify(status=self._status)

    def get_app(self):
        return self.app
