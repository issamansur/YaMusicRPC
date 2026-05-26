from typing import Optional

from yamusicrpc.models import TrackInfo


class AppState:
    # keyring / secret
    yandex_token: Optional[str] = None

    # json
    is_autostart: bool = False
