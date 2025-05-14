import time
from typing import Optional, Union

from yandex_music import ClientAsync, Track

from .data import DISCORD_CLIENT_ID
from .models import CurrentState, TrackInfo
from .yandex import YandexTokenReceiver, YandexListener
from .discord import DiscordIPCClient


class ActivityManager:
    __yandex_token_receiver: Optional[YandexTokenReceiver]
    __yandex_listener: Optional[YandexListener]
    __client: Optional[ClientAsync]
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

    # Track utils
    async def __get_track_by_id(self, track_id: Union[int, str]) -> Track:
        tracks = await self.__client.tracks([track_id])
        track: Track = tracks[0]
        return track

    @staticmethod
    def __get_track_artists(track: Track) -> str:
        return ', '.join(track.artists_name())

    async def get_track_info_by_state(self, state: CurrentState) -> TrackInfo:
        track: Track = await self.__get_track_by_id(state.track_id)
        artists: str = self.__get_track_artists(track)

        return TrackInfo(
            title=track.title,
            artist=artists,
            duration=state.duration,
            progress=state.progress,
        )

    # Main func
    async def start(self):
        token: Optional[str] = self.__yandex_token_receiver.get_token()
        self.__yandex_listener = YandexListener(token)
        self.__client = await ClientAsync(token).init()
        self.__discord_ipc_client.connect()

        async with self.__yandex_listener as l:
            async for current_state in l.listen():

                # Yandex API has bugs with time while track changing
                if current_state.progress != 0:
                    continue

                start_time: int = int(time.time()) - current_state.progress
                track: TrackInfo = await self.get_track_info_by_state(current_state)
                self.__discord_ipc_client.set_yandex_music_activity(
                    title=track.title,
                    artists=track.artists,
                    start=start_time,
                    end=start_time + track.duration,
                )
