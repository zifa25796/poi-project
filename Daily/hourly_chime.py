"""Hourly chime — announces the time on the hour in Machine-style speech."""

from __future__ import annotations

import sys
import os
import threading
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "VoiceLine", "src"))
from voice_line import VoiceLine

HOUR_WORDS = {
    0: "twelve", 1: "one", 2: "two", 3: "three", 4: "four",
    5: "five", 6: "six", 7: "seven", 8: "eight", 9: "nine",
    10: "ten", 11: "eleven",
}

HOUR_12 = {h: (h % 12) for h in range(24)}

_vl: VoiceLine | None = None
_vl_lock = threading.Lock()
_speak_lock = threading.Lock()


def _get_vl() -> VoiceLine:
    global _vl
    if _vl is None:
        with _vl_lock:
            if _vl is None:
                _vl = VoiceLine()
    return _vl


def safe_speak(text: str) -> None:
    """Thread-safe speak — prevents concurrent AudioSegment playback collisions."""
    with _speak_lock:
        _get_vl().speak(text)


def _hour_phrase(hour: int) -> str:
    """Return a spoken phrase for the given hour (0–23)."""
    h12 = HOUR_12[hour]
    word = HOUR_WORDS[h12]
    phrase = f"{word} o'clock"
    if hour == 0:
        phrase = f"twelve o'clock midnight"
    elif hour == 12:
        phrase = f"twelve o'clock noon"
    return phrase


def chime(now: datetime | None = None) -> str:
    """Speak the current hour. Returns the phrase spoken."""
    if now is None:
        now = datetime.now()
    phrase = _hour_phrase(now.hour)
    safe_speak(phrase)
    return phrase


def force_chime(hour: int) -> str:
    """Speak a given hour regardless of current time. For testing."""
    phrase = _hour_phrase(hour)
    safe_speak(phrase)
    return phrase
