"""Daily — Person of Interest desktop companion.

Orchestrates VoiceLine speech and CameraView surveillance.
Feature toggles live in config.json.
"""

import json
import logging
import os
import re
import subprocess
import threading
import time
import urllib.request
from datetime import datetime

from hourly_chime import chime
from idle_detector import idle_seconds
from voice_line.logging_setup import configure_logging

configure_logging()

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config.json")

# ── shared state ─────────────────────────────────────────────────
_tunnel_url = None
_url_lock = threading.Lock()


def _app(msg: str, level=logging.INFO):
    logging.getLogger("daily.app").log(level, msg)


def _cf(msg: str, level=logging.INFO):
    logging.getLogger("daily.tunnel").log(level, msg)


def _deep_merge(base: dict, override: dict) -> dict:
    for key, value in override.items():
        if key in base and isinstance(base[key], dict) and isinstance(value, dict):
            _deep_merge(base[key], value)
        else:
            base[key] = value
    return base


def load_config() -> dict:
    with open(CONFIG_PATH) as f:
        cfg = json.load(f)
    local_path = os.path.join(os.path.dirname(__file__), "config.local.json")
    if os.path.exists(local_path):
        with open(local_path) as f:
            _deep_merge(cfg, json.load(f))
    return cfg


def _start_api(port: int):
    import uvicorn
    from api_server import app as api_app

    uvicorn.run(api_app, host="0.0.0.0", port=port,
                log_config=None, access_log=False)


def _send_telegram(bot_token: str, chat_id: str, msg: str):
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    data = json.dumps({"chat_id": chat_id, "text": msg}).encode()
    req = urllib.request.Request(url, data=data,
                                 headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=10):
            logging.getLogger("daily.tg").info("Message sent")
    except Exception as e:
        logging.getLogger("daily.tg").warning("Send failed | %s", type(e).__name__)


def _start_cloudflare_tunnel(port: int, cloudflared_path: str,
                              tg_enabled: bool = False,
                              tg_token: str = "", tg_chat: str = ""):
    global _tunnel_url
    cmd = [cloudflared_path, "tunnel", "--url", f"http://localhost:{port}"]
    try:
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )
    except FileNotFoundError:
        _cf(f"cloudflared not found at '{cloudflared_path}'", logging.ERROR)
        return
    except Exception as e:
        _cf(f"Failed to start: {e}", logging.ERROR)
        return

    url_pattern = re.compile(r"https://[a-zA-Z0-9-]+\.trycloudflare\.com")
    found = False
    for line in proc.stdout:
        if not found and (m := url_pattern.search(line)):
            found = True
            with _url_lock:
                _tunnel_url = m.group(0)
            _cf(f"Public URL: {_tunnel_url}")
            if tg_enabled:
                _send_telegram(tg_token, tg_chat, _tunnel_url)

    code = proc.wait()
    with _url_lock:
        _tunnel_url = None
    _cf(f"Tunnel exited | code={code}", logging.WARNING)


def _poll_telegram(bot_token: str):
    """Long-poll Telegram for /url command, reply with current tunnel URL."""
    offset = 0
    poll_failed = False
    api_url = f"https://api.telegram.org/bot{bot_token}"
    while True:
        try:
            data = json.dumps({"offset": offset, "timeout": 30}).encode()
            req = urllib.request.Request(f"{api_url}/getUpdates", data=data,
                                         headers={"Content-Type": "application/json"})
            resp = urllib.request.urlopen(req, timeout=35)
            result = json.loads(resp.read())
            resp.close()
            if poll_failed:
                logging.getLogger("daily.tg").info("Polling recovered")
                poll_failed = False
            for update in result.get("result", []):
                offset = update["update_id"] + 1
                msg = update.get("message", {})
                text = msg.get("text", "")
                chat_id = msg.get("chat", {}).get("id")
                if text.strip() == "/url" and chat_id:
                    with _url_lock:
                        reply = _tunnel_url or "Tunnel not ready yet"
                    _send_telegram(bot_token, str(chat_id), reply)
        except Exception as exc:
            if not poll_failed:
                logging.getLogger("daily.tg").warning("Polling failed; retrying | %s", type(exc).__name__)
                poll_failed = True
            time.sleep(5)


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

    cf_cfg = cfg.get("cloudflare_tunnel", {})
    cf_enabled = cf_cfg.get("enabled", False)
    cf_path = cf_cfg.get("cloudflared_path", "cloudflared.exe")
    tg_cfg = cf_cfg.get("telegram", {})
    tg_enabled = tg_cfg.get("enabled", False)
    tg_token = tg_cfg.get("bot_token", "")
    tg_chat = tg_cfg.get("chat_id", "")

    _app(f"Hourly chime: {'ON' if chime_enabled else 'OFF'}"
         f" (pauses after {idle_timeout_minutes}m idle)")
    _app(f"API server:  {'ON' if api_enabled else 'OFF'}"
         f"{' (port ' + str(api_port) + ')' if api_enabled else ''}")
    _app(f"Cloudflare:  {'ON' if cf_enabled else 'OFF'}")
    _app(f"Camera check: {'ON' if camera_enabled else 'OFF'}")
    _app("Press Ctrl+C to exit.")

    if api_enabled:
        threading.Thread(target=_start_api, args=(api_port,), daemon=True).start()

    if cf_enabled:
        threading.Thread(target=_start_cloudflare_tunnel,
                         args=(api_port, cf_path, tg_enabled, tg_token, tg_chat),
                         daemon=True).start()

    if tg_enabled:
        threading.Thread(target=_poll_telegram, args=(tg_token,),
                         daemon=True).start()

    # ── startup identity check ──────────────────────────
    if camera_enabled:
        _app("Checking identity on startup...")
        try:
            hud_dur = camera_cfg.get("hud_duration_seconds", 5)
            voice_del = camera_cfg.get("voice_delay_seconds", 1)
            from identity_check import is_admin
            if is_admin(duration_seconds=hud_dur, voice_delay=voice_del):
                _app("ADMIN confirmed — welcome back")
            else:
                _app("Not ADMIN or no face detected")
        except Exception as e:
            _app(f"Startup camera check failed: {e}", logging.ERROR)

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
                    _app(f"Camera check failed: {e}", logging.ERROR)
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
