class EmptyParameterError(Exception):
    def __init__(self, parameter: str) -> None:
        self.message = f"{parameter} cannot be empty"
        super().__init__(self.message)

    def __str__(self):
        return f"{self.message}"
