"""HTTP server for the Events service (standard library only)."""

from __future__ import annotations

import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any
from urllib.parse import unquote

DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8002

# path -> allowed methods
ROUTES: dict[str, tuple[str, ...]] = {
    "/health": ("GET",),
}


class EventsHandler(BaseHTTPRequestHandler):
    """Request handler; HTTP/1.0, so the connection closes after each response."""

    protocol_version = "HTTP/1.0"
    server_version = "EventsService/0.1"

    def _send_json(
        self,
        status: int,
        payload: dict[str, Any],
        extra_headers: dict[str, str] | None = None,
    ) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        for name, value in (extra_headers or {}).items():
            self.send_header(name, value)
        self.end_headers()
        self.wfile.write(body)

    def _send_error(
        self,
        status: int,
        code: str,
        message: str,
        extra_headers: dict[str, str] | None = None,
    ) -> None:
        self._send_json(
            status,
            {"error": {"code": code, "message": message, "details": None}},
            extra_headers,
        )

    def _dispatch(self) -> None:
        path = unquote(self.path.split("?", 1)[0])
        allowed = ROUTES.get(path)
        if allowed is None:
            self._send_error(404, "route_not_found", f"Route {path} not found")
            return
        if self.command not in allowed:
            self._send_error(
                405,
                "method_not_allowed",
                f"Method {self.command} not allowed for {path}",
                {"Allow": ", ".join(allowed)},
            )
            return
        if path == "/health":
            self._send_json(200, {"status": "ok"})

    def do_GET(self) -> None:  # noqa: N802
        self._dispatch()

    def do_POST(self) -> None:  # noqa: N802
        self._dispatch()

    def do_PUT(self) -> None:  # noqa: N802
        self._dispatch()

    def do_PATCH(self) -> None:  # noqa: N802
        self._dispatch()

    def do_DELETE(self) -> None:  # noqa: N802
        self._dispatch()


def create_server(host: str, port: int) -> ThreadingHTTPServer:
    """Create the server; port=0 picks a free port (handy for tests)."""
    return ThreadingHTTPServer((host, port), EventsHandler)


def main() -> None:
    host = os.environ.get("HOST", DEFAULT_HOST)
    port = int(os.environ.get("PORT", str(DEFAULT_PORT)))
    server = create_server(host, port)
    print(f"Events service listening on http://{host}:{server.server_address[1]}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()