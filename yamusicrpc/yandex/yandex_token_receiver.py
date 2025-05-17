import webbrowser
from typing import Optional

from yamusicrpc.data import LOCAL_HOST, LOCAL_PORT, YANDEX_CLIENT_ID
from yamusicrpc.server import OAuthServer, ServerThread


class YandexTokenReceiver:
    yandex_client_id: str
    local_host: str
    local_port: int

    __oauth_server: OAuthServer
    __server_thread: ServerThread

    def __init__(
            self,
            yandex_client_id: str = YANDEX_CLIENT_ID,
            local_host: str = LOCAL_HOST,
            local_port: int = LOCAL_PORT
    ) -> None:
        self.local_host = local_host
        self.local_port = local_port
        self.yandex_client_id = yandex_client_id

        self.__oauth_server = OAuthServer(local_host, local_port)
        self.__server_thread = ServerThread(self.__oauth_server.get_app(), local_host, local_port)

    def get_local_uri(self) -> str:
        return f'http://{self.local_host}:{self.local_port}/'

    def get_redirect_uri(self) -> str:
        return f'{self.get_local_uri()}callback'

    def get_token(self, timeout: int = 60) -> Optional[str]:
        self.__server_thread.start()

        print(f"[YandexTokenReceiver] Сервер запущен на {self.get_local_uri()}")

        webbrowser.open(
            f'https://oauth.yandex.ru/authorize?'
            f'response_type=token'
            f'&scope=music%3Acontent&scope=music%3Aread&scope=music%3Awrite'
            f'&client_id={self.yandex_client_id}'
            f'&redirect_uri={self.get_redirect_uri()}'
        )
        print("[YandexTokenReceiver] Открыт браузер для авторизации...")

        self.__oauth_server.token_received_event.wait(timeout=timeout)
        self.__server_thread.shutdown()
        print("[YandexTokenReceiver] Сервер остановлен")
        return self.__oauth_server.access_token
