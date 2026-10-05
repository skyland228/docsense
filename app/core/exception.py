


class InvalidCredentialException(Exception):
    pass


class UserWithThisEmailAlreadyExistsError(Exception):
    pass


class UserWithThisUsernameAlreadyExistsError(Exception):
    pass


class FileTooLargeError(Exception):
    pass


class FailedSaveDocument(Exception):
    pass