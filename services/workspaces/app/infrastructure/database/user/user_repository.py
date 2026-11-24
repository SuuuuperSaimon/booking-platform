class UserRepository:
    def __init__(self, connection):
        self.connection = connection
        self.cur = self.connection.cursor()

    def find_user_by_email(self, email):
        cur = self.cur.execute("SELECT * FROM users WHERE email = %s", (email,))

        return cur.fetchone()

    def find_user_by_username(self, username):
        cur = self.cur.execute("SELECT * FROM users WHERE display_name = %s", (username,))

        return cur.fetchone()

    def create_user(self, user):
        self.cur.execute(
            """
            INSERT INTO users (
                id,
                email,
                password,
                display_name
            ) VALUES (%s, %s, %s, %s)
            RETURNING id, display_name AS username, created_at
            """,
            (
                user.id,
                user.email,
                user.password,
                user.username,
            ),
        )

        created_user = self.cur.fetchone()

        if created_user is None:
            raise RuntimeError("INSERT did not return the created user")

        return created_user

