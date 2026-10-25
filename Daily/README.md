# Daily

Windows background companion: hourly speech, return detection, CameraView HUD, and a VoiceLine HTTP API.

## Setup and launch

Follow the [root setup instructions](../README.md). Run from the POI root:

```powershell
uv sync
uv run python Daily/app.py
```

Daily uses the root environment with VoiceLine installed editable. CameraView runs in a separate process using the same Python executable. Press Ctrl+C to stop.

## Configuration

Shared defaults are in `config.json`. Add personal overrides to ignored `config.local.json`; nested dictionaries merge with the defaults. Keep tokens and local executable paths in that override file.

## Layout

| File | Purpose |
|---|---|
| app.py | Main loop, configuration, API and tunnel startup |
| api_server.py | HTTP endpoints for speech and library queries |
| hourly_chime.py | Time announcements and serialized speech |
| identity_check.py | CameraView subprocess integration |
| idle_detector.py | Win32 keyboard/mouse idle detection |
| config.json | Shared default configuration |

The MCP bridge belongs to `../integrations/mcp_server.py`. Client setup is documented in the root README.

## Logs

Runtime logs use `[HH:MM:SS] LEVEL category module | event` on stderr. API requests
include a request ID, path, status and response time; query strings are omitted.
Speech logs show queued, started, completed or failed events, including text
and duration. HTTP acceptance does not mean playback has completed. Telegram
polling reports the first failure and recovery rather than repeating errors.
Restart Daily after updating logging code. Logs are console-only.

Interactive terminals color categories: LOCAL cyan (loopback requests), WEB
magenta (remote/LAN or proxy-forwarded requests), SPEECH green (speech output),
TTS blue (audio generation/refresh), BUILD blue (assembly), SYSTEM white.
Warnings have yellow level labels; errors have red level labels. Forwarding
headers take precedence over loopback addresses so Cloudflare traffic is WEB.
These labels are for diagnostics, not authentication. Redirected logs and
terminals with `NO_COLOR` set use plain text.

Event labels also carry color: Queued cyan, Started/Generating blue,
Completed/Saved/Refreshed green, Request cyan or magenta by origin, warnings
yellow and failures red. Words and clip counts are bold yellow; speech text
is bright white, durations green, and voice/path/request metadata cyan.

## Checks

From the POI root, `uv run python -m unittest discover -s tests -v` runs automated tests. `uv run python scripts/check_daily.py` manually checks hourly speech and return detection, opening the camera and playing sound.

## HTTP and return detection

`GET /` reports health; `/say?text=...` accepts background playback on the PC;
`/say/local?text=...` returns a WAV for playback by the requesting browser.
`/time` speaks the current hour, `/stats` reports coverage, and `/missing?top=20`
lists missing common words (top: 1–1000). The `/say/local` name describes where
the audio is played, not whether the request is local or remote.

The optional Cloudflare quick tunnel publishes a random URL. Telegram can receive
that URL on startup and answer `/url`. The local MCP bridge uses the same API
through loopback, independently of the public URL.

Camera checks run on startup and on return after the idle timeout, with a
120-loop-iteration cooldown. The welcome is spoken after the HUD process exits,
and no earlier than `voice_delay_seconds` after first ADMIN detection.
