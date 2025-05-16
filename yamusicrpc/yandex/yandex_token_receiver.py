import webbrowser
from typing import Optional

from yamusicrpc.data import LOCAL_HOST, LOCAL_PORT, YANDEX_AUTH_URL
from yamusicrpc.server import OAuthServer, ServerThread


class YandexTokenReceiver:
    local_host: str
    local_port: int

    __oauth_server: OAuthServer
    __server_thread: ServerThread

    def __init__(self, local_host: str = LOCAL_HOST, local_port: int = LOCAL_PORT):
        self.__oauth_server = OAuthServer(local_host, local_port)
        self.__server_thread = ServerThread(self.__oauth_server.get_app(), local_host, local_port)

        self.local_host = local_host
        self.local_port = local_port

    def get_token(self) -> Optional[str]:
        self.__server_thread.start()

        print(f"[YandexTokenReceiver] Сервер запущен на http://{self.local_host}:{self.local_port}")

        webbrowser.open(YANDEX_AUTH_URL)
        print("[YandexTokenReceiver] Открыт браузер для авторизации...")

        self.__oauth_server.token_received_event.wait(timeout=120)
        self.__server_thread.shutdown()
        print("[YandexTokenReceiver] Сервер остановлен")
        return self.__oauth_server.access_token
