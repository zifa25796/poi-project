# poi project

This repository is an aggregator for the "Person of Interest" (POI) desktop tools in this workspace. It references two sibling projects that are maintained in their own GitHub repositories and includes the local "Daily" companion app.

## What this repo contains

- Daily (included): a background companion that announces the time on the hour and recognizes your face when you return to the computer.
- VoiceLine (submodule): POI-style speech synthesis (submodule pointing to https://github.com/zifa25796/VoiceLine).
- CameraView / POI-MachineVision (submodule): face detection HUD (submodule pointing to https://github.com/zifa25796/POI-MachineVision).

## Submodules

VoiceLine and CameraView are added as git submodules. On GitHub they appear as clickable entries that link to the respective repositories.

After cloning this repository, initialize submodules with:

```bash
# clone including submodules
git clone --recurse-submodules https://github.com/zifa25796/poi-project.git

# or, if you already cloned without submodules
git submodule update --init --recursive
```

To update a submodule to its latest upstream commit:

```bash
cd VoiceLine
git checkout main
git pull origin main
cd ..
# record the new submodule pointer in the parent repo
git add VoiceLine
git commit -m "Update VoiceLine submodule"
git push
```

## External repositories

- VoiceLine: https://github.com/zifa25796/VoiceLine
- POI-MachineVision (CameraView): https://github.com/zifa25796/POI-MachineVision

## Included: Daily

Daily is included as a local subfolder (`Daily/`). IMPORTANT: Daily depends on two sibling projects — VoiceLine (TTS) and CameraView (HUD). You MUST configure/install those projects before Daily will function correctly. See the Prerequisites below.

Prerequisites (required before running Daily)

1. Initialize submodules (only needed if you cloned this repo):

```bash
git submodule update --init --recursive
```

2. VoiceLine (TTS)
- Install dependencies using the system Python (not a conda environment):

```powershell
C:\Users\zeke\AppData\Local\Programs\Python\Python310\python.exe -m pip install -e VoiceLine
C:\Users\zeke\AppData\Local\Programs\Python\Python310\python.exe -m pip install edge-tts pydub numpy sounddevice num2words
# Ensure ffmpeg is installed on the system (required by pydub):
# Windows: winget install ffmpeg
```
- Pre-seed the TTS word library (recommended):

```bash
cd VoiceLine
C:\Users\zeke\AppData\Local\Programs\Python\Python310\python.exe scripts/seed_tts_library.py
```

3. CameraView (HUD)
- Install dependencies:

```powershell
pip install face_recognition opencv-python numpy Pillow
```
- Add 3–5 clear front-facing photos of yourself to:

```
CameraView/known_faces/
```
- Run the HUD to verify your photos are recognized:

```bash
cd CameraView
C:\Users\zeke\AppData\Local\Programs\Python\Python310\python.exe machine_vision.py
```

Daily will not announce the time or perform return-detection unless both VoiceLine and CameraView are properly configured and available to the system Python environment.

Features

- Hourly chime — speaks the time at the top of each hour. Pauses automatically when you're away.
- Return detection — opens a CameraView HUD on return from idle, scans your face, and if you're ADMIN, says "welcome back admin."

Project layout

```
Daily/
├── app.py                # Main loop
├── hourly_chime.py       # Time announcement via VoiceLine
├── identity_check.py     # Face check via CameraView (subprocess)
├── idle_detector.py      # Win32 keyboard/mouse idle detection
├── config.json           # Feature toggles & timing
├── test_features.py      # Quick test of both features
└── README.md
```

## Daily dependencies & run

Install required Python packages for Daily / CameraView interaction (if not already installed):

```powershell
pip install face_recognition opencv-python numpy Pillow
```

Run the companion:

```powershell
cd C:\Root\CS\Python\POI\Daily
C:\Users\zeke\AppData\Local\Programs\Python\Python310\python.exe app.py
```

Quick test:

```powershell
C:\Users\zeke\AppData\Local\Programs\Python\Python310\python.exe test_features.py
```

## CameraView (HUD) — initialization notes

CameraView is provided as a submodule and is responsible for webcam face detection and the HUD.

Setup summary:

1. Install dependencies (if not already):

```bash
pip install face_recognition opencv-python numpy Pillow
```

2. Add photos of yourself for identity matching:

- Put 3–5 clear, front-facing photos (jpg or png) of yourself into `CameraView/known_faces/`.
- Use varied lighting/angles to improve recognition.

3. Run the HUD for a quick check:

```bash
cd CameraView
python machine_vision.py
```

Notes:
- CameraView expects a webcam and uses `face_recognition` (dlib/HOG) for matching. You can tune parameters at the top of `machine_vision.py`.
- If you run Daily's return-detection feature, `Daily/identity_check.py` will launch CameraView in a subprocess to scan and label the user.

## VoiceLine — initialization notes (TTS library & word generation)

VoiceLine is provided as a submodule and supplies the POI-style speech synthesis used by Daily.

Quick setup:

```bash
# from repository root (or inside VoiceLine)
cd VoiceLine
pip install -e .
pip install edge-tts
# pydub needs ffmpeg installed on the system
# Windows: winget install ffmpeg
# macOS: brew install ffmpeg
```

Pre-generate a baseline vocabulary (recommended):

```bash
# seeds ~300 common words (takes a few minutes)
python scripts/seed_tts_library.py
```

- Missing words are automatically synthesized on first use and cached, but seeding the library speeds up early usage.
- Test a phrase with:

```bash
python test_speak.py "can you hear me"
```

Additional notes:
- VoiceLine stores generated audio clips and a small SQLite DB in `VoiceLine/data/` (this directory is gitignored).
- If you change VoiceLine settings you may want to backup `VoiceLine/data/voice_line.db` before large operations.

## Notes about backups + local copies

When adding the submodules, any previous local copies were moved to `backups/` during setup (if present). If you do not see files in `backups/`, the local copies were likely already moved into the submodule entries; the active working copy for code is the submodule directories (`VoiceLine/`, `CameraView/`).

## Contributing

- For VoiceLine or CameraView changes, open PRs on their respective repositories (links above).
- For Daily changes, open PRs against this repository.

---

Generated on 2026 by automation per user request.
