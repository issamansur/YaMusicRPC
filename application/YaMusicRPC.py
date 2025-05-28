import sys
import threading
import webbrowser
from ssl import SSLContext
from typing import Optional, List
import asyncio
import time

from pystray import Icon, Menu, MenuItem

from yamusicrpc.data import DISCORD_CLIENT_ID
from yamusicrpc.exceptions import DiscordProcessNotFoundError, AdminRightsRequiredError
from yamusicrpc.models import TrackInfo
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
    receiver: Optional[YandexTokenReceiver] = None
    listener: Optional[YandexListener] = None
    player: AsyncTaskManager
    ssl: Optional[SSLContext] = None

    def __init__(self, use_ssl: bool = False):
        self.discord_client = DiscordIPCClient(DISCORD_CLIENT_ID)
        self.player = AsyncTaskManager()
        if use_ssl:
            self.ssl = CertManager.get_ssl_context()

        # create loop for long tasks
        self.loop = asyncio.new_event_loop()
        threading.Thread(target=self._run_loop, daemon=True).start()

    # LOOP FOR PARALLEL WORK WITHOUT FREEZING INTERFACE
    def _run_loop(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()

    # === INIT ===
    def start_if_needed(self):
        # Start sharing activity (if 'is_autostart' = True)
        if self.is_ready() and self.state.is_autostart:
            self.state.is_running = True
            self.start_player()

    async def init_async(self) -> None:
        # Load state
        self.state = StateManager.load_state()

        # While loading
        self.icon.menu = Menu(
            MenuItem(
                text="Инициализация...",
                action=None,
                enabled=False,
            )
        )

        # Check Discord auth
        try:
            await self.check_discord_async()
        except AdminRightsRequiredError:
            self.icon.menu = Menu(
                MenuItem(
                    text="Ошибка подключения к Discord RPC через сокет",
                    action=None,
                    enabled=False,
                ),
                MenuItem(
                    text="Запустите YaMusicRPC с правами администратора",
                    action=None,
                    enabled=False,
                ),
                MenuItem(
                    text="Выход",
                    action=self._on_exit
                )
            )
            return

        # Check Yandex auth
        await self.check_yandex_async()

        self.start_if_needed()

        self.update_menu()

    # === Connections ===
    async def check_discord_async(self):
        """
        Try connecting to discord and update state (discord_username)
        """
        try:
            info: dict = await asyncio.to_thread(self.discord_client.connect)
            username = info.get("data", {}).get("user", {}).get("username")
            if username:
                self.state.discord_username = username
                print(f"[YaMusicRPC] Connected to Discord: @{username}")

            # CLose socket (we don't need to keep it active)
            self.discord_client.close()

        except DiscordProcessNotFoundError:
            print(f"[YaMusicRPC] Discord process not found")
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
            async for track in l.listen_with_event(stop_event, check_after=5):
                if stop_event.is_set():
                    break

                start_time: int = int(time.time()) - track.progress
                end_time: int = start_time + track.duration
                await self.yandex_client.fill_track_info(track)
                self.state.current_track_info = track
                self.update_menu()
                try:
                    self.discord_client.set_yandex_music_activity(
                        title=track.title,
                        artists=track.artists,
                        start=start_time,
                        end=end_time,
                        url=track.get_track_url(),
                        image_url=track.cover_url,
                    )
                except DiscordProcessNotFoundError:
                    self.stop_player()
                    break

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
        self.state.discord_username = None
        self.discord_client.close()

    # === Button actions (handlers) ===
    def _on_login_yandex(self):
        asyncio.run_coroutine_threadsafe(self._on_login_yandex_async(), self.loop)

    async def _on_login_yandex_async(self):
        """
        Try to log in yandex to get token
        """
        # Pre-action
        self.receiver = YandexTokenReceiver(local_port=5051)
        self.state.is_yandex_authorization = True
        self.update_menu()

        # Getting token
        token: Optional[str] = await asyncio.to_thread(self.receiver.get_token)

        # Post-action
        self.receiver = None
        self.state.is_yandex_authorization = False

        if token:
            print(f"[YaMusicRpc] Yandex token was received: {token}")
            self.state.yandex_token = token

            # Save token
            StateManager.save_token(token)
            print("[YaMusicRpc] Yandex token was saved")

            # Auth
            await self.check_yandex_async()

        self.update_menu()

        self.start_if_needed()

    def _on_logout_yandex(self):
        # Remove data
        StateManager.remove_token()
        self.state.yandex_username = None
        self.state.yandex_token = None

        self.update_menu()

        # Open link to remove access to app (not necessary, but yes)
        webbrowser.open("https://id.yandex.ru/personal/data-access")

        # Disconnect
        self.stop_player()
        self.listener = None

    def _on_reconnect_discord(self):
        asyncio.run_coroutine_threadsafe(self._on_reconnect_discord_async(), self.loop)

    async def _on_reconnect_discord_async(self):
        await self.check_discord_async()

        self.start_if_needed()

        self.update_menu()

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
    def update_menu(self):
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
            if self.state.is_yandex_authorization and self.receiver:
                yandex_menu = MenuItem(
                    text="Yandex: Выполняется вход...",
                    action=lambda _: webbrowser.open(self.receiver.get_ouath_url())
                )
            else:
                yandex_menu = MenuItem(
                    text="Yandex: Войти в аккаунт",
                    action=self._on_login_yandex,
                )

        # Current track menu item
        track: Optional[TrackInfo] = self.state.current_track_info
        if self.state.current_track_info:
            track_info: str = f'{track.title} - {track.artists}'
            if len(track_info) > 25:
                track_info = track_info[:25] + ".."
            current_track_menu = MenuItem(
                text=track_info,
                action=lambda _: webbrowser.open(track.get_track_url()),
                enabled=True
            )
        else:
            current_track_menu = MenuItem(
                text="Сначала включите трансляцию",
                action=None,
                enabled=False
            )

        items: List[MenuItem] = [
            MenuItem(
                text="YaMusicRPC 1.1.0 (by @edexade)",
                action=lambda _: webbrowser.open("https://github.com/issamansur/YaMusicRPC"),
                enabled=True
            ),
            Menu.SEPARATOR,
            MenuItem(
                text="======Сейчас играет======",
                action=None,
                enabled=False
            ),
            current_track_menu,
            Menu.SEPARATOR,
            MenuItem(
                text="======Подключения=======",
                action=None,
                enabled=False
            ),
            yandex_menu,
            MenuItem(
                text=f"Discord: {self.state.discord_username}"
                if self.state.discord_username
                else "Discord: Процесс не найден",
                action=self._on_reconnect_discord,
                enabled=not self.state.discord_username,
            ),
            Menu.SEPARATOR,
            MenuItem(
                text="======Настройки=========",
                action=None,
                enabled=False
            ),
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
                enabled=True
            ),
            Menu.SEPARATOR,
            MenuItem(
                text="Выход",
                action=self._on_exit
            )
        ]

        self.icon.menu = Menu(*items)

    def run(self):
        icon_image = ImageLoader.load_icon()

        self.icon = Icon(APP_NAME, icon=icon_image, title=APP_NAME)

        # Run in parallel to show icon on time
        asyncio.run_coroutine_threadsafe(self.init_async(), loop=self.loop)

        self.icon.run()


# === Run ===
if __name__ == "__main__":
    app = YaMusicRPCApp(use_ssl=True)
    app.run()
