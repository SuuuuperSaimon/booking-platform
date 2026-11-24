from datetime import datetime, timezone
from uuid import UUID
from unittest.mock import MagicMock, Mock

import pytest

from services.workspaces.app.domain.error.user.empty_parameter_error import EmptyParameterError
from services.workspaces.app.domain.service.registration.registration_service import RegistrationService
import services.workspaces.app.infrastructure.database.user.user_repository as repository

@pytest.mark.parametrize(
    "empty_field",
    ["email", "password", "username"]
)
def test_create_user_rejects_empty_field(empty_field: str)-> None:
    data = {
        "email": "test@example.com",
        "password": "example-password",
        "username": "Alex",
    }

    data[empty_field] = ""

    service = RegistrationService()
    service.conn = Mock()
    service.hasher = Mock()

    with pytest.raises(EmptyParameterError) as error:
        service.create_user(data)

    assert str(error.value) == f"{empty_field} cannot be empty"

    service.conn.connect.assert_not_called()
    service.hasher.hash.assert_not_called()


def test_successful_create_user(monkeypatch: pytest.MonkeyPatch)-> None:
    data = {
        "email": "test@example.com",
        "password": "example-password",
        "username": "Alex",
    }

    expected_user = {
        "id": UUID("a2ae8b09-b8ec-4906-bf1b-1ed5f03033bc"),
        "username": "Alex",
        "created_at": datetime(2026, 1, 1, tzinfo=timezone.utc),
    }

    create_user_mock = Mock()
    create_user_mock.return_value = expected_user

    monkeypatch.setattr(
        repository.UserRepository,
        "create_user",
        create_user_mock
    )

    service = RegistrationService()

    connection = MagicMock()
    connection.__enter__.return_value = connection
    service.conn = Mock()
    service.conn.connect.return_value = connection

    service.hasher = Mock()
    service.hasher.hash.return_value = 'some-hashed-password'

    user_data = service.create_user(data)

    assert user_data == expected_user

    service.conn.connect.assert_called_once()
    service.hasher.hash.assert_called_once()




