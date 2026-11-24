from uuid import uuid4
from argon2 import PasswordHasher
from typing import Any

from services.workspaces.app.infrastructure.database.user.user_repository import (
    UserRepository,
)
from services.workspaces.app.infrastructure.database.db_connnector import (
    DbConnector,
)
from services.workspaces.app.domain.error.user.empty_parameter_error import (
    EmptyParameterError,
)
from services.workspaces.app.domain.entity.user import (
    User,
)

class RegistrationService:
    def __init__(self) -> None:
        self.conn = DbConnector()
        self.hasher = PasswordHasher()

    def create_user(self, data) -> dict[str, Any]:
        parameter = None

        if data["email"] == "":
            parameter = 'email'

        if data["password"] == "":
            parameter = 'password'

        if data["username"] == "":
            parameter = 'username'

        if parameter is not None:
            raise EmptyParameterError(parameter)

        user = User(
            uuid4(),
            data["email"],
            self.hasher.hash(data["password"]),
            data["username"]
        )

        with self.conn.connect() as connection:
            users = UserRepository(connection)
            created_user = users.create_user(user)

        return created_user
