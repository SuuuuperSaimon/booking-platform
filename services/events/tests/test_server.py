"""HTTP tests: a real server is started on a free port."""

from __future__ import annotations

import http.client
import json
import threading
from collections.abc import Iterator

import pytest

from services.events.app.server import create_server


@pytest.fixture()
def conn() -> Iterator[http.client.HTTPConnection]:
    server = create_server("127.0.0.1", 0)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    host, port = server.server_address[0], server.server_address[1]
    connection = http.client.HTTPConnection(str(host), port, timeout=5)
    try:
        yield connection
    finally:
        connection.close()
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def test_health_ok(conn: http.client.HTTPConnection) -> None:
    conn.request("GET", "/health")
    resp = conn.getresponse()
    body = resp.read()
    assert resp.status == 200
    assert resp.getheader("Content-Type") == "application/json; charset=utf-8"
    assert int(resp.getheader("Content-Length") or -1) == len(body)
    assert json.loads(body) == {"status": "ok"}


def test_unknown_path_404(conn: http.client.HTTPConnection) -> None:
    conn.request("GET", "/nope")
    resp = conn.getresponse()
    body = resp.read()
    assert resp.status == 404
    assert resp.getheader("Content-Type") == "application/json; charset=utf-8"
    assert int(resp.getheader("Content-Length") or -1) == len(body)
    assert json.loads(body) == {
        "error": {
            "code": "route_not_found",
            "message": "Route /nope not found",
            "details": None,
        }
    }


def test_post_health_405(conn: http.client.HTTPConnection) -> None:
    conn.request("POST", "/health", body=b"")
    resp = conn.getresponse()
    body = resp.read()
    assert resp.status == 405
    assert resp.getheader("Allow") == "GET"
    assert int(resp.getheader("Content-Length") or -1) == len(body)
    payload = json.loads(body)
    assert payload["error"]["code"] == "method_not_allowed"
    assert payload["error"]["details"] is None


def test_content_length_counts_bytes(conn: http.client.HTTPConnection) -> None:
    # Percent-encoded Cyrillic path ("нет"); the server decodes it, so the
    # error message contains non-ASCII characters (2 bytes each in UTF-8).
    conn.request("GET", "/%D0%BD%D0%B5%D1%82")
    resp = conn.getresponse()
    body = resp.read()
    assert resp.status == 404
    text = body.decode("utf-8")
    assert "нет" in json.loads(text)["error"]["message"]
    assert len(body) > len(text)  # bytes > characters
    assert int(resp.getheader("Content-Length") or -1) == len(body)