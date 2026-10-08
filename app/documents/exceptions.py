class FileTooLargeError(Exception):
    pass


class FailedSaveDocumentError(Exception):
    pass


class DocumentDoesNotExistError(Exception):
    pass


class StoredFileNotFoundError(Exception):
    pass


class FailedToDeleteDocumentError(Exception):
    pass


class FailedChangeStatusError(Exception):
    pass


class DocumentAlreadyHandleError(Exception):
    pass


class ProcessingError(Exception):
    """Базовое исключение для всех ошибок обработки."""
    pass

class UnsupportedDocumentTypeError(ProcessingError):
    pass

class DocumentProcessingTimeoutError(ProcessingError):
    pass

class DocumentDecodeError(ProcessingError):
    pass

class DocumentReadError(ProcessingError):
    pass


class DocumentTextNotReadyError(Exception):
    pass