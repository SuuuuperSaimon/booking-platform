class EmailNotUniqueError(Exception):
    def __init__(self, email: str) -> None:
        self.message = f"{email} is not unique"
        super().__init__(self.message)

    def __str__(self):
        return f"{self.message}"