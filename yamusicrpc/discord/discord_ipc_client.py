import json
import struct
import os
import socket
import tempfile
import time
import sys
from typing import Optional

from yamusicrpc.exceptions import DiscordProcessNotFound


class DiscordIPCClient:
    OP_HANDSHAKE = 0
    OP_FRAME = 1

    def __init__(self, client_id):
        self.client_id = client_id
        self.sock = None

    @staticmethod
    def _encode(opcode, payload):
        data = json.dumps(payload).encode('utf-8')
        return struct.pack('<II', opcode, len(data)) + data

    @staticmethod
    def _get_socket_path():
        ipc = 'discord-ipc-0'

        if sys.platform in ('linux', 'darwin'):
            tempdir = os.environ.get('XDG_RUNTIME_DIR') or (
                f"/run/user/{os.getuid()}" if os.path.exists(f"/run/user/{os.getuid()}") else tempfile.gettempdir())
            paths = ['.', 'snap.discord', 'app/com.discordapp.Discord', 'app/com.discordapp.DiscordCanary']
        elif sys.platform == 'win32':
            return r'\\?\pipe\discord-ipc-0'
        else:
            return None

        for path in paths:
            full_path = os.path.abspath(os.path.join(tempdir, path))
            if os.path.isdir(full_path):
                for entry in os.scandir(full_path):
                    if entry.name.startswith(ipc):
                        return entry.path
        return None

    @staticmethod
    def _test_socket_path(path) -> bool:
        if sys.platform == 'win32':
            with open(path):
                return True
        else:
            with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as client:
                client.connect(path)
                return True

    def connect(self) -> dict:
        try:
            if os.name == 'nt':
                import win32file
                self.sock = win32file.CreateFile(
                    self._get_socket_path(),
                    win32file.GENERIC_READ | win32file.GENERIC_WRITE,
                    0, None,
                    win32file.OPEN_EXISTING,
                    0, None
                )
            else:
                self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
                self.sock.connect(self._get_socket_path())
        except ConnectionRefusedError:
            raise DiscordProcessNotFound()

        handshake = {
            "v": 1,
            "client_id": self.client_id
        }
        self._send(self.OP_HANDSHAKE, handshake)
        print("[DiscordIPC] Handshake sent")

        if os.name == 'nt':
            import win32file
            response = win32file.ReadFile(self.sock, 1024)[1]
        else:
            response = self.sock.recv(1024)

        opcode, length = struct.unpack('<II', response[:8])
        payload = response[8:8 + length]
        data = json.loads(payload.decode('utf-8'))

        print(f"[DiscordIPC] User '{data.get('data').get('user').get('username')}' accepted handshake")
        return data

    def _send(self, opcode, payload):
        packet = self._encode(opcode, payload)
        if os.name == 'nt':
            import win32file
            win32file.WriteFile(self.sock, packet)
        else:
            self.sock.send(packet)

    def set_activity(self, activity: dict, pid: int = os.getpid()):
        payload = {
            "cmd": "SET_ACTIVITY",
            "args": {
                "pid": pid,
                "activity": activity
            },
            "nonce": str(time.time())
        }
        self._send(self.OP_FRAME, payload)
        print("[DiscordIPC] Activity sent")

    def set_yandex_music_activity(
            self,
            title: str,
            artists: str,
            start: int,
            end: int,
            url: str,
            image_url: Optional[str] = None,
    ) -> None:
        self.set_activity({
            "type": 2,
            # "emoji": "<:yandex:1370472333915197491>",
            "details": title,
            "state": artists,
            "timestamps": {
                "start": start,
                "end": end,
            },
            "assets": {
                "large_image": image_url if image_url else "yandex_logo",
                "small_image": "yandex_logo",
                "small_text": "YaMusicRpc by @edexade"
            },
            "buttons": [
                {
                    "label": "Open music",
                    "url": url
                },
            ]
        })

    def close(self):
        if self.sock:
            if os.name != 'nt':
                self.sock.close()
            self.sock = None
            print("[DiscordIPC] Connection closed")
