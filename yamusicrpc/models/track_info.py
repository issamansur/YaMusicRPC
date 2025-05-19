from typing import Optional, Dict, Union

from yamusicrpc.data import YANDEX_COVER_DEFAULT_SIZE


class TrackInfo:
    # required
    track_id: str
    title: str
    artists: Optional[str]

    is_paused: bool
    duration: Optional[int]
    progress: Optional[int]

    # optional
    album_id: Optional[str] = None
    cover_url: Optional[str] = None

    def __init__(
            self,
            track_id: str,
            title: str,
            artists: Optional[str] = None,
            is_paused: Optional[bool] = None,
            duration: Optional[int] = None,
            progress: Optional[int] = None,
    ) -> None:
        self.track_id = track_id
        self.title = title
        self.artists = artists
        self.duration = duration
        self.progress = progress

    def get_track_url(self) -> str:
        url: str = "https://music.yandex.ru"
        if self.album_id:
            url += f"/album/{self.album_id}"
        url += f"/track/{self.track_id}"

        return url

    @classmethod
    def from_ynison(cls, ynison: dict) -> 'TrackInfo':
        # current track
        current_list: Dict = ynison["player_state"]["player_queue"]["playable_list"]
        current_index: int = ynison["player_state"]["player_queue"]["current_playable_index"]
        current_track: Dict = current_list[current_index]

        current_track_id: Union[int, str] = current_track["playable_id"]
        current_track_title: str = current_track["title"]
        current_track_cover_url: Optional[str] = current_track.get("cover_url_optional", None)
        current_track_album_id: Optional[str] = current_track.get("album_id_optional", None)

        # status: is paused, duration, current progress
        status: Dict = ynison["player_state"]["status"]
        is_paused: bool = status["paused"]
        duration: int = int(status["duration_ms"]) // 1000
        progress: int = int(status["progress_ms"]) // 1000

        # [OPTIONAL] queue: entity id, entity type
        """
        queue: Dict = ynison["player_state"]["player_queue"]
        entity_id: Optional[Union[int, str]] = queue.get("entity_id", None)
        entity_type: Optional[Union[int, str]] = queue.get("entity_type", None)
        """

        track_info: cls = cls(
            track_id=current_track_id,
            title=current_track_title,
            # We can't get info from ynison about artist
            artists=None,

            is_paused=is_paused,
            duration=duration,
            progress=progress,
        )

        if current_track_cover_url:
            track_info.cover_url = f"https://{current_track_cover_url.strip('%')}{YANDEX_COVER_DEFAULT_SIZE}"
        if current_track_album_id:
            track_info.album_id = current_track_album_id

        return track_info
