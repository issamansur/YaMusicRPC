from typing import Union, Optional, Dict

import aiohttp

from ..models import TrackInfo


class YandexClient:
    yandex_token: str
    default_headers: Dict[str, str]

    def __init__(self, yandex_token):
        self.yandex_token = yandex_token
        self.default_headers = {
            "Authorization": f"OAuth {self.yandex_token}"
        }

    async def do_request_async(self, url: str, headers: Dict[str, str], params: Dict) -> Dict:
        headers.update(self.default_headers)

        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, params=params) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    print(f"Request failed: {response.status} — {await response.text()}")
                    return {}

    # Profile utils
    async def get_profile_info(self) -> Dict:
        url = "https://login.yandex.ru/info"
        params = {
            "format": "json"
        }

        return await self.do_request_async(url, {}, params)

    async def get_username(self) -> Optional[str]:
        profile_info: dict = await self.get_profile_info()
        return profile_info.get("display_name", None)

    # Track utils
    async def get_track_info(self, track_id: Union[str, int]) -> Dict:
        url = "https://api.music.yandex.net/tracks"
        params = {
            "track_ids": [track_id]
        }

        return await self.do_request_async(url, {}, params)

    async def fill_track_info(self, track_info: TrackInfo) -> None:
        result_json = await self.get_track_info(track_info.track_id)
        track_info_new = result_json.get('result', [{}])[0]
        artists = track_info_new.get('artists', [{}])
        track_info.artists = ", ".join(map(lambda artist: artist.get('name', '???'), artists))
