"""
Windows startup (Run key). Enable/disable run at login.
"""
import winreg

RUN_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"
APP_VALUE = "WindowsCleaner"


def get_startup_exe_path() -> str | None:
    """Return command line to run at startup (exe + --gui when frozen)."""
    import sys
    if getattr(sys, "frozen", False):
        return f'"{sys.executable}" --gui'
    return None


def set_start_with_windows(enabled: bool, exe_path: str | None = None) -> None:
    """
    Enable or disable start with Windows (current user Run key).
    exe_path: if None and running as frozen exe, uses sys.executable.
    """
    path = exe_path or get_startup_exe_path()
    if not path and enabled:
        return  # Cannot set without exe path
    key = winreg.OpenKey(
        winreg.HKEY_CURRENT_USER,
        RUN_KEY,
        0,
        winreg.KEY_SET_VALUE | winreg.KEY_QUERY_VALUE,
    )
    try:
        if enabled and path:
            winreg.SetValueEx(key, APP_VALUE, 0, winreg.REG_SZ, path)
        else:
            try:
                winreg.DeleteValue(key, APP_VALUE)
            except FileNotFoundError:
                pass
    finally:
        winreg.CloseKey(key)


def get_start_with_windows() -> bool:
    """Return True if app is in Run key."""
    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            RUN_KEY,
            0,
            winreg.KEY_READ,
        )
        try:
            winreg.QueryValueEx(key, APP_VALUE)
            return True
        except FileNotFoundError:
            return False
        finally:
            winreg.CloseKey(key)
    except Exception:
        return False
