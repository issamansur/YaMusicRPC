import asyncio
import random
import string
import json
from typing import Union, Optional, AsyncIterable

import aiohttp
from aiohttp import ClientWebSocketResponse
from yandex_music import Track

from yamusicrpc.models import CurrentState, TrackInfo


class YandexListener:
    __yandex_token: str
    __device_id: str
    __ws_proto: dict
    __base_payload: dict
    __redirect_host: Optional[str] = None

    def __init__(self, yandex_token: str) -> None:
        self.__yandex_token = yandex_token
        self.__device_id = self.generate_device_id()
        self.__ws_proto = {
            "Ynison-Device-Id": self.__device_id,
            "Ynison-Device-Info": json.dumps({"app_name": "Chrome", "type": 1}),
        }
        self.__base_payload = {
            "update_full_state": {
                "player_state": {
                    "player_queue": {
                        "current_playable_index": -1,
                        "entity_id": "",
                        "entity_type": "VARIOUS",
                        "playable_list": [],
                        "options": {"repeat_mode": "NONE"},
                        "entity_context": "BASED_ON_ENTITY_BY_DEFAULT",
                        "version": {
                            "device_id": self.__device_id,
                            "version": 9021243204784341000,
                            "timestamp_ms": 0
                        },
                        "from_optional": "",
                    },
                    "status": {
                        "duration_ms": 0,
                        "paused": True,
                        "playback_speed": 1,
                        "progress_ms": 0,
                        "version": {
                            "device_id": self.__device_id,
                            "version": 8321822175199937000,
                            "timestamp_ms": 0
                        },
                    },
                },
                "device": {
                    "capabilities": {
                        "can_be_player": True,
                        "can_be_remote_controller": False,
                        "volume_granularity": 16
                    },
                    "info": {
                        "device_id": self.__device_id,
                        "type": "WEB",
                        "title": "Chrome Browser",
                        "app_name": "Chrome",
                    },
                    "volume_info": {"volume": 0},
                    "is_shadow": True,
                },
                "is_currently_active": False,
            },
            "rid": "ac281c26-a047-4419-ad00-e4fbfda1cba3",
            "player_action_timestamp_ms": 0,
            "activity_interception_type": "DO_NOT_INTERCEPT_BY_DEFAULT",
        }

    @staticmethod
    def generate_device_id(length: int = 16) -> str:
        return ''.join(random.choices(string.ascii_lowercase, k=length))

    async def __get_redirect_to_ynison(self) -> dict:
        async with aiohttp.ClientSession() as session:
            async with session.ws_connect(
                    "wss://ynison.music.yandex.ru/redirector.YnisonRedirectService/GetRedirectToYnison",
                    headers={
                        "Sec-WebSocket-Protocol": f"Bearer, v2, {json.dumps(self.__ws_proto)}",
                        "Origin": "https://music.yandex.ru",
                        "Authorization": f"OAuth {self.__yandex_token}",
                    },
            ) as ws:
                response = await ws.receive()
                response_json = response.json()
                return response_json

    async def __update_redirect_ynison(self) -> None:
        ynison_data: dict = await self.__get_redirect_to_ynison()

        redirect_ticket: str = ynison_data.get('redirect_ticket')
        host: str = ynison_data.get('host')

        print(
            f'[YandexListener] Received host: {host}, redirect_ticket: {redirect_ticket}'
        )

        self.__ws_proto.setdefault("Ynison-Redirect-Ticket", redirect_ticket)
        self.__redirect_host = host

    # ASYNC BLOCK
    __session: aiohttp.ClientSession
    __ws: ClientWebSocketResponse

    async def __aenter__(self):
        await self.__update_redirect_ynison()
        self.__session = aiohttp.ClientSession()
        self.__ws = await self.__session.ws_connect(
            f"wss://{self.__redirect_host}/ynison_state.YnisonStateService/PutYnisonState",
            headers={
                "Sec-WebSocket-Protocol": f"Bearer, v2, {json.dumps(self.__ws_proto)}",
                "Origin": "https://music.yandex.ru",
                "Authorization": f"OAuth {self.__yandex_token}",
            }
        )
        await self.__ws.send_str(json.dumps(self.__base_payload))
        return self

    async def __aexit__(self, exc_type, exc, tb):
        if self.__ws is not None:
            await self.__ws.close()
        if self.__session is not None:
            await self.__session.close()

    async def listen(self) -> AsyncIterable[CurrentState]:
        """
        Correct using:
        ```
        yandex_listener = YandexListener(...)
        async with yandex_listener as l:
            async for current_state in l.listen():
                ...
        ```
        :return:
        """
        async for msg in self.__ws:
            if msg.type == aiohttp.WSMsgType.TEXT:
                ynison_data = msg.json()
                state: CurrentState = CurrentState.from_ynison(ynison_data)
                print(f'[YandexListener] Received state about track: {state.track_id}')
                yield state
            elif msg.type == aiohttp.WSMsgType.CLOSED:
                break
            elif msg.type == aiohttp.WSMsgType.ERROR:
                raise msg.data
