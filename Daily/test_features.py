"""Test both Daily features: hourly chime + return identity check (HUD window)."""

import json
import os
from datetime import datetime
from hourly_chime import chime


def load_config():
    with open(os.path.join(os.path.dirname(__file__), "config.json")) as f:
        return json.load(f)


def test_chime():
    print("─" * 40)
    now = datetime.now()
    print(f"Current time: {now:%H:%M:%S}")
    phrase = chime(now)
    print(f"Chime spoke: {phrase}")


def test_return_check():
    cfg = load_config()
    cam = cfg.get("camera_view", {})
    dur = cam.get("hud_duration_seconds", 5)
    delay = cam.get("voice_delay_seconds", 1)

    print("─" * 40)
    print(f"Launching Machine HUD window ({dur}s scan, {delay}s voice delay)...")
    from identity_check import is_admin
    admin = is_admin(duration_seconds=dur, voice_delay=delay)
    if admin:
        print("ADMIN confirmed — welcome back!")
    else:
        print("Not ADMIN (or no face detected)")


if __name__ == "__main__":
    test_chime()
    test_return_check()
