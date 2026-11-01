class DomainError(Exception):
    """An expected failure that maps to an HTTP status and a client-safe message."""

    status_code = 500
    detail = "Unexpected error."

    def __init__(self, detail: str | None = None) -> None:
        self.detail = detail or self.detail
        super().__init__(self.detail)


class MalformedCustomerIdError(DomainError):
    status_code = 400
    detail = "Malformed x-customer-id header."


class UnknownCustomerError(DomainError):
    status_code = 400
    detail = "Unknown customer."
