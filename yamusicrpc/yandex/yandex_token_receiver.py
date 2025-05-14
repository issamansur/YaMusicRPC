import webbrowser
from typing import Optional

from yamusicrpc.data import LOCAL_HOST, LOCAL_PORT, LOCAL_URI, YANDEX_AUTH_URL
from yamusicrpc.server import OAuthServer, ServerThread


class YandexTokenReceiver:
    def __init__(self):
        self.oauth_server = OAuthServer(LOCAL_HOST, LOCAL_PORT)
        self.server = ServerThread(self.oauth_server.get_app(), LOCAL_HOST, LOCAL_PORT)

    def get_token(self) -> Optional[str]:
        self.server.start()

        print(f"[YandexTokenReceiver] Сервер запущен на {LOCAL_URI}")

        webbrowser.open(YANDEX_AUTH_URL)
        print("[YandexTokenReceiver] Открыт браузер для авторизации...")

        self.oauth_server.token_received_event.wait(timeout=120)
        self.server.shutdown()
        print("[YandexTokenReceiver] Сервер остановлен")
        return self.oauth_server.access_token
