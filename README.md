# POI

Person of Interest desktop companion. Daily coordinates speech, hourly announcements, face recognition, and the HTTP API.

## Repositories

| Component | Responsibility | Repository |
|---|---|---|
| Daily + integrations | Companion app, HTTP API, Daily MCP bridge | [poi-project](https://github.com/zifa25796/poi-project) |
| VoiceLine | Independent speech engine and CLI | [VoiceLine](https://github.com/zifa25796/VoiceLine) |
| CameraView | Independent face recognition HUD | [POI-MachineVision](https://github.com/zifa25796/POI-MachineVision) |

VoiceLine and CameraView are Git submodules pinned to specific commits. Commit and push changes in each component repository first, then update its revision in POI. A change to a submodule file is not included by committing only the parent repository.

## Setup

Windows, Python 3.10+, uv, ffmpeg, and a webcam are required for the complete companion. Daily idle detection uses Win32. The native dlib dependency may require a compatible compiler if no wheel is available.

```powershell
git clone --recurse-submodules https://github.com/zifa25796/poi-project.git
cd poi-project
uv sync
```

For an existing checkout, run `git submodule update --init --recursive` before `uv sync`. Install ffmpeg and put it on PATH, or use VoiceLine's local bundled ffmpeg.

Put your face photos in `CameraView/known_faces/`; photos and face caches are ignored. Keep shared defaults in `Daily/config.json`. Put personal overrides in ignored `Daily/config.local.json`, which is merged into the defaults.

Run every command below from the POI root:

```powershell
uv run python Daily/app.py
uv run python CameraView/machine_vision.py
uv run python VoiceLine/scripts/seed_tts_library.py
```

`start.bat` launches Daily regardless of the checkout location. CameraView also supports independent installation; see its README.

If a copied or old `.venv` points to a missing Python installation, close processes using it, rename it as a backup, and recreate it with `uv sync --python 3.10`. Existing voice data lives outside `.venv`.

## MCP

The Daily HTTP bridge is `integrations/mcp_server.py`. Start Daily first; the default URL is `http://127.0.0.1:9000`. Copy `.mcp.example.json` into your client's local configuration and replace both placeholder paths with your checkout path. Override `VOICELINE_API_URL` when needed. Local `.mcp.json` files are ignored.

The old `VoiceLine/mcp_server.py` path remains a compatibility launcher inside a POI checkout. Standalone VoiceLine provides the Python API and CLI without Daily.

## Layout

```text
POI/
├── Daily/                 Companion implementation and default config
├── integrations/          MCP adapter for Daily
├── scripts/               Manual checks that use audio/camera
├── tests/                 Automated integration tests
├── VoiceLine/             Speech submodule: src/, tests/, scripts/, archive/
├── CameraView/            HUD submodule
├── AGENTS.md              Shared coding and assistant instructions
├── .mcp.example.json      Portable MCP configuration template
├── pyproject.toml
├── uv.lock
└── start.bat
```

`VoiceLine/src/voice_line/assets/` contains packaged sound resources. `VoiceLine/data/` contains generated clips and the database; set `VOICELINE_DATA_DIR` to override that location. Existing data paths remain the default. Back up the database together with its clips; existing records may contain absolute clip paths.

`backups/`, `releases/`, generated data, personal settings, and build outputs stay local. Upload distribution ZIPs to GitHub Releases rather than committing them.

## Validation

Automated tests do not open the camera or play speech:

```powershell
uv run python -m unittest discover -s tests -v
uv run python -m unittest discover -s VoiceLine/tests -v
uv run python -m unittest discover -s Daily -p test_logging.py -v
```

Manual checks use speakers and/or the camera:

```powershell
uv run python scripts/check_daily.py
uv run python VoiceLine/scripts/check_speech.py "can you hear me"
```
