"""Base class for Gold format adapters."""

from abc import ABC, abstractmethod

from formaforge.models.silver import CdmDocument


class BaseAdapter(ABC):
    adapter_name: str = ""

    @abstractmethod
    def render(self, doc: CdmDocument, **opts: str) -> str:
        """Render CdmDocument to a format-specific string."""

    def estimate_tokens(self, text: str) -> int:
        return max(1, len(text.encode()) // 4)
