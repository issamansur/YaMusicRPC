from typing import Union, Optional

import aiohttp

from yandex_music import ClientAsync, Track

from ..models import CurrentState, TrackInfo


class YandexClient(ClientAsync):
    def __init__(self, yandex_token):
        super().__init__(yandex_token)

    # Profile utils
    async def get_profile_info(self) -> dict:
        url = "https://login.yandex.ru/info"
        headers = {
            "Authorization": f"OAuth {self.token}"
        }
        params = {
            "format": "json"
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, params=params) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    print(f"⚠️ Ошибка запроса: {response.status} — {await response.text()}")
                    return {}

    async def get_username(self) -> Optional[str]:
        profile_info: dict = await self.get_profile_info()
        return profile_info.get("display_name", None)

    # Track utils
    async def __get_track_by_id(self, track_id: Union[int, str]) -> Track:
        tracks = await self.tracks([track_id])
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
