"""Daily — Person of Interest desktop companion.

Orchestrates VoiceLine speech and CameraView surveillance.
Feature toggles live in config.json.
"""

import json
import os
import threading
import time
from datetime import datetime

from hourly_chime import chime
from idle_detector import idle_seconds

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config.json")

# ── ANSI colours ──────────────────────────────────────────────────
_CYAN = "\033[36m"
_GREEN = "\033[32m"
_RESET = "\033[0m"


def _app(msg: str):
    """Print a timestamped app message in cyan."""
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"{_CYAN}[APP  {ts}]{_RESET} {msg}")


def load_config() -> dict:
    with open(CONFIG_PATH) as f:
        return json.load(f)


def _start_api(port: int):
    import uvicorn
    from api_server import app as api_app

    uvicorn.run(api_app, host="0.0.0.0", port=port,
                log_config=_uvicorn_log_config(), access_log=True)


def _uvicorn_log_config() -> dict:
    """Return a log config that uses [API  HH:MM:SS] prefix in green."""
    fmt_default = f"{_GREEN}[API  %(asctime)s]{_RESET} %(message)s"
    fmt_access = (
        f'{_GREEN}[API  %(asctime)s]{_RESET} '
        '%(client_addr)s - "%(request_line)s" %(status_code)s'
    )
    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "()": "uvicorn.logging.DefaultFormatter",
                "fmt": fmt_default,
                "datefmt": "%H:%M:%S",
            },
            "access": {
                "()": "uvicorn.logging.AccessFormatter",
                "fmt": fmt_access,
                "datefmt": "%H:%M:%S",
            },
        },
        "handlers": {
            "default": {
                "formatter": "default",
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stdout",
            },
            "access": {
                "formatter": "access",
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stdout",
            },
        },
        "loggers": {
            "uvicorn": {"handlers": ["default"], "level": "INFO", "propagate": False},
            "uvicorn.error": {"level": "INFO"},
            "uvicorn.access": {
                "handlers": ["access"], "level": "INFO", "propagate": False,
            },
        },
    }


def main():
    cfg = load_config()

    chime_cfg = cfg.get("hourly_chime", {})
    chime_enabled = chime_cfg.get("enabled", False)
    idle_timeout_minutes = chime_cfg.get("idle_timeout_minutes", 5)

    api_cfg = cfg.get("api_server", {})
    api_enabled = api_cfg.get("enabled", False)
    api_port = api_cfg.get("port", 9000)

    camera_cfg = cfg.get("camera_view", {})
    camera_enabled = camera_cfg.get("enabled", False)

    _app(f"Hourly chime: {'ON' if chime_enabled else 'OFF'}"
         f" (pauses after {idle_timeout_minutes}m idle)")
    _app(f"API server:  {'ON' if api_enabled else 'OFF'}"
         f"{' (port ' + str(api_port) + ')' if api_enabled else ''}")
    _app(f"Camera check: {'ON' if camera_enabled else 'OFF'}")
    _app("Press Ctrl+C to exit.")

    if api_enabled:
        threading.Thread(target=_start_api, args=(api_port,), daemon=True).start()

    last_announced = None
    was_away = False
    return_cooldown = 0  # skip N seconds after a return event

    try:
        while True:
            now = datetime.now()
            hour = now.hour

            away = idle_seconds() > idle_timeout_minutes * 60

            # ── return detection ──────────────────────────
            if camera_enabled and was_away and not away and return_cooldown <= 0:
                _app("User returned — checking identity...")
                try:
                    hud_dur = camera_cfg.get("hud_duration_seconds", 5)
                    voice_del = camera_cfg.get("voice_delay_seconds", 1)
                    from identity_check import is_admin
                    if is_admin(duration_seconds=hud_dur, voice_delay=voice_del):
                        _app("ADMIN confirmed — welcome back")
                    else:
                        _app("Not ADMIN or no face detected")
                except Exception as e:
                    _app(f"Camera check failed: {e}")
                return_cooldown = 120  # don't re-trigger for 2 min

            if return_cooldown > 0:
                return_cooldown -= 1

            # ── hourly chime ──────────────────────────────
            if (chime_enabled
                    and not away
                    and now.minute == 0
                    and now.second < 2
                    and last_announced != hour):
                phrase = chime(now)
                if phrase:
                    _app(phrase)
                last_announced = hour

            if now.minute >= 2:
                last_announced = None

            was_away = away
            time.sleep(1)

    except KeyboardInterrupt:
        _app("Shutting down.")


if __name__ == "__main__":
    main()
