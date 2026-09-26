import ctypes
from ctypes import wintypes


class LASTINPUTINFO(ctypes.Structure):
    _fields_ = [
        ("cbSize", wintypes.UINT),
        ("dwTime", wintypes.DWORD),
    ]


def get_idle_seconds():
    """Return Windows keyboard/mouse idle time in seconds."""
    try:
        info = LASTINPUTINFO()
        info.cbSize = ctypes.sizeof(LASTINPUTINFO)
        if not ctypes.windll.user32.GetLastInputInfo(ctypes.byref(info)):
            return 0.0
        tick_count = ctypes.windll.kernel32.GetTickCount()
        elapsed_ms = (tick_count - info.dwTime) & 0xFFFFFFFF
        return max(0.0, elapsed_ms / 1000.0)
    except Exception as exc:
        print(f"⚠️ Could not read Windows idle time: {exc}")
        return 0.0
