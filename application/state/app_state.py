from typing import Optional


class AppState:
    # keyring / secret
    yandex_token: Optional[str] = None

    # json
    is_autostart: bool = False

    # local
    is_yandex_authorization: bool = False
    is_running: bool = False
    yandex_username: Optional[str] = None
    discord_username: Optional[str] = None