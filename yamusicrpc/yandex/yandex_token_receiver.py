import webbrowser
from typing import Optional

from yamusicrpc.data import LOCAL_HOST, LOCAL_PORT, LOCAL_URI, YANDEX_AUTH_URL
from yamusicrpc.server import OAuthServer, ServerThread


class YandexTokenReceiver:
    __oauth_server: OAuthServer
    __server: ServerThread

    def __init__(self):
        self.__oauth_server = OAuthServer(LOCAL_HOST, LOCAL_PORT)
        self.__server = ServerThread(self.__oauth_server.get_app(), LOCAL_HOST, LOCAL_PORT)

    def get_token(self) -> Optional[str]:
        self.__server.start()

        print(f"[YandexTokenReceiver] Сервер запущен на {LOCAL_URI}")

        webbrowser.open(YANDEX_AUTH_URL)
        print("[YandexTokenReceiver] Открыт браузер для авторизации...")

        self.__oauth_server.token_received_event.wait(timeout=120)
        self.__server.shutdown()
        print("[YandexTokenReceiver] Сервер остановлен")
        return self.__oauth_server.access_token
