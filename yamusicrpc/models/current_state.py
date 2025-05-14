from typing import Optional, Union, Dict


class CurrentState:
    # Required fields
    track_id: Union[int, str]
    is_paused: bool
    duration: int
    progress: int
    # Optional fields (not needed to use)
    entity_id: Optional[str]
    entity_type: Optional[str]

    def __init__(
            self,
            track_id: int,
            is_paused: bool,
            duration: int,
            progress: int,
            entity_id: Optional[str],
            entity_type: Optional[str],
    ) -> None:
        self.track_id = track_id
        self.is_paused = is_paused
        self.duration = duration
        self.progress = progress
        self.entity_id = entity_id
        self.entity_type = entity_type

    @classmethod
    def from_ynison(cls, ynison: dict) -> 'CurrentState':
        # current track id
        current_list: Dict = ynison["player_state"]["player_queue"]["playable_list"]
        current_index: int = ynison["player_state"]["player_queue"]["current_playable_index"]
        current_track: Dict = current_list[current_index]
        current_track_id: Union[int, str] = current_track["playable_id"]

        # status: is paused, duration, current progress
        status: Dict = ynison["player_state"]["status"]
        is_paused: bool = status["paused"]
        duration: int = int(status["duration_ms"]) // 1000
        progress: int = int(status["progress_ms"]) // 1000

        # [OPTIONAL] queue: entity id, entity type
        queue: Dict = ynison["player_state"]["player_queue"]
        entity_id: Optional[Union[int, str]] = queue.get("entity_id", None)
        entity_type: Optional[Union[int, str]] = queue.get("entity_type", None)

        return cls(
            track_id=current_track_id,
            is_paused=is_paused,
            duration=duration,
            progress=progress,
            entity_id=entity_id,
            entity_type=entity_type,
        )
