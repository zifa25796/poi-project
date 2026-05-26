# poi project

This repository is an aggregator for the "Person of Interest" (POI) desktop tools in this workspace. It intentionally references two sibling projects that are maintained in their own GitHub repositories and includes the local "Daily" companion app.

## What this repo contains

- Daily (included): a background companion that announces the time on the hour and recognizes your face when you return to the computer.
- VoiceLine (referenced): external repo for POI-style speech synthesis — not maintained here.
- CameraView / POI-MachineVision (referenced): external repo for face detection HUD — not maintained here.

Note: CameraView and VoiceLine have their own GitHub pages and are referenced by link. They are intentionally ignored in this repository to avoid duplication.

## External repositories

- VoiceLine: https://github.com/zifa25796/VoiceLine
- POI-MachineVision (CameraView): https://github.com/zifa25796/POI-MachineVision

## Included: Daily

Daily is included as a local subfolder (`Daily/`). Key points (extracted from `Daily/README.md`):

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

Dependencies

Run:

```powershell
pip install face_recognition opencv-python numpy Pillow
```

(VoiceLine dependencies are provided by the external VoiceLine repo.)

Setup highlights

1. Add a clear photo of your face to `..\CameraView\known_faces\` so the HUD can identify you as ADMIN.
2. Edit `Daily/config.json` to configure timeouts and durations.

Usage

```powershell
cd C:\Root\CS\Python\POI\Daily
python app.py
```

Quick test:

```powershell
python test_features.py
```

## Notes about git and ignored components

This repository intentionally ignores the `CameraView/` and `VoiceLine/` subfolders because they are maintained in external GitHub repositories. If those folders are currently tracked in this repository's git index, they will be removed from the index (but not deleted from disk) so that future commits do not include them.

## Contributing

If you want to contribute to VoiceLine or CameraView, please open issues / pull requests on their respective GitHub repositories linked above. For changes to the Daily app (included here), send PRs against this repo.

---

Generated on 2026 by automation per user request.
