import pytest
from datetime import datetime, timezone
from unittest.mock import Mock
import json
from io import BytesIO

from services.workspaces.app.application.registration.handle_registration import RegistrationHandle
from services.workspaces.app.domain.error.user.empty_parameter_error import (
    EmptyParameterError,
)


def test_successful(monkeypatch: pytest.MonkeyPatch) -> None:
    data = {
        "email": "test@example.com",
        "password": "example-password",
        "username": "Alex",
    }

    raw_body = json.dumps(data).encode("utf-8")

    environ = {
        "CONTENT_TYPE": "application/json",
        "CONTENT_LENGTH": str(len(raw_body)),
        "wsgi.input": BytesIO(raw_body),
    }

    service_result = {
        "id": "a2ae8b09-b8ec-4906-bf1b-1ed5f03033bc",
        "username": "Alex",
        "created_at": datetime(2026, 1, 1, tzinfo=timezone.utc),
    }

    expected_response = {
        "id": "a2ae8b09-b8ec-4906-bf1b-1ed5f03033bc",
        "username": "Alex",
        "created_at": "2026-01-01T00:00:00+00:00",
    }

    handler = RegistrationHandle()
    handler.service = Mock()
    handler.service.create_user.return_value = service_result

    status, response = handler.handle_register_user(environ)

    assert status == 201
    assert response == expected_response

    handler.service.create_user.assert_called_once()

def test_failed_with_invalid_json() -> None:
    environ = {
        "CONTENT_TYPE": "application/json",
        "CONTENT_LENGTH": str(len(b'{"email":')),
        "wsgi.input": BytesIO(b'{"email":'),
    }

    handler = RegistrationHandle()
    handler.service = Mock()

    status, response = handler.handle_register_user(environ)

    assert status == 400
    assert response == {"error": "Invalid JSON"}

    handler.service.create_user.assert_not_called()

def test_failed_with_wrong_service() -> None:
    data = {
        "email": "test@example.com",
        "password": "example-password",
        "username": "",
    }

    raw_body = json.dumps(data).encode("utf-8")

    environ = {
        "CONTENT_TYPE": "application/json",
        "CONTENT_LENGTH": str(len(raw_body)),
        "wsgi.input": BytesIO(raw_body),
    }

    handler = RegistrationHandle()
    handler.service = Mock()
    handler.service.create_user.side_effect = EmptyParameterError("username")

    status, response = handler.handle_register_user(environ)

    assert status == 400
    assert response == {"error": "username cannot be empty"}

    handler.service.create_user.assert_called_once_with(data)

