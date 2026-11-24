import json
import logging
from wsgiref.types import StartResponse, WSGIEnvironment
from http import HTTPStatus

from services.workspaces.app.application.registration.handle_registration import RegistrationHandle

class App:
    def __init__(self) -> None:
        self.handler = RegistrationHandle()
        self.logger = logging.getLogger(__name__)

    def __call__(
        self,
        environ: WSGIEnvironment,
        start_response: StartResponse,
    ) -> list[bytes]:
        method = environ["REQUEST_METHOD"]
        path = environ["PATH_INFO"]

        extra_headers: list[tuple[str, str]] = []
        payload: dict[str, object]

        try:
            if path == "/health" and method == "GET":
                status_code = 200
                payload = {"status": "ok"}
            elif path == "/users":
                if method == "POST":
                    status_code, payload = self.handler.handle_register_user(environ)
                else:
                    status_code = 405
                    payload = {"error": "Method not allowed"}
                    extra_headers.append(("Allow", "POST"))
            else:
                status_code = 404
                payload = {"error": "Not found"}

            body = json.dumps(
                payload,
                ensure_ascii=False,
            ).encode("utf-8")
        except Exception:
            self.logger.exception("Unhandled error while processing request")

            status_code = 500
            body = b'{"error":"Internal server error"}'

        status = f"{status_code} {HTTPStatus(status_code).phrase}"

        headers = [
            ("Content-Type", "application/json; charset=utf-8"),
            ("Content-Length", str(len(body))),
        ]
        headers.extend(extra_headers)

        start_response(status, headers)

        return [body]

application = App()