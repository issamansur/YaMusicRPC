import os
import sys
import platform

class AutostartManager:
    @staticmethod
    def _get_exec_path() -> str:
        """
        Return path to executable
        - For built `.exe` (PyInstaller) — it's exe-file.
        - For developing — python + path to script.
        """
        if getattr(sys, 'frozen', False):
            return sys.executable
        else:
            return f'{sys.executable}" "{os.path.abspath(sys.argv[0])}'

    @staticmethod
    def enable(app_name: str):
        exec_path = AutostartManager._get_exec_path()
        system = platform.system()

        if system == "Windows":
            try:
                import winreg
                reg_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
                key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, reg_path)
                winreg.SetValueEx(key, app_name, 0, winreg.REG_SZ, exec_path)
                print("[AutostartManager] Autostart was enabled (Windows)")
            except Exception as e:
                print(f"[AutostartManager] Unable to enable autostart (Windows): {e}")

        elif system == "Darwin":
            if getattr(sys, 'frozen', False):
                app_path = os.path.abspath(os.path.join(sys.executable, "../../.."))
            else:
                app_path = None  # можно задать вручную путь к .app или использовать exec_path

            if app_path is None:
                # fallback на exec_path, if not in .app
                program_args = [exec_path]
            else:
                program_args = ["/usr/bin/open", app_path]

            plist_path = os.path.expanduser(f"~/Library/LaunchAgents/{app_name}.plist")
            plist_content = f"""<?xml version="1.0" encoding="UTF-8"?>
            <plist version="1.0">
            <dict>
                <key>Label</key>
                <string>{app_name}</string>
                <key>ProgramArguments</key>
                <array>
                    {''.join(f'<string>{arg}</string>' for arg in program_args)}
                </array>
                <key>RunAtLoad</key>
                <true/>
            </dict>
            </plist>"""
            try:
                with open(plist_path, "w") as f:
                    f.write(plist_content)
                print("[AutostartManager] Autostart was enabled (macOS)")
            except Exception as e:
                print(f"[AutostartManager] Unable to enable autostart (macOS): {e}")

        elif system == "Linux":
            autostart_dir = os.path.expanduser("~/.config/autostart")
            os.makedirs(autostart_dir, exist_ok=True)
            desktop_path = os.path.join(autostart_dir, f"{app_name}.desktop")
            desktop_entry = f"""[Desktop Entry]
Type=Application
Exec={exec_path}
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
Name={app_name}
Comment=Autostart for {app_name}
"""
            try:
                with open(desktop_path, "w") as f:
                    f.write(desktop_entry)
                os.chmod(desktop_path, 0o755)
                print("[AutostartManager] Autostart was enabled (Linux)")
            except Exception as e:
                print(f"[AutostartManager] Unable to enable autostart (Linux): {e}")

    @staticmethod
    def disable(app_name: str):
        system = platform.system()

        if system == "Windows":
            try:
                import winreg
                reg_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path, 0, winreg.KEY_SET_VALUE)
                winreg.DeleteValue(key, app_name)
                print("[AutostartManager] Autostart was disabled (Windows)")
            except FileNotFoundError:
                print("[AutostartManager] Autostart record was not found (Windows)")
            except Exception as e:
                print(f"[AutostartManager] Unable to disable autostart (Windows): {e}")

        elif system == "Darwin":
            plist_path = os.path.expanduser(f"~/Library/LaunchAgents/{app_name}.plist")
            try:
                if os.path.exists(plist_path):
                    os.remove(plist_path)
                    print("[AutostartManager] Autostart was disabled (macOS)")
                else:
                    print("[AutostartManager] plist-file was not found (macOS)")
            except Exception as e:
                print(f"[AutostartManager] Unable to disable autostart (macOS): {e}")

        elif system == "Linux":
            desktop_path = os.path.expanduser(f"~/.config/autostart/{app_name}.desktop")
            try:
                if os.path.exists(desktop_path):
                    os.remove(desktop_path)
                    print("[AutostartManager] Autostart was disabled (Linux)")
                else:
                    print("[AutostartManager] .desktop-file was not found (Linux)")
            except Exception as e:
                print(f"[AutostartManager] Unable to disable autostart (Linux): {e}")