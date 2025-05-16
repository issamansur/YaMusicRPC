from typing import Union

from yandex_music import ClientAsync, Track

from ..models import CurrentState, TrackInfo


class YandexClient(ClientAsync):
    def __init__(self, yandex_token):
        super().__init__(yandex_token)

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