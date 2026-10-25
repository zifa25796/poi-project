import unittest

from starlette.requests import Request
from starlette.responses import Response

from api_server import log_request, request_origin


class RequestLogTests(unittest.IsolatedAsyncioTestCase):
    def test_origin_distinguishes_tunnel_from_loopback(self):
        cases = [("127.0.0.1", [], "LOCAL"), ("::1", [], "LOCAL"),
                 ("127.0.0.1", [(b"cf-ray", b"test")], "WEB"),
                 ("127.0.0.1", [(b"x-forwarded-for", b"203.0.113.1")], "WEB"),
                 ("192.168.1.10", [], "WEB")]
        for host, headers, expected in cases:
            with self.subTest(host=host, headers=headers):
                request = Request({"type": "http", "headers": headers, "client": (host, 1234)})
                self.assertEqual(request_origin(request), expected)

    async def test_request_logs_path_status_and_returns_id(self):
        request = Request({"type": "http", "method": "GET", "path": "/say",
                           "query_string": b"text=secret", "headers": [],
                           "client": ("127.0.0.1", 1234), "scheme": "http", "server": ("localhost", 9000)})

        async def respond(request):
            return Response(status_code=400)

        with self.assertLogs("daily.api", level="WARNING") as logs:
            response = await log_request(request, respond)
        self.assertIn("GET /say status=400", logs.output[0])
        self.assertNotIn("secret", logs.output[0])
        self.assertEqual(len(response.headers["X-Request-ID"]), 8)

    async def test_failure_is_logged_and_propagated(self):
        request = Request({"type": "http", "method": "GET", "path": "/say", "headers": []})

        async def fail(request):
            raise RuntimeError("test failure")

        with self.assertLogs("daily.api", level="ERROR") as logs:
            with self.assertRaises(RuntimeError):
                await log_request(request, fail)
        self.assertIn("Request failed", logs.output[0])


if __name__ == "__main__":
    unittest.main()
