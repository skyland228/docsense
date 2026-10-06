class InvalidCredentialExceptionError(Exception):
    pass


class UserWithThisEmailAlreadyExistsError(Exception):
    pass


class UserWithThisUsernameAlreadyExistsError(Exception):
    pass
