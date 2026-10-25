from __future__ import annotations

import sys
import os
import json
import urllib.parse
import urllib.request

API_URL = os.environ.get("VOICELINE_API_URL", "http://127.0.0.1:9000").rstrip("/")


def api_request(path: str, **params) -> dict:
    url = f"{API_URL}/{path}"
    if params:
        url += "?" + urllib.parse.urlencode(params)
    try:
        with urllib.request.urlopen(url, timeout=10) as response:
            return json.load(response)
    except (OSError, ValueError) as exc:
        raise RuntimeError(f"Daily API request failed at {API_URL}. Ensure Daily is running: {exc}") from exc


def handle_request(request: dict) -> dict | None:
    """处理 JSON-RPC 请求：initialize / tools/list / tools/call。"""
    method = request.get("method", "")

    # ── 握手 Handshake ──────────────────────────────────────────
    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": request["id"],
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {
                    "name": "voice-line",
                    "version": "0.1.0",
                },
            },
        }

    if method == "notifications/initialized":
        return None

    # ── 工具列表 Tool listing ────────────────────────────────────
    if method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": request["id"],
            "result": {
                "tools": [
                    {
                        "name": "voice_speak",
                        "description": "Queue Machine-style speech for playback through the running Daily HTTP API. Returns when accepted; playback continues in Daily and is visible in its logs. Daily must be running.",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "text": {
                                    "type": "string",
                                    "description": "The sentence to speak in Machine style",
                                },
                            },
                            "required": ["text"],
                        },
                    },
                    {
                        "name": "voice_stats",
                        "description": "Show VoiceLine word library coverage statistics.",
                        "inputSchema": {
                            "type": "object",
                            "properties": {},
                        },
                    },
                    {
                        "name": "voice_missing",
                        "description": "List common English words not yet in the VoiceLine library.",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "top": {
                                    "type": "integer",
                                    "description": "Number of missing words to show (default: 20)",
                                },
                            },
                        },
                    },
                ]
            },
        }

    # ── 工具调用 Tool execution ────────────────────────────────
    if method == "tools/call":
        params = request.get("params", {})
        tool_name = params.get("name", "")
        args = params.get("arguments", {})

        if tool_name == "voice_speak":
            text = args.get("text", "")
            if not isinstance(text, str) or not text.strip():
                return {"jsonrpc": "2.0", "id": request["id"],
                        "result": {"content": [{"type": "text", "text": "Error: text is required"}]}}

            api_request("say", text=text.strip())

            return {
                "jsonrpc": "2.0",
                "id": request["id"],
                "result": {
                    "content": [
                        {"type": "text", "text": "Accepted by Daily for playback"},
                    ],
                },
            }

        if tool_name == "voice_stats":
            stats = api_request("stats")["stats"]
            return {
                "jsonrpc": "2.0",
                "id": request["id"],
                "result": {
                    "content": [{"type": "text", "text": stats}],
                },
            }

        if tool_name == "voice_missing":
            top = args.get("top", 20)
            missing = api_request("missing", top=top)["missing"]
            lines = [f"  #{r:4d}  {w}" for r, w in missing]
            return {
                "jsonrpc": "2.0",
                "id": request["id"],
                "result": {
                    "content": [{"type": "text", "text": "\n".join(lines)}],
                },
            }

    return None


def main():
    """MCP 主循环：从 stdin 读 JSON-RPC 请求，处理后写回 stdout。"""
    # Read JSON-RPC messages from stdin, write to stdout
    buffer = ""
    while True:
        try:
            chunk = sys.stdin.readline()
            if not chunk:
                break
            buffer += chunk
            try:
                request = json.loads(buffer)
                buffer = ""
            except json.JSONDecodeError:
                continue  # wait for more data

            response = handle_request(request)
            if response is not None:
                sys.stdout.write(json.dumps(response) + "\n")
                sys.stdout.flush()
        except Exception as e:
            error = {
                "jsonrpc": "2.0",
                "id": request.get("id") if "request" in dir() else None,
                "error": {"code": -32000, "message": str(e)},
            }
            sys.stdout.write(json.dumps(error) + "\n")
            sys.stdout.flush()


if __name__ == "__main__":
    main()
