# Daily — Person of Interest Desktop Companion

A background companion app that announces the time on the hour and recognizes
your face when you return to the computer — all in the style of *Person of
Interest*'s "The Machine."

## Features

**Hourly Chime** — Speaks the time at the top of each hour (e.g. "nine o'clock").
Pauses automatically when you're away from the keyboard.

**Return Detection** — When you come back after being idle, opens the Machine
surveillance HUD, scans your face, and if you're ADMIN, says *"welcome back
admin."*

## Project Layout

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

Depends on two sibling projects:

| Project | Path | Purpose |
|---------|------|---------|
| VoiceLine | `../VoiceLine` | POI-style speech synthesis |
| CameraView | `../CameraView` | Face detection HUD |

## Setup

### 1. Install dependencies

```powershell
pip install face_recognition opencv-python numpy Pillow
```

VoiceLine dependencies are already installed if you've run it before.

### 2. Add your face

Put a clear photo of your face (`.jpg` or `.png`) in:

```
..\CameraView\known_faces\
```

The HUD will recognize you as ADMIN.

### 3. Configure

Edit `config.json`:

```json
{
  "hourly_chime": {
    "enabled": true,              // Master on/off
    "idle_timeout_minutes": 5     // Pause chime after N min no activity
  },
  "camera_view": {
    "enabled": true,              // Master on/off
    "hud_duration_seconds": 5,    // How long HUD window stays
    "voice_delay_seconds": 1      // Wait N seconds before "welcome back"
  }
}
```

## Usage

### Run the companion

```powershell
cd C:\Root\CS\Python\POI\Daily
python app.py
```

Press `Ctrl+C` to stop.

### Quick test

```powershell
python test_features.py
```

Tests both the hourly chime and a simulated return detection.

## How It Works

1. **Idle detection** — Polls `GetLastInputInfo` every second. If no keyboard or
   mouse input for `idle_timeout_minutes`, the user is considered "away."

2. **Hourly chime** — At minute 0 of each hour, calls VoiceLine to speak the
   time. Skipped if the user is away.

3. **Return detection** — When idle transitions from "away" to "present," the
   CameraView HUD opens in a subprocess. If ADMIN is detected, VoiceLine speaks
   *"welcome back admin"* after the configured delay. The HUD window closes
   after `hud_duration_seconds`.

4. **Subprocess isolation** — The HUD scan runs in a separate process to avoid
   OpenCV camera resource contention with the main loop.
