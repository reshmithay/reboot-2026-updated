from datetime import datetime


class InvalidTransactionError(Exception):
    """Raised when a transaction payload fails validation."""
    pass


class AnomalyNotFoundError(Exception):
    """Raised when an anomaly record cannot be found."""
    pass


class BlockchainWriteError(Exception):
    """Raised when writing to the blockchain fails."""
    pass


class MLModelNotLoadedError(Exception):
    """Raised when the ML model file is missing or corrupt."""
    pass


class NarrativeGenerationError(Exception):
    """Raised when LLM narrative generation fails."""
    pass


class RateLimitError(Exception):
    """Raised when external API rate limits are exceeded."""

    def __init__(self, service: str, retry_after: int = 60):
        self.service = service
        self.retry_after = retry_after
        super().__init__(f"{service} rate limit exceeded. Retry after {retry_after}s.")
