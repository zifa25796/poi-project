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

### 2. VoiceLine (TTS)

```bash
cd VoiceLine
pip install -e .
pip install edge-tts pydub numpy sounddevice num2words
# pydub requires ffmpeg: winget install ffmpeg (Windows) / brew install ffmpeg (macOS)
python scripts/seed_tts_library.py   # pre-generate ~300 common words (recommended)
```

### 3. CameraView (HUD)

```bash
pip install face_recognition opencv-python numpy Pillow
```

Add 3–5 clear front-facing photos of yourself to `CameraView/known_faces/`. Verify:

```bash
cd CameraView
python machine_vision.py
```

### 4. Run Daily

```bash
cd Daily
python app.py
```

Quick test: `python test_features.py`

Daily will not function unless both VoiceLine and CameraView are properly configured.

## Project layout

```
Daily/
├── app.py              # Main loop
├── hourly_chime.py     # Time announcement via VoiceLine
├── identity_check.py   # Face check via CameraView (subprocess)
├── idle_detector.py    # Win32 keyboard/mouse idle detection
├── config.json         # Feature toggles & timing
├── test_features.py    # Quick test of both features
└── README.md
```

## External repos

- VoiceLine: https://github.com/zifa25796/VoiceLine
- CameraView (POI-MachineVision): https://github.com/zifa25796/POI-MachineVision

## Contributing

- VoiceLine or CameraView changes → open PRs on their respective repos.
- Daily changes → open PRs against this repo.
