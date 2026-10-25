import io
import json
import unittest
import subprocess
import sys
from pathlib import Path
from unittest.mock import patch
from urllib.parse import parse_qs, urlsplit

from integrations import mcp_server


class McpApiTests(unittest.TestCase):
    def test_legacy_launcher_still_initializes(self):
        launcher = Path(__file__).resolve().parents[1] / "VoiceLine" / "mcp_server.py"
        result = subprocess.run(
            [sys.executable, str(launcher)],
            input=json.dumps({"jsonrpc": "2.0", "id": 7, "method": "initialize"}) + "\n",
            text=True, capture_output=True, check=True, timeout=10,
        )
        self.assertEqual(json.loads(result.stdout)["id"], 7)

    def call_tool(self, name, **arguments):
        return mcp_server.handle_request({
            "id": 1, "method": "tools/call",
            "params": {"name": name, "arguments": arguments},
        })

    def test_speech_is_forwarded_without_losing_query_characters(self):
        response = io.BytesIO(json.dumps({"ok": True}).encode())
        with patch.object(mcp_server.urllib.request, "urlopen", return_value=response) as send:
            result = self.call_tool("voice_speak", text="hello & goodbye?")
        url = urlsplit(send.call_args.args[0])
        self.assertEqual(url.path, "/say")
        self.assertEqual(parse_qs(url.query), {"text": ["hello & goodbye?"]})
        self.assertIn("Accepted", result["result"]["content"][0]["text"])

    def test_daily_unavailable_is_reported(self):
        with patch.object(mcp_server.urllib.request, "urlopen", side_effect=OSError("refused")):
            with self.assertRaisesRegex(RuntimeError, "Ensure Daily is running"):
                self.call_tool("voice_speak", text="hello")

    def test_stats_and_missing_use_daily(self):
        with patch.object(mcp_server, "api_request", return_value={"stats": "coverage"}) as api:
            self.assertEqual(self.call_tool("voice_stats")["result"]["content"][0]["text"], "coverage")
            api.assert_called_once_with("stats")
        with patch.object(mcp_server, "api_request", return_value={"missing": [[1, "hello"]]}) as api:
            self.assertIn("hello", self.call_tool("voice_missing", top=5)["result"]["content"][0]["text"])
            api.assert_called_once_with("missing", top=5)


if __name__ == "__main__":
    unittest.main()
