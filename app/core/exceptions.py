"""Domain and application exceptions."""


class FinTechChatbotException(Exception):
    """Base exception for all domain errors."""
    def __init__(self, message: str, status_code: int = 400):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class DocumentValidationError(FinTechChatbotException):
    def __init__(self, message: str):
        super().__init__(message, status_code=422)


class DocumentNotFoundError(FinTechChatbotException):
    def __init__(self, document_id: str):
        super().__init__(f"Document with ID '{document_id}' not found.", status_code=404)


class SourceNotFoundError(FinTechChatbotException):
    def __init__(self, source_id: str):
        super().__init__(f"Source with ID '{source_id}' not found.", status_code=404)


class IndexNotFoundError(FinTechChatbotException):
    def __init__(self, message: str = "Retrieval index is not built or unavailable."):
        super().__init__(message, status_code=503)


class CalculationError(FinTechChatbotException):
    def __init__(self, message: str):
        super().__init__(message, status_code=422)


class NoLLMPolicyViolationError(FinTechChatbotException):
    def __init__(self, message: str):
        super().__init__(f"No-LLM Policy Violation: {message}", status_code=403)
