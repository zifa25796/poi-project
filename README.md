# POI

Aggregator for the "Person of Interest" desktop tools. Includes the Daily companion app and references two sibling projects as git submodules.

## What's here

- **Daily** — background companion that announces the time on the hour and recognizes your face when you return to the computer.
- **VoiceLine** (submodule) — POI-style speech synthesis.
- **CameraView** (submodule) — face detection HUD.

## Setup

### 1. Clone & submodules

```bash
git clone --recurse-submodules <repo-url>
# or if already cloned:
git submodule update --init --recursive
```

### 2. Install dependencies (uv)

```bash
uv sync
```

This creates a `.venv` and installs all packages, including VoiceLine as an editable install.

System requirement: **ffmpeg** must be installed (required by pydub for audio processing).
- Windows: `winget install ffmpeg`
- macOS: `brew install ffmpeg`

### 3. CameraView (HUD)

Add 3–5 clear front-facing photos of yourself to `CameraView/known_faces/`. Verify:

```bash
uv run python CameraView/machine_vision.py
```

### 4. Seed VoiceLine (optional)

Pre-generate ~300 common words to speed up first use:

```bash
uv run python VoiceLine/scripts/seed_tts_library.py
```

### 5. Run Daily

```bash
uv run python Daily/app.py
```

Quick test: `uv run python Daily/test_features.py`

## Project layout

```
Daily/
├── app.py              # Main loop
├── hourly_chime.py     # Time announcement via VoiceLine
├── identity_check.py   # Face check via CameraView (subprocess)
├── idle_detector.py    # Win32 keyboard/mouse idle detection
├── config.json         # Feature toggles & timing
├── api_server.py       # HTTP API for remote trigger
├── test_features.py    # Quick test of both features
└── README.md
```

## External repos

- VoiceLine: https://github.com/zifa25796/VoiceLine
- CameraView (POI-MachineVision): https://github.com/zifa25796/POI-MachineVision

## Contributing

- VoiceLine or CameraView changes → open PRs on their respective repos.
- Daily changes → open PRs against this repo.
