from fastapi import status


class AppException(Exception):
    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
    detail: str = "Internal server error"

    def __init__(self, detail: str | None = None) -> None:
        if detail is not None:
            self.detail = detail
        super().__init__(self.detail)


class FileTooLargeError(AppException):
    status_code = status.HTTP_413_CONTENT_TOO_LARGE
    detail = "File too large"


class FailedSaveDocumentError(AppException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    detail = "Failed to save document"


class DocumentDoesNotExistError(AppException):
    status_code = status.HTTP_404_NOT_FOUND
    detail = "Document does not exist"


class StoredFileNotFoundError(AppException):
    status_code = status.HTTP_404_NOT_FOUND
    detail = "File not found"


class FailedToDeleteDocumentError(AppException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    detail = "Failed to delete document"


class FailedChangeStatusError(AppException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    detail = "Failed to process document"


class DocumentAlreadyHandleError(AppException):
    status_code = status.HTTP_409_CONFLICT
    detail = "Document is already being processed"


class DocumentTextNotReadyError(AppException):
    status_code = status.HTTP_409_CONFLICT
    detail = "Document text is not ready"


class ProcessingError(AppException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    detail = "Document processing error"


class UnsupportedDocumentTypeError(ProcessingError):
    status_code = status.HTTP_415_UNSUPPORTED_MEDIA_TYPE
    detail = "Unsupported document type"
    def __init__(self, content_type: str | None = None):
        self.content_type = content_type
        super().__init__(self.detail)


class DocumentProcessingTimeoutError(ProcessingError):
    status_code = status.HTTP_504_GATEWAY_TIMEOUT
    detail = "Document processing timeout"


class DocumentDecodeError(ProcessingError):
    status_code = status.HTTP_422_UNPROCESSABLE_CONTENT
    detail = "Document content could not be decoded"


class DocumentReadError(ProcessingError):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    detail = "Failed to read document"


class InvalidPdfError(ProcessingError):
    status_code = 400
    detail = 'Invalid PDF'


class DocumentVersionDoesNotExist(AppException):
    status_code = 404
    detail = 'Version does not exist'