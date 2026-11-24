from services.workspaces.app.domain.entity.user import User

def test_successful()-> None:
    id = 'some-random-uuid'
    email = 'test@mail.com'
    password = 'some-password'
    username = 'some-username'

    user = User(
        id,
        email,
        password,
        username
    )

    assert user.id == id
    assert user.email == email
    assert user.password == password
    assert user.username == username

