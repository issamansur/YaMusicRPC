import sys
import webbrowser
from ssl import SSLContext
from typing import Optional, List
import asyncio
import time

from pystray import Icon, Menu, MenuItem

from yamusicrpc.data import DISCORD_CLIENT_ID
from yamusicrpc.exceptions import DiscordProcessNotFound
from yamusicrpc.yandex import YandexTokenReceiver, YandexClient, YandexListener
from yamusicrpc.discord import DiscordIPCClient

from application.data import APP_NAME
from application.state import AppState, StateManager
from application.utils import AsyncTaskManager, ImageLoader, AutostartManager, CertManager


class YaMusicRPCApp:
    icon: Optional[Icon] = None

    state: AppState = AppState()
    discord_client: Optional[DiscordIPCClient] = None
    yandex_client: Optional[YandexClient] = None
    listener: Optional[YandexListener] = None
    player: AsyncTaskManager
    ssl: Optional[SSLContext] = None

    def __init__(self, use_ssl: bool = False):
        self.player = AsyncTaskManager()
        if use_ssl:
            self.ssl = CertManager.get_ssl_context()

    # === INIT ===
    def start_if_needed(self):
        # Start sharing activity (if 'is_autostart' = True)
        if self.is_ready() and self.state.is_autostart:
            self.state.is_running = True
            self.start_player()

    async def init_async(self) -> None:
        # Load state
        self.state = StateManager.load_state()

        # Check Discord auth
        self.check_discord()

        # Check Yandex auth
        await self.check_yandex_async()

        self.start_if_needed()

    # === Connections ===
    def check_discord(self):
        """
        Try connecting to discord and update state (discord_username)
        """
        try:
            self.discord_client = DiscordIPCClient(DISCORD_CLIENT_ID)
            info: dict = self.discord_client.connect()
            username = info.get("data", {}).get("user", {}).get("username")
            if username:
                self.state.discord_username = username
                print(f"[YaMusicRPC] Connected to Discord: @{username}")

            # CLose socket (we don't need to keep it active)
            self.discord_client.close()

        except DiscordProcessNotFound:
            self.state.discord_username = None

    async def check_yandex_async(self):
        """
        Try connecting to Yandex and update state (yandex_username)
        (We are counting that we already have token)
        """
        if self.state.yandex_token:
            self.yandex_client = YandexClient(self.state.yandex_token, self.ssl)

            username: str = await self.yandex_client.get_username()

            if username:
                self.state.yandex_username = username
                print(f"[YaMusicRPC] Connected to Yandex: @{username}")

                self.listener = YandexListener(self.state.yandex_token, self.ssl)

    # === Main func to sharing activity ===
    async def play(self, stop_event: asyncio.Event):
        async with self.listener as l:
            # Using overload to not wait next message
            """
            async for current_state in l.listen():
                if stop_event.is_set():
                    print("[YaMusicRPC] Stop event was received")
                    break
            """
            async for track in l.listen_with_event(stop_event, check_after=5):
                start_time: int = int(time.time()) - track.progress
                end_time: int = start_time + track.duration
                await self.yandex_client.fill_track_info(track)
                try:
                    self.discord_client.set_yandex_music_activity(
                        title=track.title,
                        artists=track.artists,
                        start=start_time,
                        end=end_time,
                        url=track.get_track_url(),
                        image_url=track.cover_url,
                    )
                except DiscordProcessNotFound:
                    self.stop_player()

        if stop_event.is_set():
            print("[YaMusicRPC] Stop event was received")

    def is_ready(self) -> bool:
        return bool(self.state.yandex_username) and bool(self.state.discord_username)

    # === Player ===
    def start_player(self):
        if not self.player.is_running():
            self.state.is_running = True
            # Prepare
            self.discord_client.connect()

            self.player.start(self.play)

    def stop_player(self):
        if self.player.is_running():
            self.player.stop()

        # hard shutdown
        self.state.is_running = False
        self.discord_client.close()

    # === Actions (handlers) ===
    def _on_login_yandex(self, icon, item):
        """
        Try to log in yandex to get token
        """
        # Getting yandex token
        ytr: YandexTokenReceiver = YandexTokenReceiver(local_port=5051)
        token: Optional[str] = ytr.get_token()

        if token:
            print(f"[YaMusicRpc] Yandex token was received: {token}")
            self.state.yandex_token = token

            # Save token
            StateManager.save_token(token)
            print("[YaMusicRpc] Yandex token was saved")

            # Auth
            asyncio.run(self.check_yandex_async())

            icon.menu = self.generate_menu()

            self.start_if_needed()

    def _on_logout_yandex(self, icon):
        # Remove data
        StateManager.remove_token()
        self.state.yandex_username = None
        self.state.yandex_token = None

        icon.menu = self.generate_menu()

        # Open link to remove access to app (not necessary, but yes)
        webbrowser.open("https://id.yandex.ru/personal/data-access")

        # Disconnect
        self.stop_player()
        self.listener = None

    def _on_reconnect_discord(self, icon):
        self.check_discord()

        icon.menu = self.generate_menu()

        self.start_if_needed()

    def _on_toggle_play(self, icon, item):
        if not self.state.is_running:
            self.start_player()
            print("[YaMusicRpc] Start sharing activity")
        else:
            self.stop_player()
            print("[YaMusicRpc] Stop sharing activity")

    def _on_toggle_autostart(self, icon, item):
        self.state.is_autostart = not self.state.is_autostart
        if self.state.is_autostart:
            AutostartManager.enable(APP_NAME)
            print("[YaMusicRpc] Autostart was enabled")
        else:
            AutostartManager.disable(APP_NAME)
            print("[YaMusicRpc] Autostart was disabled")

        StateManager.save_state(self.state)

    def _on_exit(self, icon, item):
        print("[YaMusicRpc] Closing application..")

        # Stop if needed
        self.stop_player()

        # Save state (not necessary, but yes)
        StateManager.save_state(self.state)

        self.icon.stop()
        sys.exit(0)

    # === Menu ===
    def generate_menu(self):
        # Yandex menu item
        if self.state.yandex_username:
            items: List[MenuItem] = [
                MenuItem(
                    text="Выйти из аккаунта",
                    action=self._on_logout_yandex
                )
            ]

            yandex_menu = MenuItem(
                text=f"Yandex: {self.state.yandex_username}",
                action=Menu(*items),
            )
        else:
            yandex_menu = MenuItem(
                text="Yandex: Войти в аккаунт",
                action=self._on_login_yandex,
            )

        items: List[MenuItem] = [
            MenuItem(
                text="YaMusicRPC (by @edexade)",
                action=None,
                enabled=False
            ),
            Menu.SEPARATOR,
            MenuItem(
                f"Discord: {self.state.discord_username}"
                if self.state.discord_username
                else "Discord: Процесс не найден",
                lambda icon, item: self._on_reconnect_discord(icon),
                enabled=not self.state.discord_username,
            ),
            yandex_menu,
            Menu.SEPARATOR,
            # Enabled if discord and yandex connected
            MenuItem(
                text="Транслировать в Discord",
                action=self._on_toggle_play,
                checked=lambda item: self.state.is_running,
                enabled=self.is_ready()
            ),
            MenuItem(
                text="Запускать при включении",
                action=self._on_toggle_autostart,
                checked=lambda item: self.state.is_autostart,
                enabled=self.is_ready(),
            ),
            Menu.SEPARATOR,
            MenuItem(
                text="Выход",
                action=self._on_exit
            )
        ]

        return Menu(*items)

    def run(self):
        icon_image = ImageLoader.load_icon(is_after_build=True)

        asyncio.run(self.init_async())

        self.icon = Icon(APP_NAME, icon=icon_image, title=APP_NAME)

        self.icon.menu = self.generate_menu()
        self.icon.run()


# === Run ===
if __name__ == "__main__":
    app = YaMusicRPCApp(use_ssl=True)
    app.run()
