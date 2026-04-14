"""Errors for the text extraction subsystem."""

from minilog.errors import MinilogError


class DownloadError(MinilogError):
    """Raised when a source download or conversion fails."""

    def __init__(self, source: str, reason: str) -> None:
        self.source = source
        self.reason = reason
        super().__init__(f"Download failed for '{source}': {reason}")
