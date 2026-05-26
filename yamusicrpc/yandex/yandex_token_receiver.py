import time
import webbrowser
from typing import Optional

import requests

from yamusicrpc.data import LOCAL_HOST, LOCAL_PORT, YANDEX_CLIENT_ID, YANDEX_CLIENT_SECRET
from yamusicrpc.server import DeviceAuthServer, ServerThread

_OAUTH_BASE_URL = 'https://oauth.yandex.ru'

# Delay (seconds) to let the browser receive the final status before server shuts down
_SHUTDOWN_DELAY = 4


class YandexTokenReceiver:
    local_host: str
    local_port: int

    def __init__(
            self,
            local_host: str = LOCAL_HOST,
            local_port: int = LOCAL_PORT,
            client_id: str = YANDEX_CLIENT_ID,
            client_secret: str = YANDEX_CLIENT_SECRET,
    ) -> None:
        self.local_host = local_host
        self.local_port = local_port
        self._client_id = client_id
        self._client_secret = client_secret

    def get_local_url(self) -> str:
        return f'http://{self.local_host}:{self.local_port}/'

    def _request_device_code(self) -> dict:
        resp = requests.post(
            f'{_OAUTH_BASE_URL}/device/code',
            data={
                'client_id': self._client_id,
                'device_name': 'YaMusicRPC',
            },
        )
        resp.raise_for_status()
        return resp.json()

    def _poll_yandex_token(self, device_code: str) -> Optional[str]:
        resp = requests.post(
            f'{_OAUTH_BASE_URL}/token',
            data={
                'grant_type': 'device_code',
                'code': device_code,
                'client_id': self._client_id,
                'client_secret': self._client_secret,
            },
        )
        data = resp.json()
        if resp.status_code != 200:
            if data.get('error') == 'authorization_pending':
                return None
            raise Exception(data.get('error_description', data.get('error', 'Unknown auth error')))
        return data.get('access_token')

    def get_token(self, timeout: int = 300) -> Optional[str]:
        code_data = self._request_device_code()
        user_code: str = code_data['user_code']
        verification_url: str = code_data['verification_url']
        device_code: str = code_data['device_code']
        interval: int = code_data.get('interval', 5)
        expires_in: int = code_data.get('expires_in', timeout)

        print(f'[YandexTokenReceiver] Device code: {user_code}')

        server = DeviceAuthServer(self.local_host, self.local_port)
        server.set_device_code(user_code, verification_url)
        server_thread = ServerThread(server.get_app(), self.local_host, self.local_port)
        server_thread.start()

        print(f'[YandexTokenReceiver] Server started at {self.get_local_url()}')
        webbrowser.open(self.get_local_url())

        token: Optional[str] = None
        deadline = time.monotonic() + min(timeout, expires_in)

        try:
            while True:
                time.sleep(interval)

                if time.monotonic() >= deadline:
                    server.set_expired()
                    print('[YandexTokenReceiver] Auth timeout')
                    time.sleep(_SHUTDOWN_DELAY)
                    break

                token = self._poll_yandex_token(device_code)
                if token is not None:
                    server.set_success()
                    print('[YandexTokenReceiver] Token received')
                    time.sleep(_SHUTDOWN_DELAY)
                    break
        finally:
            server_thread.shutdown()
            print('[YandexTokenReceiver] Server stopped')

        return token
