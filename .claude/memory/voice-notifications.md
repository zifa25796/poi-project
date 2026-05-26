---
name: voice-notifications
description: Use VoiceLine MCP to play spoken notifications at end of every turn
metadata:
  type: feedback
---

At the end of every response / turn, call the VoiceLine MCP tool:

  mcp__voice-line__voice_speak

with a short English message (10 words max) summarising what just happened. Always use English for the spoken message.

Format template (recommended):

  Done: <brief summary>

Examples:

  Done: README updated and pushed
  Done: Daily tests completed

**Why:** User prefers short spoken confirmations instead of watching the terminal.

Implementation notes:
- The assistant should construct a concise English summary (one short clause) and call the VoiceLine MCP tool with that text at the end of each turn.
- Keep messages under ~10 words and begin with "Done:" when appropriate.

[[voice-notifications]] in user memory is the canonical copy; this is the project-level mirror.
