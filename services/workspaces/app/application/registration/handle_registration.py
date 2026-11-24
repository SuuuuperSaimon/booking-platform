import json

from wsgiref.types import WSGIEnvironment

from services.workspaces.app.domain.service.registration.registration_service import (
    RegistrationService,
    EmptyParameterError,
)

class RegistrationHandle:
    def __init__(self) -> None:
        self.service = RegistrationService()

    def handle_register_user(self, environ: WSGIEnvironment):
        content_type = environ.get("CONTENT_TYPE", "")
        media_type = content_type.split(";", 1)[0].strip().lower()

        if media_type != "application/json":
            return 415, {"error": "Content-Type must be application/json"}

        length = int(environ.get("CONTENT_LENGTH"))
        raw_body = environ["wsgi.input"].read(length)

        try:
            data = json.loads(raw_body.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            return 400, {"error": "Invalid JSON"}

        try:
            user = self.service.create_user(data)
        except EmptyParameterError as error:
            return 400, {"error": str(error)}

        return 201, {
            "id": str(user["id"]),
            "username": user["username"],
            "created_at": user["created_at"].isoformat(),
        }