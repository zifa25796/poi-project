# Project rules

- Keep code simple, direct, and self-documenting. Comment only on non-obvious reasons. Do not add docstrings unless requested.
- POI owns Daily and integrations. VoiceLine and CameraView are independent Git submodules. Commit their changes in their own repositories before updating POI revisions.
- Keep machine-specific settings, face photos, generated audio, databases, backups, and release archives out of Git.
- Use the root uv environment for POI development. See README.md for validation commands.
- Play a short English completion or action notification through VoiceLine, under ten words, without saving audio.
