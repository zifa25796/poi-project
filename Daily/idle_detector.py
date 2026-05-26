"""Detect user idle time via Win32 GetLastInputInfo (keyboard + mouse)."""

import ctypes
from ctypes import wintypes

user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32


class LASTINPUTINFO(ctypes.Structure):
    _fields_ = [
        ("cbSize", wintypes.UINT),
        ("dwTime", wintypes.DWORD),
    ]


def idle_seconds() -> float:
    """Return seconds since last keyboard or mouse input."""
    lii = LASTINPUTINFO()
    lii.cbSize = ctypes.sizeof(LASTINPUTINFO)
    user32.GetLastInputInfo(ctypes.byref(lii))
    return (kernel32.GetTickCount() - lii.dwTime) / 1000.0


def is_user_away(idle_timeout_minutes: float) -> bool:
    """Return True if the user appears to be away from the computer."""
    return idle_seconds() > idle_timeout_minutes * 60
