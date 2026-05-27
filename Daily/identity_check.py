"""One-shot face recognition via CameraView's Machine HUD — subprocess isolation."""

import subprocess
import os
import time
import threading

PYTHON = sys.executable
RUNNER = os.path.join(os.path.dirname(__file__), "..", "CameraView", "hud_scan_runner.py")


def is_admin(duration_seconds: float = 5.0, voice_delay: float = 1.0) -> bool:
    """Launch Machine HUD in a subprocess.
    Speaks 'welcome back admin' *voice_delay* seconds after ADMIN is first detected."""

    proc = subprocess.Popen(
        [PYTHON, RUNNER, str(duration_seconds)],
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True,
        bufsize=1,
    )

    admin_seen = False
    admin_notified = False
    admin_first_at = None

    for line in proc.stdout:
        line = line.strip()
        if line == "ADMIN_FIRST" and not admin_seen:
            admin_seen = True
            admin_first_at = time.time()
        elif line == "ADMIN":
            admin_seen = True
        elif line == "NONE":
            break

    proc.wait()

    # If ADMIN was detected but process exited before voice_delay elapsed
    if admin_seen and not admin_notified:
        elapsed = time.time() - (admin_first_at or time.time())
        remaining = voice_delay - elapsed
        if remaining > 0:
            time.sleep(remaining)
        from hourly_chime import _get_vl
        _get_vl().speak("welcome back admin")
        admin_notified = True

    return admin_seen
