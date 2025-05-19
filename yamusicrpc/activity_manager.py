import time
from typing import Optional

from .data import DISCORD_CLIENT_ID
from .yandex import YandexTokenReceiver, YandexListener, YandexClient
from .discord import DiscordIPCClient


class ActivityManager:
    __yandex_token_receiver: Optional[YandexTokenReceiver]
    __yandex_listener: Optional[YandexListener]
    __client: Optional[YandexClient]
    __discord_ipc_client: DiscordIPCClient

    def __init__(
            self,
            yandex_token_receiver: YandexTokenReceiver = YandexTokenReceiver(),
            discord_ipc_client: DiscordIPCClient = DiscordIPCClient(DISCORD_CLIENT_ID),
    ):
        self.__yandex_token_receiver = yandex_token_receiver
        self.__yandex_listener = None
        self.__client = None
        self.__discord_ipc_client = discord_ipc_client

    # Main func
    async def start(self):
        token: Optional[str] = self.__yandex_token_receiver.get_token()
        self.__yandex_listener = YandexListener(token)
        self.__client = YandexClient(token)
        self.__discord_ipc_client.connect()

        async with self.__yandex_listener as l:
            async for track in l.listen():
                start_time: int = int(time.time()) - track.progress
                await self.__client.fill_track_info(track)
                self.__discord_ipc_client.set_yandex_music_activity(
                    title=track.title,
                    artists=track.artists,
                    start=start_time,
                    end=start_time + track.duration,
                    url=track.get_track_url(),
                    image_url=track.cover_url
                )
