import json
import os
import sys
from typing import Optional

import keyring

from . import AppState
from ..data import APP_NAME, CONFIG_NAME, STATE_KEY


class StateManager:
    TOKEN_FILENAME = os.path.expanduser("~/.yandex_token")

    @staticmethod
    def get_config_path():
        base = os.path.expanduser("~")
        if sys.platform == "win32":
            base = os.getenv("APPDATA", base)
        elif sys.platform == "darwin":
            base = os.path.join(base, "Library", "Application Support")
        else:
            base = os.path.join(base, ".config")
        folder = os.path.join(base, APP_NAME)
        os.makedirs(folder, exist_ok=True)
        return os.path.join(folder, CONFIG_NAME)

    @classmethod
    def save_token(cls, token: str):
        try:
            keyring.set_password(STATE_KEY, "yandex_token", token)
        except Exception as e:
            print(f"[StateManager] Failed to save token in keyring: {e}")
            try:
                with open(cls.TOKEN_FILENAME, "w") as f:
                    f.write(token)
                os.chmod(cls.TOKEN_FILENAME, 0o600)  # Only for user
            except Exception as file_error:
                print(f"[StateManager] Failed to save token in file: {file_error}")

    @classmethod
    def load_token(cls) -> Optional[str]:
        try:
            token = keyring.get_password(STATE_KEY, "yandex_token")
            if token:
                return token
        except Exception as e:
            print(f"[StateManager] Failed to load token from keyring: {e}")

        # Fallback
        try:
            if os.path.exists(cls.TOKEN_FILENAME):
                with open(cls.TOKEN_FILENAME, "r") as f:
                    return f.read().strip()
        except Exception as e:
            print(f"[StateManager] Failed to load token from file: {e}")

        return None

    @classmethod
    def remove_token(cls):
        removed = False

        # Remove from keyring
        try:
            keyring.delete_password(STATE_KEY, "yandex_token")
            print("[StateManager] Token was successfully removed from keyring")
            removed = True
        except Exception as e:
            print(f"[StateManager] Failed to remove token from keyring: {e}")

        # Remove file (in any case)
        if os.path.exists(cls.TOKEN_FILENAME):
            try:
                os.remove(cls.TOKEN_FILENAME)
                print("[StateManager] Token was successfully removed from file")
                removed = True
            except Exception as e:
                print(f"[StateManager] Failed to remove token from file: {e}")

        if not removed:
            print(f"[StateManager] Failed to find token in keyring/file")

    @classmethod
    def save_state(cls, state: AppState):
        # Settings
        with open(cls.get_config_path(), "w", encoding="utf-8") as f:
            json.dump({
                "autostart": state.is_autostart
            }, f)

    @classmethod
    def load_state(cls) -> AppState:
        state = AppState()

        # Settings
        path = cls.get_config_path()
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    cfg = json.load(f)
                    state.is_autostart = cfg.get("autostart", state.is_autostart)
            except Exception as e:
                print(f"[StateManager] Failed to save config.json: {e}")

        # Token
        token = cls.load_token()
        if token:
            state.yandex_token = token

        return state