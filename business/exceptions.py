class BusinessError(Exception):
    """Base class for business logic exceptions"""

    pass


class AuthenticationError(BusinessError):
    """Raised when authentication fails"""

    pass


class ValidationError(BusinessError):
    """Raised when business validation fails"""

    pass


class ResourceNotFoundError(BusinessError):
    """Raised when a requested resource is not found"""

    pass
