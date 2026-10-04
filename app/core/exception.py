


class InvalidCredentialException(Exception):
    pass


class UserWithThisEmailAlreadyExistsError(Exception):
    pass


class UserWithThisUsernameAlreadyExistsError(Exception):
    pass